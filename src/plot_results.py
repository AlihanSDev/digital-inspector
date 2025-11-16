import matplotlib
matplotlib.use('Agg')  # Без GUI
import matplotlib.pyplot as plt
import json
import os
import cv2

def plot_detection_stats(results_data, output_path):
    categories = {"signature": 0, "stamp": 0, "qr": 0}
    for img_data in results_data["images"].values():
        for obj in img_data:
            cat = obj["category"]
            categories[cat] += 1

    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories.keys(), categories.values(), color=["#FF6B6B", "#4ECDC4", "#45B7D1"])
    plt.title("Количество обнаруженных объектов", fontsize=14, fontweight='bold')
    plt.xlabel("Категория", fontsize=12)
    plt.ylabel("Число", fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height, f'{int(height)}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_category_pie(results_data, output_path):
    categories = {"signature": 0, "stamp": 0, "qr": 0}
    for img_data in results_data["images"].values():
        for obj in img_data:
            cat = obj["category"]
            categories[cat] += 1

    sizes = list(categories.values())
    if sum(sizes) == 0:
        return

    plt.figure(figsize=(7, 7))
    plt.pie(sizes, labels=list(categories.keys()), autopct='%1.1f%%', startangle=90, colors=["#FF6B6B", "#4ECDC4", "#45B7D1"])
    plt.title("Доля категорий среди всех детекций")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def plot_confidence_distribution(results_data, output_path):
    confidences = []
    for img_data in results_data["images"].values():
        for obj in img_data:
            confidences.append(obj["confidence"])

    plt.figure(figsize=(10, 5))
    plt.hist(confidences, bins=20, color='#4ECDC4', edgecolor='black', alpha=0.7)
    plt.title("Распределение уверенности (confidence) модели")
    plt.xlabel("Уверенность")
    plt.ylabel("Частота")
    plt.grid(True, alpha=0.3)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def plot_objects_per_page_hist(results_data, output_path):
    counts = [len(objs) for objs in results_data["images"].values()]
    plt.figure(figsize=(10, 5))
    plt.hist(counts, bins=max(1, len(set(counts))), color='#FF6B6B', edgecolor='black', alpha=0.7)
    plt.title("Распределение числа объектов на странице")
    plt.xlabel("Число объектов")
    plt.ylabel("Количество страниц")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def plot_inference_speed(results_data, output_path):
    metadata = results_data["metadata"]
    avg_time = metadata.get("average_time_per_image_seconds", 0)
    images_per_sec = metadata.get("images_per_second", 0)

    fig, ax = plt.subplots(figsize=(8, 2))
    ax.axis('off')
    ax.text(0.1, 0.6, f"Среднее время на изображение: {avg_time} с", fontsize=14)
    ax.text(0.1, 0.3, f"Скорость обработки: {images_per_sec} изображений/с", fontsize=14)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def save_example_detection(predictions_dir, output_path):
    for img_name in os.listdir(predictions_dir):
        if img_name.endswith(".png") and "_" in img_name:
            img_path = os.path.join(predictions_dir, img_name)
            img = cv2.imread(img_path)
            if img is not None and img.size > 0:
                cv2.imwrite(output_path, img)
                print(f"Пример детекции сохранён: {output_path}")
                return

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(__file__))
    results_path = os.path.join(project_root, "predictions", "results.json")
    screenshots_dir = os.path.join(project_root, "screenshots")
    predictions_dir = os.path.join(project_root, "predictions")

    os.makedirs(screenshots_dir, exist_ok=True)

    if not os.path.exists(results_path):
        print("results.json не найден. Запусти inference.py!")
        exit()

    with open(results_path, "r", encoding="utf-8") as f:
        results_data = json.load(f)

    plot_detection_stats(results_data, os.path.join(screenshots_dir, "detection_counts.png"))
    plot_category_pie(results_data, os.path.join(screenshots_dir, "category_pie.png"))
    plot_confidence_distribution(results_data, os.path.join(screenshots_dir, "confidence_hist.png"))
    plot_objects_per_page_hist(results_data, os.path.join(screenshots_dir, "objects_per_page.png"))
    plot_inference_speed(results_data, os.path.join(screenshots_dir, "speed_summary.png"))
    save_example_detection(predictions_dir, os.path.join(screenshots_dir, "example_detection.png"))

    print("Все графики сохранены в папку screenshots/")