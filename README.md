# Сайт психолога Павла Макарцова

Статичный сайт для GitHub Pages. Без Tilda, без трекеров, без внешних CDN — всё лежит в репозитории.

- **Готовый сайт** — папка `docs/` (её и публикует GitHub Pages).
- **Исходники** — папка `src/`: тексты страниц, CSS, JS, данные о документах.
- **Сборка** — `python tools/build.py` (нужен только Python 3, без библиотек).
- **Проверка** — `python tools/check.py`: битые ссылки и картинки, заголовки, description.

## Публикация на GitHub Pages: https://pmakartsov.github.io/

Сайт открывается по корневому адресу, без подпапки, если репозиторий называется
**`pmakartsov.github.io`**: точно как имя пользователя, плюс `.github.io`.
`SITE_URL` в `tools/build.py` уже указывает на этот адрес.

1. Войдите на github.com под пользователем `pmakartsov`.
2. Нажмите **+** → **New repository**:
   - Repository name: `pmakartsov.github.io`
   - Public (для бесплатного GitHub Pages)
   - галочки README / .gitignore / license **не ставить** → **Create repository**.
3. В PowerShell в папке `E:\Downloads\site_new`:
   ```
   git init
   git config user.name "Pavel Makartsov"
   git config user.email "mpavel1969@gmail.com"
   git add .
   git commit -m "Сайт психолога"
   git branch -M main
   git remote add origin https://github.com/pmakartsov/pmakartsov.github.io.git
   git push -u origin main
   ```
   При первом `push` откроется окно входа в GitHub, войдите в браузере.
4. На GitHub в репозитории: **Settings → Pages → Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: **main**, папка **/docs** → **Save**.
5. Через 1–3 минуты сайт откроется на https://pmakartsov.github.io/.
   Ход публикации виден во вкладке **Actions**.

### Обновление сайта после правок
```
python tools/build.py
git add .
git commit -m "Что изменил"
git push
```

### Поисковики (по желанию, после публикации)
- Яндекс Вебмастер (webmaster.yandex.ru) и Google Search Console: добавьте сайт,
  подтвердите права (мета-тег или HTML-файл в `docs/`) и отправьте
  `https://pmakartsov.github.io/sitemap.xml`.

### Свой домен (например, `makartsov.ru`)
Settings → Pages → Custom domain. У регистратора домена добавьте записи, которые там
покажет GitHub. Затем впишите новый адрес в `SITE_URL` и пересоберите сайт.

## Как поменять текст, цены, документы

| Что | Где |
|---|---|
| Тексты страниц | `src/pages/*.html` (сверху — заголовок и описание для поиска) |
| Шапка, подвал, блок «Записаться» | `src/partials/` |
| Телефон, почта, Telegram, ВК | `PERSON` в начале `tools/build.py` |
| Цены | `src/pages/services.html`, `src/data/offers.json` (для поисковиков), форма в `src/pages/contacts.html` |
| Подписи к дипломам и сертификатам | `src/data/documents.json` |
| Новый диплом или сертификат (PDF/скан) | `python tools/add_document.py файл.pdf cert-08`, затем запись в `src/data/documents.json` |
| Договор-оферта, согласие на работу с несовершеннолетним | `src/files/*.docx` и `*.pdf` (после правки .docx пересохраните PDF из Word) |
| Главное фото, favicon (Ψ), картинка для соцсетей | `python tools/make_hero_and_icons.py фото.png` (исходник `1.png` — в истории git, коммит `fad0377`) |
| Адрес кабинета | `PERSON` в `tools/build.py` |
| Цвета и шрифты | `src/css/10-base.css` (переменные в `:root`) |

После любых правок: `python tools/build.py`, затем commit + push.

Новая статья: скопируйте `src/pages/articles/self-care.html`, поменяйте `out:`, заголовки
и текст, добавьте карточку в `src/partials/posts.html`.

Новые картинки: положите их в `docs/assets/img/` в формате WebP и добавьте в
`src/images.json` (имя, ширина, высота) — или перепишите и запустите `tools/prepare_assets.py`.

## Что внутри

- 8 страниц + политика конфиденциальности + 404; старые адреса Tilda
  (`about_me.html`, `price.html`, `diploma.html`, …) перенаправляют на новые.
- Адаптивная вёрстка от 320 px, мобильное меню, кнопка «Записаться» внизу экрана на телефоне.
- Документы: галерея с просмотром в полном размере (стрелки, свайпы, Esc).
- Форма записи без сервера: собирает заявку и открывает Telegram или почту с готовым текстом.
- Картинки в WebP нескольких размеров (`srcset`), ленивая загрузка; шрифты Lora и Manrope локально.
  Вес сайта ~5 МБ вместо ~23 МБ, страница — 10–40 КБ HTML.
- SEO: уникальные title и description, Open Graph, микроразметка schema.org
  (Person, ProfessionalService, услуги с ценами, FAQ, статьи, хлебные крошки).
- Доступность: семантическая разметка, навигация с клавиатуры, видимый фокус,
  контраст AA, `prefers-reduced-motion`, работа без JavaScript.
- Lighthouse: Accessibility 100, Best Practices 100, SEO 100 на всех страницах.
