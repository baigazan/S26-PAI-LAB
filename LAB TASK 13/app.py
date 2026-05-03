import cv2
import imutils
import numpy as np
import time
import pyautogui
import os
import subprocess
from keras.preprocessing.image import img_to_array
from keras.models import load_model

# Open YouTube in browser
os.system('open -a "Google Chrome" https://www.youtube.com/watch?v=jNQXAC9IVRw')
time.sleep(5)  # Wait for browser to open

# Activate Chrome to bring it to front
subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
time.sleep(2)  # Wait for activation

# Click in the center of the screen to focus the YouTube player
screen_width, screen_height = pyautogui.size()
pyautogui.click(screen_width // 2, screen_height // 2)
time.sleep(1)  # Wait for click

# Paths to models
detection_model_path = 'haarcascade_files/haarcascade_frontalface_default.xml'
emotion_model_path = 'models/_mini_XCEPTION.102-0.66.hdf5'

# Load models
print("Loading emotion model...")
face_detection = cv2.CascadeClassifier(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]

# Setup webcam
print("Setting up webcam...")
cv2.namedWindow('your_face')
cv2.resizeWindow('your_face', 640, 480)
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Camera failed to open. Trying index 1...")
    camera = cv2.VideoCapture(1)
if camera.isOpened():
    print("Camera opened successfully!")
else:
    print("Camera failed to open on both indices. Check permissions or hardware.")
    exit(1)

# Timer to throttle media control actions
last_action_time = time.time()
action_delay = 5  # seconds

print("Starting detection loop...")
while True:
    print("Reading frame...")
    ret, frame = camera.read()
    if not ret:
        print("Failed to read frame. Reason: Camera may not be accessible in this environment (e.g., VS Code terminal). Try running in macOS Terminal app.")
        break

    frame = imutils.resize(frame, width=300)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detection.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5,
        minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE
    )

    canvas = np.zeros((250, 300, 3), dtype="uint8")
    frameClone = frame.copy()
    preds = []

    if len(faces) > 0:
        print(f"Faces detected: {len(faces)}")
        (fX, fY, fW, fH) = sorted(
            faces, reverse=True,
            key=lambda x: (x[2] - x[0]) * (x[3] - x[1])
        )[0]

        roi = gray[fY:fY + fH, fX:fX + fW]
        roi = cv2.resize(roi, (64, 64))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        preds = emotion_classifier.predict(roi)[0]
        emotion_probability = np.max(preds)
        label = EMOTIONS[preds.argmax()]
        print(f"Emotion: {label}, Probability: {emotion_probability:.2f}")

        # Media Control Actions (throttled)
        current_time = time.time()
        if current_time - last_action_time > action_delay:
            if label == 'happy':
                print(f"Performing action for happy")
                pyautogui.press('space')  # Play/Pause
            elif label == 'sad':
                print(f"Performing action for sad")
                pyautogui.press('m')  # Mute
            elif label == 'surprised':
                print(f"Performing action for surprised")
                pyautogui.hotkey('shift', 'n')  # Next video
            elif label == 'angry':
                print(f"Performing action for angry")
                pyautogui.press('up')  # Volume up
            last_action_time = current_time
        else:
            print(f"Action throttled for {label}")

        # Display emotion label and rectangle
        cv2.putText(frameClone, label, (fX, fY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),
                      (0, 0, 255), 2)
    else:
        print("No faces detected")

    # Draw emotion probability bars
    for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
        text = "{}: {:.2f}%".format(emotion, prob * 100)
        w = int(prob * 300)
        cv2.rectangle(canvas, (7, (i * 35) + 5),
                      (w, (i * 35) + 35), (0, 0, 255), -1)
        cv2.putText(canvas, text, (10, (i * 35) + 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (255, 255, 255), 2)

    # Show windows
    cv2.imshow('your_face', frameClone)
    cv2.imshow("Probabilities", canvas)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
camera.release()
cv2.destroyAllWindows()