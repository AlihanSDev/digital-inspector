import gradio as gr
import cv2
import json
from ultralytics import YOLO
from pdf2image import convert_from_path
import numpy as np
import tempfile
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "best.pt")
model = YOLO(MODEL_PATH)
ID_TO_CAT = {0: "signature", 1: "stamp", 2: "qr"}

def process(file):
    filepath = file.name

    images_with_boxes = []
    all_objects = []

    if filepath.lower().endswith(".pdf"):
        pages = convert_from_path(filepath, dpi=200, poppler_path=r"C:\poppler-25.11.0\Library\bin")

        for i, page in enumerate(pages):
            img = np.array(page)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            temp_img_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
            cv2.imwrite(temp_img_path, img)

            pred = model(temp_img_path, conf=0.25)[0]
            image = cv2.imread(temp_img_path)
            objects = []

            if pred.boxes:
                for box in pred.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    objects.append({
                        "category": ID_TO_CAT[cls],
                        "bbox": [x1, y1, x2 - x1, y2 - y1],
                        "confidence": conf
                    })

                    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            images_with_boxes.append(image_rgb)
            all_objects.append({
                "page": i + 1,
                "objects": objects
            })

            os.unlink(temp_img_path)

    else:
        pred = model(filepath, conf=0.25)[0]
        image = cv2.imread(filepath)
        objects = []

        if pred.boxes:
            for box in pred.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                objects.append({
                    "category": ID_TO_CAT[cls],
                    "bbox": [x1, y1, x2 - x1, y2 - y1],
                    "confidence": conf
                })

                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        images_with_boxes.append(image_rgb)
        all_objects.append({
            "page": 1,
            "objects": objects
        })

    return images_with_boxes, all_objects

demo = gr.Interface(
    fn=process,
    inputs=gr.File(label="Upload PDF or PNG"),
    outputs=[gr.Gallery(label="Pages with Detections"), gr.JSON(label="Detection Results")],
    title="Digital Inspector",
    description="Detect signatures, stamps and QR codes on all pages of PDF or image."
)

if __name__ == "__main__":
    demo.launch()