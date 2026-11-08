# Сайт психолога Павла Макарцова

Статичный сайт для GitHub Pages. Без Tilda, без трекеров, без внешних CDN — всё лежит в репозитории.

- **Готовый сайт** — папка `docs/` (её и публикует GitHub Pages).
- **Исходники** — папка `src/`: тексты страниц, CSS, JS, данные о документах.
- **Сборка** — `python tools/build.py` (нужен только Python 3, без библиотек).
- **Проверка** — `python tools/check.py`: битые ссылки и картинки, заголовки, description.

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
