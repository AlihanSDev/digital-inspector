import cv2
import os
import json
import time
from ultralytics import YOLO

ID_TO_CAT = {0: "signature", 1: "stamp", 2: "qr"}


def infer(model_path, images_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    model = YOLO(model_path)
    results_json = {"metadata": {}, "images": {}}

    image_files = [f for f in os.listdir(images_dir) if f.endswith(".png")]
    total_time = 0.0
    total_images = len(image_files)

    for img in image_files:
        path = os.path.join(images_dir, img)

        start_time = time.time()
        pred = model(path, conf=0.25)[0]
        elapsed_time = time.time() - start_time
        total_time += elapsed_time

        image = cv2.imread(path)
        objects = []

        if pred.boxes is not None:
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

        cv2.imwrite(os.path.join(out_dir, img), image)
        results_json["images"][img] = objects

    # Добавляем метаданные
    results_json["metadata"] = {
        "total_images_processed": total_images,
        "total_time_seconds": round(total_time, 2),
        "average_time_per_image_seconds": round(total_time / total_images, 3) if total_images > 0 else 0,
        "images_per_second": round(total_images / total_time, 2) if total_time > 0 else 0
    }

    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results_json, f, indent=2, ensure_ascii=False)

    print(f"Обработано {total_images} изображений за {total_time:.2f} секунд")
    print(f"Среднее время на изображение: {results_json['metadata']['average_time_per_image_seconds']:.3f} с")
    print(f"Скорость: {results_json['metadata']['images_per_second']} изображений/с")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(__file__))
    model_path = os.path.join(project_root, "best.pt")
    images_dir = os.path.join(project_root, "data", "images")
    out_dir = os.path.join(project_root, "predictions")

    infer(model_path, images_dir, out_dir)