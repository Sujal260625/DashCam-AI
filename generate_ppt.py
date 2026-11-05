"""
Image-Centric, Modern White-Theme Presentation Generator (.pptx)
for the Dashcam AI: Real-Time Object Detection & Road Risk Analysis System.

Birla Vishvakarma Mahavidyalaya (BVM Engineering College)
Department of Information Technology
Student: Sujal Patel (ID: 23IT401)
Mentor: Dhruvin R. Kotak
"""

import sys
import os
import urllib.request

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("python-pptx is not installed. Run: pip install python-pptx")
    sys.exit(1)

# Paths to visual assets
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_BRAIN_DIR = r"C:\Users\Shree_Ganesh99\.gemini\antigravity\brain\894dad48-f3ca-4547-a6a3-91ef0a1a0c77"

IMG_HERO = os.path.join(BASE_BRAIN_DIR, "dashcam_ai_hero_1791798311487.jpg")
IMG_TRACKING = os.path.join(BASE_BRAIN_DIR, "yolo_bytetrack_demo_1791798343186.jpg")
IMG_LANES = os.path.join(BASE_BRAIN_DIR, "lane_detection_visual_1791798365777.jpg")
IMG_DISTANCE = os.path.join(BASE_BRAIN_DIR, "monocular_distance_math_1791798388185.jpg")
IMG_RISK = os.path.join(BASE_BRAIN_DIR, "risk_zones_visual_1791798418268.jpg")
IMG_HUD = os.path.join(BASE_BRAIN_DIR, "hud_telemetry_ui_1791798448242.jpg")
IMG_HARDWARE = os.path.join(BASE_BRAIN_DIR, "edge_hardware_dashcam_1791798494160.jpg")

BVM_LOGO_PATH = os.path.join(SCRIPT_DIR, "bvm_logo.png")


