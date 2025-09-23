import cv2
import time
import os
from ultralytics import YOLO

# === CONFIGURATION ===
model = YOLO("yolov8n.pt")  # Replace with your trained model if needed
stream_url = 'http://192.168.0.100:5000/video'  # Laptop IP
output_dir = 'detections'
os.makedirs(output_dir, exist_ok=True)

# === STREAM SETUP ===
cap = cv2.VideoCapture(stream_url)
if not cap.isOpened():
    print("❌ Failed to connect to stream.")
    exit()

print("📡 Connected to stream. Starting detection...")

last_save_time = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to grab frame.")
            break

        current_time = time.time()
        if current_time - last_save_time >= 1:
            last_save_time = current_time

            # Run inference
            results = model.predict(frame)

            # Annotate frame
            annotated_frame = results[0].plot(boxes=True, masks=False)

            # Draw FPS
            inference_time = results[0].speed.get('inference', 0)
            fps = 1000 / inference_time if inference_time > 0 else 0
            text = f'FPS: {fps:.1f}'
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(text, font, 1, 2)[0]
            text_x = annotated_frame.shape[1] - text_size[0] - 10
            text_y = text_size[1] + 10
            cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2)

            # Save detection
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"{output_dir}/detect_{timestamp}.jpg"
            cv2.imwrite(filename, annotated_frame)
            print(f"✅ Saved: {filename}")

        # Optional: display frame (uncomment if using VNC)
        # cv2.imshow("YOLOv8 Detection", annotated_frame)
        # if cv2.waitKey(1) == ord("q"):
        #     break

except KeyboardInterrupt:
    print("\n🛑 Detection stopped by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
