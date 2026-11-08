/* Сайт психолога Павла Макарцова — интерактив без зависимостей */
(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }

  /* ---------- Toast ---------- */
  var toastEl, toastTimer;
  function toast(message) {
    if (!toastEl) {
      toastEl = doc.createElement("div");
      toastEl.className = "toast";
      toastEl.setAttribute("role", "status");
      toastEl.setAttribute("aria-live", "polite");
      doc.body.appendChild(toastEl);
    }
    toastEl.textContent = message;
    toastEl.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-visible"); }, 2600);
  }

  /* ---------- Mobile navigation ---------- */
  function initNav() {
    var toggle = $(".nav-toggle");
    var nav = $("#site-nav");
    if (!toggle || !nav) return;
    var mq = window.matchMedia("(max-width: 1199px)");

    function setOpen(open) {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Закрыть меню" : "Открыть меню");
      nav.classList.toggle("is-open", open);
      root.classList.toggle("nav-open", open);
      if (mq.matches) {
        if (open) nav.removeAttribute("inert"); else nav.setAttribute("inert", "");
      }
      if (open) {
        var first = $("a", nav);
        if (first) first.focus();
      }
    }
    function sync() {
      if (mq.matches) {
        if (!nav.classList.contains("is-open")) nav.setAttribute("inert", "");
      } else {
        nav.removeAttribute("inert");
        if (nav.classList.contains("is-open")) setOpen(false);
      }
    }

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    if (mq.addEventListener) mq.addEventListener("change", sync); else mq.addListener(sync);
    sync();
  }

  /* ---------- Copy phone / email ---------- */
  function initCopy() {
    $$("[data-copy]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var text = btn.getAttribute("data-copy");
        var done = function () { toast("Скопировано: " + text); };
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text); done(); });
        } else {
          fallbackCopy(text);
          done();
        }
      });
    });
  }
  function fallbackCopy(text) {
    var ta = doc.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    doc.body.appendChild(ta);
    ta.select();
    try { doc.execCommand("copy"); } catch (e) { /* ignore */ }
    doc.body.removeChild(ta);
  }

  /* ---------- Reveal on scroll ---------- */
  function initReveal() {
    var items = $$(".reveal");
    if (!items.length) return;
    if (reduceMotion || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Sticky mobile CTA + back-to-top ---------- */
  function initFloating() {
    var cta = $(".mobile-cta");
    var top = $(".to-top");
    var hero = $(".hero, .page-hero, .article-hero, .about-hero");
    if (!cta && !top) return;
    var threshold = hero ? hero.offsetTop + hero.offsetHeight : 480;
    var ticking = false;
    function update() {
      var y = window.pageYOffset || root.scrollTop;
      var nearBottom = window.innerHeight + y > doc.body.scrollHeight - 420;
      if (cta) cta.classList.toggle("is-visible", y > threshold && !nearBottom);
      if (top) top.classList.toggle("is-visible", y > 900);
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener("resize", function () {
      threshold = hero ? hero.offsetTop + hero.offsetHeight : 480;
    });
    if (top) {
      top.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
        var skip = $(".skip-link");
        if (skip) skip.focus({ preventScroll: true });
      });
    }
    update();
  }

  /* ---------- Table of contents: highlight current section ---------- */
  function initToc() {
    var links = $$(".toc a[href^='#']");
    if (!links.length || !("IntersectionObserver" in window)) return;
    var map = {};
    var targets = links.map(function (a) {
      var el = doc.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)));
      if (el) map[el.id] = a;
      return el;
    }).filter(Boolean);
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          links.forEach(function (a) { a.classList.remove("is-active"); a.removeAttribute("aria-current"); });
          var a = map[entry.target.id];
          if (a) { a.classList.add("is-active"); a.setAttribute("aria-current", "true"); }
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    targets.forEach(function (t) { io.observe(t); });
  }

  /* ---------- Lightbox for documents ---------- */
  function initLightbox() {
    var triggers = $$("[data-lightbox]");
    if (!triggers.length) return;

    var dialog = doc.createElement("dialog");
    dialog.className = "lightbox";
    dialog.setAttribute("aria-label", "Просмотр документа");
    dialog.innerHTML =
      '<div class="lightbox__bar">' +
        '<span class="lightbox__counter" aria-live="polite"></span>' +
        '<div class="lightbox__tools">' +
          '<a class="lightbox__btn lightbox__open" href="#" target="_blank" rel="noopener" aria-label="Открыть в полном размере в новой вкладке">' + icon("external") + '</a>' +
          '<button class="lightbox__btn lightbox__close" type="button" aria-label="Закрыть">' + icon("close") + '</button>' +
        '</div>' +
      '</div>' +
      '<div class="lightbox__stage">' +
        '<button class="lightbox__btn lightbox__prev" type="button" aria-label="Предыдущий документ">' + icon("prev") + '</button>' +
        '<img alt="" decoding="async">' +
        '<button class="lightbox__btn lightbox__next" type="button" aria-label="Следующий документ">' + icon("next") + '</button>' +
      '</div>' +
      '<p class="lightbox__caption"></p>';
    doc.body.appendChild(dialog);

    var img = $("img", dialog);
    var stage = $(".lightbox__stage", dialog);
    var caption = $(".lightbox__caption", dialog);
    var counter = $(".lightbox__counter", dialog);
    var openLink = $(".lightbox__open", dialog);
    var group = [];
    var index = 0;
    var opener = null;

    function show(i) {
      index = (i + group.length) % group.length;
      var t = group[index];
      var thumb = $("img", t);
      var src = t.getAttribute("href");
      if (img.getAttribute("src") !== src) {
        stage.classList.add("is-loading");
        img.src = src;
      }
      img.alt = thumb ? thumb.alt : "";
      caption.textContent = t.getAttribute("data-caption") || (thumb ? thumb.alt : "");
      counter.textContent = (index + 1) + " из " + group.length;
      openLink.href = t.getAttribute("href");
      var single = group.length < 2;
      $(".lightbox__prev", dialog).hidden = single;
      $(".lightbox__next", dialog).hidden = single;
      // предзагрузка соседних
      [index + 1, index - 1].forEach(function (n) {
        var g = group[(n + group.length) % group.length];
        if (g) { var p = new Image(); p.src = g.getAttribute("href"); }
      });
    }
    function open(trigger) {
      var name = trigger.getAttribute("data-lightbox");
      group = triggers.filter(function (t) { return t.getAttribute("data-lightbox") === name; });
      opener = trigger;
      show(group.indexOf(trigger));
      if (typeof dialog.showModal === "function") dialog.showModal(); else dialog.setAttribute("open", "");
      root.style.overflow = "hidden";
      $(".lightbox__close", dialog).focus();
    }
    function close() {
      if (typeof dialog.close === "function") dialog.close(); else dialog.removeAttribute("open");
    }
    function loaded() { stage.classList.remove("is-loading"); }
    img.addEventListener("load", loaded);
    img.addEventListener("error", loaded);
    dialog.addEventListener("close", function () {
      root.style.overflow = "";
      img.removeAttribute("src");
      stage.classList.remove("is-loading");
      if (opener) opener.focus();
    });

    triggers.forEach(function (t) {
      t.addEventListener("click", function (e) {
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1) return;
        e.preventDefault();
        open(t);
      });
    });
    $(".lightbox__close", dialog).addEventListener("click", close);
    $(".lightbox__prev", dialog).addEventListener("click", function () { show(index - 1); });
    $(".lightbox__next", dialog).addEventListener("click", function () { show(index + 1); });
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog || e.target.classList.contains("lightbox__stage")) close();
    });
    dialog.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); show(index + 1); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); show(index - 1); }
      else if (e.key === "Home") { e.preventDefault(); show(0); }
      else if (e.key === "End") { e.preventDefault(); show(group.length - 1); }
    });

    // свайпы
    var x0 = null, y0 = null;
    stage.addEventListener("touchstart", function (e) {
      x0 = e.touches[0].clientX; y0 = e.touches[0].clientY;
    }, { passive: true });
    stage.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      var dy = e.changedTouches[0].clientY - y0;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) show(index + (dx < 0 ? 1 : -1));
      else if (dy > 90 && Math.abs(dy) > Math.abs(dx) * 1.5) close();
      x0 = y0 = null;
    }, { passive: true });
  }

  function icon(name) {
    var paths = {
      close: '<path d="M6 6l12 12M18 6 6 18"/>',
      prev: '<path d="m15 18-6-6 6-6"/>',
      next: '<path d="m9 18 6-6-6-6"/>',
      external: '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>'
    };
    return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + paths[name] + "</svg>";
  }

  /* ---------- Booking form: собирает заявку и открывает мессенджер / почту ---------- */
  function initBooking() {
    var form = $("#booking-form");
    if (!form) return;
    var status = $(".form__status", form);
    var cfg = {
      telegram: form.getAttribute("data-telegram"),
      email: form.getAttribute("data-email")
    };

    // предвыбор услуги из ссылки вида contacts.html?service=...#booking
    var params = new URLSearchParams(window.location.search);
    var preset = params.get("service");
    var select = form.elements.service;
    if (preset && select) {
      $$("option", select).forEach(function (o) { if (o.value === preset) select.value = preset; });
    }

    function setError(field, msg) {
      var input = form.elements[field];
      var err = $("#" + field + "-error", form);
      if (input && input.setAttribute) input.setAttribute("aria-invalid", msg ? "true" : "false");
      if (err) err.textContent = msg || "";
    }

    function validate() {
      var ok = true;
      var name = form.elements.name.value.trim();
      var contact = form.elements.contact.value.trim();
      setError("name", "");
      setError("contact", "");
      setError("consent", "");
      if (name.length < 2) { setError("name", "Пожалуйста, укажите, как к вам обращаться"); ok = false; }
      if (contact.length < 5) { setError("contact", "Укажите телефон, e-mail или ник в Telegram"); ok = false; }
      if (!form.elements.consent.checked) { setError("consent", "Нужно согласие на обработку данных"); ok = false; }
      return ok;
    }

    function compose() {
      var f = form.elements;
      var fmt = $$("input[name='format']", form).filter(function (r) { return r.checked; })[0];
      var lines = [
        "Здравствуйте, Павел! Хочу записаться на консультацию.",
        "",
        "Имя: " + f.name.value.trim(),
        "Как связаться: " + f.contact.value.trim(),
        "Услуга: " + (f.service.options[f.service.selectedIndex] || {}).text,
        "Формат: " + (fmt ? fmt.value : "не важно")
      ];
      if (f.time && f.time.value.trim()) lines.push("Удобное время: " + f.time.value.trim());
      if (f.message && f.message.value.trim()) lines.push("", "Коротко о запросе: " + f.message.value.trim());
      return lines.join("\n");
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) {
        var bad = $("[aria-invalid='true']", form);
        if (bad) bad.focus();
        return;
      }
      var text = compose();
      var via = e.submitter && e.submitter.value ? e.submitter.value : "telegram";
      if (via === "email") {
        window.location.href = "mailto:" + cfg.email +
          "?subject=" + encodeURIComponent("Запись на консультацию") +
          "&body=" + encodeURIComponent(text);
        status.textContent = "Открываем почтовую программу… Если она не открылась — напишите на " + cfg.email + ".";
      } else {
        var copied = false;
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(text).then(function () { copied = true; }, function () {});
        }
        window.open("https://t.me/" + cfg.telegram + "?text=" + encodeURIComponent(text), "_blank", "noopener");
        status.textContent = "Открываем Telegram. Текст заявки уже подставлен" +
          (copied ? " и скопирован" : "") + " — останется нажать «Отправить».";
      }
    });

    ["name", "contact"].forEach(function (n) {
      form.elements[n].addEventListener("input", function () {
        if (form.elements[n].getAttribute("aria-invalid") === "true") setError(n, "");
      });
    });
    form.elements.consent.addEventListener("change", function () { setError("consent", ""); });
  }

  /* ---------- Share ---------- */
  function initShare() {
    $$("[data-share]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var data = { title: doc.title, url: window.location.href };
        if (navigator.share) {
          navigator.share(data).catch(function () {});
        } else {
          fallbackCopy(data.url);
          toast("Ссылка скопирована");
        }
      });
    });
  }

  /* ---------- Current year ---------- */
  function initYear() {
    $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
  }

  /* ---------- Возраст по дате рождения (data-age="ГГГГ-ММ-ДД") ---------- */
  function yearsSince(iso) {
    var p = iso.split("-").map(Number);
    var now = new Date();
    var years = now.getFullYear() - p[0];
    if (now.getMonth() + 1 < p[1] || (now.getMonth() + 1 === p[1] && now.getDate() < p[2])) years--;
    return years;
  }
  function yearsWord(n) {
    var a = n % 100, b = n % 10;
    if (a >= 11 && a <= 14) return "лет";
    if (b === 1) return "год";
    if (b >= 2 && b <= 4) return "года";
    return "лет";
  }
  function initAge() {
    $$("[data-age]").forEach(function (el) { el.textContent = yearsSince(el.getAttribute("data-age")); });
    $$("[data-age-word]").forEach(function (el) { el.textContent = yearsWord(yearsSince(el.getAttribute("data-age-word"))); });
  }

  function init() {
    initNav();
    initCopy();
    initReveal();
    initFloating();
    initToc();
    initLightbox();
    initBooking();
    initShare();
    initYear();
    initAge();
  }

  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init); else init();
})();
