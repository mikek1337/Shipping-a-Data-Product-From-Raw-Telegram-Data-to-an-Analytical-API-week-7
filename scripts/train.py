from ultralytics import YOLO

# Load a pre-trained YOLOv8n model
model = YOLO('yolov8n.pt')

# Train the model with your custom dataset
# Adjust epochs, batch size, and image size as needed
results = model.train(
    data='phdata.yaml',
    epochs=100,      # Number of training epochs
    imgsz=640,       # Input image size (e.g., 640x640)
    batch=-1,        # Auto-batch size based on GPU memory
    name='yolov8_pharmacy_products_detection' # Name for the training run
)