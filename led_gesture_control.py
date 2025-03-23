import cv2
import mediapipe as mp
import pyfirmata2
import time
import math

# Try connecting to Arduino safely
try:
    # Attempt to establish a connection to the Arduino board on COM8
    board = pyfirmata2.Arduino("COM8")  # Update the COM port accordingly
    # Define the pin for controlling the PWM output (e.g., controlling the LED brightness)
    ledPin = board.get_pin("d:3:p")     # Update the PWM Pin accordingly
except Exception as e:
    # Print error message if connection fails and exit the program
    print(f"Error connecting to Arduino: {e}")
    exit()

# Initialize Video Capture
cap = cv2.VideoCapture(0)               # Use default camera (usually the first webcam)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)  # Set the frame width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500) # Set the frame height
cap.set(cv2.CAP_PROP_FPS, 30)           # Set the frames per second to 30

# Initialize MediaPipe components for hand tracking
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hand = mp_hands.Hands(max_num_hands=1)  # Only track one hand at a time

# Define the distance range for controlling PWM values
MIN_DISTANCE = 0.05  # Minimum hand distance (smallest pinch)
MAX_DISTANCE = 0.35  # Maximum hand distance (widest pinch)
pwm_smoothed = 0     # Initialize a variable to store the smoothed PWM value
alpha = 0.5          # Exponential Moving Average (EMA) smoothing factor (adjust for smoother transitions)

while True:
    success, frame = cap.read()  # Capture a frame from the video feed
    if not success:
        continue  # Skip the frame if it was not read successfully

    frame = cv2.flip(frame, 1)  # Flip the frame horizontally (mirror image)
    RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB for MediaPipe processing
    result = hand.process(RGB_frame)  # Process the frame using MediaPipe hand tracking

    if result.multi_hand_landmarks:
        # If hand landmarks are detected, process them
        handLandmarks = result.multi_hand_landmarks[0]  # Get the first detected hand's landmarks
        thumbTip = handLandmarks.landmark[4]  # Thumb tip landmark
        indexTip = handLandmarks.landmark[8]  # Index finger tip landmark

        # Get the frame dimensions
        h, w, _ = frame.shape
        # Convert the normalized coordinates to pixel values
        thumb_x, thumb_y = int(thumbTip.x * w), int(thumbTip.y * h)
        index_x, index_y = int(indexTip.x * w), int(indexTip.y * h)

        # Calculate the Euclidean distance between the thumb tip and index tip
        distance = math.sqrt((thumbTip.x - indexTip.x) ** 2 + (thumbTip.y - indexTip.y) ** 2)

        # Normalize the distance to a PWM value between 0 and 1
        if distance < MIN_DISTANCE:
            pwm_value = 0  # If distance is too small, set PWM to 0
        elif distance > MAX_DISTANCE:
            pwm_value = 1  # If distance is too large, set PWM to 1
        else:
            pwm_value = (distance - MIN_DISTANCE) / (MAX_DISTANCE - MIN_DISTANCE)  # Normalize between 0 and 1

        # Apply smoothing using Exponential Moving Average (EMA) to reduce PWM fluctuations
        pwm_smoothed = alpha * pwm_value + (1 - alpha) * pwm_smoothed
        ledPin.write(pwm_smoothed)  # Write the smoothed PWM value to the Arduino pin

        # Debugging output to show the current distance and PWM value
        print(f"Distance: {distance:.4f}, PWM: {pwm_smoothed:.4f}")

        # Draw a line between the thumb and index tip to visualize the distance
        cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 3)

        # Draw the hand landmarks and connections on the frame
        mp_drawing.draw_landmarks(frame, handLandmarks, mp_hands.HAND_CONNECTIONS)

    # Resize the frame for display (optional)
    frame = cv2.resize(frame, (450, 350))  # Resize for a smaller display window
    cv2.imshow("Capture Image", frame)  # Display the frame in a window

    # Exit loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
