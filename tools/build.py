"""Сборка сайта: src/ → docs/

Запуск:  python tools/build.py
Результат — готовый статичный сайт в папке docs/ (её публикует GitHub Pages).
"""
import hashlib
import html
import json
import math
import os
import re
import shutil
import sys
from datetime import date

# ---------------------------------------------------------------------------
# Настройки
# ---------------------------------------------------------------------------
# Полный адрес сайта со слешем на конце, например:
#   "https://username.github.io/psychologist/"  или  "https://makartsov.ru/"
# Нужен для canonical, Open Graph, sitemap.xml. Пока пусто — эти теги не выводятся.
SITE_URL = "https://pmakartsov.github.io/"

SITE_NAME = "Психолог Павел Макарцов"
PERSON = {
    "name": "Павел Макарцов",
    "full_name": "Макарцов Павел Сергеевич",
    "city": "Екатеринбург",
    "street": "ул. Энгельса, д. 36",
    "address": "г. Екатеринбург, ул. Энгельса, д. 36",
    "map_url": "https://yandex.ru/maps/?text=" + "Екатеринбург, улица Энгельса, 36".replace(" ", "+"),
    "phone": "+79122824269",
    "phone_display": "+7 912 282-42-69",
    "email": "mpavel1969@gmail.com",
    "telegram": "PMakartsov",
    "vk": "https://vk.com/mpavel1969",
}
NAV = [
    ("home", "Главная", "index.html"),
    ("about", "Обо мне", "about.html"),
    ("services", "Услуги и цены", "services.html"),
    ("education", "Образование", "education.html"),
    ("articles", "Статьи", "articles.html"),
    ("legal", "Документы", "legal.html"),
    ("contacts", "Контакты", "contacts.html"),
]
# Старые адреса Tilda → новые страницы (чтобы старые ссылки не ломались)
REDIRECTS = {
    "about_me.html": "about.html",
    "price.html": "services.html",
    "diploma.html": "education.html",
    "emotional_burnout.html": "articles/emotional-burnout.html",
    "self-help.html": "articles/self-care.html",
}

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "docs")

sys.stdout.reconfigure(encoding="utf-8")
IMAGES = json.load(open(os.path.join(SRC, "images.json"), encoding="utf-8"))

# ---------------------------------------------------------------------------
# Иконки (stroke, 24×24, в стиле Lucide)
# ---------------------------------------------------------------------------
ICONS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "send": '<path d="M14.54 21.69a.5.5 0 0 0 .94-.02l6.5-19a.5.5 0 0 0-.64-.63l-19 6.5a.5.5 0 0 0-.02.93l7.93 3.18a2 2 0 0 1 1.11 1.11z"/><path d="m21.85 2.15-10.94 10.93"/>',
    "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "pin": '<path d="M20 10c0 5-5.54 10.19-7.4 11.8a1 1 0 0 1-1.2 0C9.54 20.19 4 15 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "video": '<path d="m16 13 5.22 3.48a.5.5 0 0 0 .78-.42V7.87a.5.5 0 0 0-.75-.43L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "sprout": '<path d="M7 20h10M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8zM14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "bulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5M9 18h6M10 22h4"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "arrow-right": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "arrow-up": '<path d="m5 12 7-7 7 7M12 19V5"/>',
    "zoom": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3M11 8v6M8 11h6"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.59 13.51 6.83 3.98M15.41 6.51l-6.82 3.98"/>',
    "copy": '<rect x="8" y="8" width="14" height="14" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    "cap": '<path d="M21.42 10.92a1 1 0 0 0-.02-1.84L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.83l8.57 3.91a2 2 0 0 0 1.66 0zM22 10v6M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.48 12.89 17 22l-5-3-5 3 1.52-9.11"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    "buoy": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="m4.93 4.93 4.24 4.24M14.83 9.17l4.24-4.24M14.83 14.83l4.24 4.24M9.17 14.83l-4.24 4.24"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><path d="m16.24 7.76-1.8 5.41a2 2 0 0 1-1.27 1.27L7.76 16.24l1.8-5.41a2 2 0 0 1 1.27-1.27z"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8M21 3v5h-5M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16M8 16H3v5"/>',
    "eye": '<path d="M2.06 12.35a1 1 0 0 1 0-.7 10.75 10.75 0 0 1 19.88 0 1 1 0 0 1 0 .7 10.75 10.75 0 0 1-19.88 0"/><circle cx="12" cy="12" r="3"/>',
    "mountain": '<path d="m8 3 4 8 5-5 5 15H2L8 3z"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "armchair": '<path d="M19 9V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v3M3 16a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-4 0v1.5a.5.5 0 0 1-.5.5h-9a.5.5 0 0 1-.5-.5V11a2 2 0 0 0-4 0zM5 18v2M19 18v2"/>',
    "layers": '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83zM22 17.65l-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65M22 12.65l-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "wave": '<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>',
    "battery": '<rect x="2" y="7" width="16" height="10" rx="2"/><path d="M22 11v2M6 11v2"/>',
    "hourglass": '<path d="M5 22h14M5 2h14M17 22v-4.17a2 2 0 0 0-.59-1.42L12 12l-4.41 4.41A2 2 0 0 0 7 17.83V22M7 2v4.17a2 2 0 0 0 .59 1.42L12 12l4.41-4.41A2 2 0 0 0 17 6.17V2"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
}


