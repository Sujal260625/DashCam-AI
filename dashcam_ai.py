"""
AI-Based Tesla-Style Dashcam Object Detection & Road Risk Analysis System
==========================================================================
Real-time pipeline: Vehicle/Pedestrian/Sign Detection (YOLOv8) +
Multi-object Tracking (ByteTrack) + Lane Detection (OpenCV) +
Monocular Distance & Time-to-Collision (TTC) Estimation +
Audio Warning Alerts (Non-blocking Beeps) + Live HUD Dashboard.

Works on:
  - Live webcam            : python dashcam_ai.py --source 0
  - A video file           : python dashcam_ai.py --source myvideo.mp4
  - RTSP/IP camera stream  : python dashcam_ai.py --source rtsp://...
"""

import argparse
import time
import threading
from collections import deque

import cv2
import numpy as np
from ultralytics import YOLO

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------

# COCO classes relevant to a dashcam scene
RELEVANT_CLASSES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    6: "train",
    7: "truck",
    9: "traffic light",
    11: "stop sign",
}

# Real-world approximate widths (meters) used for monocular distance estimation
KNOWN_WIDTH_M = {
    "car": 1.8,
    "truck": 2.5,
    "bus": 2.5,
    "motorcycle": 0.8,
    "bicycle": 0.6,
    "person": 0.5,
    "train": 3.0,
}

FOCAL_LENGTH_PX = 700  # approximate focal length in pixels; calibrate per camera for accuracy

RISK_COLORS = {
    "SAFE": (0, 200, 0),
    "CAUTION": (0, 200, 255),
    "DANGER": (0, 0, 255),
}


# --------------------------------------------------------------------------
# AUDIO ALERT SYSTEM (Non-blocking background chimes)
# --------------------------------------------------------------------------

class AudioAlertManager:
    """Distance-adaptive proximity audio warning manager.
    - Near object (<3.5m): Strong, rapid high-urgency beeps (BEEP! BEEP!).
    - Medium object (3.5m - 6.0m): Alert beeps.
    - Moving away (6.0m - 9.0m): Slower, gentler beeps.
    - Far away (>9.0m / clear): Beeps slow down and close completely (silence).
    """

    def __init__(self, enabled=True):
        self.enabled = enabled and HAS_WINSOUND
        self.last_beep_time = 0.0
        self.last_drift_time = 0.0
        self._is_beeping = False

    def update_proximity(self, min_distance=None, danger_count=0, caution_count=0, drift_alert=None):
        """Dynamically adjusts beep frequency & speed based on object proximity."""
        if not self.enabled:
            return

        now = time.time()

        if min_distance is not None and (danger_count > 0 or caution_count > 0):
            if min_distance < 3.5:
                # Critical / Very Near: Strong, rapid high-pitch double beep
                interval = 0.35
                pitch = 2200
                duration = 85
                is_double = True
            elif min_distance < 6.0:
                # Near / Danger: Fast warning beep
                interval = 0.65
                pitch = 1800
                duration = 100
                is_double = False
            elif min_distance < 9.0:
                # Approaching / Caution: Slow gentle beep
                interval = 1.35
                pitch = 1200
                duration = 110
                is_double = False
            else:
                # Far away / Object cleared: Silence (closed)
                interval = None

            if interval is not None and (now - self.last_beep_time >= interval):
                if not self._is_beeping:
                    self.last_beep_time = now
                    threading.Thread(
                        target=self._play_tone,
                        args=(pitch, duration, is_double),
                        daemon=True,
                    ).start()

        elif drift_alert is not None:
            if now - self.last_drift_time >= 2.0:
                self.last_drift_time = now
                threading.Thread(
                    target=self._play_tone,
                    args=(650, 150, False),
                    daemon=True,
                ).start()

    def _play_tone(self, freq, duration, is_double=False):
        self._is_beeping = True
        try:
            winsound.Beep(freq, duration)
            if is_double:
                time.sleep(0.04)
                winsound.Beep(freq + 250, duration)
        except Exception:
            pass
        finally:
            self._is_beeping = False

    def play_danger(self):
        self.update_proximity(min_distance=2.5, danger_count=1)

    def play_caution(self):
        self.update_proximity(min_distance=6.5, caution_count=1)

    def play_drift(self):
        self.update_proximity(min_distance=None, drift_alert="DRIFT")


