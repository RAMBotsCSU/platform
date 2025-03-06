import cv2
import numpy as np
import logging
from pycoral.utils import edgetpu
from pycoral.adapters import common, classify
import time
import asyncio

from robot.sparky import Sparky
from ..mode import Mode


class HandGestureMode(Mode):

    def __init__(self, robot: Sparky) -> None:
        super().__init__(robot)
        
        logging.basicConfig(level=logging.INFO)

        # Change depending on the model being used
        self.MODEL_FILE = "../../Resources/ai_models/hand_command_uint8_v2.tflite"
        self.LABELS_FILE = "../../Resources/labels.txt"

        # Loading model and labels
        self.interpreter = self.load_model(self.MODEL_FILE)
        print("model loaded succesfully")
        self.labels = self.load_labels(self.LABELS_FILE) if self.LABELS_FILE else {}
        self.input_shape = common.input_size(self.interpreter)
        self.input_details = self.interpreter.get_input_details()

        # Setting up camera
        self.cap = self.setup_camera()

    
    def load_model(self, model_path: str):
        try:
            interpreter = edgetpu.make_interpreter(model_path)
            interpreter.allocate_tensors()
            logging.info("Model loaded successfully.")
            return interpreter
        except Exception as e:
            logging.error(f"Failed to load model: {e}")
            raise


    def load_labels(self, labels_path: str) -> dict:
        try:
            with open(labels_path, 'r') as f:
                return {int(line.split()[0]): line.strip().split(maxsplit=1)[1] for line in f.readlines()}
        except Exception as e:
            logging.error(f"Failed to load labels: {e}")
            raise


    def setup_camera(self, camera_index: int = 0, width: int = 640, height: int = 480):
        
        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
            raise ValueError("Error: Camera not found or could not be opened.")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, 30)

        return cap
    

    def preprocess_frame(self, frame):

        resized_frame = cv2.resize(frame, self.input_shape)
        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        scale, zero_point = self.input_details[0]['quantization']
        if scale > 0:
            resized_frame = ((resized_frame / 255.0) / scale + zero_point).astype(np.uint8)
        input_tensor = np.expand_dims(resized_frame, axis=0)
        
        return input_tensor
    

    def run_inference(self, input_tensor):
        input_details = self.interpreter.get_input_details()
        self.interpreter.set_tensor(input_details[0]['index'], input_tensor)
        self.interpreter.invoke()

        classes = classify.get_classes(self.interpreter, top_k=1, score_threshold=0.0)

        return classes
    
        
    def display_results(frame: np.ndarray, classes: list, labels: dict, position: tuple = (10, 30)) -> np.ndarray:
        for c in classes:
            label = labels.get(c.id, f"Class {c.id}")
            score = c.score
            cv2.putText(frame, f"{label}: {score:.2f}", position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame
    
    # unsure if this works
    def smooth_move(current_value, target_value, step=10):
        if current_value < target_value:
            return min(current_value + step, target_value)
        elif current_value > target_value:
            return max(current_value - step, target_value)
        return current_value
    

    async def start(self):
        
        logging.info("Starting Hand Gesture Mode. Press 'q' to quit.")
        
        try:
            while True:

                start_time = time.time() # only used to see how long inference takes
                ret, frame = self.cap.read()

                if not ret:
                    logging.error("Error: Unable to read from the camera.")
                    break

                cv2.imshow("Debug Input Frame", frame)

                input_tensor = self.preprocess_frame(frame)
                classes = self.run_inference(input_tensor)

                # movement values
                rfb, rlr, lfb, llr, rt, lt = 0, 0, 0, 0, 0, 0

                if classes:
                    for c in classes:
                        gesture = self.labels.get(c.id, "Unknown")
                        print(f"Detected: {gesture} with confidence {c.score:.2f}")

                        # TODO figure out values 
                        
                        if c.score >= 0.9: # confidence threshold

                            placeholder_indent = 0

                            # if gesture == "one":  # Move forward
                            #     taget_rfb, target_lfb = 100, 100
                            #     target_rlr, target_llr, target_rt, target_lt = 0, 0, 0, 0

                            # elif gesture == "peace_inverted":  # Move backward
                            #     target_rfb, target_lfb = 100, 100
                            #     target_rlr, target_llr, target_rt, target_lt = 0, 0, 0, 0

                            # elif gesture == "palm":  # Push-up (raise body)
                            #     target_rfb, target_lfb = 100, 100
                            #     target_rfb, tareget_lfb, target_rlr, target_llr = 0, 0, 0, 0

                            # elif gesture == "fist":  # Push-down (lower body)
                            #     target_rt, target_lt = 50, 50
                            #     targetrfb, target_lfb, target_rlr, target_llr = 0, 0, 0, 0

                            # elif gesture == "stop":  # Stop all movement
                            #     target_rfb, target_rlr, target_lfb, target_llr, target_rt, target_lt = 0, 0, 0, 0, 0, 0

                # rfb = self.smooth_move(rfb, target_rfb)
                # rlr = self.smooth_move(rlr, target_rlr)
                # lfb = self.smooth_move(lfb, target_lfb)
                # llr = self.smooth_move(llr, target_llr)
                # rt = self.smooth_move(rt, target_rt)
                # lt = self.smooth_move(lt, target_lt)

            
                frame = self.display_results(frame, classes, self.labels)

                await self.robot.move(rfb, rlr, lfb, llr, rt, lt)
                await asyncio.sleep(0.1)

        finally:
            self.cap.release()
            cv2.destroyAllWindows()


async def setup(robot: Sparky):
    return HandGestureMode(robot)
