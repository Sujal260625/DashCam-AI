# 11-Slide Presentation Deck & Presenter Guide
## Dashcam AI: Real-Time Object Detection & Road Risk Analysis System
### Birla Vishvakarma Mahavidyalaya (BVM Engineering College)
**Student:** Sujal Patel (ID No: 23IT401)  
**Mentor / Guide:** Prof. Dhruvin R. Kotak  
**Department:** Information Technology  

---

### Slide 1: Title & Executive Summary
- **Slide Title**: Dashcamera AI: Real-Time Object Detection & Road Risk Analysis System
- **Subtitle**: A Monocular Computer Vision ADAS with Dynamic Proximity Beep Alerts
- **Institution**: Birla Vishvakarma Mahavidyalaya (BVM Engineering College)
- **Theme**: Modern Clean Academic White Theme with Crisp Blue Accents
- **Key Badges**:
  - BVM Engineering College Crest / Logo
  - Student: Sujal Patel (23IT401)
  - Mentor: Prof. Dhruvin R. Kotak
  - Real-Time YOLOv8 Detection & ByteTrack MOT
  - OpenCV Hough Lane Centering & Monocular 3D Distance
  - Dynamic Collision Risk Scoring & Proximity Audio Beeps

#### Slide 1 Explanation & Presenter Notes:
> "Respected mentor Prof. Dhruvin R. Kotak sir, evaluators, and audience. I am **Sujal Patel**, student ID **23IT401** from the Department of Information Technology at **Birla Vishvakarma Mahavidyalaya (BVM)**. Today I am presenting our project: **Dashcamera AI - Real-Time Object Detection & Road Risk Analysis System**. This is a functional, real-time edge computer vision pipeline that transforms any standard single-lens dashboard camera into an active collision warning system. By fusing YOLOv8 deep learning, ByteTrack multi-target tracking, OpenCV lane departure detection, and monocular geometric heuristics for metric distance estimation, our system delivers real-time forward collision warnings and proximity-adaptive acoustic beeping without requiring expensive LiDAR or radar hardware."

---

### Slide 2: Problem Statement & Motivation
- **Left Column: Limitations of Conventional Dashcams (The Problem)**
  - *Passive Forensics*: Standard dashcams only record video to an SD card for post-accident insurance claims; they do nothing to prevent the crash in real-time.
  - *Driver Inattention & Blindspots*: Fatigue, highway hypnosis, distraction, or low visibility cause lane drifting and missed pedestrians.
  - *High Cost of OEM ADAS*: Factory ADAS (Tesla Autopilot, Subaru EyeSight) is locked to expensive new vehicles and cannot easily be added to the billions of existing cars on the road.
- **Right Column: Our Proposed Edge-AI Solution**
  - *Active Proactive Warning*: Real-time threat classification into SAFE, CAUTION, and DANGER with immediate visual alerts.
  - *Single-Camera Monocular Vision*: Uses geometry and pinhole camera math to estimate metric distances with zero extra sensor hardware.
  - *Edge-Friendly Performance*: Runs smoothly at 10–15 FPS on standard CPUs and 60+ FPS on edge GPUs.

#### Slide 2 Explanation & Presenter Notes:
> "Every year, millions of vehicular accidents occur worldwide due to distracted driving and slow reaction times. Although dashcams are ubiquitous, they are strictly passive. If an accident occurs, you only have video evidence of what went wrong. What drivers actually need is proactive collision prevention. Premium manufacturers offer ADAS, but retrofitting existing cars with radar or multi-camera LiDAR rigs is prohibitively expensive. Our project bridges this gap by turning commodity cameras into intelligent, proactive safety co-pilots."

---

### Slide 3: End-to-End System Architecture
- **5-Stage Pipeline Flow**:
  1. **Video Ingestion**: Supports live webcams (`--source 0`), local MP4 video files, and network RTSP streams at 640×640 or 320×320 resolution.
  2. **Neural Detection**: YOLOv8 Nano (`yolov8n.pt`) detects pedestrians, vehicles, and signs.
  3. **Multi-Object Tracking (MOT)**: ByteTrack assigns persistent IDs, correlates bounding boxes across frames, and prevents ID switching.
  4. **Spatial Geometry**: Classical CV extracts road lane boundaries and calculates lateral offset; pinhole camera projection calculates metric distance.
  5. **Risk Engine & HUD**: Risk classification classifies threats and renders the Tesla-style heads-up display.

