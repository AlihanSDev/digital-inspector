import os
import re
import json

CATEGORY_TO_ID = {"signature": 0, "stamp": 1, "qr": 2}

def safe(name):
    return re.sub(r'[\\/:"*?<>|]+', '_', name)

def convert_annotations(json_path, images_dir, labels_dir):
    os.makedirs(labels_dir, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for pdf_name, pages in data.items():
        safe_pdf = safe(pdf_name)

        for page_key, info in pages.items():
            page_num = page_key.split("_")[1]

            img_file = f"{safe_pdf}_page_{page_num}.png"
            label_file = f"{safe_pdf}_page_{page_num}.txt"

            img_path = os.path.join(images_dir, img_file)
            label_path = os.path.join(labels_dir, label_file)

            pw = info["page_size"]["width"]
            ph = info["page_size"]["height"]

            lines = []

            for ann in info["annotations"]:
                for _, item in ann.items():
                    cls = CATEGORY_TO_ID[item["category"]]
                    x, y = item["bbox"]["x"], item["bbox"]["y"]
                    w, h = item["bbox"]["width"], item["bbox"]["height"]

                    xc = (x + w / 2) / pw
                    yc = (y + h / 2) / ph
                    wn = w / pw
                    hn = h / ph

                    lines.append(f"{cls} {xc} {yc} {wn} {hn}")

            with open(label_path, "w") as f:
                f.write("\n".join(lines))

            print("Saved:", label_path)

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(__file__))
    json_path = os.path.join(project_root, "jsons", "selected_annotations.json")
    images_dir = os.path.join(project_root, "data", "images")
    labels_dir = os.path.join(project_root, "data", "labels")

    convert_annotations(json_path, images_dir, labels_dir)