def icon(name, cls="icon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'{ICONS[name]}</svg>')


# Знак Ψ («пси») — логотип и favicon
PSI_PATH = "M10.6 9.4v5.2a9.4 9.4 0 0 0 18.8 0V9.4M20 6.9v25M15 31.9h10"


def logo_svg(bg="#4d6b2b", fg="#fff"):
    return ('<svg class="logo__mark" viewBox="0 0 40 40" aria-hidden="true" focusable="false">'
            f'<rect width="40" height="40" rx="9" fill="{bg}"/>'
            f'<path d="{PSI_PATH}" fill="none" stroke="{fg}" stroke-width="3.4" '
            'stroke-linecap="round" stroke-linejoin="round"/></svg>')


LOGO_SVG = logo_svg()

# ---------------------------------------------------------------------------
# Хелперы
# ---------------------------------------------------------------------------
esc = lambda s: html.escape(str(s), quote=True)


def plural(n, one, few, many):
    n = abs(n) % 100
    if 11 <= n <= 14:
        return many
    return {1: one, 2: few, 3: few, 4: few}.get(n % 10, many)


def img_folder(name):
    return "assets/img/docs/" if name.startswith(("diploma-", "cert-")) else "assets/img/"


def img_tag(ctx, name, alt="", sizes="100vw", cls="", eager=False, pick=800):
    variants = IMAGES[name]
    folder = ctx["root"] + img_folder(name)
    big = variants[-1]
    src = min(variants, key=lambda v: abs(v["w"] - pick))
    srcset = ", ".join(f'{folder}{v["file"]} {v["w"]}w' for v in variants)
    attrs = [f'src="{folder}{src["file"]}"', f'srcset="{srcset}"', f'sizes="{esc(sizes)}"',
             f'width="{big["w"]}"', f'height="{big["h"]}"', f'alt="{esc(alt)}"']
    if cls:
        attrs.append(f'class="{cls}"')
    attrs.append('fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"')
    return "<img " + " ".join(attrs) + ">"


def full_image_url(ctx, name):
    return ctx["root"] + img_folder(name) + IMAGES[name][-1]["file"]


def parse_attrs(s):
    out = {}
    for m in re.finditer(r'([\w-]+)(?:="([^"]*)")?', s):
        out[m.group(1)] = m.group(2) if m.group(2) is not None else True
    return out


def docs_gallery(ctx, group):
    data = json.load(open(os.path.join(SRC, "data", "documents.json"), encoding="utf-8"))[group]
    first = IMAGES[data[0]["image"]][-1]
    portrait = first["h"] > first["w"]
    items = []
    for d in data:
        name = d["image"]
        sizes = "(min-width: 1160px) 260px, (min-width: 640px) 33vw, 100vw"
        items.append(
            f'<li><a class="doc" href="{full_image_url(ctx, name)}" data-lightbox="{group}" '
            f'data-caption="{esc(d["caption"])}">'
            f'<span class="doc__img">{img_tag(ctx, name, d["alt"], sizes, pick=640)}'
            f'<span class="doc__zoom">{icon("zoom")}</span></span>'
            f'<span class="doc__caption">{esc(d["title"])}</span>'
            f'<span class="visually-hidden">— открыть в полном размере</span></a></li>')
    cls = "docs-grid docs-grid--portrait" if portrait else "docs-grid"
    return f'<ul class="{cls}" role="list">' + "".join(items) + "</ul>"


def breadcrumbs_html(ctx):
    items = [("Главная", "index.html")] + ctx["crumbs"]
    li = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            li.append(f'<li><a href="{ctx["root"]}{href}">{esc(label)}</a></li>')
        else:
            li.append(f'<li aria-current="page">{esc(label)}</li>')
    return '<nav class="breadcrumbs" aria-label="Хлебные крошки"><ol>' + "".join(li) + "</ol></nav>"


def parse_crumbs(s):
    out = []
    for part in [p.strip() for p in s.split(">") if p.strip()]:
        label, _, href = part.partition("|")
        out.append((label.strip(), href.strip() or None))
    return out


def text_of(fragment):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(re.sub(r"\s+", " ", t)).strip()


def abs_url(path):
    return (SITE_URL + path) if SITE_URL else path


# Время чтения каждой страницы (out → минуты). Заполняется до сборки, чтобы карточки статей
# ({{reading_time articles/…}}) и сами статьи ({{reading_time}}) показывали одно и то же число.
READING_TIME = {}


def reading_minutes(body):
    """Минуты чтения по тексту статьи: без оглавления, крошек, блока об авторе и шорткодов."""
    m = re.search(r"<article\b.*?</article>", body, flags=re.S)
    t = m.group(0) if m else body
    t = re.sub(r"\{\{.*?\}\}", " ", t)
    t = re.sub(r"<nav\b.*?</nav>", " ", t, flags=re.S)
    t = re.sub(r'<section class="author-box".*?</section>', " ", t, flags=re.S)
    return max(1, math.ceil(len(text_of(t).split()) / 180))


# ---------------------------------------------------------------------------
# Шорткоды
# ---------------------------------------------------------------------------
def render_shortcodes(text, ctx, depth=0):
    def repl(m):
        name, rest = m.group(1), (m.group(2) or "").strip()
        if name.isupper():  # плейсхолдеры layout-а подставляются отдельно
            return m.group(0)
        if name == ">":
            part = open(os.path.join(SRC, "partials", rest + ".html"), encoding="utf-8").read()
            return render_shortcodes(part, ctx, depth + 1) if depth < 5 else part
        if name == "root":
            return ctx["root"]
        if name == "icon":
            return icon(rest)
        if name == "logo":
            return logo_svg("#83aa4b") if rest == "light" else logo_svg()
        if name == "age":
            # возраст на момент сборки; на странице JS пересчитывает его по текущей дате
            today, born = date.today(), date(1969, 1, 18)
            years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            return (f'<span data-age="1969-01-18">{years}</span> '
                    f'<span data-age-word="1969-01-18">{plural(years, "год", "года", "лет")}</span>')
        if name == "img":
            a = parse_attrs(rest)
            return img_tag(ctx, a["name"], a.get("alt", ""), a.get("sizes", "100vw"), a.get("class", ""),
                           bool(a.get("eager")), int(a.get("pick", 800)))
        if name == "imgsrc":
            return full_image_url(ctx, rest)
        if name == "docs":
            return docs_gallery(ctx, rest)
        if name == "breadcrumbs":
            return breadcrumbs_html(ctx)
        if name == "reading_time":
            key = rest or ctx["out"]
            if key not in READING_TIME:
                raise KeyError(f"{{{{reading_time {key}}}}}: нет такой страницы (в {ctx['out']})")
            return str(READING_TIME[key])
        if name in ctx["meta"]:
            return esc(ctx["meta"][name])
        if name in PERSON:
            return esc(PERSON[name])
        raise KeyError(f"Неизвестный шорткод {{{{{name}}}}} в {ctx['out']}")

    return re.sub(r"\{\{\s*(>|[\w-]+)\s*([^}]*)\}\}", repl, text)


# ---------------------------------------------------------------------------
# JSON-LD
# ---------------------------------------------------------------------------
def schema_base():
    p = PERSON
    person = {
        "@type": "Person",
        "@id": abs_url("#person"),
        "name": p["name"],
        "givenName": "Павел",
        "additionalName": "Сергеевич",
        "familyName": "Макарцов",
        "jobTitle": "Психолог",
        "image": abs_url("assets/img/pavel-hero-800.jpg"),
        "telephone": p["phone"],
        "email": "mailto:" + p["email"],
        "url": abs_url(""),
        "sameAs": [p["vk"], "https://t.me/" + p["telegram"]],
        "alumniOf": [
            {"@type": "CollegeOrUniversity", "name": "Московский педагогический государственный университет имени В.И. Ленина"},
            {"@type": "CollegeOrUniversity", "name": "Уральский федеральный университет имени первого Президента России Б.Н. Ельцина"},
        ],
        "knowsAbout": ["Когнитивно-поведенческая терапия", "Нейрокогнитивная диагностика", "Тревожность",
                       "Эмоциональное выгорание", "Самооценка", "Детско-родительские отношения", "Подростковая психология"],
        "knowsLanguage": "ru",
    }
    service = {
        "@type": "ProfessionalService",
        "@id": abs_url("#practice"),
        "name": SITE_NAME,
        "url": abs_url(""),
        "image": abs_url("assets/img/og-image.jpg"),
        "telephone": p["phone"],
        "email": p["email"],
        "priceRange": "3000–28000 ₽",
        "currenciesAccepted": "RUB",
        "address": {"@type": "PostalAddress", "streetAddress": "ул. Энгельса, 36", "addressLocality": p["city"],
                    "addressRegion": "Свердловская область", "addressCountry": "RU"},
        "hasMap": p["map_url"],
        "termsOfService": abs_url("legal.html"),
        "areaServed": [{"@type": "City", "name": p["city"]}, {"@type": "Country", "name": "Россия"}],
        "founder": {"@id": abs_url("#person")},
        "employee": {"@id": abs_url("#person")},
    }
    website = {"@type": "WebSite", "@id": abs_url("#website"), "url": abs_url(""), "name": SITE_NAME,
               "inLanguage": "ru-RU", "publisher": {"@id": abs_url("#person")}}
    return [person, service, website]


def schema_for(ctx, content):
    meta, graph = ctx["meta"], []
    kinds = [k.strip() for k in meta.get("schema", "").split(",") if k.strip()]
    if "base" in kinds:
        graph += schema_base()
    page_url = abs_url(ctx["url_path"])
    if ctx["crumbs"]:
        items = [("Главная", "")] + [(l, h or ctx["url_path"]) for l, h in ctx["crumbs"]]
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": l,
             "item": abs_url("" if h in ("", "index.html") else h)} for i, (l, h) in enumerate(items)]})
    if "article" in kinds:
        graph.append({
            "@type": "Article", "headline": meta["h1"], "description": meta["description"],
            "image": abs_url(img_folder(meta["cover"]) + IMAGES[meta["cover"]][-1]["file"]),
            "datePublished": meta["published"], "dateModified": meta.get("modified", meta["published"]),
            "inLanguage": "ru-RU", "mainEntityOfPage": page_url,
            "author": {"@type": "Person", "@id": abs_url("#person"), "name": PERSON["name"], "url": abs_url("about.html")},
            "publisher": {"@type": "Person", "@id": abs_url("#person"), "name": PERSON["name"]},
            "wordCount": len(text_of(content).split()),
        })
    if "faq" in kinds:
        qa = re.findall(r"<summary>(.*?)</summary>\s*<div class=\"faq__answer\">(.*?)</div>\s*</details>", content, flags=re.S)
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": text_of(q), "acceptedAnswer": {"@type": "Answer", "text": text_of(a)}} for q, a in qa]})
    if "offers" in kinds:
        offers = json.load(open(os.path.join(SRC, "data", "offers.json"), encoding="utf-8"))
        graph.append({"@type": "OfferCatalog", "name": "Услуги психолога", "itemListElement": [
            {"@type": "Offer", "price": o["price"], "priceCurrency": "RUB",
             "itemOffered": {"@type": "Service", "name": o["name"], "description": o["description"],
                             "provider": {"@id": abs_url("#person")}}} for o in offers]})
    if not graph:
        return ""
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"