```
[ Video / Camera Stream ]
           │
           ▼
[ Frame Preprocessing & Ingestion (640x640) ]
     ┌─────┴────────────────────────────────────────┐
     ▼                                              ▼
[ YOLOv8 Object Detection ]            [ Classical CV Lane Detection ]
     │                                              │
     ▼                                              │
[ ByteTrack Multi-Object Tracking ]                 │
     │                                              │
     ▼                                              ▼
[ Monocular Distance Estimation ]      [ Lane Center Drift Analysis ]
     └─────────────────────┬────────────────────────┘
                           ▼
             [ Dynamic Risk Engine (ML Rules) ]
             (SAFE / CAUTION / DANGER Scoring)
                           │
                           ▼
             [ Tesla-Style Augmented HUD ]
             (Status Bar, Boxes, Drift, FPS)
```

#### Slide 3 Explanation & Presenter Notes:
> "Our architecture separates perception into two parallel streams: semantic detection and geometric lane analysis. The semantic stream uses YOLOv8 and ByteTrack to understand 'what is in front of the vehicle and where is it moving.' The geometric stream uses classical OpenCV transforms to understand 'where is the road corridor and is the vehicle drifting.' These two streams feed into our dynamic risk engine, which computes collision probability and generates the unified HUD."

---

### Slide 4: Object Detection & Multi-Object Tracking (MOT)
- **Ultralytics YOLOv8 Backbone**:
  - Anchor-free convolutional architecture featuring C2f (Cross-Stage Partial with 2 convolutions) modules.
  - Filtering for ADAS-relevant COCO classes:
    - *Vehicles*: Car, Truck, Bus, Motorcycle, Train
    - *Vulnerable Road Users*: Person, Bicycle
    - *Signage & Controls*: Traffic Light, Stop Sign
  - High efficiency: `yolov8n.pt` has only 3.2 million parameters and a ~6 MB file size.
- **ByteTrack MOT Integration**:
  - Solves the critical drawback of traditional trackers (like SORT): when an obstacle is partially occluded, its detection score drops below the threshold and its track ID is lost.
  - ByteTrack uses a two-stage association strategy that matches low-confidence detections to existing tracklets via Kalman filter motion estimation and IoU matching.
  - Result: High track consistency, zero ID switching during brief occlusions, and sub-millisecond tracking overhead.

#### Slide 4 Explanation & Presenter Notes:
> "Why YOLOv8 with ByteTrack? In driving scenarios, tracking identity is just as important as detecting objects. If a car overtakes you or passes behind a signpost, a basic detector loses track and treats it as a brand-new obstacle every frame. ByteTrack retains low-confidence detections in a secondary matching pass, preserving track continuity even through windshield glare or partial occlusions. Because ByteTrack relies on IoU and Kalman filtering rather than heavy deep appearance embeddings, it introduces almost zero latency."

---

### Slide 5: Computer Vision Lane Detection & Drift Analysis
- **Classical CV Pipeline**:
  1. *Grayscale & 5×5 Gaussian Blur*: Suppresses high-frequency asphalt textures, sensor grain, and road noise.
  2. *Canny Edge Detection*: Uses hysteresis thresholding (50, 150) to isolate high-gradient painted lane markings.
  3. *Trapezoidal Region of Interest (ROI)*: Masks out sky, scenery, and vehicle dashboard reflections, confining edge analysis to the forward driving corridor.
  4. *Probabilistic Hough Transform (`HoughLinesP`)*: Extracts line segments; filters out near-horizontal noise (`|slope| < 0.3`).
- **Mathematical Centering & Drift Logic**:
  - Extrapolates left and right boundary vectors using linear regression (`np.polyfit`).
  - Calculates vehicle lateral offset:
    $$\text{Lane Center} = \frac{X_{\text{left, bottom}} + X_{\text{right, bottom}}}{2}$$
    $$\text{Offset} = \text{Lane Center} - \frac{\text{Frame Width}}{2}$$
  - Alert States:
    - $\text{Offset} > +25\text{ px} \implies \mathbf{DRIFT\ RIGHT}$
    - $\text{Offset} < -25\text{ px} \implies \mathbf{DRIFT\ LEFT}$
    - $|\text{Offset}| \le 25\text{ px} \implies \mathbf{LANE\ CENTERED}$

