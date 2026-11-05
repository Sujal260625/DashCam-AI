import cv2
import numpy as np

W, H = 960, 540
FPS = 20
N = 100
out = cv2.VideoWriter("/home/claude/dashcam_ai/sample/test_drive.mp4",
                       cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))

for i in range(N):
    frame = np.full((H, W, 3), (90, 90, 90), dtype=np.uint8)  # road
    cv2.rectangle(frame, (0, 0), (W, int(H * 0.55)), (180, 140, 90), -1)  # sky

    # lane lines converging (simple perspective)
    t = i / N
    left_bottom = int(W * 0.10)
    right_bottom = int(W * 0.90)
    left_top = int(W * 0.46)
    right_top = int(W * 0.54)
    cv2.line(frame, (left_bottom, H), (left_top, int(H * 0.60)), (255, 255, 255), 6)
    cv2.line(frame, (right_bottom, H), (right_top, int(H * 0.60)), (255, 255, 255), 6)

    # a "car" approaching (growing box) drawn as a car-like rectangle+roof so YOLO can generalize less reliably;
    # instead we just verify the pipeline runs without crashing.
    car_w = int(60 + t * 200)
    car_h = int(car_w * 0.6)
    cx = W // 2 + int(30 * np.sin(t * 3))
    cy = int(H * 0.60 + t * (H * 0.30))
    cv2.rectangle(frame, (cx - car_w // 2, cy - car_h // 2), (cx + car_w // 2, cy + car_h // 2), (0, 0, 200), -1)
    cv2.rectangle(frame, (cx - car_w // 3, cy - car_h), (cx + car_w // 3, cy - car_h // 2), (0, 0, 150), -1)

    # a pedestrian-like figure on the side
    px = int(W * 0.20)
    py = int(H * 0.75)
    cv2.circle(frame, (px, py - 30), 10, (200, 200, 0), -1)
    cv2.rectangle(frame, (px - 8, py - 20), (px + 8, py + 20), (200, 200, 0), -1)

    out.write(frame)

out.release()
print("Test video written.")