# ---------------------------------------------------------------------------
# Сборка страниц
# ---------------------------------------------------------------------------
def parse_page(path):
    raw = open(path, encoding="utf-8").read()
    head, sep, body = raw.partition("\n---\n")
    if not sep:
        raise ValueError(f"{path}: нет разделителя '---' после метаданных")
    meta = {}
    for line in head.splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, body


def nav_html(ctx):
    items = []
    for key, label, href in NAV:
        attr = ""
        if key == ctx["meta"].get("nav"):
            attr = ' aria-current="page"' if ctx["out"] == href else ' class="is-active"'
        items.append(f'<li><a href="{ctx["root"]}{href}"{attr}>{label}</a></li>')
    return "".join(items)


def asset_version(rel):
    return hashlib.md5(open(os.path.join(OUT, rel), "rb").read()).hexdigest()[:8]


def build_page(path, layout, versions):
    meta, body = parse_page(path)
    out = meta["out"]
    depth = out.count("/")
    ctx = {
        "meta": meta, "out": out,
        "root": "../" * depth,
        "url_path": "" if out == "index.html" else out,
        "crumbs": parse_crumbs(meta.get("crumbs", "")),
    }
    if out == "404.html":
        ctx["root"] = "{{BASE}}"
    content = render_shortcodes(body, ctx)

    og_image = meta.get("og_image") or "assets/img/og-image.jpg"
    if meta.get("cover") and not meta.get("og_image"):
        og_image = img_folder(meta["cover"]) + IMAGES[meta["cover"]][-2 if len(IMAGES[meta["cover"]]) > 1 else -1]["file"]
    head_extra = []
    if SITE_URL and out != "404.html":
        head_extra.append(f'<link rel="canonical" href="{abs_url(ctx["url_path"])}">')
        head_extra.append(f'<meta property="og:url" content="{abs_url(ctx["url_path"])}">')
    if meta.get("noindex"):
        head_extra.append('<meta name="robots" content="noindex, follow">')
    if meta.get("og_type") == "article":
        head_extra.append(f'<meta property="article:published_time" content="{meta["published"]}">')
        head_extra.append(f'<meta property="article:author" content="{PERSON["name"]}">')

    # 1) партиалы layout-а  2) простые плейсхолдеры  3) шорткоды  4) контент
    page = re.sub(r"\{\{>\s*([\w-]+)\s*\}\}",
                  lambda m: open(os.path.join(SRC, "partials", m.group(1) + ".html"), encoding="utf-8").read().rstrip(),
                  layout)
    simple = {
        "TITLE": esc(meta["title"]),
        "DESCRIPTION": esc(meta["description"]),
        "OG_TITLE": esc(meta.get("og_title", meta["title"])),
        "OG_TYPE": meta.get("og_type", "website"),
        "OG_IMAGE": abs_url(og_image) if SITE_URL else ctx["root"] + og_image,
        "HEAD_EXTRA": "\n  ".join(head_extra),
        "NAV": nav_html(ctx),
        "BODY_CLASS": (esc(meta.get("body_class", "")) + ("" if meta.get("mobile_cta") == "no" else " has-mobile-cta")).strip(),
        "CSS_V": versions["css"], "JS_V": versions["js"],
    }
    for k, v in simple.items():
        page = page.replace("{{" + k + "}}", v)
    page = render_shortcodes(page, ctx)
    late = {
        "MOBILE_CTA": "" if meta.get("mobile_cta") == "no" else render_shortcodes("{{> mobile-cta}}", ctx),
        "SCHEMA": schema_for(ctx, content),
        "CONTENT": content,
    }
    for k, v in late.items():
        page = page.replace("{{" + k + "}}", v)

    if out == "404.html":
        if SITE_URL:
            base = re.sub(r"^https?://[^/]+", "", SITE_URL)
            page = page.replace("<head>", f'<head>\n  <base href="{base}">', 1)
        else:
            page = page.replace("<head>", "<head>\n  <script>(function(){var p=location.pathname.split('/'),b='/';"
                                "if(/\\.github\\.io$/.test(location.hostname)&&p.length>2&&p[1])b='/'+p[1]+'/';"
                                "document.write('<base href=\"'+b+'\">');})();</script>", 1)
        page = page.replace("{{BASE}}", "")

    page = re.sub(r"\n\s*\n+", "\n", page)
    dst = os.path.join(OUT, out.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(page)
    return out, meta


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    css = css.replace(";}", "}")
    return css.strip() + "\n"


def build_assets():
    css_dir = os.path.join(SRC, "css")
    css = "".join(open(os.path.join(css_dir, f), encoding="utf-8").read() + "\n"
                  for f in sorted(os.listdir(css_dir)) if f.endswith(".css"))
    os.makedirs(os.path.join(OUT, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets", "js"), exist_ok=True)
    open(os.path.join(OUT, "assets", "css", "style.css"), "w", encoding="utf-8", newline="\n").write(minify_css(css))
    for f in os.listdir(os.path.join(SRC, "js")):
        shutil.copy2(os.path.join(SRC, "js", f), os.path.join(OUT, "assets", "js", f))
    files_out = os.path.join(OUT, "assets", "files")
    os.makedirs(files_out, exist_ok=True)
    for f in os.listdir(os.path.join(SRC, "files")):
        shutil.copy2(os.path.join(SRC, "files", f), os.path.join(files_out, f))
    return {"css": asset_version("assets/css/style.css"), "js": asset_version("assets/js/main.js")}


def write(rel, text):
    open(os.path.join(OUT, rel), "w", encoding="utf-8", newline="\n").write(text)


def build_static(pages):
    write(".nojekyll", "")
    open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8").write(
        LOGO_SVG.replace(' class="logo__mark"', ' xmlns="http://www.w3.org/2000/svg"')
        .replace(' aria-hidden="true" focusable="false"', ""))
    write("site.webmanifest", json.dumps({
        "name": SITE_NAME, "short_name": "Макарцов", "lang": "ru", "start_url": "./", "display": "browser",
        "background_color": "#f8f6f1", "theme_color": "#4d6b2b",
        "icons": [{"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }, ensure_ascii=False, indent=2))
    robots = "User-agent: *\nAllow: /\n"
    if SITE_URL:
        robots += f"\nSitemap: {SITE_URL}sitemap.xml\n"
        today = date.today().isoformat()
        urls = []
        for out, meta in pages:
            if out == "404.html" or meta.get("noindex"):
                continue
            loc = abs_url("" if out == "index.html" else out)
            urls.append(f"  <url><loc>{loc}</loc><lastmod>{meta.get('modified', today)}</lastmod></url>")
        write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")
    elif os.path.exists(os.path.join(OUT, "sitemap.xml")):
        os.remove(os.path.join(OUT, "sitemap.xml"))
    write("robots.txt", robots)
    for old, new in REDIRECTS.items():
        write(old, f'<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">'
                   f'<title>Страница переехала</title><meta name="robots" content="noindex">'
                   f'<link rel="canonical" href="{abs_url(new) if SITE_URL else new}">'
                   f'<meta http-equiv="refresh" content="0; url={new}"></head>'
                   f'<body><p>Страница переехала: <a href="{new}">{new}</a></p></body></html>\n')


def main():
    versions = build_assets()
    layout = open(os.path.join(SRC, "layout.html"), encoding="utf-8").read()
    pages_dir = os.path.join(SRC, "pages")
    paths = [os.path.join(dp, f) for dp, _, files in os.walk(pages_dir) for f in sorted(files) if f.endswith(".html")]
    for p in paths:
        meta, body = parse_page(p)
        READING_TIME[meta["out"]] = reading_minutes(body)
    built = [build_page(p, layout, versions) for p in paths]
    build_static(built)
    print(f"Готово: {len(built)} страниц → {OUT}")
    for out, meta in sorted(built):
        print(f"  {out:38} {meta['title']}")
    if not SITE_URL:
        print("\n[!] SITE_URL не задан: canonical, og:url и sitemap.xml не созданы (см. начало tools/build.py).")


if __name__ == "__main__":
    main()