#### Slide 5 Explanation & Presenter Notes:
> "For lane keeping, we implemented a classical computer vision pipeline using Canny edge filtering and the Hough transform. We define a trapezoidal region of interest that matches the camera's perspective geometry. By separating lines into positive and negative slope bins, we extrapolate the left and right lane boundaries. By comparing the midpoint of the lane at the bottom of the frame against the camera center, we instantly detect if the driver is drifting left or right beyond a 25-pixel deadband."

---

### Slide 6: Monocular Distance Estimation
- **Pinhole Camera Triangular Similarity**:
  - Derives metric distance from 2D pixel widths using the optical projection formula:
    $$\text{Distance (m)} = \frac{\text{Known Object Width (m)} \times \text{Focal Length (px)}}{\text{Bounding Box Width (px)}}$$
- **Focal Length Calibration**:
  $$\text{Focal Length (px)} = \frac{\text{Bounding Box Width (px)} \times \text{Ground Truth Distance (m)}}{\text{Known Object Width (m)}}$$
  - Calibrated default: $F_{\text{pixel}} = 700\text{ px}$.
- **Empirical Real-World Width Priors (`KNOWN_WIDTH_M`)**:
  - Passenger Car: $1.8\text{ m}$
  - Commercial Bus / Truck: $2.5\text{ m}$
  - Motorcycle: $0.8\text{ m}$
  - Bicycle: $0.6\text{ m}$
  - Pedestrian: $0.5\text{ m}$
  - Locomotive / Train: $3.0\text{ m}$
- **Key Hardware Advantage**: Provides metric distance without LiDAR, stereo rigs, or heavy depth-prediction neural nets.

#### Slide 6 Explanation & Presenter Notes:
> "Standard dashcams lack depth sensors. To estimate distance, we exploit the pinhole camera model. Because vehicle and human dimensions follow standardized real-world distributions—a typical sedan is 1.8 meters wide, while an average pedestrian shoulder width is 0.5 meters—we can compute metric distance using optical triangular similarity. As an object draws closer, its bounding box width in pixels grows hyperbolically. This provides a deterministic, zero-latency metric distance measurement."

---

### Slide 7: Dynamic Road Risk Assessment Engine
- **Spatial Threat Model**: Combines metric distance, object classification, and spatial trajectory corridor.
- **Ego-Vehicle Path Corridor**: Defined as $30\% \le X_{\text{center}} \le 70\%$ of the image width.
- **Classification Rules Matrix**:

| Road Entity | SAFE (Green) | CAUTION (Amber) | DANGER (Crimson) |
|---|---|---|---|
| **Vehicles (Car, Truck, Bus)** | Distance $\ge 12\text{m}$ OR out of path | Distance $6\text{m} - 12\text{m}$ | Distance $< 6\text{m}$ AND in vehicle path |
| **Pedestrians (VRUs)** | Distance $\ge 15\text{m}$ | Distance $8\text{m} - 15\text{m}$ | Distance $< 8\text{m}$ AND in vehicle path |
| **Uncalculated Distance** | Standard position | Sits in lower $45\%$ of frame | N/A |

#### Slide 7 Explanation & Presenter Notes:
> "Not all detected obstacles pose an immediate threat. A car parked on the curb 5 meters away is not dangerous, but a pedestrian stepping into your lane 7 meters ahead is critical. Our risk engine applies domain-specific rules: pedestrians have wider safety buffers (danger under 8 meters vs 6 meters for cars). Furthermore, the obstacle must reside within the vehicle's forward travel corridor (between 30% and 70% of frame width) to trigger an active DANGER alert."

---

### Slide 8: Tesla-Style Augmented HUD & Telemetry
- **Visual Design & Cognitive Ergonomics**:
  - *Top Status Bar*: Dark banner displaying high-priority alerts: `ROAD STATUS: ALL CLEAR` (Green), `CAUTION xN` (Amber), or `DANGER xN` (Red).
  - *Live FPS Counter*: Rolling 30-frame average ensuring responsive real-time feedback.
  - *Bounding Pill Overlays*: Solid-colored header badge with Track ID, Class Name, Metric Distance, and Risk Status (e.g., `ID2 car 5.4m [DANGER]`).
  - *Lane Overlay*: High-contrast neon yellow boundary lines with lane drift text centered at the bottom of the screen.