def ensure_bvm_logo():
    """Downloads BVM Engineering College logo if not already cached locally."""
    if os.path.exists(BVM_LOGO_PATH) and os.path.getsize(BVM_LOGO_PATH) > 1000:
        return BVM_LOGO_PATH

    urls = [
        "https://upload.wikimedia.org/wikipedia/en/2/2c/Birla_Vishvakarma_Mahavidyalaya_logo.png",
        "https://bvmengineering.ac.in/assets/images/bvm-logo-1.png",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                if len(data) > 1000:
                    with open(BVM_LOGO_PATH, "wb") as f:
                        f.write(data)
                    return BVM_LOGO_PATH
        except Exception:
            continue
    return None


def build_visual_presentation():
    logo_file = ensure_bvm_logo()

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # -------------------------------------------------------------------------
    # MODERN CLEAN WHITE THEME COLOR PALETTE
    # -------------------------------------------------------------------------
    BG_WHITE = RGBColor(255, 255, 255)         # Pure White
    PAGE_LIGHT = RGBColor(248, 250, 252)       # Light Slate Background #f8fafc
    CARD_BG = RGBColor(255, 255, 255)          # White Card
    CARD_BORDER = RGBColor(226, 232, 240)      # Clean Slate Border #e2e8f0

    TEXT_TITLE = RGBColor(15, 23, 42)          # Deep Charcoal Navy #0f172a
    TEXT_SUBTITLE = RGBColor(30, 41, 59)       # Slate #1e293b
    TEXT_BODY = RGBColor(51, 65, 85)           # Body Slate #334155
    TEXT_MUTED = RGBColor(100, 116, 139)       # Muted Text #64748b

    ACCENT_BLUE = RGBColor(29, 78, 216)        # Royal Blue #1d4ed8
    ACCENT_CYAN = RGBColor(14, 116, 144)       # Deep Cyan / Teal #0e7490
    BVM_RED = RGBColor(185, 28, 28)            # BVM Crimson / Maroon #b91c1c
    SAFE_GREEN = RGBColor(16, 149, 97)         # Emerald Green #10b981
    WARN_AMBER = RGBColor(217, 119, 6)         # Deep Amber #d97706
    DANGER_RED = RGBColor(220, 38, 38)         # Alert Red #dc2626

    blank_layout = prs.slide_layouts[6]

    def add_slide_scaffold(title, badge_text, slide_num):
        slide = prs.slides.add_slide(blank_layout)

        # Background: Crisp light slate
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = PAGE_LIGHT
        bg.line.fill.background()

        # Top Accent Header Bar (Royal Blue)
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = ACCENT_BLUE
        top_bar.line.fill.background()

        # Header Box
        hb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.5), Inches(0.95))
        tf = hb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = badge_text.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_BLUE

        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.size = Pt(25)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_TITLE
        p1.space_before = Pt(2)

        # Top-Right Tiny BVM Logo / Header Badge
        if logo_file and os.path.exists(logo_file):
            try:
                slide.shapes.add_picture(logo_file, Inches(11.8), Inches(0.35), height=Inches(0.9))
            except Exception:
                pass

        # Footer
        fb = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.3))
        ftf = fb.text_frame
        fp = ftf.paragraphs[0]
        fp.text = f"Dashcam AI  •  Birla Vishvakarma Mahavidyalaya  •  Sujal Patel (23IT401)  •  Slide {slide_num} / 11"
        fp.font.size = Pt(10)
        fp.font.color.rgb = TEXT_MUTED

        return slide

    def try_add_picture(slide, path, left, top, width, height):
        if os.path.exists(path):
            try:
                pic = slide.shapes.add_picture(path, left, top, width, height)
                return pic
            except Exception:
                pass
        # Fallback card
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        p = box.text_frame.paragraphs[0]
        p.text = f"[Visual: {os.path.basename(path)}]"
        p.font.color.rgb = TEXT_MUTED
        return box

    # =========================================================================
    # SLIDE 1: COVER SLIDE (Clean White Theme + BVM Logo + Sujal Patel + Mentor)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid(); bg1.fill.fore_color.rgb = PAGE_LIGHT; bg1.line.fill.background()

    # Top Royal Blue Accent Strip
    top1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.1))
    top1.fill.solid(); top1.fill.fore_color.rgb = ACCENT_BLUE; top1.line.fill.background()

    # Left Container (Cover Info Card)
    left_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.6), Inches(6.5), Inches(6.3))
    left_card.fill.solid(); left_card.fill.fore_color.rgb = CARD_BG
    left_card.line.color.rgb = CARD_BORDER; left_card.line.width = Pt(1.5)

    # Place BVM Logo on Title Card
    if logo_file and os.path.exists(logo_file):
        try:
            s1.shapes.add_picture(logo_file, Inches(1.1), Inches(0.85), height=Inches(1.0))
        except Exception:
            pass

    # College Header Text beside logo
    clg_box = s1.shapes.add_textbox(Inches(2.25), Inches(0.8), Inches(4.8), Inches(1.1))
    ctf = clg_box.text_frame; ctf.word_wrap = True
    ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0
    p = ctf.paragraphs[0]
    p.text = "BIRLA VISHVAKARMA MAHAVIDYALAYA"
    p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = BVM_RED
    p = ctf.add_paragraph()
    p.text = "Engineering College (An Autonomous Institution)"
    p.font.size = Pt(10.5); p.font.color.rgb = TEXT_MUTED
    p = ctf.add_paragraph()
    p.text = "Department of Information Technology"
    p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = TEXT_SUBTITLE

    # Project Title Section
    title_box = s1.shapes.add_textbox(Inches(1.1), Inches(2.05), Inches(5.9), Inches(2.2))
    ttf = title_box.text_frame; ttf.word_wrap = True
    ttf.margin_left = ttf.margin_top = ttf.margin_right = ttf.margin_bottom = 0

    p = ttf.paragraphs[0]
    p.text = "DASHCAMERA AI"
    p.font.size = Pt(28); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE

    p = ttf.add_paragraph()
    p.text = "Real-Time Object Detection & Road Risk Analysis System"
    p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = TEXT_TITLE
    p.space_before = Pt(4)

    p = ttf.add_paragraph()
    p.text = "A Monocular Computer Vision ADAS with Dynamic Proximity Beep Alerts"
    p.font.size = Pt(12); p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(6)

    # Student & Mentor Credentials Box (Clean Card)
    meta_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(4.35), Inches(5.9), Inches(2.25))
    meta_card.fill.solid(); meta_card.fill.fore_color.rgb = RGBColor(241, 245, 249)  # Light Slate tint
    meta_card.line.color.rgb = RGBColor(203, 213, 225); meta_card.line.width = Pt(1)

    mtf = meta_card.text_frame; mtf.word_wrap = True
    p = mtf.paragraphs[0]
    p.text = "PROJECT CREDENTIALS"
    p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE; p.space_after = Pt(4)

    p = mtf.add_paragraph()
    p.text = "• Prepared By: Sujal Patel"
    p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = TEXT_TITLE

    p = mtf.add_paragraph()
    p.text = "   Student ID: 23IT401  |  B.Tech Information Technology"
    p.font.size = Pt(11.5); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(2)

    p = mtf.add_paragraph()
    p.text = "• Guided / Mentored By: Dhruvin R. Kotak"
    p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = BVM_RED; p.space_before = Pt(6)

    p = mtf.add_paragraph()
    p.text = "   Department of Information Technology, BVM Engineering College"
    p.font.size = Pt(11); p.font.color.rgb = TEXT_MUTED; p.space_before = Pt(2)

    # Hero Visual on Right Side
    try_add_picture(s1, IMG_HERO, Inches(7.55), Inches(0.6), Inches(5.0), Inches(6.3))

    # =========================================================================
    # SLIDE 2: PASSIVE VS ACTIVE (The Problem & Mission)
    # =========================================================================
    s2 = add_slide_scaffold("From Passive Recording to Active Edge AI", "Problem Statement & Motivation", 2)

    # Left Card: Traditional Dashcam
    card_trad = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.0))
    card_trad.fill.solid(); card_trad.fill.fore_color.rgb = CARD_BG
    card_trad.line.color.rgb = DANGER_RED; card_trad.line.width = Pt(1.5)
    tft = card_trad.text_frame; tft.word_wrap = True
    p = tft.paragraphs[0]; p.text = "Conventional Dashcam (Passive)"; p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = DANGER_RED; p.space_after = Pt(14)
    bullets_trad = [
        "• Purely Post-Mortem Forensics: Only records video to an SD card for post-accident insurance claims.",
        "• Zero Real-Time Warnings: Provides no alert when drifting out of lane or rapidly approaching stationary obstacles.",
        "• Human Inattention & Fatigue: Distraction and fatigue account for over 80% of preventable highway collisions.",
        "• High Cost of OEM ADAS: Built-in ADAS is restricted to expensive vehicles and cannot be retrofitted easily."
    ]
    for b in bullets_trad:
        p = tft.add_paragraph(); p.text = b; p.font.size = Pt(12.5); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(8)

    # Right Card: Our Solution
    card_sol = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    card_sol.fill.solid(); card_sol.fill.fore_color.rgb = CARD_BG
    card_sol.line.color.rgb = SAFE_GREEN; card_sol.line.width = Pt(1.5)
    tfs = card_sol.text_frame; tfs.word_wrap = True
    p = tfs.paragraphs[0]; p.text = "Our Dashcam AI Solution (Active Safety)"; p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = SAFE_GREEN; p.space_after = Pt(14)
    bullets_sol = [
        "• Proactive Collision Prevention: Computes real-time risk levels (SAFE / CAUTION / DANGER) every frame.",
        "• Monocular 3D Distance: Pinhole camera geometry extracts metric depth using existing single 2D camera lenses.",
        "• Proximity-Adaptive Audio Alerts: Generates rapid high-pitch beeps when obstacles approach, fading away when clear.",
        "• Commodity Hardware Ready: Runs efficiently on laptops, Jetson edge boards, and Raspberry Pi without LiDAR."
    ]
    for b in bullets_sol:
        p = tfs.add_paragraph(); p.text = b; p.font.size = Pt(12.5); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE (5-Stage Vision Pipeline)
    # =========================================================================
    s3 = add_slide_scaffold("End-to-End System Architecture", "5-Stage Real-Time Perception Pipeline", 3)
    stages = [
        ("1. Ingestion", "Dashcam MP4 / AVI / MOV or live camera feeds at 640px resolution.", ACCENT_BLUE, Inches(0.8)),
        ("2. AI Detection", "YOLOv8 Nano detects vehicles, pedestrians, cyclists & road signs in real time.", ACCENT_CYAN, Inches(3.2)),
        ("3. Tracking", "ByteTrack assigns unique IDs and tracks trajectories across frames.", SAFE_GREEN, Inches(5.6)),
        ("4. Geometry", "Monocular distance Z = (f * W) / w & Canny/Hough lane departure offset.", WARN_AMBER, Inches(8.0)),
        ("5. ADAS HUD", "Dynamic safety badge, Time-to-Collision (TTC) & proximity audio beeper.", DANGER_RED, Inches(10.4)),
    ]
    for title, desc, col, x in stages:
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(2.15), Inches(5.0))
        card.fill.solid(); card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = col; card.line.width = Pt(1.5)
        tf = card.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = title; p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = col; p.space_after = Pt(10)
        p = tf.add_paragraph(); p.text = desc; p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 4: YOLOV8 + BYTETRACK (Image Prominent)
    # =========================================================================
    s4 = add_slide_scaffold("Multi-Object Detection & Tracking", "YOLOv8 Nano + ByteTrack Multi-Target Association", 4)
    try_add_picture(s4, IMG_TRACKING, Inches(0.8), Inches(1.6), Inches(7.0), Inches(5.0))
    rc4 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.1), Inches(1.6), Inches(4.4), Inches(5.0))
    rc4.fill.solid(); rc4.fill.fore_color.rgb = CARD_BG; rc4.line.color.rgb = CARD_BORDER
    tf4 = rc4.text_frame; tf4.word_wrap = True
    p = tf4.paragraphs[0]; p.text = "Detection & Tracking Highlights"; p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE; p.space_after = Pt(10)
    bullets_s4 = [
        "• Model: YOLOv8 Nano (3.2M parameters) optimized for high-speed edge inference.",
        "• Target Classes: Cars, trucks, buses, motorcycles, bicycles, persons, traffic lights, and stop signs.",
        "• ByteTrack MOT: Solves object re-identification during occlusions, preserving tracking IDs across frames.",
        "• Hood Rejection Filter: Masks out reflections on the vehicle's own windshield and hood to eliminate false alerts."
    ]
    for b in bullets_s4:
        p = tf4.add_paragraph(); p.text = b; p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 5: LANE DETECTION (Image Prominent)
    # =========================================================================
    s5 = add_slide_scaffold("Lane Departure Warning (LDW)", "Canny Edges, Hough Transform & Driving Corridor", 5)
    try_add_picture(s5, IMG_LANES, Inches(0.8), Inches(1.6), Inches(7.0), Inches(5.0))
    rc5 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.1), Inches(1.6), Inches(4.4), Inches(5.0))
    rc5.fill.solid(); rc5.fill.fore_color.rgb = CARD_BG; rc5.line.color.rgb = CARD_BORDER
    tf5 = rc5.text_frame; tf5.word_wrap = True
    p = tf5.paragraphs[0]; p.text = "Lane Centering Pipeline"; p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = SAFE_GREEN; p.space_after = Pt(10)
    bullets_s5 = [
        "• Region of Interest (ROI): Dynamic trapezoid mask focused exclusively on the drivable road surface ahead.",
        "• Edge Detection & Hough: Canny edges filtered through Probabilistic Hough Lines (cv2.HoughLinesP).",
        "• Polynomial Slope Fitting: Separates lines into left and right boundaries using slope sign thresholds.",
        "• Lateral Offset: Compares road center against vehicle center; alerts driver when lane departure is detected."
    ]
    for b in bullets_s5:
        p = tf5.add_paragraph(); p.text = b; p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 6: MONOCULAR DISTANCE ESTIMATION (Image Prominent)
    # =========================================================================
    s6 = add_slide_scaffold("Monocular Distance Estimation", "Pinhole Camera Geometry & Zero-Hardware Depth", 6)
    try_add_picture(s6, IMG_DISTANCE, Inches(0.8), Inches(1.6), Inches(7.0), Inches(5.0))
    rc6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.1), Inches(1.6), Inches(4.4), Inches(5.0))
    rc6.fill.solid(); rc6.fill.fore_color.rgb = CARD_BG; rc6.line.color.rgb = CARD_BORDER
    tf6 = rc6.text_frame; tf6.word_wrap = True
    p = tf6.paragraphs[0]; p.text = "Mathematical Formulation"; p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = WARN_AMBER; p.space_after = Pt(10)
    bullets_s6 = [
        "• Formula:\n   Distance (Z) = (focal_length * Real_Width) / bbox_pixel_width",
        "• Class-Calibrated Widths (W):\n   - Car: 1.80m  |  Bus: 2.60m\n   - Truck: 2.50m  |  Person: 0.55m\n   - Motorcycle: 0.80m",
        "• Relative Velocity:\n   Computes rate of distance closure (delta d / delta t) over a rolling 10-frame window.",
        "• Zero Extra Hardware: Replaces bulky LiDAR sensors with pure 2D geometry."
    ]
    for b in bullets_s6:
        p = tf6.add_paragraph(); p.text = b; p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(6)

    # =========================================================================
    # SLIDE 7: DYNAMIC COLLISION THREAT ENGINE (Image Prominent)
    # =========================================================================
    s7 = add_slide_scaffold("Dynamic Collision Risk & Time-to-Collision (TTC)", "Class-Aware Spatial Threat Matrix & Velocity", 7)
    try_add_picture(s7, IMG_RISK, Inches(0.8), Inches(1.6), Inches(7.0), Inches(5.0))
    rc7 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.1), Inches(1.6), Inches(4.4), Inches(5.0))
    rc7.fill.solid(); rc7.fill.fore_color.rgb = CARD_BG; rc7.line.color.rgb = DANGER_RED
    tf7 = rc7.text_frame; tf7.word_wrap = True
    p = tf7.paragraphs[0]; p.text = "Active Risk Thresholds"; p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = DANGER_RED; p.space_after = Pt(8)
    bullets_s7 = [
        "• Time-to-Collision (TTC):\n   TTC = Distance / Closing_Speed (m/s)\n   - TTC < 2.0s  -->  URGENT DANGER\n   - TTC < 3.5s  -->  ACTIVE CAUTION",
        "• SAFE (Green Zone):\n   Distance >= 12m or outside forward trajectory.",
        "• CAUTION (Amber Zone):\n   Distance 6m - 12m or closing TTC < 3.5s.",
        "• DANGER (Crimson Alert):\n   Distance < 6m OR TTC < 2.0s directly in front of the vehicle."
    ]
    for b in bullets_s7:
        p = tf7.add_paragraph(); p.text = b; p.font.size = Pt(11.5); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(6)

    # =========================================================================
    # SLIDE 8: AUGMENTED HUD & PROXIMITY AUDIO BEEPS (Image Prominent)
    # =========================================================================
    s8 = add_slide_scaffold("Augmented Cockpit HUD & Adaptive Audio Alerts", "Distraction-Free Visual & Acoustic Warnings", 8)
    try_add_picture(s8, IMG_HUD, Inches(0.8), Inches(1.6), Inches(7.0), Inches(5.0))
    rc8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.1), Inches(1.6), Inches(4.4), Inches(5.0))
    rc8.fill.solid(); rc8.fill.fore_color.rgb = CARD_BG; rc8.line.color.rgb = CARD_BORDER
    tf8 = rc8.text_frame; tf8.word_wrap = True
    p = tf8.paragraphs[0]; p.text = "HUD Ergonomics & Audio"; p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE; p.space_after = Pt(8)
    bullets_s8 = [
        "• Top KPI Dashboard:\n   Live Road Status, Pipeline FPS, Tracked Objects, and Lane Status.",
        "• Proximity-Adaptive Beeping:\n   - < 3.5m: Strong, rapid high-pitch double-beep (2200 Hz, 0.35s).\n   - 3.5m - 6m: Fast danger alert (1800 Hz, 0.65s).\n   - 6m - 9m: Gentle caution alert (1200 Hz, 1.35s).\n   - > 9m / Cleared: Beeps slow down and close into silence.",
        "• Non-Blocking Audio Threads:\n   Daemon threads run sound synthesis without slowing video playback."
    ]
    for b in bullets_s8:
        p = tf8.add_paragraph(); p.text = b; p.font.size = Pt(11.5); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(6)

    # =========================================================================
    # SLIDE 9: EDGE BENCHMARKS & HARDWARE DEPLOYMENT (Image Prominent)
    # =========================================================================
    s9 = add_slide_scaffold("Performance Benchmarks & Edge Deployment", "Empirical Execution Across Hardware Platforms", 9)
    try_add_picture(s9, IMG_HARDWARE, Inches(0.8), Inches(1.6), Inches(7.0), Inches(5.0))
    rc9 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.1), Inches(1.6), Inches(4.4), Inches(5.0))
    rc9.fill.solid(); rc9.fill.fore_color.rgb = CARD_BG; rc9.line.color.rgb = CARD_BORDER
    tf9 = rc9.text_frame; tf9.word_wrap = True
    p = tf9.paragraphs[0]; p.text = "Hardware Benchmark Matrix"; p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = SAFE_GREEN; p.space_after = Pt(8)
    bullets_s9 = [
        "• NVIDIA RTX GPU:\n   60 - 85+ FPS (Full HD Pipeline) - Real-time ADAS.",
        "• Modern Laptop CPU (i7 / Ryzen 7):\n   12 - 18 FPS (640px) - Practical for dashcam replay.",
        "• Low-Power Edge SBC (Jetson Nano / Pi 5):\n   20 - 30 FPS (--imgsz 320) - Compact standalone device.",
        "• Resolution Scaling:\n   --imgsz 320 cuts compute by 75% for embedded deployments.",
        "• TensorRT & ONNX Exportable:\n   Allows INT8/FP16 quantization for edge accelerators."
    ]
    for b in bullets_s9:
        p = tf9.add_paragraph(); p.text = b; p.font.size = Pt(11.5); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(6)

    # =========================================================================
    # SLIDE 10: FUTURE ROADMAP & CONCLUSION
    # =========================================================================
    s10 = add_slide_scaffold("Future Roadmap & Project Conclusion", "Next Engineering Milestones & Takeaways", 10)
    roadmap_items = [
        ("Learned Lane Segmentation", "Replace Hough lines with lightweight U-Net on BDD100K for curved, weathered, and unlit roads.", ACCENT_BLUE, Inches(0.8), Inches(1.6)),
        ("Sign & Signal Recognition", "Fine-tune YOLOv8 on Indian traffic dataset for comprehensive speed limit, school zone, and light recognition.", ACCENT_CYAN, Inches(6.8), Inches(1.6)),
        ("Blackbox Incident Recorder", "Automated circular video recording triggered during DANGER states with encrypted telemetry snapshots.", WARN_AMBER, Inches(0.8), Inches(4.2)),
        ("Radar / Sensor Fusion", "Fuse low-cost 24GHz/77GHz mmWave radar sensors for zero-visibility fog, heavy rain, and night conditions.", SAFE_GREEN, Inches(6.8), Inches(4.2)),
    ]
    for title, desc, col, x, y in roadmap_items:
        card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.7), Inches(2.2))
        card.fill.solid(); card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = col; card.line.width = Pt(1.5)
        tf = card.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = title; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = col; p.space_after = Pt(6)
        p = tf.add_paragraph(); p.text = desc; p.font.size = Pt(12.5); p.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 11: THANK YOU & PROJECT CREDENTIALS (Requested Closing Slide)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    bg11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg11.fill.solid(); bg11.fill.fore_color.rgb = PAGE_LIGHT; bg11.line.fill.background()

    # Top Royal Blue Strip
    top11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.1))
    top11.fill.solid(); top11.fill.fore_color.rgb = ACCENT_BLUE; top11.line.fill.background()

    # Main Center Card
    main_card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(0.6), Inches(10.333), Inches(6.3))
    main_card.fill.solid(); main_card.fill.fore_color.rgb = CARD_BG
    main_card.line.color.rgb = CARD_BORDER; main_card.line.width = Pt(1.5)

    # BVM Logo at the top of the card
    if logo_file and os.path.exists(logo_file):
        try:
            s11.shapes.add_picture(logo_file, Inches(5.8), Inches(0.9), height=Inches(1.2))
        except Exception:
            pass

    # Thank You Text Frame
    ty_box = s11.shapes.add_textbox(Inches(2.0), Inches(2.2), Inches(9.333), Inches(4.5))
    ty_tf = ty_box.text_frame; ty_tf.word_wrap = True
    ty_tf.margin_left = ty_tf.margin_top = ty_tf.margin_right = ty_tf.margin_bottom = 0

    p = ty_tf.paragraphs[0]
    p.text = "THANK YOU!"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(38); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE

    p = ty_tf.add_paragraph()
    p.text = "Questions & Discussion"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(16); p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(4); p.space_after = Pt(20)

    # Sub-card with Credentials
    cred_card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.2), Inches(3.6), Inches(8.933), Inches(2.9))
    cred_card.fill.solid(); cred_card.fill.fore_color.rgb = RGBColor(241, 245, 249)
    cred_card.line.color.rgb = RGBColor(203, 213, 225); cred_card.line.width = Pt(1)

    ctf = cred_card.text_frame; ctf.word_wrap = True
    p = ctf.paragraphs[0]
    p.text = "Dashcam AI: Real-Time Object Detection & Road Risk Analysis System"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = TEXT_TITLE; p.space_after = Pt(12)

    # Two column layout inside card: Student on left, Mentor on right
    p = ctf.add_paragraph()
    p.text = "Presented By:"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE

    p = ctf.add_paragraph()
    p.text = "Sujal Patel  (ID No: 23IT401)"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = TEXT_TITLE

    p = ctf.add_paragraph()
    p.text = "Department of Information Technology, BVM Engineering College"
    p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.space_before = Pt(2); p.space_after = Pt(10)

    p = ctf.add_paragraph()
    p.text = "Under the Mentorship / Guidance of:"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BVM_RED

    p = ctf.add_paragraph()
    p.text = "Prof. Dhruvin R. Kotak"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = BVM_RED

    p = ctf.add_paragraph()
    p.text = "Birla Vishvakarma Mahavidyalaya Engineering College (Vallabh Vidyanagar)"
    p.font.size = Pt(12); p.font.color.rgb = TEXT_MUTED; p.space_before = Pt(2)

    # Save Presentation (with automatic fallback if file is locked / open in PowerPoint)
    output_filename = "AI_Dashcam_Road_Risk_System.pptx"
    output_path = os.path.join(SCRIPT_DIR, output_filename)
    try:
        prs.save(output_path)
        print(f"\n[SUCCESS] Modern white-theme presentation saved to: {output_path}\n")
        return output_path
    except PermissionError:
        fallback_filename = "AI_Dashcam_Road_Risk_System_WhiteTheme.pptx"
        fallback_path = os.path.join(SCRIPT_DIR, fallback_filename)
        print(f"\n[WARNING] '{output_filename}' is currently OPEN in PowerPoint!")
        print(f"[FALLBACK] Saving presentation to: {fallback_filename}")
        prs.save(fallback_path)
        print(f"[SUCCESS] Saved successfully to: {fallback_path}")
        print("(Tip: Close PowerPoint if you wish to overwrite the original filename)\n")
        return fallback_path


if __name__ == "__main__":
    build_visual_presentation()
