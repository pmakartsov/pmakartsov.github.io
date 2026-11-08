"""Одноразовая подготовка картинок/шрифтов из зеркала Tilda (E:\\Downloads\\site).
Для обычной работы не нужен — используйте build.py."""
import os, sys, json, re, shutil, urllib.request
from PIL import Image, ImageOps, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding="utf-8")

SRC = r"E:\Downloads\site\assets"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
IMG = os.path.join(OUT, "assets", "img")
DOCS = os.path.join(IMG, "docs")
FONTS = os.path.join(OUT, "assets", "fonts")
CSS = os.path.join(OUT, "assets", "css")
for d in (IMG, DOCS, FONTS, CSS, os.path.join(OUT, "assets", "js")):
    os.makedirs(d, exist_ok=True)

manifest = {}

def load(rel):
    im = Image.open(os.path.join(SRC, rel.replace("/", os.sep)))
    im = ImageOps.exif_transpose(im)
    return im

def save_variants(im, name, widths, folder=IMG, quality=80, crop=None):
    if crop:  # crop = target aspect (w/h), centered, biased to top for portraits
        w, h = im.size
        ar = crop
        if w / h > ar:
            nw = int(h * ar); x = (w - nw) // 2
            im = im.crop((x, 0, x + nw, h))
        else:
            nh = int(w / ar); y = int((h - nh) * 0.25)
            im = im.crop((0, y, w, y + nh))
    has_alpha = im.mode in ("RGBA", "LA", "P")
    im = im.convert("RGBA" if has_alpha else "RGB")
    out = []
    for w in widths:
        if w > im.width:
            w = im.width
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS)
        fn = f"{name}-{w}.webp"
        r.save(os.path.join(folder, fn), "WEBP", quality=quality, method=6)
        out.append({"file": fn, "w": w, "h": h, "kb": round(os.path.getsize(os.path.join(folder, fn)) / 1024)})
    manifest[name] = out
    return im

# --- photos of Pavel
p = save_variants(load("tild3537-6330-4662-b539-633365386432/IMG_6731.jpeg"), "pavel-portrait", [480, 800, 1200], crop=4/5)
p.convert("RGB").resize((800, 1000), Image.LANCZOS).save(os.path.join(IMG, "pavel-portrait-800.jpg"), quality=82, optimize=True, progressive=True)
save_variants(load("tild3736-3430-4433-b665-666263363539/IMG_6735.jpeg"), "pavel-about", [480, 800, 1200], crop=1)

# --- article images
save_variants(load("tild3766-3161-4561-b737-346139646331/image_fx_2.jpg"), "burnout-cover", [480, 800, 1024])
save_variants(load("tild3039-3432-4333-b966-656536396165/photo1413920346627a4.jpeg"), "burnout-photo", [800, 1200])
save_variants(load("tild6439-3836-4336-b562-353366663636/image_fx.jpg"), "burnout-illustration", [480, 800, 1024])
save_variants(load("tild3161-6365-4836-b866-313034393835/close-up-woman-natur.jpg"), "selfcare-cover", [480, 800, 1200, 1600])
save_variants(load("tild6534-3130-4461-b464-626432613334/noroot.png"), "card-burnout", [480, 716])
save_variants(load("tild6437-6237-4632-b237-323133633635/noroot.png"), "card-selfcare", [480, 800])
save_variants(load("tild3234-3162-4465-b035-643032626233/image_fx_6.jpeg"), "card-consultation", [480, 768])

# --- documents
diplomas = [
    "tild3831-6430-4835-a262-613661613530/photo.jpg",
    "tild6161-3037-4539-a161-623366326238/__page-0001.jpg",
    "tild3034-6233-4133-a535-346661303937/_6_1.jpeg",
    "tild3137-3733-4034-b066-636435616336/_5.jpeg",
    "tild6439-3863-4264-b363-663036376237/_4.jpeg",
    "tild6262-3438-4233-a661-623066333230/_3.jpeg",
    "tild3738-3133-4135-b430-353062653132/_2.jpeg",
    "tild3035-6330-4934-b032-653339316539/_1.jpeg",
]
certs = [
    "tild6362-3538-4933-b639-393764353732/___10.png",
    "tild6463-3732-4730-a430-303332666139/_1.jpeg",
    "tild6663-6235-4138-a261-393239353933/_2-fotor-20250417133.jpg",
    "tild3031-3630-4535-b439-346266353539/_3.jpeg",
    "tild6630-6563-4666-a334-393566353361/__page-0001.jpg",
    "tild3734-6563-4335-b966-393161363364/_5.jpeg",
]
for prefix, lst in (("diploma", diplomas), ("cert", certs)):
    for i, rel in enumerate(lst, 1):
        im = load(rel).convert("RGB")
        save_variants(im, f"{prefix}-{i:02d}", [640, 1800], folder=DOCS, quality=78)

