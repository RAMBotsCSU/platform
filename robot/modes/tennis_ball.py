import threading
import time
import numpy as np
import cv2
from PIL import Image
from pycoral.utils import edgetpu
from utilities import calculate_direction, bbox_center_point
import queue
import os

class MachineLearningHandler:
    def __init__(self, controller, ball_queue):
        """
        Initializes the MachineLearningHandler with the given controller and ball_queue.

        Args:
            controller (MyController): The controller instance.
            ball_queue (queue.Queue): Queue to communicate movement commands based on ball tracking.
        """
        self.controller = controller
        self.ball_queue = ball_queue

        # Paths to the machine learning model
        self.ball_model_path = 'Resources/Models/BallTrackingModelQuant_edgetpu.tflite'

        # Camera settings
        self.CAMERA_WIDTH = 320
        self.CAMERA_HEIGHT = 240
        self.INPUT_WIDTH_AND_HEIGHT = 224

        # Initialize the interpreter for ball tracking
        self.ball_interpreter = None
        self.input_index = None
        self.initialize_ball_model()

    def initialize_ball_model(self):
        """
        Initializes the Edge TPU interpreter for the ball tracking model.
        """
        try:
            # Initialize the Edge TPU interpreter
            self.ball_interpreter = edgetpu.make_interpreter(self.ball_model_path)
            self.ball_interpreter.allocate_tensors()

            # Get input tensor details
            input_details = self.ball_interpreter.get_input_details()
            self.input_index = input_details[0]['index']
            print("Ball tracking model initialized successfully.")
        except Exception as e:
            print(f"Error initializing ball tracking model: {e}")

    def ball_thread_funct(self):
        """
        Function to process video frames and perform ball tracking.
        This function runs in a separate thread.
        """
        # Initialize the video capture from the default camera
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, 30)

        if not cap.isOpened():
            print("Error: Could not open video capture.")
            return

        print("Ball tracking thread started.")
        try:
            while True:
                # Check if the machine learning mode is active
                if not self.controller.running_ML:
                    time.sleep(0.1)
                    continue

                # Read a frame from the camera
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture image.")
                    continue

                # Preprocess the frame
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (self.INPUT_WIDTH_AND_HEIGHT, self.INPUT_WIDTH_AND_HEIGHT))
                input_data = np.expand_dims(image, axis=0).astype(np.uint8)

                # Set the input tensor
                self.ball_interpreter.set_tensor(self.input_index, input_data)

                # Run inference
                self.ball_interpreter.invoke()

                # Get the output tensors
                output_details = self.ball_interpreter.get_output_details()
                positions = self.ball_interpreter.get_tensor(output_details[0]['index'])
                confidences = self.ball_interpreter.get_tensor(output_details[1]['index']) / 255.0

                # Process the outputs
                result = self.process_ball_detection(positions, confidences)

                # If a ball is detected, calculate the movement direction
                if result:
                    pos = result['pos']
                    # Scale positions back to original frame size
                    scale_x = self.CAMERA_WIDTH / self.INPUT_WIDTH_AND_HEIGHT
                    scale_y = self.CAMERA_HEIGHT / self.INPUT_WIDTH_AND_HEIGHT
                    x1 = int(pos[0] * scale_x)
                    y1 = int(pos[1] * scale_y)
                    x2 = int(pos[2] * scale_x)
                    y2 = int(pos[3] * scale_y)

                    # Calculate the center of the bounding box
                    center = bbox_center_point(x1, y1, x2, y2)

                    # Determine the direction to move
                    move_value = calculate_direction(center[0], frame_width=self.CAMERA_WIDTH)

                    # Put the move command into the ball_queue
                    self.ball_queue.put(move_value)
                else:
                    # If no ball detected, you may decide to stop moving or keep previous command
                    pass

                # Optional: Display the frame with bounding box (for debugging)
                # self.display_result(result, frame)

                # Add a small delay to limit the processing rate
                time.sleep(0.05)
        finally:
            # Release the video capture when done
            cap.release()
            cv2.destroyAllWindows()
            print("Ball tracking thread terminated.")

    def process_ball_detection(self, positions, confidences):
        """
        Processes the detection results from the ball tracking model.

        Args:
            positions (np.array): Array of bounding box positions.
            confidences (np.array): Array of confidence scores.

        Returns:
            dict or None: Returns a dictionary with 'pos' key if a valid detection is found,
                          otherwise returns None.
        """
        # Iterate over detections
        for idx, score in enumerate(confidences):
            pos = positions[idx]
            area_pos = self.area(pos)
            if score > 0.99 and (350 <= area_pos < 50176):
                # Valid detection found
                return {'pos': pos}
        return None

    def area(self, pos):
        """
        Calculates the area of a bounding box given by positions.

        Args:
            pos (list or np.array): Positions [x1, y1, x2, y2].

        Returns:
            float: The area of the bounding box.
        """
        side_length = self.distance((pos[0], pos[1]), (pos[2], pos[3]))
        return side_length ** 2

    def distance(self, point1, point2):
        """
        Calculates the Euclidean distance between two points.

        Args:
            point1 (tuple): Coordinates (x1, y1).
            point2 (tuple): Coordinates (x2, y2).

        Returns:
            float: The distance between the two points.
        """
        return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

    def display_result(self, result, frame):
        """
        Displays the detection results on the frame.

        Args:
            result (dict): Detection result containing positions.
            frame (np.array): The original video frame.
        """
        if result:
            pos = result['pos']
            scale_x = self.CAMERA_WIDTH / self.INPUT_WIDTH_AND_HEIGHT
            scale_y = self.CAMERA_HEIGHT / self.INPUT_WIDTH_AND_HEIGHT
            x1 = int(pos[0] * scale_x)
            y1 = int(pos[1] * scale_y)
            x2 = int(pos[2] * scale_x)
            y2 = int(pos[3] * scale_y)

            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.putText(frame, 'Tennis Ball', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        # Display the frame
        cv2.imshow('Ball Tracking', frame)
        cv2.waitKey(1)
