import cv2
import numpy as np
import logging
from pycoral.utils import edgetpu
from pycoral.adapters import common, classify
import time


def load_model(model_path: str):
    """Load the TFLite model with Edge TPU support."""
    try:
        interpreter = edgetpu.make_interpreter(model_path)
        interpreter.allocate_tensors()
        logging.info("Model loaded successfully.")
        return interpreter
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        raise


def load_labels(labels_path: str) -> dict:
    """Load labels from a text file."""
    try:
        with open(labels_path, 'r') as f:
            return {int(line.split()[0]): line.strip().split(maxsplit=1)[1] for line in f.readlines()}
    except Exception as e:
        logging.error(f"Failed to load labels: {e}")
        raise


def setup_camera(camera_index: int = 0, width: int = 640, height: int = 480):
    """Initialize and configure the camera."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise ValueError("Error: Camera not found or could not be opened.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 30)
    return cap

def preprocess_frame(frame, input_shape, input_details):
    
    # Resize and convert to RGB
    resized_frame = cv2.resize(frame, input_shape)
    resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    # Handle UINT8 quantized model input
    scale, zero_point = input_details[0]['quantization']
    if scale > 0:
        resized_frame = ((resized_frame / 255.0) / scale + zero_point).astype(np.uint8)

    # Expand dimensions for batch input
    input_tensor = np.expand_dims(resized_frame, axis=0)

    logging.debug(f"Frame variance: {np.var(frame)}")  # Variance of the original frame
    logging.debug(f"Input tensor variance: {np.var(input_tensor)}")  # Variance of the input tensor

    return input_tensor

def run_inference(interpreter, input_tensor):
    
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]['index'], input_tensor)
    interpreter.invoke()

    output_details = interpreter.get_output_details()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    logging.debug(f"Raw model output: {output_data}")

    
    classes = classify.get_classes(interpreter, top_k=1, score_threshold=0.0)
    
    # Log or print the classes
    if classes:
        for c in classes:
            logging.info(f"Predicted Class ID: {c.id}, Score: {c.score:.2f}")
    else:
        logging.info("No predictions above the score threshold.")
    
    return classes


def display_results(frame: np.ndarray, classes: list, labels: dict, position: tuple = (10, 30)) -> np.ndarray:
    """Display the inference results on the frame."""
    for c in classes:
        label = labels.get(c.id, f"Class {c.id}")
        score = c.score
        cv2.putText(frame, f"{label}: {score:.2f}", position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return frame


def run_hand_gesture():
    """Main function to run hand gesture recognition."""
    logging.basicConfig(level=logging.INFO)

    MODEL_FILE = "hand_command_uint8_v2.tflite"
    LABELS_FILE = "labels.txt"

    # Load model and labels
    interpreter = load_model(MODEL_FILE)
    print("model loaded succesfully")
    labels = load_labels(LABELS_FILE) if LABELS_FILE else {}
    input_shape = common.input_size(interpreter)
    input_details = interpreter.get_input_details()

    # Set up the camera
    cap = setup_camera()
    logging.info("Camera setup complete. Press 'q' to quit.")

    try:
        while True:
            start_time = time.time()

            ret, frame = cap.read()
            if not ret:
                logging.error("Error: Unable to read from the camera.")
                break
            # Inside the loop before preprocessing the frame
            logging.debug(f"Frame index: {int(time.time() * 1000)}")  # Log current time as a pseudo frame index
            cv2.imshow("Debug Input Frame", frame)  # Display the current frame for visual confirmation

            # Preprocess the frame, run inference, and display results
            input_tensor = preprocess_frame(frame, input_shape, input_details)
            classes = run_inference(interpreter, input_tensor)
            if classes:
                for c in classes:
                    print(f"Detected: {labels.get(c.id, 'Unknown')} with confidence {c.score:.2f}")
            else:
                print("No confident predictions.")
            frame = display_results(frame, classes, labels)

            # Show frame
            cv2.imshow("Hand Gesture Recognition", frame)

            # Calculate and display FPS
            fps = 1.0 / (time.time() - start_time)
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            fps = 1.0 / (time.time() - start_time)
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_hand_gesture()