# --------------------------------------------------------------------------
# LANE DETECTION (classic OpenCV approach: ROI -> Canny -> Hough -> average)
# --------------------------------------------------------------------------

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    return cv2.bitwise_and(img, mask)


def average_slope_intercept(lines, img_shape):
    left_fit, right_fit = [], []
    if lines is None:
        return None, None
    lines = np.asarray(lines).reshape(-1, 4)
    for line in lines:
        x1, y1, x2, y2 = int(line[0]), int(line[1]), int(line[2]), int(line[3])
        if x2 == x1:
            continue
        slope, intercept = np.polyfit((x1, x2), (y1, y2), 1)
        if abs(slope) < 0.3:  # ignore near-horizontal noise
            continue
        if slope < 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))

    h = img_shape[0]

    def make_line(fit):
        if not fit:
            return None
        slope, intercept = np.average(fit, axis=0)
        y1 = h
        y2 = int(h * 0.62)
        if slope == 0:
            return None
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        return (x1, y1, x2, y2)

    return make_line(left_fit), make_line(right_fit)


def detect_lanes(frame):
    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    roi_vertices = np.array([[
        (int(w * 0.05), h),
        (int(w * 0.45), int(h * 0.60)),
        (int(w * 0.55), int(h * 0.60)),
        (int(w * 0.95), h),
    ]], dtype=np.int32)
    cropped = region_of_interest(edges, roi_vertices)

    lines = cv2.HoughLinesP(
        cropped, 2, np.pi / 180, threshold=45,
        minLineLength=40, maxLineGap=100,
    )
    left, right = average_slope_intercept(lines, frame.shape)

    overlay = np.zeros_like(frame)
    lane_center_offset = None
    for ln in (left, right):
        if ln:
            cv2.line(overlay, (ln[0], ln[1]), (ln[2], ln[3]), (0, 255, 255), 8)

    if left and right:
        bottom_mid_lane = (left[0] + right[0]) / 2
        frame_center = w / 2
        lane_center_offset = (bottom_mid_lane - frame_center)  # px, +right / -left

    return overlay, lane_center_offset


# --------------------------------------------------------------------------
# MONOCULAR DISTANCE & TIME-TO-COLLISION (TTC)
# --------------------------------------------------------------------------

def estimate_distance_m(cls_name, bbox_w_px):
    real_w = KNOWN_WIDTH_M.get(cls_name)
    if real_w is None or bbox_w_px <= 1:
        return None
    return (real_w * FOCAL_LENGTH_PX) / bbox_w_px


def calculate_ttc(track_history, current_time, current_dist):
    """
    Computes closing speed (v_rel in m/s) and Time-to-Collision (TTC in seconds).
    Returns (ttc_seconds, v_rel_mps).
    """
    if current_dist is None or not track_history:
        return None, 0.0

    # Look back ~0.20 to 0.60 seconds in the tracking history to smooth out noise
    t_old, d_old = track_history[0]
    for past_t, past_d in track_history:
        if (current_time - past_t) >= 0.15:
            t_old, d_old = past_t, past_d
            break

    dt = current_time - t_old
    if dt < 0.10:
        return None, 0.0

    dd = current_dist - d_old
    v_rel = dd / dt  # m/s (negative = getting closer)

    # If closing in at more than 0.4 m/s (~1.5 km/h)
    if v_rel < -0.4:
        closing_speed = -v_rel
        ttc = current_dist / closing_speed
        return max(0.1, ttc), v_rel

    return None, v_rel


def classify_risk(cls_name, distance_m, box, frame_shape, ttc=None):
    """
    Dynamic risk classification combining distance, trajectory corridor,
    and Time-To-Collision (TTC).
    """
    h, w = frame_shape[:2]
    x1, y1, x2, y2 = box
    box_center_x = (x1 + x2) / 2
    in_path = (w * 0.30 < box_center_x < w * 0.70)
    near_bottom = y2 > h * 0.55

    # High-Priority TTC Trigger (Urgent Collision Imminent)
    if ttc is not None and in_path:
        if ttc < 2.0:
            return "DANGER", distance_m
        elif ttc < 3.5:
            return "CAUTION", distance_m

    if distance_m is None:
        level = "CAUTION" if near_bottom else "SAFE"
        return level, distance_m

    if cls_name == "person":
        if distance_m < 8 and in_path:
            level = "DANGER"
        elif distance_m < 15:
            level = "CAUTION"
        else:
            level = "SAFE"
    else:  # vehicles
        if distance_m < 6 and in_path:
            level = "DANGER"
        elif distance_m < 12:
            level = "CAUTION"
        else:
            level = "SAFE"

    return level, distance_m


