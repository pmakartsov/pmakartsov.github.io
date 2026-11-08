"""Добавить скан документа (PDF или картинку) в галерею «Образование».

Запуск:  python tools/add_document.py "путь\\к\\файлу.pdf" cert-07
Создаёт docs/assets/img/docs/<имя>-640.webp и <имя>-1800.webp и записывает размеры в src/images.json.
Затем добавьте подпись в src/data/documents.json и пересоберите сайт (python tools/build.py).
Нужен Pillow, для PDF — ещё PyMuPDF (pip install pymupdf). Из PDF берётся первая страница.
"""
import io
import json
import os
import sys
from PIL import Image, ImageOps

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(ROOT, "docs", "assets", "img", "docs")
MANIFEST = os.path.join(ROOT, "src", "images.json")
WIDTHS = (640, 1800)


def load(path):
    if path.lower().endswith(".pdf"):
        import pymupdf
        page = pymupdf.open(path)[0]
        zoom = 2400 / page.rect.width  # с запасом, потом уменьшаем — так текст чётче
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    path, name = sys.argv[1], sys.argv[2]
    im = load(path)
    images = json.load(open(MANIFEST, encoding="utf-8"))
    variants = []
    for w in WIDTHS:
        w = min(w, im.width)
        h = round(im.height * w / im.width)
        fn = f"{name}-{w}.webp"
        im.resize((w, h), Image.LANCZOS).save(os.path.join(DOCS, fn), "WEBP", quality=78, method=6)
        variants.append({"file": fn, "w": w, "h": h, "kb": round(os.path.getsize(os.path.join(DOCS, fn)) / 1024)})
    images[name] = variants
    json.dump(images, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(name + ":", ", ".join(f'{v["file"]} {v["w"]}x{v["h"]} {v["kb"]} КБ' for v in variants))


if __name__ == "__main__":
    main()
