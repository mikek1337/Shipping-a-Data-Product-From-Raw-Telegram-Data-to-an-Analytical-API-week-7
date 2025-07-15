import os
from ultralytics import YOLO
import json
import time
print(os.getenv['DBT_PROFILES_DIR'])
# --- Configuration ---
IMAGE_DIR = "data/raw/telegram_images"  # Directory where scraped images are stored
PROCESSED_IMAGES_LOG = "processed_images.json"  # Log file for processed image IDs
YOLO_MODEL_PATH = "yolov8n.pt"  # Path to a pre-trained YOLOv8 model (nano version for quick start)
# You can download models from: https://github.com/ultralytics/ultralytics/releases
# For example, yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt

# --- Initialize YOLOv8 Model ---
try:
    model = YOLO(YOLO_MODEL_PATH)
    print(f"YOLOv8 model '{YOLO_MODEL_PATH}' loaded successfully.")
except Exception as e:
    print(f"Error loading YOLOv8 model: {e}")
    print("Please ensure the model file exists or download it, e.g., 'yolov8n.pt'")
    exit()

# --- Helper Functions ---
def get_processed_images():
    """Loads the set of processed image IDs from the log file."""
    if os.path.exists(PROCESSED_IMAGES_LOG):
        with open(PROCESSED_IMAGES_LOG, 'r') as f:
            return set(json.load(f))
    return set()

def add_processed_image(image_filename):
    """Adds an image filename to the processed log."""
    processed_images = get_processed_images()
    processed_images.add(image_filename)
    with open(PROCESSED_IMAGES_LOG, 'w') as f:
        json.dump(list(processed_images), f)

def get_image_id_from_filename(filename):
    """
    Extracts a message_id from the image filename.
    Assumes filenames are like 'message_<id>_image_<num>.jpg' or similar.
    Adjust this function based on your actual filename format.
    """
    try:
        # Example: "message_12345_image_0.jpg" -> "12345"
        parts = filename.split('.')
        if len(parts) > 1:
            return parts[0]
    except Exception as e:
        print(f"Warning: Could not extract message_id from {filename}: {e}")
    return None

def process_new_images():
    """Scans for new images, performs detection, and returns results."""
    processed_images = get_processed_images()
    detection_results = []
    
    print(f"Scanning for new images in: {IMAGE_DIR}")

    for dirlist in os.listdir(IMAGE_DIR):
        for filelist in os.listdir(f'{IMAGE_DIR}/{dirlist}'):
            for filename in os.listdir(f'{IMAGE_DIR}/{dirlist}/{filelist}'):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    if filename not in processed_images:
                        image_path = os.path.join(f'{IMAGE_DIR}/{dirlist}/{filelist}', filename)
                        message_id = get_image_id_from_filename(filename)

                        if message_id:
                            print(f"Processing new image: {filename} (message_id: {message_id})")
                            try:
                                # Perform inference
                                results = model(image_path)  # results list of Results objects
                                
                                # Process results
                                for r in results:
                                    boxes = r.boxes.cpu().numpy()
                                    names = r.names
                                    for box in boxes:
                                        class_id = int(box.cls[0])
                                        class_name = names[class_id]
                                        confidence = float(box.conf[0])
                                        
                                        detection_results.append({
                                            "message_id": message_id,
                                            "detected_object_class": class_name,
                                            "confidence_score": confidence
                                        })
                                
                                add_processed_image(filename)
                                print(f"Finished processing {filename}. Detections found: {len(results[0].boxes)}")
                            except Exception as e:
                                print(f"Error processing image {filename}: {e}")
                        else:
                            print(f"Skipping {filename}: Could not determine message_id.")
                    # else:
            #     print(f"Skipping {filename}: Already processed.") # Uncomment for verbose logging

    return detection_results

# --- Main Execution Loop (Optional: run continuously) ---
if __name__ == "__main__":
    print("Starting image detection script...")
    while True:
        new_detections = process_new_images()
        if new_detections:
            # In a real-world scenario, you'd push these detections to a staging area
            # or directly insert into your data warehouse.
            print("\n--- New Detections Found ---")
            for detection in new_detections:
                print(detection)
            print("--- End of Detections ---\n")
            
            # Here, you would save new_detections to a file or database
            # for dbt to pick up. For example, append to a CSV or JSONL file.
            with open("yolov8_detections_raw.jsonl", "a") as f:
                for detection in new_detections:
                    f.write(json.dumps(detection) + "\n")
            print("Detections saved to yolov8_detections_raw.jsonl")

        else:
            print("No new images to process.")
        
        # Wait for some time before scanning again
        time.sleep(60) # Scan every 60 seconds (adjust as needed)