# --------------------------------------------------------------------------
# DASHBOARD OVERLAY
# --------------------------------------------------------------------------

def draw_dashboard(frame, tracks, lane_overlay, lane_offset, fps):
    out = frame.copy()
    if lane_overlay is not None:
        out = cv2.addWeighted(out, 1.0, lane_overlay, 0.9, 0)

    danger_count = caution_count = 0
    min_ttc = None

    for t in tracks:
        x1, y1, x2, y2 = t["box"]
        color = RISK_COLORS[t["risk"]]
        if t["risk"] == "DANGER":
            danger_count += 1
        elif t["risk"] == "CAUTION":
            caution_count += 1

        ttc = t.get("ttc")
        if ttc is not None and t["risk"] in ("DANGER", "CAUTION"):
            if min_ttc is None or ttc < min_ttc:
                min_ttc = ttc

        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        dist_txt = f"{t['distance']:.1f}m" if t["distance"] else "?"
        ttc_txt = f" TTC:{ttc:.1f}s" if ttc is not None else ""
        label = f"ID{t['id']} {t['cls']} {dist_txt}{ttc_txt} [{t['risk']}]"

        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
        cv2.rectangle(out, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
        cv2.putText(out, label, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX,
                    0.48, (0, 0, 0), 1, cv2.LINE_AA)

    # Top Status Bar
    h, w = out.shape[:2]
    cv2.rectangle(out, (0, 0), (w, 36), (15, 20, 28), -1)
    status = "ALL CLEAR"
    status_color = RISK_COLORS["SAFE"]

    if danger_count:
        ttc_alert = f" (TTC: {min_ttc:.1f}s!)" if min_ttc else ""
        status = f"DANGER x{danger_count}{ttc_alert}"
        status_color = RISK_COLORS["DANGER"]
    elif caution_count:
        status = f"CAUTION x{caution_count}"
        status_color = RISK_COLORS["CAUTION"]

    cv2.putText(out, f"ROAD STATUS: {status}", (12, 24), cv2.FONT_HERSHEY_SIMPLEX,
                0.62, status_color, 2, cv2.LINE_AA)
    cv2.putText(out, f"FPS: {fps:.1f}", (w - 115, 24), cv2.FONT_HERSHEY_SIMPLEX,
                0.58, (255, 255, 255), 2, cv2.LINE_AA)

    # Lane Drift Indicator
    drift_alert = None
    if lane_offset is not None:
        direction = "CENTER"
        badge_color = (0, 255, 255)
        if lane_offset > 25:
            direction = "DRIFT RIGHT"
            badge_color = (0, 165, 255)
            drift_alert = "RIGHT"
        elif lane_offset < -25:
            direction = "DRIFT LEFT"
            badge_color = (0, 165, 255)
            drift_alert = "LEFT"
        cv2.putText(out, f"LANE: {direction}", (w // 2 - 75, h - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, badge_color, 2, cv2.LINE_AA)

    return out, danger_count, caution_count, drift_alert


# --------------------------------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------------------------------

def run(source, weights="yolov8n.pt", conf=0.35, save_path=None, show=True,
        imgsz=640, max_frames=None, sound=True):
    model = YOLO(weights)
    audio = AudioAlertManager(enabled=sound)

    try:
        src = int(source)
    except ValueError:
        src = source

    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source: {source}")

    fps_in = cap.get(cv2.CAP_PROP_FPS) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = None
    if save_path:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(save_path, fourcc, fps_in, (w, h))

    frame_idx = 0
    fps_hist = deque(maxlen=30)
    # Track ID -> deque of (timestamp, distance_m)
    track_histories = {}

    print(f"[INFO] Source opened: {source}  ({w}x{h} @ {fps_in:.1f}fps)")
    print(f"[INFO] Audio alerts: {'ENABLED' if audio.enabled else 'DISABLED'}")
    print("[INFO] Press 'q' to quit (when --show is enabled).")

    while True:
        t0 = time.time()
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if max_frames and frame_idx > max_frames:
            break

        now = time.time()

        # ---- Detection + Tracking (YOLOv8 + ByteTrack) ----
        results = model.track(
            frame, persist=True, conf=conf, imgsz=imgsz,
            classes=list(RELEVANT_CLASSES.keys()), tracker="bytetrack.yaml",
            verbose=False,
        )

        tracks = []
        r = results[0]
        if r.boxes is not None and r.boxes.id is not None:
            boxes = r.boxes.xyxy.cpu().numpy()
            ids = r.boxes.id.cpu().numpy().astype(int)
            clss = r.boxes.cls.cpu().numpy().astype(int)

            for box, tid, c in zip(boxes, ids, clss):
                x1, y1, x2, y2 = map(int, box)
                cls_name = RELEVANT_CLASSES.get(c, str(c))
                bbox_w = x2 - x1

                # Reject ego-vehicle hood detection at bottom of windshield
                h_f, w_f = frame.shape[:2]
                if y2 >= h_f * 0.85 and y1 >= h_f * 0.55 and bbox_w >= w_f * 0.35:
                    continue

                distance = estimate_distance_m(cls_name, bbox_w)

                # Maintain history for velocity & TTC
                if tid not in track_histories:
                    track_histories[tid] = deque(maxlen=20)

                ttc = None
                v_rel = 0.0
                if distance is not None:
                    ttc, v_rel = calculate_ttc(track_histories[tid], now, distance)
                    track_histories[tid].append((now, distance))

                risk, distance = classify_risk(cls_name, distance, (x1, y1, x2, y2), frame.shape, ttc=ttc)

                tracks.append({
                    "id": tid, "cls": cls_name, "box": (x1, y1, x2, y2),
                    "distance": distance, "ttc": ttc, "v_rel": v_rel, "risk": risk,
                })

        # Purge stale track histories periodically
        if frame_idx % 150 == 0:
            current_ids = {t["id"] for t in tracks}
            for tid in list(track_histories.keys()):
                if tid not in current_ids and track_histories[tid] and (now - track_histories[tid][-1][0] > 3.0):
                    del track_histories[tid]

        # ---- Lane Detection ----
        lane_overlay, lane_offset = detect_lanes(frame)

        # ---- FPS ----
        dt = time.time() - t0
        fps_hist.append(1.0 / dt if dt > 0 else 0)
        fps = sum(fps_hist) / len(fps_hist)

        # ---- Dashboard & Audio Alert Triggers ----
        dashboard, danger_count, caution_count, drift_alert = draw_dashboard(
            frame, tracks, lane_overlay, lane_offset, fps
        )

        min_dist = None
        for t in tracks:
            if t.get("distance") is not None and t["risk"] in ("DANGER", "CAUTION"):
                if min_dist is None or t["distance"] < min_dist:
                    min_dist = t["distance"]

        audio.update_proximity(
            min_distance=min_dist,
            danger_count=danger_count,
            caution_count=caution_count,
            drift_alert=drift_alert,
        )

        if writer:
            writer.write(dashboard)
        if show:
            cv2.imshow("Dashcam AI - Road Risk Analysis", dashboard)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if writer:
        writer.release()
    if show:
        cv2.destroyAllWindows()
    print(f"[INFO] Pipeline completed. Total frames processed: {frame_idx}")


def main():
    ap = argparse.ArgumentParser(description="Real-time Dashcam AI Road Risk System with TTC & Audio Alerts")
    ap.add_argument("--source", default="0", help="0 for webcam, or path/URL to video/RTSP stream")
    ap.add_argument("--weights", default="yolov8n.pt", help="YOLOv8 weights (n/s/m/l/x)")
    ap.add_argument("--conf", type=float, default=0.35, help="Detection confidence threshold")
    ap.add_argument("--imgsz", type=int, default=640, help="Inference image size")
    ap.add_argument("--save", default=None, help="Path to save annotated output video (mp4)")
    ap.add_argument("--no-show", action="store_true", help="Disable live display window")
    ap.add_argument("--no-sound", action="store_true", help="Disable audio beep alerts")
    ap.add_argument("--max-frames", type=int, default=None, help="Limit frames (for testing)")
    args = ap.parse_args()

    run(
        source=args.source, weights=args.weights, conf=args.conf,
        save_path=args.save, show=not args.no_show, imgsz=args.imgsz,
        max_frames=args.max_frames, sound=not args.no_sound,
    )


if __name__ == "__main__":
    main()
