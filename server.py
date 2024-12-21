import cv2
import argparse
import numpy as np
from ultralytics import YOLO
import time
import socket

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 Live Detection")
    parser.add_argument(
        "--model-path",
        default="best.pt",  # Path to your YOLO model
        type=str,
        help="Path to the YOLO model file"
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Host and port for the server
    HOST = '0.0.0.0'  # Listen on all available interfaces
    PORT = 12345

    # Bind the socket to the host and port
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen(1)
    print('Server listening on', PORT)

    # Accept client connection
    client_socket, client_address = server_socket.accept()
    print('Connected by', client_address)

    model_path = args.model_path

    # Load the YOLO model
    model = YOLO(model_path)

    confidence_threshold = 0.5  # You can adjust this value as needed

    # Capture video from webcam
    cap = cv2.VideoCapture(0)

    start_time = time.time()

    # Loop through video frames
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Unable to capture frame from webcam.")
            break

        # Divide the frame into four quadrants
        height, width, _ = frame.shape
        half_width = width // 2
        half_height = height // 2

        # Define the four regions of interest
        roi1 = frame[:half_height, :half_width]
        roi2 = frame[:half_height, half_width:]
        roi3 = frame[half_height:, :half_width]
        roi4 = frame[half_height:, half_width:]

        # Perform object detection on each ROI
        results1 = model(roi1, conf=confidence_threshold, agnostic_nms=True)[0]
        results2 = model(roi2, conf=confidence_threshold, agnostic_nms=True)[0]
        results3 = model(roi3, conf=confidence_threshold, agnostic_nms=True)[0]
        results4 = model(roi4, conf=confidence_threshold, agnostic_nms=True)[0]

        # Count detected objects in each ROI
        num_objects1 = len(results1)
        num_objects2 = len(results2)
        num_objects3 = len(results3)
        num_objects4 = len(results4)

        # Get the quadrant with the most objects
        max_objects_quadrant = max(num_objects1, num_objects2, num_objects3, num_objects4)

        # Create an array with the values of the four quadrants
        object_counts = [num_objects1, num_objects2, num_objects3, num_objects4]

        # Draw rectangles around each quadrant and label them
        cv2.rectangle(frame, (0, 0), (half_width, half_height), (255, 0, 0), 2)
        cv2.putText(frame, "A", (half_width // 2, half_height // 2), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 0, 0), 2)

        cv2.rectangle(frame, (half_width, 0), (width, half_height), (0, 255, 0), 2)
        cv2.putText(frame, "B", (half_width + half_width // 2, half_height // 2), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        cv2.rectangle(frame, (0, half_height), (half_width, height), (0, 0, 255), 2)
        cv2.putText(frame, "C", (half_width // 2, half_height + half_height // 2), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)

        cv2.rectangle(frame, (half_width, half_height), (width, height), (255, 255, 0), 2)
        cv2.putText(frame, "D", (half_width + half_width // 2, half_height + half_height // 2), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 0), 2)

        # Display object count for each quadrant
        cv2.putText(frame, f"A Objects: {num_objects1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 0, 0), 2)
        cv2.putText(frame, f"B Objects: {num_objects2}", (half_width + 10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)
        cv2.putText(frame, f"C Objects: {num_objects3}", (10, half_height + 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)
        cv2.putText(frame, f"D Objects: {num_objects4}", (half_width + 10, half_height + 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 0), 2)

        cv2.imshow("YOLO Live Detection", frame)

        # Send the array to the client
        try:
            data = bytes(str(object_counts), 'utf-8')
            client_socket.sendall(data)
            time.sleep(1)  # Add 1-second delay after sending data
        except Exception as e:
            print('Error sending data:', e)
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    main()

    # gg