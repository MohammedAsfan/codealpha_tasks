# Object Detection and Tracking

A real-time object detection and tracking system built using Python, OpenCV, and YOLO.

## Features

- Real-time webcam object detection
- YOLO-based object recognition
- Object tracking with tracking IDs
- Confidence filtering
- Bounding boxes and object labels
- Real-time object count
- Supports built-in, external, and virtual cameras
- Simple and easy-to-use implementation

## Technologies Used

- Python
- OpenCV
- Ultralytics YOLO

## How It Works

1. The camera captures video frames.
2. YOLO detects objects in each frame.
3. The tracking system assigns IDs to detected objects.
4. Bounding boxes and labels are displayed.
5. Objects with low confidence are filtered out.
6. The number of detected objects is displayed on the screen.

## Installation

Clone the repository and install the required packages:

```bash
pip install -r requirements.txt