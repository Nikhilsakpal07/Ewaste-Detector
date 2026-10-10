from ultralytics import YOLO

if __name__ == '__main__':
    # Load the pretrained model for Object Detection (Notice we removed -cls to switch to bounding boxes!)
    model = YOLO('yolov8n.pt') 

    # Train the model with the new e-waste dataset
    model.train(
        data='d:/e waste project/WasteDetector-main/WasteDetector/data.yaml',
        epochs=50,      # Increased to 50 for much better accuracy!
        imgsz=640,      # Standard resolution for object detection
        batch=16,
        workers=4,
        verbose=True
    )

    # The best weights will be saved automatically to runs/detect/train/weights/best.pt