# --- fonts (self-hosted, cyrillic + latin)
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
url = "https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&family=Manrope:wght@400..800&display=swap"
css = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua}), timeout=30).read().decode()
faces = []
for sub, block in re.findall(r"/\* (\S+) \*/\s*@font-face\s*{(.*?)}", css, flags=re.S):
    if sub not in ("cyrillic", "latin"):
        continue
    fam = re.search(r"font-family: '([^']+)'", block).group(1)
    style = re.search(r"font-style: (\w+)", block).group(1)
    weight = re.search(r"font-weight: ([\d ]+);", block).group(1)
    src = re.search(r"src: url\(([^)]+)\)", block).group(1)
    rng = re.search(r"unicode-range: ([^;]+);", block).group(1)
    fn = f"{fam.lower()}-{style}-{sub}.woff2"
    with urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": ua}), timeout=30) as r:
        open(os.path.join(FONTS, fn), "wb").write(r.read())
    faces.append(f"@font-face {{\n  font-family: \"{fam}\";\n  font-style: {style};\n  font-weight: {weight};\n  font-display: swap;\n  src: url(\"../fonts/{fn}\") format(\"woff2\");\n  unicode-range: {rng};\n}}")
open(os.path.join(OUT, "..", "src", "css", "00-fonts.css"), "w", encoding="utf-8").write("/* Self-hosted fonts: Lora, Manrope (OFL) */\n" + "\n".join(faces) + "\n")

# --- favicon / touch icon / og image
GREEN = (77, 107, 43); BG = (248, 246, 241)
def leaf_icon(size):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.22), fill=GREEN)
    s = size / 64
    # two leaves (approximate the svg mark)
    d.ellipse((18 * s, 14 * s, 38 * s, 44 * s), fill=(255, 255, 255))
    d.ellipse((30 * s, 22 * s, 48 * s, 48 * s), fill=(214, 228, 190))
    d.line((32 * s, 50 * s, 32 * s, 24 * s), fill=GREEN, width=max(2, int(3 * s)))
    return im
leaf_icon(180).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"))
leaf_icon(512).save(os.path.join(IMG, "icon-512.png"))
leaf_icon(192).save(os.path.join(IMG, "icon-192.png"))
ico = leaf_icon(64)
ico.save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

fdir = r"C:\Windows\Fonts"
def font(names, size):
    for n in names:
        fp = os.path.join(fdir, n)
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()
og = Image.new("RGB", (1200, 630), BG)
portrait = p.convert("RGB").resize((504, 630), Image.LANCZOS)
og.paste(portrait, (696, 0))
d = ImageDraw.Draw(og)
d.rectangle((0, 0, 14, 630), fill=GREEN)
d.text((80, 150), "Павел Макарцов", font=font(["georgiab.ttf", "georgia.ttf"], 66), fill=(23, 33, 27))
d.text((82, 245), "Психолог · КПТ · онлайн и очно", font=font(["segoeuisb.ttf", "segoeui.ttf"], 34), fill=GREEN)
for i, line in enumerate(["Тревога, выгорание, самооценка,", "отношения, поддержка подростков", "и родителей"]):
    d.text((82, 330 + i * 46), line, font=font(["segoeui.ttf"], 30), fill=(89, 100, 94))
d.text((82, 520), "+7 912 282-42-69", font=font(["segoeuisb.ttf", "segoeui.ttf"], 30), fill=(23, 33, 27))
og.save(os.path.join(IMG, "og-image.jpg"), quality=86, optimize=True, progressive=True)

json.dump(manifest, open(os.path.join(OUT, "..", "src", "images.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(os.path.join(OUT, "assets")) for f in fs)
print("images:", sum(len(v) for v in manifest.values()), "fonts:", len(faces), "assets KB:", round(tot / 1024))
