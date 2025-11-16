import os
import re
from pdf2image import convert_from_path

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # digital-inspector root
PDF_DIR = os.path.join(BASE_DIR, "data", "pdfs")
IMG_DIR = os.path.join(BASE_DIR, "data", "images")

def safe_name(name: str):
    return re.sub(r'[\\/:"*?<>|]+', '_', name)

def convert_pdfs(pdf_dir, out_dir, dpi=300):
    os.makedirs(out_dir, exist_ok=True)
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

    for pdf in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf)
        safe_pdf = safe_name(pdf)

        pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=r"C:\poppler-25.11.0\Library\bin")
        for i, page in enumerate(pages, start=1):
            out_path = os.path.join(out_dir, f"{safe_pdf}_page_{i}.png")
            page.save(out_path, "PNG")
            print("Saved:", out_path)

if __name__ == "__main__":
    convert_pdfs(PDF_DIR, IMG_DIR)
