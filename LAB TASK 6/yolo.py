import os
import cv2
import numpy as np
from datetime import datetime


# Paths (use files in repo root by default)
ROOT = os.path.dirname(os.path.abspath(__file__))
WEIGHTS = os.path.join(ROOT, 'yolov3.weights')
CFG = os.path.join(ROOT, 'yolov3.cfg')
NAMES = os.path.join(ROOT, 'coco.names')

# Load YOLO (fail early with helpful message)
if not os.path.exists(WEIGHTS) or not os.path.exists(CFG) or not os.path.exists(NAMES):
    raise FileNotFoundError('yolov3 weights/cfg/names not found. Run the downloader or place files in the project root.')

net = cv2.dnn.readNet(WEIGHTS, CFG)

with open(NAMES, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# get output layer names robustly
layer_names = net.getLayerNames()
try:
    outs_idx = net.getUnconnectedOutLayers()
    # net.getUnconnectedOutLayers() can return Nx1 array; flatten and convert
    outs_idx = outs_idx.flatten()
    output_layers = [layer_names[i - 1] for i in outs_idx]
except Exception:
    # fallback
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Animal classes (from COCO dataset)
animal_classes = {"cow", "sheep", "horse", "dog", "cat", "elephant"}


def _clamp_box(x, y, w, h, W, H):
    # Ensure box is inside image bounds and widths/heights positive
    x = max(0, int(x))
    y = max(0, int(y))
    w = int(w)
    h = int(h)
    if x + w > W:
        w = W - x
    if y + h > H:
        h = H - y
    w = max(0, w)
    h = max(0, h)
    return x, y, w, h


def detect_herd(image_path, conf_threshold=0.4, nms_threshold=0.4):
    img = cv2.imread(image_path)
    # If the path is a video or imread failed, try grabbing the first video frame
    if img is None:
        # try video
        cap = cv2.VideoCapture(image_path)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            raise ValueError(f'Could not read image or video: {image_path}')
        img = frame

    H, W = img.shape[:2]

    blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    # Detect objects
    for out in outputs:
        for detection in out:
            scores = detection[5:]
            if len(scores) == 0:
                continue
            class_id = int(np.argmax(scores))
            confidence = float(scores[class_id])

            if confidence > conf_threshold and classes[class_id] in animal_classes:
                center_x = float(detection[0]) * W
                center_y = float(detection[1]) * H
                w = float(detection[2]) * W
                h = float(detection[3]) * H

                x = center_x - (w / 2.0)
                y = center_y - (h / 2.0)

                x, y, w, h = _clamp_box(x, y, w, h, W, H)

                # Only keep boxes with area
                if w <= 0 or h <= 0:
                    continue

                boxes.append([int(x), int(y), int(w), int(h)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    centers = []

    result_img = img.copy()

    if len(boxes) > 0:
        # NMSBoxes expects boxes as [x, y, w, h]
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
        if len(indices) > 0:
            # indices may be nested array; flatten
            if isinstance(indices, (np.ndarray, list)):
                try:
                    flat = np.array(indices).flatten()
                except Exception:
                    flat = indices
            else:
                flat = indices

            for i in flat:
                i = int(i)
                x, y, w, h = boxes[i]
                label = classes[class_ids[i]]
                conf = confidences[i]

                centers.append((x + w // 2, y + h // 2))

                # styled box: thick with shadow (draw twice)
                cv2.rectangle(result_img, (x, y), (x + w, y + h), (0, 0, 0), thickness=5)
                cv2.rectangle(result_img, (x, y), (x + w, y + h), (34, 139, 34), thickness=2)
                text = f"{label} {conf:.2f}"
                cv2.putText(result_img, text, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(result_img, text, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

    # 🧠 Herd Detection (simple logic)
    herd_count = len(centers)

    if herd_count >= 3:
        cv2.putText(result_img, "HERD DETECTED!", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

    # Save with timestamp to avoid browser caching
    out_dir = os.path.join(ROOT, 'static', 'output')
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(out_dir, f'result_{ts}.jpg')
    cv2.imwrite(output_path, result_img)

    # return web path and count
    web_path = os.path.relpath(output_path, ROOT)
    return web_path.replace('\\', '/'), herd_count