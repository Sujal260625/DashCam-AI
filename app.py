"""
AI Dashcam Object Detection & Road Risk Analysis System
=========================================================
Real-Time Interactive Streamlit Dashboard

Features:
- Automatic 0% to 100% real-time progress bar when dashcam video is uploaded
- Automatic transition to Play and Stop controls upon completion
- Dynamic real-time updating telemetry (FPS, distance, TTC, speeds, hazards)
- Ego-vehicle hood rejection filter
- Clean, icon-free dark ADAS interface
"""

import os
import tempfile
import time
from collections import deque
import warnings

warnings.filterwarnings("ignore")

import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO

from dashcam_ai import (
    AudioAlertManager,
    KNOWN_WIDTH_M,
    RELEVANT_CLASSES,
    classify_risk,
    detect_lanes,
    draw_dashboard,
    estimate_distance_m,
)


def safe_render_image(placeholder, img):
    """Renders video frame cleanly across Streamlit versions without warnings."""
    try:
        if isinstance(img, np.ndarray):
            placeholder.image(img, channels="RGB", width="stretch")
        else:
            placeholder.image(img, width="stretch")
    except (TypeError, ValueError):
        if isinstance(img, np.ndarray):
            placeholder.image(img, channels="RGB", use_container_width=True)
        else:
            placeholder.image(img, use_container_width=True)


# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashcam AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { background-color: #070a13; }
    .stApp { background-color: #070a13; color: #f8fafc; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Top KPI Cards */
    .kpi-card {
        background: #111726;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: center;
    }
    .kpi-val {
        font-size: 22px;
        font-weight: 800;
        color: #06b6d4;
        font-family: monospace;
    }
    .kpi-lbl {
        font-size: 11px;
        font-weight: 600;
        color: #94a3b8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-top: 2px;
    }
    
    /* Road Status Badges */
    .badge-clear {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid #10b981;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 800;
        text-align: center;
        font-size: 18px;
    }
    .badge-caution {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid #f59e0b;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 800;
        text-align: center;
        font-size: 18px;
    }
    .badge-danger {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 800;
        text-align: center;
        font-size: 18px;
        animation: pulse-danger 1s infinite alternate;
    }
    @keyframes pulse-danger {
        from { box-shadow: 0 0 4px #ef4444; }
        to { box-shadow: 0 0 16px #ef4444; }
    }
    
    /* Progress section */
    .progress-box {
        background: #111726;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 16px;
    }
    .progress-title {
        font-size: 14px;
        font-weight: 700;
        color: #06b6d4;
        margin-bottom: 8px;
    }
    
    /* Obstacle cards */
    .obstacle-pill {
        background: #111726;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
    }
    .tag-danger { color: #ef4444; font-weight: 700; background: rgba(239,68,68,0.15); padding: 2px 8px; border-radius: 4px; }
    .tag-caution { color: #f59e0b; font-weight: 700; background: rgba(245,158,11,0.15); padding: 2px 8px; border-radius: 4px; }
    .tag-safe { color: #10b981; font-weight: 700; background: rgba(16,185,129,0.15); padding: 2px 8px; border-radius: 4px; }
    
    /* Clean button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 8px 20px !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"] {
        background-color: rgba(239, 68, 68, 0.15) !important;
        color: #ef4444 !important;
        border: 1px solid #ef4444 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #ef4444 !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# SIDEBAR SETTINGS
# -----------------------------------------------------------------------------
st.sidebar.title("ADAS Settings")

# Dashcam Video Upload
st.sidebar.subheader("Dashcam Video")
uploaded_file = st.sidebar.file_uploader(
    "Upload Video File (MP4 / AVI / MOV)",
    type=["mp4", "avi", "mov", "mkv"],
    help="Upload your recorded dashcam driving video",
)

video_source = None
CACHE_DIR = os.path.join(tempfile.gettempdir(), "dashcam_ai_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

if uploaded_file is not None:
    cached_path = os.path.join(CACHE_DIR, uploaded_file.name)
    if not os.path.exists(cached_path) or os.path.getsize(cached_path) != uploaded_file.size:
        with open(cached_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    video_source = cached_path

st.sidebar.markdown("---")

# Automated Optimized ADAS Parameters
model_name = "yolov8n.pt"
conf_thresh = 0.35
imgsz = 640
focal_length = 700

# Toggles
enable_lanes = st.sidebar.checkbox("Lane Detection", value=True)
enable_sound = st.sidebar.checkbox("Audio Beep Alerts", value=True)
loop_video = st.sidebar.checkbox("Continuous Loop Video", value=True)

# -----------------------------------------------------------------------------
# MAIN DASHBOARD UI
# -----------------------------------------------------------------------------

# Top KPI Telemetry Row (4 Clean Columns)
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_ph = st.empty()
    status_ph.markdown('<div class="badge-clear">ALL CLEAR</div>', unsafe_allow_html=True)

with col2:
    fps_ph = st.empty()
    fps_ph.markdown('<div class="kpi-card"><div class="kpi-val">0.0</div><div class="kpi-lbl">PIPELINE FPS</div></div>', unsafe_allow_html=True)

with col3:
    count_ph = st.empty()
    count_ph.markdown('<div class="kpi-card"><div class="kpi-val">0</div><div class="kpi-lbl">TRACKED OBJECTS</div></div>', unsafe_allow_html=True)

with col4:
    lane_ph = st.empty()
    lane_ph.markdown('<div class="kpi-card"><div class="kpi-val">-</div><div class="kpi-lbl">LANE STATUS</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Progress section placeholder
progress_box_ph = st.empty()

# Main Content Grid: Video on Left, Telemetry Table on Right
col_left, col_right = st.columns([1.75, 1.0])

with col_left:
    video_ph = st.empty()
    if video_source is None:
        video_ph.info("Upload a dashcam video file in the sidebar to begin.")

with col_right:
    st.markdown("##### Live Obstacle Telemetry")
    table_ph = st.empty()
    table_ph.caption("No obstacles currently detected.")

# Controls placeholder (Play/Stop buttons)
controls_ph = st.empty()

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "processed_video_id" not in st.session_state:
    st.session_state.processed_video_id = None
if "processed_frames" not in st.session_state:
    st.session_state.processed_frames = []
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False
if "current_frame_idx" not in st.session_state:
    st.session_state.current_frame_idx = 0
if "playback_fps" not in st.session_state:
    st.session_state.playback_fps = 30.0

# -----------------------------------------------------------------------------
# PHASE 1: AUTOMATIC 0% TO 100% VIDEO PROCESSING
# -----------------------------------------------------------------------------
current_config_id = None
if uploaded_file is not None:
    current_config_id = f"{uploaded_file.name}_{uploaded_file.size}_{model_name}_{conf_thresh}_{imgsz}_{focal_length}_{enable_lanes}"

needs_processing = (
    video_source is not None
    and st.session_state.processed_video_id != current_config_id
)

if needs_processing:
    # Reset any active playback
    st.session_state.is_playing = False
    st.session_state.current_frame_idx = 0
    st.session_state.processed_frames = []

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        st.error(f"Could not open video stream: {video_source}")
    else:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            total_frames = 150  # reasonable fallback
        fps_in = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_time_step = 1.0 / fps_in
        st.session_state.playback_fps = fps_in

        # Temporary focal length override
        import dashcam_ai
        dashcam_ai.FOCAL_LENGTH_PX = focal_length

        model = YOLO(model_name)

        with progress_box_ph.container():
            prog_title_ph = st.empty()
            prog_bar_ph = st.empty()
            prog_title_ph.markdown('<div class="progress-title">Processing video: 0%</div>', unsafe_allow_html=True)
            prog_bar_ph.progress(0.0)

        frames_data = []
        track_histories = {}
        frame_idx = 0
        fps_hist = deque(maxlen=20)

        while True:
            t_start = time.time()
            ok, frame = cap.read()
            if not ok:
                break

            frame_idx += 1
            video_clock = frame_idx * frame_time_step
            h_f, w_f = frame.shape[:2]

            # YOLOv8 + ByteTrack
            results = model.track(
                frame,
                persist=True,
                conf=conf_thresh,
                imgsz=imgsz,
                classes=list(RELEVANT_CLASSES.keys()),
                tracker="bytetrack.yaml",
                verbose=False,
            )

            tracks = []
            obstacles_list = []
            r = results[0]

            if r.boxes is not None and r.boxes.id is not None:
                boxes = r.boxes.xyxy.cpu().numpy()
                ids = r.boxes.id.cpu().numpy().astype(int)
                clss = r.boxes.cls.cpu().numpy().astype(int)

                for box, tid, c in zip(boxes, ids, clss):
                    x1, y1, x2, y2 = map(int, box)
                    cls_name = RELEVANT_CLASSES.get(c, str(c))
                    bbox_w = x2 - x1

                    # Ego-vehicle hood rejection filter
                    if y2 >= h_f * 0.85 and y1 >= h_f * 0.55 and bbox_w >= w_f * 0.35:
                        continue

                    distance = estimate_distance_m(cls_name, bbox_w)

                    if tid not in track_histories:
                        track_histories[tid] = deque(maxlen=25)

                    ttc = None
                    v_rel_kmh = 0.0

                    if distance is not None:
                        history = track_histories[tid]
                        if len(history) >= 2:
                            past_t, past_d = history[0]
                            for pt, pd_val in history:
                                if (video_clock - pt) >= 0.12:
                                    past_t, past_d = pt, pd_val
                                    break
                            dt = video_clock - past_t
                            if dt >= 0.08:
                                dd = distance - past_d
                                v_rel_mps = dd / dt
                                v_rel_kmh = v_rel_mps * 3.6
                                if v_rel_mps < -0.3:
                                    closing_speed = -v_rel_mps
                                    ttc = max(0.1, distance / closing_speed)

                        history.append((video_clock, distance))

                    risk, distance = classify_risk(
                        cls_name, distance, (x1, y1, x2, y2), frame.shape, ttc=ttc
                    )

                    tracks.append({
                        "id": tid,
                        "cls": cls_name,
                        "box": (x1, y1, x2, y2),
                        "distance": distance,
                        "ttc": ttc,
                        "v_rel": v_rel_kmh,
                        "risk": risk,
                    })

                    dist_text = f"{distance:.1f} m" if distance else "N/A"
                    ttc_text = f"{ttc:.1f} s" if ttc is not None else "--"
                    speed_text = f"{v_rel_kmh:+.0f} km/h" if v_rel_kmh != 0.0 else "0 km/h"

                    obstacles_list.append({
                        "ID": f"ID-{tid}",
                        "Class": cls_name.capitalize(),
                        "Distance": dist_text,
                        "TTC": ttc_text,
                        "Speed": speed_text,
                        "Risk": risk,
                    })

            # Lane Detection
            lane_overlay = None
            lane_offset = None
            if enable_lanes:
                lane_overlay, lane_offset = detect_lanes(frame)

            t_elapsed = time.time() - t_start
            fps_hist.append(1.0 / t_elapsed if t_elapsed > 0 else 30.0)
            fps = sum(fps_hist) / len(fps_hist)

            dashboard, danger_count, caution_count, drift_alert = draw_dashboard(
                frame, tracks, lane_overlay, lane_offset, fps
            )

            # Compress to JPEG bytes for low-memory storage
            ret, buf = cv2.imencode(".jpg", dashboard, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_bytes = buf.tobytes()

            min_dist = None
            for t in tracks:
                if t.get("distance") is not None and t["risk"] in ("DANGER", "CAUTION"):
                    if min_dist is None or t["distance"] < min_dist:
                        min_dist = t["distance"]

            frames_data.append({
                "frame_bytes": frame_bytes,
                "danger_count": danger_count,
                "caution_count": caution_count,
                "drift_alert": drift_alert,
                "min_distance": min_dist,
                "fps": fps,
                "lane_offset": lane_offset,
                "tracks_count": len(tracks),
                "obstacles": obstacles_list,
            })

            # Update 0% to 100% progress in-place (no new lines appended)
            if frame_idx % 4 == 0 or frame_idx == total_frames:
                progress_pct = min(1.0, frame_idx / total_frames)
                prog_bar_ph.progress(progress_pct)
                prog_title_ph.markdown(
                    f'<div class="progress-title">Processing video: {int(progress_pct * 100)}% (Frame {frame_idx} of {total_frames})</div>',
                    unsafe_allow_html=True,
                )

        cap.release()

        # Complete progress
        prog_bar_ph.progress(1.0)
        prog_title_ph.markdown(
            '<div class="progress-title" style="color: #10b981;">Processing complete: 100%</div>',
            unsafe_allow_html=True,
        )

        st.session_state.processed_frames = frames_data
        st.session_state.processed_video_id = current_config_id
        st.session_state.is_playing = True  # Automatically ready to play
        st.session_state.current_frame_idx = 0
        time.sleep(0.4)
        st.rerun()

# -----------------------------------------------------------------------------
# PHASE 2: PLAYBACK CONTROLS (APPEARS AUTOMATICALLY AFTER PROCESSING)
# -----------------------------------------------------------------------------
is_processed = (
    video_source is not None
    and st.session_state.processed_video_id == current_config_id
    and len(st.session_state.processed_frames) > 0
)

if is_processed:
    progress_box_ph.empty()  # Hide progress bar once ready

    # Render Play / Stop controls
    with controls_ph.container():
        ctrl_col1, ctrl_col2, ctrl_col3, _ = st.columns([1.2, 1.2, 1.2, 2.4])

        if not st.session_state.is_playing:
            if ctrl_col1.button("Play Video", type="primary", key="btn_play"):
                st.session_state.is_playing = True
                st.rerun()
        else:
            if ctrl_col1.button("Stop Pipeline", type="secondary", key="btn_stop"):
                st.session_state.is_playing = False
                st.rerun()

        if ctrl_col2.button("Restart", key="btn_restart"):
            st.session_state.current_frame_idx = 0
            st.session_state.is_playing = True
            st.rerun()

        if ctrl_col3.button("Re-process", key="btn_reprocess"):
            st.session_state.processed_video_id = None
            st.session_state.processed_frames = []
            st.session_state.is_playing = False
            st.rerun()

    # -------------------------------------------------------------------------
    # REAL-TIME PLAYBACK LOOP
    # -------------------------------------------------------------------------
    frames = st.session_state.processed_frames
    num_frames = len(frames)
    audio = AudioAlertManager(enabled=enable_sound)
    target_fps = st.session_state.playback_fps or 30.0
    frame_interval = 1.0 / target_fps

    if st.session_state.is_playing:
        start_idx = st.session_state.current_frame_idx

        for idx in range(start_idx, num_frames):
            if not st.session_state.is_playing:
                break

            t0 = time.time()
            data = frames[idx]
            st.session_state.current_frame_idx = idx

            # 1. Update Video Frame
            safe_render_image(video_ph, data["frame_bytes"])

            # 2. Update Status Banner
            if data["danger_count"] > 0:
                status_ph.markdown(
                    f'<div class="badge-danger">DANGER ({data["danger_count"]})</div>',
                    unsafe_allow_html=True,
                )
            elif data["caution_count"] > 0:
                status_ph.markdown(
                    f'<div class="badge-caution">CAUTION ({data["caution_count"]})</div>',
                    unsafe_allow_html=True,
                )
            else:
                status_ph.markdown(
                    '<div class="badge-clear">ALL CLEAR</div>',
                    unsafe_allow_html=True,
                )

            # 3. Update Dynamic Telemetry Cards
            fps_ph.markdown(
                f'<div class="kpi-card"><div class="kpi-val">{data["fps"]:.1f}</div><div class="kpi-lbl">PIPELINE FPS</div></div>',
                unsafe_allow_html=True,
            )
            count_ph.markdown(
                f'<div class="kpi-card"><div class="kpi-val">{data["tracks_count"]}</div><div class="kpi-lbl">TRACKED OBJECTS</div></div>',
                unsafe_allow_html=True,
            )

            lane_disp = "CENTER"
            if data["lane_offset"] is not None:
                if data["lane_offset"] > 25:
                    lane_disp = "DRIFT RIGHT"
                elif data["lane_offset"] < -25:
                    lane_disp = "DRIFT LEFT"
            lane_ph.markdown(
                f'<div class="kpi-card"><div class="kpi-val">{lane_disp}</div><div class="kpi-lbl">LANE STATUS</div></div>',
                unsafe_allow_html=True,
            )

            # 4. Update Dynamic Obstacles List
            if data["obstacles"]:
                cards_html = ""
                for obs in data["obstacles"]:
                    risk_class = "tag-safe"
                    if obs["Risk"] == "DANGER":
                        risk_class = "tag-danger"
                    elif obs["Risk"] == "CAUTION":
                        risk_class = "tag-caution"

                    cards_html += f"""
                    <div class="obstacle-pill">
                        <div><strong>{obs['ID']}</strong> ({obs['Class']})</div>
                        <div>{obs['Distance']} | TTC: {obs['TTC']} | {obs['Speed']}</div>
                        <div class="{risk_class}">{obs['Risk']}</div>
                    </div>
                    """
                table_ph.markdown(cards_html, unsafe_allow_html=True)
            else:
                table_ph.caption("No obstacles in forward corridor.")

            # 5. Audio Alert Triggers (Distance-Adaptive Proximity Beeping)
            audio.update_proximity(
                min_distance=data.get("min_distance"),
                danger_count=data["danger_count"],
                caution_count=data["caution_count"],
                drift_alert=data["drift_alert"],
            )

            # Pacing for real-time video playback speed
            elapsed = time.time() - t0
            sleep_time = max(0.005, frame_interval - elapsed)
            time.sleep(sleep_time)

        # Loop or end handling
        if st.session_state.is_playing:
            if loop_video:
                st.session_state.current_frame_idx = 0
                st.rerun()
            else:
                st.session_state.is_playing = False
                st.rerun()

    else:
        # Paused state display (shows current paused frame and telemetry)
        curr_idx = min(st.session_state.current_frame_idx, num_frames - 1)
        if curr_idx >= 0 and curr_idx < num_frames:
            data = frames[curr_idx]
            safe_render_image(video_ph, data["frame_bytes"])

            if data["danger_count"] > 0:
                status_ph.markdown(
                    f'<div class="badge-danger">DANGER ({data["danger_count"]})</div>',
                    unsafe_allow_html=True,
                )
            elif data["caution_count"] > 0:
                status_ph.markdown(
                    f'<div class="badge-caution">CAUTION ({data["caution_count"]})</div>',
                    unsafe_allow_html=True,
                )
            else:
                status_ph.markdown(
                    '<div class="badge-clear">ALL CLEAR</div>',
                    unsafe_allow_html=True,
                )

            fps_ph.markdown(
                f'<div class="kpi-card"><div class="kpi-val">{data["fps"]:.1f}</div><div class="kpi-lbl">PIPELINE FPS</div></div>',
                unsafe_allow_html=True,
            )
            count_ph.markdown(
                f'<div class="kpi-card"><div class="kpi-val">{data["tracks_count"]}</div><div class="kpi-lbl">TRACKED OBJECTS</div></div>',
                unsafe_allow_html=True,
            )

            lane_disp = "CENTER"
            if data["lane_offset"] is not None:
                if data["lane_offset"] > 25:
                    lane_disp = "DRIFT RIGHT"
                elif data["lane_offset"] < -25:
                    lane_disp = "DRIFT LEFT"
            lane_ph.markdown(
                f'<div class="kpi-card"><div class="kpi-val">{lane_disp}</div><div class="kpi-lbl">LANE STATUS</div></div>',
                unsafe_allow_html=True,
            )

            if data["obstacles"]:
                cards_html = ""
                for obs in data["obstacles"]:
                    risk_class = "tag-safe"
                    if obs["Risk"] == "DANGER":
                        risk_class = "tag-danger"
                    elif obs["Risk"] == "CAUTION":
                        risk_class = "tag-caution"

                    cards_html += f"""
                    <div class="obstacle-pill">
                        <div><strong>{obs['ID']}</strong> ({obs['Class']})</div>
                        <div>{obs['Distance']} | TTC: {obs['TTC']} | {obs['Speed']}</div>
                        <div class="{risk_class}">{obs['Risk']}</div>
                    </div>
                    """
                table_ph.markdown(cards_html, unsafe_allow_html=True)
            else:
                table_ph.caption("No obstacles in forward corridor.")
