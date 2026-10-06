import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11s.pt")

# Open webcam
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not access webcam.")
        break

    # Run YOLO detection and tracking
    results = model.track(
        frame,
        persist=True,
        conf=0.60,
        verbose=False
    )

    # Draw detections
    annotated_frame = results[0].plot()

    # Count detected objects
    object_count = len(results[0].boxes)

    # Display detection count
    cv2.putText(
        annotated_frame,
        f"Objects detected: {object_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Display result
    cv2.imshow(
        "CodeAlpha - Object Detection and Tracking",
        annotated_frame
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()