"""Главная фотография (из 1.png), иконки сайта в виде знака Ψ и картинка для соцсетей.

Запуск:  python tools/make_hero_and_icons.py   (нужен Pillow)
"""
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(ROOT, "docs")
IMG = os.path.join(DOCS, "assets", "img")
MANIFEST = os.path.join(ROOT, "src", "images.json")
GREEN = (77, 107, 43)
BG = (248, 246, 241)

images = json.load(open(MANIFEST, encoding="utf-8"))

# --- главное фото: кадр 4:5, лицо в верхней трети
src = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, "1.png"))).convert("RGB")
hero = src.crop((121, 0, 1079, 1198))  # 958×1198 ≈ 4:5
variants = []
for w in (480, 800, 958):
    h = round(hero.height * w / hero.width)
    fn = f"pavel-hero-{w}.webp"
    hero.resize((w, h), Image.LANCZOS).save(os.path.join(IMG, fn), "WEBP", quality=82, method=6)
    variants.append({"file": fn, "w": w, "h": h, "kb": round(os.path.getsize(os.path.join(IMG, fn)) / 1024)})
images["pavel-hero"] = variants
hero.resize((800, 1000), Image.LANCZOS).save(os.path.join(IMG, "pavel-hero-800.jpg"), quality=82, optimize=True, progressive=True)

# старое главное фото больше не используется
for v in images.pop("pavel-portrait", []):
    p = os.path.join(IMG, v["file"])
    if os.path.exists(p):
        os.remove(p)
old_jpg = os.path.join(IMG, "pavel-portrait-800.jpg")
if os.path.exists(old_jpg):
    os.remove(old_jpg)
json.dump(images, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# --- иконка Ψ (рисуется с 8-кратным запасом для сглаживания)
def psi_icon(size, rounded=True):
    k = 8
    S = size * k
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = S / 64
    if rounded:
        d.rounded_rectangle((0, 0, S - 1, S - 1), radius=int(14 * u), fill=GREEN)
    else:
        d.rectangle((0, 0, S, S), fill=GREEN)
    w = int(5.5 * u)
    white = (255, 255, 255, 255)
    r = w / 2

    def cap(x, y):
        d.ellipse((x - r, y - r, x + r, y + r), fill=white)

    # чаша: две вертикали + нижняя полуокружность
    d.line((17 * u, 15 * u, 17 * u, 25 * u), fill=white, width=w)
    d.line((47 * u, 15 * u, 47 * u, 25 * u), fill=white, width=w)
    d.arc((17 * u - r, 10 * u - r, 47 * u + r, 40 * u + r), 0, 180, fill=white, width=w)
    # ствол и основание
    d.line((32 * u, 11 * u, 32 * u, 51 * u), fill=white, width=w)
    d.line((24 * u, 51 * u, 40 * u, 51 * u), fill=white, width=w)
    for x, y in ((17, 15), (47, 15), (32, 11), (24, 51), (40, 51)):
        cap(x * u, y * u)
    return im.resize((size, size), Image.LANCZOS)


psi_icon(180, rounded=False).convert("RGB").save(os.path.join(DOCS, "apple-touch-icon.png"))
psi_icon(192).save(os.path.join(IMG, "icon-192.png"))
psi_icon(512).save(os.path.join(IMG, "icon-512.png"))
psi_icon(256).save(os.path.join(DOCS, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])


# --- картинка для соцсетей 1200×630
def font(names, size):
    for n in names:
        fp = os.path.join(r"C:\Windows\Fonts", n)
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


og = Image.new("RGB", (1200, 630), BG)
og.paste(src.crop((216, 120, 984, 1080)).resize((504, 630), Image.LANCZOS), (696, 0))
d = ImageDraw.Draw(og)
d.rectangle((0, 0, 14, 630), fill=GREEN)
d.text((80, 150), "Павел Макарцов", font=font(["georgiab.ttf", "georgia.ttf"], 66), fill=(23, 33, 27))
d.text((82, 245), "Психолог · КПТ · онлайн и очно", font=font(["segoeuisb.ttf", "segoeui.ttf"], 34), fill=GREEN)
for i, line in enumerate(["Тревога, выгорание, самооценка,", "отношения, подростки и родители,", "диагностика детей"]):
    d.text((82, 330 + i * 46), line, font=font(["segoeui.ttf"], 30), fill=(89, 100, 94))
d.text((82, 520), "+7 912 282-42-69 · Екатеринбург", font=font(["segoeuisb.ttf", "segoeui.ttf"], 30), fill=(23, 33, 27))
og.save(os.path.join(IMG, "og-image.jpg"), quality=86, optimize=True, progressive=True)

print("hero:", ", ".join(f'{v["w"]}x{v["h"]} {v["kb"]}KB' for v in variants))