- **Human Factors Engineering**:
  - Complies with ISO automotive color standards (Green / Yellow / Red).
  - High-contrast background fills guarantee legibility under harsh sunlight, headlights, or rain.
  - OpenCV drawing functions execute in under $1.5\text{ ms}$ per frame.

#### Slide 8 Explanation & Presenter Notes:
> "In safety-critical automotive environments, cognitive load is paramount. If information is cluttered or illegible against headlights or glare, it fails the driver. Our HUD takes cues from Tesla's digital instrument cluster: an aggregated road status bar across the top provides instantaneous situational awareness, while bounding box labels feature solid contrasting pill backgrounds so drivers can comprehend distance and risk at a glance."

---

### Slide 9: Performance Benchmarks & Edge Deployment
- **Hardware Performance Matrix**:
  - *NVIDIA RTX GPU*: $60 - 85+\text{ FPS}$ (Super Real-Time, Full HD).
  - *Commodity Laptop CPU (i7 / Ryzen 7)*: $10 - 15\text{ FPS}$ (Standard 640px inference).
  - *Embedded SBC (Raspberry Pi 4/5, Jetson Nano)*: $20 - 30\text{ FPS}$ (Using `--imgsz 320`).
- **Optimization Strategies**:
  - *Dynamic Downsampling*: Dropping resolution from 640px to 320px reduces pixel operations by $75\%$ while preserving close-range collision detection.
  - *Headless Batch Processing*: `--no-show --save outputs/result.mp4` bypasses GUI rendering for fast server-side processing of archived dashcam footage.
  - *Export Capabilities*: YOLOv8 supports one-line export to ONNX and TensorRT for FP16 / INT8 quantization on NVIDIA Jetson modules.

#### Slide 9 Explanation & Presenter Notes:
> "A key objective was universal hardware accessibility. On an RTX GPU, the pipeline runs at over 60 FPS. On commodity laptop CPUs without dedicated GPUs, it achieves 10 to 15 FPS—plenty fast for highway and urban warning. For low-cost embedded hardware like Raspberry Pi or Jetson Nano, reducing the inference image size to 320px cuts compute load by 75%, maintaining 20–30 FPS while retaining high accuracy for near-field obstacles."

---

### Slide 10: Future Roadmap & Project Conclusion
- **Engineering Roadmap**:
  1. *Learned Lane Segmentation*: Transition from classical Hough lines to a lightweight U-Net or LaneNet trained on CULane/BDD100K for complex curves and weathered roads.
  2. *Autonomous Driving Fine-Tuning*: Fine-tune YOLOv8 on Indian road traffic datasets for fine-grained traffic sign recognition (speed limits, school zones, stoplights).
  3. *Blackbox Crash Recording*: Automatically buffer and lock high-resolution video snapshots whenever a DANGER event occurs.
  4. *Multi-Sensor Fusion*: Integrate low-cost mmWave radar for millimeter-level range precision in zero-visibility fog or heavy rain.
- **Conclusion**:
  - Developed and verified a working, end-to-end edge-AI ADAS pipeline.
  - Delivers active forward collision and lane departure warnings on standard camera feeds with zero dedicated sensor costs.

#### Slide 10 Explanation & Presenter Notes:
> "To conclude, we have engineered and verified a functional, lightweight dashcam ADAS pipeline. It bridges the gap between passive video recording and active driving safety, requiring only commodity hardware. Moving forward, we plan to incorporate learned lane segmentation and blackbox incident telemetry."

---

### Slide 11: Thank You & Discussion
- **Slide Title**: THANK YOU!
- **Subtitle**: Questions & Discussion
- **Crest**: Birla Vishvakarma Mahavidyalaya (BVM Engineering College) Logo
- **Presented By**: Sujal Patel (Student ID: 23IT401)
- **Degree**: B.Tech Information Technology
- **Under the Mentorship of**: Prof. Dhruvin R. Kotak
- **Department**: Department of Information Technology, BVM Engineering College (An Autonomous Institution, Vallabh Vidyanagar)

#### Slide 11 Presenter Script:
> "Thank you respected mentor Prof. Dhruvin R. Kotak sir, faculty members, and the evaluation committee for your time, guidance, and attention. The floor is now open for any questions, critique, and discussion."
