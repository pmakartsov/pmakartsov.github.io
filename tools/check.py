"""Проверка собранного сайта: битые ссылки/картинки, незаменённые {{шорткоды}}, заголовки, alt, вес.

Запуск:  python tools/check.py
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

sys.stdout.reconfigure(encoding="utf-8")
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.h1, self.imgs_no_alt, self.heads = [], set(), 0, 0, []
        self.title = self.desc = None
        self._in_title = False
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if k in a and a[k]:
                self.refs.append((tag, a[k]))
        if "srcset" in a:
            for part in a["srcset"].split(","):
                self.refs.append((tag, part.strip().split(" ")[0]))
        if tag == "img" and "alt" not in a:
            self.imgs_no_alt += 1
        if tag in ("h1", "h2", "h3", "h4"):
            self.heads.append(int(tag[1]))
            if tag == "h1":
                self.h1 += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data


def main():
    pages = {}
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(dp, f), OUT).replace(os.sep, "/")
                src = open(os.path.join(dp, f), encoding="utf-8").read()
                p = Page()
                p.feed(src)
                p.raw = src
                pages[rel] = p

    problems = 0
    for rel, p in sorted(pages.items()):
        issues = []
        if "{{" in p.raw:
            issues.append("незаменённые {{…}}: " + ", ".join(sorted(set(re.findall(r"\{\{[^}]{0,40}\}\}", p.raw)))[:5]))
        redirect = 'http-equiv="refresh"' in p.raw
        if not redirect:
            if p.h1 != 1:
                issues.append(f"h1: {p.h1}")
            if p.lang != "ru":
                issues.append("нет lang=ru")
            if not p.desc:
                issues.append("нет description")
            elif not 70 <= len(p.desc) <= 200:
                issues.append(f"description {len(p.desc)} симв.")
            if p.title and len(p.title) > 75:
                issues.append(f"title {len(p.title)} симв.")
            for a, b in zip(p.heads, p.heads[1:]):
                if b > a + 1:
                    issues.append(f"пропуск уровня заголовка h{a}→h{b}")
                    break
            if p.imgs_no_alt:
                issues.append(f"img без alt: {p.imgs_no_alt}")
        base = os.path.dirname(rel)
        for tag, ref in p.refs:
            if ref.startswith(("http:", "https:", "mailto:", "tel:", "data:", "javascript:")) or ref.startswith("//"):
                continue
            u = urlsplit(ref)
            path = unquote(u.path)
            if rel == "404.html" and not path.startswith("/"):
                target = path
            else:
                target = os.path.normpath(os.path.join(base, path)).replace(os.sep, "/") if path else rel
            if path.endswith("/") or target in (".", ""):
                target = (target.rstrip("/") + "/index.html").lstrip("./")
            if not os.path.exists(os.path.join(OUT, target)):
                issues.append(f"нет файла: {ref}")
                continue
            if u.fragment and target.endswith(".html") and target in pages:
                if u.fragment not in pages[target].ids:
                    issues.append(f"нет якоря: {ref}")
        size = os.path.getsize(os.path.join(OUT, rel))
        print(f"{'OK ' if not issues else '!! '} {rel:40} {size // 1024:4} КБ  {(p.title or '').strip()[:60]}")
        for i in sorted(set(issues)):
            print("      -", i)
        problems += len(set(issues))

    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
    print(f"\nСтраниц: {len(pages)}, проблем: {problems}, общий вес docs/: {total / 1024 / 1024:.1f} МБ")
    return problems


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
