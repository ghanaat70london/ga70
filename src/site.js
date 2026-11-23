/* Ghana at 70 UK site script. Edit SITE_CONFIG to change contact details. */
/* SVG2 pathLength set here so the HTML validates */
try {
  document.querySelectorAll("[data-pl]").forEach(function (e) {
    e.setAttribute("pathLength", e.getAttribute("data-pl"));
  });
} catch {}
var SITE_CONFIG = {
  contactEmail: "ghanaat70.uk@gmail.com",
  contactPhone: "07824 555307",
  endpoint: "/api/register",
  anniversary: "2027-03-06T00:00:00Z",
  /* Optional direct checkout links, one per day, used only if Ticket Tailor below is not set.
     Every "Book now" button for that day then goes straight to that link. Leave empty otherwise. */
  pay: { gala: "", ghanaday: "", sunday: "", weekend: "" },
  /* TICKET TAILOR. Paste values ONLY from your own Ticket Tailor account, never typed from memory.
     Where to find them: Ticket Tailor > your event > Share event > Website embed code > the pop-out (button) code.
     That code has one script tag and a link calling TTWidget.loadEvent(boxOffice, eventId, "widget").
       widgetScript: the src of that script tag, copied exactly.
       boxOffice:    the first value inside loadEvent, copied exactly.
       events:       the numeric event ID (second value) from each event's own code. The Weekend Pass is its own
                     Ticket Tailor event, so it has its own ID and link.
       customDomain: leave empty unless you buy the Ticket Tailor custom domain add on (then the fourth value).
       links:        each event's public Ticket Tailor page, and your box office page. These are the fallback
                     whenever a browser blocks the pop-out, so every buyer can always book.
     While boxOffice, widgetScript or an event ID is empty, that day keeps the current booking flow. */
  ticketTailor: {
    widgetScript: "https://cdn.tickettailor.com/js/widgets/min/widget.js",
    boxOffice: "interopa",
    customDomain: "",
    events: { gala: "2542641", ghanaday: "2542611", sunday: "2542630", weekend: "" },
    links: {
      gala: "https://buytickets.at/interopa/2542641",
      ghanaday: "https://buytickets.at/interopa/2542611",
      sunday: "https://buytickets.at/interopa/2542630",
      weekend: "",
      boxoffice: "https://buytickets.at/interopa",
    },
  },
  /* Tickets are on sale from 18 November 2026. Bookings are taken now: by bank transfer, or a secure payment link follows by email until the card links above are pasted in. */
  salesOpen: "2026-11-18T00:00:00Z",
  /* PRICES, the one place they are set. build.py reads this block for every page, the structured data and llms.txt,
     and the booking panel below uses it, so change a price here and nowhere else. Whole pounds, VAT and fees included.
       gala: Royal Jubilee Gala per guest. firstRelease: Gala first release per guest. table: Gala table of ten (9 x gala).
       quizTeam: Ghana Day quiz team booking, 6 tickets. familyTable: Sunday family table booking, 5 tickets. */
  prices: { gala: 200, firstRelease: 150, table: 1800, ghanaday: 50, quizTeam: 300, sunday: 150, familyTable: 750, weekend: 330 },
  /* FIRST RELEASE, the one switch. GBP 150 on the first 25 Gala tickets, up to 2 per order.
     When the 25 are sold set on: false, commit, and every first release mention leaves every page at once.
     The site never shows how many first release tickets exist. */
  firstRelease: { on: true, perOrder: 2 },
  /* Places left, copied from GoHighLevel when you want to show them. Leave null to hide.
     Example: left: { gala: 42, sunday: 60 } shows "Only 42 places left". */
  left: { gala: null, ghanaday: null, sunday: null },
  /* Real figures only. booked: total guests booked, from GoHighLevel, e.g. 186. Leave null to hide. */
  booked: null,
  /* A real deadline you will keep, e.g. "2027-01-15T23:59:00Z", with its label. Leave empty to hide. */
  priorityCloses: "",
  priorityLabel: "Priority release closes",
  /* Set true only once instalments (for example Klarna through Stripe) are switched on in GoHighLevel. */
  instalments: false,
  /* Measurement. Paste each ID to switch that tool on.
     ga4: Google Analytics 4 (G-XXXXXXX). Counts every visit, country and page from the first visit WITHOUT cookies (Consent Mode), full detail after Accept.
     googleAds: Google Ads conversion ID (AW-XXXXXXX). metaPixel, tiktok, linkedin (partner ID), snapchat (pixel ID), clarity (Microsoft Clarity project ID, heatmaps and recordings).
     All advertising tools and Clarity load only after the visitor chooses Accept. A cookie choice bar appears when any ID is set. */
  tracking: { ga4: "", googleAds: "", metaPixel: "", tiktok: "", linkedin: "", snapchat: "", clarity: "" },
  /* Meta: paste the Business Manager domain verification code (the content value only). Also paste the same Meta Pixel ID into Ticket Tailor (Box office settings, Tracking) so Purchase is counted where the payment happens. */
  metaDomainVerification: "",
  /* Cloudflare Web Analytics: cookieless visitor counts. Switch it on in Cloudflare, the Pages project, Metrics, Web Analytics. Cloudflare adds it to every page, no code needed. */
};

/* ===== Ticket Tailor: official pop-out checkout, with a plain link fallback. No card data touches this site. ===== */
(function () {
  var TT = SITE_CONFIG.ticketTailor || {},
    ev = TT.events || {},
    ln = TT.links || {};
  var DAYS = ["gala", "ghanaday", "sunday", "weekend"];
  var live = function (d) {
    return !!(TT.widgetScript && TT.boxOffice && ev[d]);
  };
  var link = function (d) {
    return ln[d] || (live(d) ? ln.boxoffice : "") || "";
  };
  var any = DAYS.some(live) || !!ln.boxoffice;
  window.GA70TT = { live: live, any: any };
  if (!any) return;
  document.documentElement.classList.add("tt-on");
  /* Pop-up checkout: a dialog on this site holding the official Ticket Tailor inline widget for the chosen event.
     The widget code is exactly what Ticket Tailor gives under Promote > Website embed code > Event listing widget,
     with that event's ID. Ticket Tailor takes the payment inside its own frame. */
  var NAMES = { gala: "The Royal Jubilee Gala", ghanaday: "Ghana Day Festival", sunday: "Women of the Motherland", weekend: "The Weekend Pass" };
  var ttUrl = function (d) {
    return (
      "https://www.tickettailor.com/events/" + encodeURIComponent(TT.boxOffice) + "/" + encodeURIComponent(ev[d]) +
      "/select-date?ref=website_widget&show_search_filter=true&show_date_filter=true&show_sort=true"
    );
  };
  var dlg = null,
    lastFocus = null,
    slowTimer = 0;
  var closeTT = function () {
    if (!dlg || dlg.hidden) return;
    dlg.hidden = true;
    clearTimeout(slowTimer);
    dlg.querySelector("[data-tt-body]").innerHTML = "";
    document.documentElement.classList.remove("co-open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  };
  var openTT = function (d, opener) {
    if (!dlg) {
      dlg = document.createElement("div");
      dlg.className = "co co-tt";
      dlg.hidden = true;
      dlg.innerHTML =
        '<div class="co-back" data-tt-close></div>' +
        '<div class="co-panel" role="dialog" aria-modal="true" aria-labelledby="tt-title">' +
        '<button class="co-x" type="button" data-tt-close aria-label="Close">×</button>' +
        '<h2 id="tt-title" class="tt-title"></h2>' +
        '<div class="tt-body" data-tt-body></div>' +
        '<p class="tt-alt">Trouble with this window? <a data-tt-alt target="_blank" rel="noopener">Open the booking page</a></p>' +
        "</div>";
      document.body.appendChild(dlg);
      dlg.addEventListener("click", function (e) {
        if (e.target.closest("[data-tt-close]")) closeTT();
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeTT();
      });
    }
    lastFocus = opener;
    dlg.querySelector(".tt-title").textContent = NAMES[d] || "Tickets";
    dlg.querySelector("[data-tt-alt]").href = link(d);
    var body = dlg.querySelector("[data-tt-body]");
    body.innerHTML = '<p class="tt-wait">Opening the secure Ticket Tailor checkout</p>';
    var w = document.createElement("div");
    w.className = "tt-widget";
    var sc = document.createElement("script");
    sc.src = TT.widgetScript;
    var at = {
      "data-url": ttUrl(d),
      "data-type": "inline",
      "data-inline-minimal": "true",
      "data-inline-show-logo": "false",
      "data-inline-bg-fill": "true",
      "data-inline-inherit-ref-from-url-param": "",
      "data-inline-ref": (window.__ga70ref && window.__ga70ref()) || "website_widget",
    };
    for (var k in at) sc.setAttribute(k, at[k]);
    sc.onerror = function () {
      location.href = link(d);
    };
    w.appendChild(sc);
    body.appendChild(w);
    dlg.hidden = false;
    document.documentElement.classList.add("co-open");
    dlg.querySelector(".co-x").focus();
    /* If the widget has not drawn its frame after 10 seconds, point the guest at the booking page */
    clearTimeout(slowTimer);
    slowTimer = setTimeout(function () {
      if (!body.querySelector("iframe")) {
        var wait = body.querySelector(".tt-wait");
        if (wait) wait.textContent = "The checkout is slow to open. Use the link below to book on the Ticket Tailor page.";
      } else {
        var wt = body.querySelector(".tt-wait");
        if (wt) wt.remove();
      }
    }, 10000);
    var poll = setInterval(function () {
      if (dlg.hidden) return clearInterval(poll);
      if (body.querySelector("iframe")) {
        var wt = body.querySelector(".tt-wait");
        if (wt) wt.remove();
        clearInterval(poll);
      }
    }, 250);
  };
  /* Real links on every booking button, so no script, a long press or a new tab still reaches the box office */
  var setHref = function () {
    document.querySelectorAll("[data-pay]").forEach(function (a) {
      var d = a.getAttribute("data-pay"),
        u = d === "pick" ? ln.boxoffice || "" : link(d);
      if (u && a.tagName === "A") {
        a.href = u;
        a.rel = "noopener";
      }
    });
    document.querySelectorAll("[data-tt-link]").forEach(function (a) {
      var u = link(a.getAttribute("data-tt-link"));
      if (u) {
        a.href = u;
        a.closest("[data-tt-fallback]") && (a.closest("[data-tt-fallback]").hidden = false);
      }
    });
    document.querySelectorAll("[data-tt-show]").forEach(function (el) {
      el.hidden = false;
    });
    document.querySelectorAll("[data-tt-hide]").forEach(function (el) {
      el.hidden = true;
    });
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setHref);
  else setHref();
  document.addEventListener(
    "click",
    function (e) {
      var a = e.target.closest && e.target.closest("[data-pay]");
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      var d = a.getAttribute("data-pay");
      if (d === "pick") {
        var all = document.getElementById("all-days");
        if (all) {
          e.preventDefault();
          e.stopImmediatePropagation();
          all.scrollIntoView({ behavior: "smooth", block: "start" });
          return;
        }
        if (ln.boxoffice) {
          e.stopImmediatePropagation();
          return;
        }
        e.preventDefault();
        e.stopImmediatePropagation();
        location.href = "tickets.html#all-days";
        return;
      }
      if (DAYS.indexOf(d) < 0 || !(live(d) || link(d))) return;
      e.stopImmediatePropagation();
      if (live(d)) {
        e.preventDefault();
        try {
          openTT(d, a);
          return;
        } catch {}
      }
      var u = link(d);
      if (u) {
        e.preventDefault();
        location.href = u;
      }
    },
    true,
  );
})();

(function () {
  /* Comfort view: larger text, calmer visuals, no motion. Remembered per visitor */
  var root = document.documentElement;
  var setComfort = function (on) {
    root.classList.toggle("comfort", on);
    document.querySelectorAll("[data-comfort]").forEach(function (b) {
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    try {
      localStorage.setItem("ga70-comfort", on ? "1" : "0");
    } catch {}
  };
  var savedComfort = null;
  try {
    savedComfort = localStorage.getItem("ga70-comfort");
  } catch {}
  if (
    savedComfort === "1" ||
    (savedComfort === null && window.matchMedia && window.matchMedia("(prefers-contrast: more)").matches)
  )
    setComfort(true);
  document.querySelectorAll("[data-comfort]").forEach(function (b) {
    b.addEventListener("click", function () {
      setComfort(!root.classList.contains("comfort"));
    });
  });

  /* Mobile navigation */
  var toggle = document.querySelector(".nav-toggle");
  var links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      var l = toggle.querySelector(".nt-l");
      if (l) l.textContent = open ? "Close" : "Menu";
      else toggle.textContent = open ? "Close" : "Menu";
      var hd = document.querySelector(".site-header");
      if (hd)
        document.documentElement.style.setProperty(
          "--hdr",
          Math.round(hd.getBoundingClientRect().bottom) + "px",
        );
      document.documentElement.classList.toggle("nav-open", open);
    });
    links.addEventListener("click", function (e) {
      if (e.target.closest("a") && links.classList.contains("open")) {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        var l = toggle.querySelector(".nt-l");
        if (l) l.textContent = "Menu";
        document.documentElement.classList.remove("nav-open");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && links.classList.contains("open")) {
        toggle.click();
        toggle.focus();
      }
    });
    window.matchMedia("(min-width: 1181px)").addEventListener("change", function (m) {
      if (m.matches && links.classList.contains("open")) toggle.click();
    });
  }

  /* Grouped menus: tap or hover, Escape or a tap outside closes */
  var dds = [].slice.call(document.querySelectorAll(".dd"));
  var closeAll = function (except) {
    dds.forEach(function (d) {
      if (d !== except) {
        d.classList.remove("open");
        d.querySelector(".dd-btn").setAttribute("aria-expanded", "false");
      }
    });
  };
  var desktop = window.matchMedia("(min-width: 1181px) and (hover: hover)");
  dds.forEach(function (d) {
    var b = d.querySelector(".dd-btn"),
      t = null;
    b.addEventListener("click", function () {
      if (desktop.matches && d.classList.contains("open") && Date.now() - (d._hov || 0) < 600) return;
      var o = !d.classList.contains("open");
      closeAll(d);
      d.classList.toggle("open", o);
      b.setAttribute("aria-expanded", o ? "true" : "false");
    });
    d.addEventListener("mouseenter", function () {
      if (!desktop.matches) return;
      clearTimeout(t);
      closeAll(d);
      if (!d.classList.contains("open")) d._hov = Date.now();
      d.classList.add("open");
      b.setAttribute("aria-expanded", "true");
    });
    d.addEventListener("mouseleave", function () {
      if (!desktop.matches) return;
      t = setTimeout(function () {
        d.classList.remove("open");
        b.setAttribute("aria-expanded", "false");
      }, 180);
    });
    d.addEventListener("focusout", function (e) {
      if (desktop.matches && !d.contains(e.relatedTarget)) {
        d.classList.remove("open");
        b.setAttribute("aria-expanded", "false");
      }
    });
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".dd") && !e.target.closest(".nav-toggle")) closeAll();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      var o = document.querySelector(".dd.open .dd-btn");
      closeAll();
      if (o) o.focus();
    }
  });
  /* Open the group for the current page in the mobile menu */
  if (toggle)
    toggle.addEventListener("click", function () {
      var h = document.querySelector(".dd.here") || document.querySelector(".dd");
      if (h && !desktop.matches && links.classList.contains("open")) {
        h.classList.add("open");
        h.querySelector(".dd-btn").setAttribute("aria-expanded", "true");
      }
    });

  /* Instant checkout once sales open */
  document.querySelectorAll("[data-pay]").forEach(function (a) {
    var link = SITE_CONFIG.pay && SITE_CONFIG.pay[a.getAttribute("data-pay")];
    if (link) {
      a.href = link;
      a.textContent = "Pay now, secure checkout";
      a.setAttribute("rel", "noopener");
      var r = a.closest(".ticket-copy");
      var rs = r && r.querySelector(".reassure");
      if (rs)
        rs.textContent = "Card, Apple Pay or Google Pay · Instant golden ticket by email · Transferable";
    }
  });

  /* Contact details */
  document.querySelectorAll("[data-email]").forEach(function (el) {
    el.textContent = SITE_CONFIG.contactEmail;
    if (el.tagName === "A") el.href = "mailto:" + SITE_CONFIG.contactEmail;
  });
  document.querySelectorAll("[data-phone]").forEach(function (el) {
    el.textContent = SITE_CONFIG.contactPhone;
    if (el.tagName === "A") el.href = "tel:" + SITE_CONFIG.contactPhone.replace(/\s/g, "");
  });
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* Countdown to Independence Day */
  var cd = document.querySelector("[data-countdown]");
  if (cd) {
    var target = new Date(SITE_CONFIG.anniversary).getTime();
    var cells = {
      d: cd.querySelector("[data-d]"),
      h: cd.querySelector("[data-h]"),
      m: cd.querySelector("[data-m]"),
      s: cd.querySelector("[data-s]"),
    };
    var tick = function () {
      var diff = Math.max(0, target - Date.now());
      var d = Math.floor(diff / 86400000);
      var h = Math.floor(diff / 3600000) % 24;
      var m = Math.floor(diff / 60000) % 60;
      var s = Math.floor(diff / 1000) % 60;
      cells.d.textContent = d;
      cells.h.textContent = String(h).padStart(2, "0");
      if (cells.m) cells.m.textContent = String(m).padStart(2, "0");
      if (cells.s) cells.s.textContent = String(s).padStart(2, "0");
    };
    tick();
    setInterval(tick, 1000);
  }

  /* Gold thread weave behind the hero */
  document.querySelectorAll("[data-weave]").forEach(function (canvas) {
    if (!canvas.getContext) return;
    var ctx = canvas.getContext("2d");
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var draw = function (t) {
      var w = canvas.clientWidth,
        h = canvas.clientHeight,
        dpr = Math.min(window.devicePixelRatio || 1, 3);
      if (!w || !h) {
        if (!reduce) requestAnimationFrame(draw);
        return;
      }
      if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
        canvas.width = Math.round(w * dpr);
        canvas.height = Math.round(h * dpr);
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      var step = 36,
        phase = (t || 0) / 4000;
      for (var x = 0; x < w + step; x += step) {
        var i = x / step;
        var a = 0.05 + 0.07 * (0.5 + 0.5 * Math.sin(phase + i * 0.55));
        ctx.fillStyle = "rgba(252,224,138," + a.toFixed(3) + ")";
        ctx.fillRect(x, 0, i % 4 === 0 ? 6 : 2, h);
      }
      for (var y = 0; y < h + step; y += step) {
        var j = y / step;
        var b = 0.04 + 0.06 * (0.5 + 0.5 * Math.cos(phase * 1.3 + j * 0.7));
        ctx.fillStyle = "rgba(212,166,42," + b.toFixed(3) + ")";
        ctx.fillRect(0, y, w, j % 3 === 0 ? 5 : 2);
      }
      for (var gx = 0; gx < w; gx += step * 4) {
        for (var gy = 0; gy < h; gy += step * 3) {
          var s = 0.5 + 0.5 * Math.sin(phase * 2 + gx * 0.01 + gy * 0.013);
          ctx.fillStyle = "rgba(252,224,138," + (0.05 + 0.1 * s).toFixed(3) + ")";
          ctx.fillRect(gx + 12, gy + 12, 12, 12);
        }
      }
      var g = ctx.createRadialGradient(w / 2, h * 0.42, 40, w / 2, h * 0.42, Math.max(w, h) * 0.55);
      g.addColorStop(0, "rgba(11,61,44,.92)");
      g.addColorStop(0.55, "rgba(11,61,44,.55)");
      g.addColorStop(1, "rgba(7,42,30,0)");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
      if (!reduce) {
        if (canvas.__vis === false)
          setTimeout(function () {
            requestAnimationFrame(draw);
          }, 250);
        else requestAnimationFrame(draw);
      }
    };
    if ("IntersectionObserver" in window)
      new IntersectionObserver(function (es) {
        canvas.__vis = es[0].isIntersecting;
      }).observe(canvas);
    requestAnimationFrame(draw);
  });

  /* Generative Kente cloth: strips sewn side by side, warp and weft blocks alternating like hand woven cloth */
  var KG = "#D4A62A",
    KG2 = "#F2D06B",
    KN = "#0B3D2C",
    KN2 = "#006B3F",
    KR = "#CE1126";
  function mulberry(a) {
    return function () {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function stripes(c, x, y, w, h, seq) {
    var tot = seq.reduce(function (s, v) {
        return s + v[1];
      }, 0),
      px = x;
    for (var i = 0; i < seq.length; i++) {
      var sw = (seq[i][1] / tot) * w;
      c.fillStyle = seq[i][0];
      c.fillRect(px, y, sw + 0.5, h);
      px += sw;
    }
  }
  var BLOCKS = [
    function warp(c, x, y, w, h) {
      stripes(c, x, y, w, h, [
        [KN, 5],
        [KG, 2],
        [KN2, 2],
        [KG, 1],
        [KR, 2],
        [KG, 1],
        [KN2, 2],
        [KG, 2],
        [KN, 5],
      ]);
    },
    function weft(c, x, y, w, h) {
      c.fillStyle = KG;
      c.fillRect(x, y, w, h);
      var n = 7;
      for (var i = 0; i < n; i++) {
        c.fillStyle = i % 3 === 1 ? KN2 : KN;
        if (i % 2) c.fillRect(x, y + (i * h) / n, w, (h / n) * 0.5);
      }
      c.fillStyle = KR;
      c.fillRect(x + w * 0.35, y + h * 0.44, w * 0.3, h * 0.12);
      c.fillStyle = KG2;
      c.fillRect(x + w * 0.45, y + h * 0.47, w * 0.1, h * 0.06);
    },
    function diamond(c, x, y, w, h) {
      c.fillStyle = KG;
      c.fillRect(x, y, w, h);
      var cx = x + w / 2,
        cy = y + h / 2;
      var d = function (s, col) {
        c.fillStyle = col;
        c.beginPath();
        c.moveTo(cx, cy - h * s);
        c.lineTo(cx + w * s, cy);
        c.lineTo(cx, cy + h * s);
        c.lineTo(cx - w * s, cy);
        c.closePath();
        c.fill();
      };
      d(0.48, KN);
      d(0.34, KG2);
      d(0.22, KN2);
      d(0.1, KR);
      c.fillStyle = KN;
      c.fillRect(x, y, w, h * 0.06);
      c.fillRect(x, y + h * 0.94, w, h * 0.06);
    },
    function zigzag(c, x, y, w, h) {
      c.fillStyle = KN;
      c.fillRect(x, y, w, h);
      c.strokeStyle = KG;
      c.lineWidth = Math.max(2, w * 0.09);
      var n = 4;
      for (var r = 0; r < n; r++) {
        var yy = y + ((r + 0.5) * h) / n;
        c.beginPath();
        for (var k = 0; k <= 4; k++) {
          var xx = x + (k * w) / 4;
          c.lineTo(xx, yy + (((k % 2 ? -1 : 1) * h) / n) * 0.28);
        }
        c.stroke();
      }
      c.fillStyle = KR;
      c.fillRect(x, y + h / 2 - 1.5, w, 3);
      c.fillStyle = KG2;
      c.fillRect(x, y, w, 2);
      c.fillRect(x, y + h - 2, w, 2);
    },
    function check(c, x, y, w, h) {
      var n = 6,
        m = Math.round((n * h) / w);
      for (var i = 0; i < n; i++)
        for (var j = 0; j < m; j++) {
          c.fillStyle = (i + j) % 2 ? KG : KN2;
          c.fillRect(x + (i * w) / n, y + (j * h) / m, w / n + 0.5, h / m + 0.5);
        }
      c.fillStyle = KR;
      c.fillRect(x + w * 0.42, y, w * 0.16, h);
      c.fillStyle = KG;
      c.fillRect(x + w * 0.46, y, w * 0.08, h);
    },
    function ladder(c, x, y, w, h) {
      stripes(c, x, y, w, h, [
        [KG, 3],
        [KN, 1],
        [KG, 3],
      ]);
      var n = 8;
      for (var i = 0; i < n; i++) {
        c.fillStyle = i % 4 === 2 ? KR : KN2;
        c.fillRect(x + w * 0.12, y + ((i + 0.3) * h) / n, w * 0.76, (h / n) * 0.35);
      }
    },
  ];
  function weaveCloth(canvas) {
    var ctx = canvas.getContext && canvas.getContext("2d");
    if (!ctx) return;
    var w = canvas.clientWidth,
      h = canvas.clientHeight;
    if (!w || !h) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 3);
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var horiz = w > h;
    if (horiz) {
      ctx.translate(0, h);
      ctx.rotate(-Math.PI / 2);
      var tmp = w;
      w = h;
      h = tmp;
    }
    var pal = canvas.getAttribute("data-palette");
    if (pal === "ruby") {
      KG = "#D4A62A";
      KG2 = "#F6DB86";
      KN = "#0B3D2C";
      KN2 = "#B5121F";
      KR = "#006B3F";
    } else {
      KG = "#D4A62A";
      KG2 = "#F2D06B";
      KN = "#0B3D2C";
      KN2 = "#006B3F";
      KR = "#CE1126";
    }
    var rand = mulberry(parseInt(canvas.getAttribute("data-kente"), 10) || 7);
    var sw = Math.max(
      26,
      Math.min(64, parseFloat(canvas.getAttribute("data-strip")) || w / Math.max(1, Math.round(w / 52))),
    );
    var strips = Math.ceil(w / sw),
      bl = sw * 1.25;
    for (var s = 0; s < strips; s++) {
      var x = s * sw,
        shift = rand() * bl;
      var order = [Math.floor(rand() * 6), Math.floor(rand() * 6), Math.floor(rand() * 6)];
      for (var b = -1, y = -shift; y < h; b++, y += bl) {
        var type = (b + s) % 2 === 0 ? 0 : order[((b % 3) + 3) % 3];
        if (type === 0 && (b + s) % 2 !== 0) type = 2;
        BLOCKS[type](ctx, x, y, sw, bl);
      }
      var g = ctx.createLinearGradient(x, 0, x + sw, 0);
      g.addColorStop(0, "rgba(0,0,0,.22)");
      g.addColorStop(0.2, "rgba(255,255,255,.08)");
      g.addColorStop(0.55, "rgba(255,255,255,0)");
      g.addColorStop(1, "rgba(0,0,0,.25)");
      ctx.fillStyle = g;
      ctx.fillRect(x, 0, sw, h);
      ctx.fillStyle = "rgba(11,61,44,.55)";
      ctx.fillRect(x + sw - 1, 0, 1, h);
    }
    ctx.globalAlpha = 0.07;
    ctx.fillStyle = "#000";
    for (var ty = 0; ty < h; ty += 3) ctx.fillRect(0, ty, w, 1);
    ctx.globalAlpha = 1;
  }
  var cloths = document.querySelectorAll("canvas[data-kente]");
  var weaveAll = function () {
    cloths.forEach(weaveCloth);
  };
  if (cloths.length) {
    weaveAll();
    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(weaveAll, 150);
    });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(weaveAll);
  }

  /* ===== Apple style motion layer ===== */
  var reduceMotion =
    (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) ||
    document.documentElement.classList.contains("comfort");
  var hasIO = "IntersectionObserver" in window;

  /* Days to Independence Day in the announcement bar */
  document.querySelectorAll("[data-days]").forEach(function (el) {
    el.textContent = Math.max(
      0,
      Math.ceil((new Date(SITE_CONFIG.anniversary).getTime() - Date.now()) / 86400000),
    );
  });

  /* Visitor source, kept for the session and sent with every form */
  var SRCKEYS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "ttclid",
    "li_fat_id",
    "ref",
  ];
  try {
    var q = new URLSearchParams(location.search);
    SRCKEYS.forEach(function (k) {
      if (q.get(k)) sessionStorage.setItem(k, q.get(k));
    });
    if (!sessionStorage.getItem("landing")) {
      sessionStorage.setItem("landing", location.pathname);
      sessionStorage.setItem("referrer", document.referrer || "");
    }
  } catch {}
  /* Alliance partner links (change request 3.4): ?ref=kumasi-alumni-uk is kept for the visit, sent with every form
     and booking as "ref", and shown in the booking form as "Who invited you?" with hyphens as spaces. */
  window.__ga70ref = function () {
    var r = "";
    try {
      r = new URLSearchParams(location.search).get("ref") || sessionStorage.getItem("ref") || "";
    } catch {}
    return String(r).replace(/[^\w .'-]/g, "").slice(0, 120);
  };
  window.__ga70src = function () {
    var o = {};
    try {
      SRCKEYS.concat(["landing", "referrer"]).forEach(function (k) {
        var v = sessionStorage.getItem(k);
        if (v) o[k] = v;
      });
    } catch {}
    try {
      var qp = new URLSearchParams(location.search);
      SRCKEYS.forEach(function (k) {
        if (!o[k] && qp.get(k)) o[k] = qp.get(k);
      });
      if (!o.referrer && document.referrer) o.referrer = document.referrer;
    } catch {}
    o.device = /Mobi|Android|iPhone/i.test(navigator.userAgent)
      ? "Mobile"
      : /iPad|Tablet/i.test(navigator.userAgent)
        ? "Tablet"
        : "Desktop";
    o.language = navigator.language || "";
    o.screen = screen.width + "x" + screen.height;
    try {
      o.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    } catch {}
    return o;
  };

  if (hasIO) {
    /* Reveal on scroll, from a visible resting state */
    var revealSel =
      ".section-head, .card, .day, .gt-wrap, .speaker, .b, .mc, .invite, .menu, .gmenu, .pledge, .form-card, .ad";
    var rvIO = new IntersectionObserver(
      function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            rvIO.unobserve(e.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px" },
    );
    document.querySelectorAll(revealSel).forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) {
        el.classList.add("rv");
        rvIO.observe(el);
      }
    });
  }

  /* Capture card: once, after real interest, never if dismissed or registered */
  var cap = document.getElementById("capture");
  var store = function (k, v) {
    try {
      if (v === undefined) return localStorage.getItem(k);
      localStorage.setItem(k, v);
    } catch {
      return null;
    }
  };
  if (cap && !store("ga70-cap") && !document.querySelector("#register .form-done:not([hidden])")) {
    var shown = false;
    /* Calm: never over a booking area or the checkout, only on leaving or after a long, quiet read */
    var busy = function () {
      if (document.documentElement.classList.contains("co-open")) return true;
      return [].some.call(
        document.querySelectorAll("#book, #register, #tickets, .ticket-row, .form-card"),
        function (el) {
          var r = el.getBoundingClientRect();
          return r.top < innerHeight && r.bottom > 0;
        },
      );
    };
    var show = function () {
      if (shown || store("ga70-cap") || store("ga70-basket") || busy()) return;
      shown = true;
      cap.hidden = false;
    };
    if (!matchMedia("(hover: none), (max-width: 900px)").matches) setTimeout(show, 90000);
    document.addEventListener("mouseout", function (e) {
      if (!e.relatedTarget && e.clientY < 8) show();
    });
    cap.querySelector(".capture-x").addEventListener("click", function () {
      cap.hidden = true;
      store("ga70-cap", "closed");
    });
  }
  document.addEventListener("ga70:registered", function () {
    store("ga70-cap", "done");
  });

  /* ===== Apple smoothness layer ===== */
  /* Momentum scrolling on desktop pointers */
  var pageName = function (u) {
    var n = (u || "")
      .split("?")[0]
      .split("/")
      .pop()
      .replace(/\.html$/, "");
    return n || "index";
  };
  /* Every new page starts at the top. A link to a section lands exactly on it, after fonts and images settle. */
  var navType = ((performance.getEntriesByType && performance.getEntriesByType("navigation")[0]) || {}).type;
  var landHash = function () {
    var t = location.hash.length > 1 && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (!t) return;
    var y = t.getBoundingClientRect().top + window.pageYOffset - 96;
    if (window.__ga70lenis) window.__ga70lenis.scrollTo(y, { immediate: true });
    else window.scrollTo(0, y);
  };
  try {
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  } catch {}
  var toTop = function () {
    if (location.hash) return;
    window.scrollTo(0, 0);
    if (window.__ga70lenis) window.__ga70lenis.scrollTo(0, { immediate: true });
  };
  if (navType !== "back_forward") {
    if (!location.hash) {
      toTop();
      document.addEventListener("DOMContentLoaded", toTop);
      window.addEventListener("load", toTop);
      window.addEventListener("pageshow", function (ev) {
        if (!ev.persisted) toTop();
      });
    } else {
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(landHash);
      window.addEventListener("load", function () {
        setTimeout(landHash, 60);
      });
    }
  }
  /* Same page section links on touch devices glide rather than jump */
  if (!(window.Lenis && !reduceMotion && window.matchMedia("(pointer: fine)").matches)) {
    document.querySelectorAll('a[href*="#"]').forEach(function (a) {
      a.addEventListener("click", function (e) {
        var href = a.getAttribute("href");
        if (href === "#") return;
        var hash = href.slice(href.indexOf("#")),
          base = href.split("#")[0];
        if (base && pageName(base) !== pageName(location.pathname)) return;
        var t = hash.length > 1 && document.getElementById(decodeURIComponent(hash.slice(1)));
        if (!t) return;
        e.preventDefault();
        window.scrollTo({
          top: t.getBoundingClientRect().top + window.pageYOffset - 96,
          behavior: reduceMotion ? "auto" : "smooth",
        });
        history.replaceState(null, "", hash);
      });
    });
  }
  var lenis = null;
  if (window.Lenis && !reduceMotion && window.matchMedia("(pointer: fine)").matches) {
    lenis = new window.Lenis({
      duration: 1.15,
      easing: function (x) {
        return Math.min(1, 1.001 - Math.pow(2, -10 * x));
      },
      smoothWheel: true,
    });
    var raf = function (time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    };
    requestAnimationFrame(raf);
    window.__ga70lenis = lenis;
    if (!location.hash && navType !== "back_forward") lenis.scrollTo(0, { immediate: true });
    document.documentElement.classList.add("smooth");
    window.addEventListener("load", function () {
      lenis.resize();
    });
    if (document.fonts && document.fonts.ready)
      document.fonts.ready.then(function () {
        lenis.resize();
      });
    document.querySelectorAll('a[href*="#"]').forEach(function (a) {
      a.addEventListener("click", function (e) {
        var href = a.getAttribute("href"),
          hash = href.slice(href.indexOf("#"));
        var samePage = href.charAt(0) === "#" || pageName(href.split("#")[0]) === pageName(location.pathname);
        var target = hash.length > 1 && document.querySelector(hash);
        if (samePage && target) {
          e.preventDefault();
          lenis.resize();
          lenis.scrollTo(target, { offset: -96 });
          history.replaceState(null, "", hash);
        }
      });
    });
  }

  /* Header settles into a compact glass bar after the first scroll */
  var headerEl = document.querySelector(".site-header");
  var compact = function () {
    if (headerEl) headerEl.classList.toggle("compact", window.scrollY > 60);
  };
  window.addEventListener("scroll", compact, { passive: true });
  compact();

  /* The real header height, kept in --hdr-h at every width and scroll state, so sticky bars sit right under it (change request 5.1) */
  var setHdrH = function () {
    if (headerEl) document.documentElement.style.setProperty("--hdr-h", headerEl.offsetHeight + "px");
  };
  setHdrH();
  if (headerEl && window.ResizeObserver) new ResizeObserver(setHdrH).observe(headerEl);
  window.addEventListener("resize", setHdrH, { passive: true });

  /* Hero recedes as you scroll, like a product stage */
  var heroEl = document.querySelector(".hero"),
    archEl = heroEl && heroEl.querySelector(".arch"),
    drapes = heroEl ? heroEl.querySelectorAll(".drape") : [];
  if (heroEl && archEl && !reduceMotion) {
    var heroTick = false;
    var heroScroll = function () {
      heroTick = false;
      var h = heroEl.offsetHeight,
        p = Math.max(0, Math.min(1, window.scrollY / h));
      archEl.style.transform =
        "translate3d(0," + (p * 60).toFixed(1) + "px,0) scale(" + (1 - p * 0.08).toFixed(4) + ")";
      archEl.style.opacity = (1 - p * 0.5).toFixed(3);
      drapes.forEach(function (d, i) {
        d.style.transform = "translate3d(0," + (p * (i ? -90 : 90)).toFixed(1) + "px,0)";
      });
    };
    window.addEventListener(
      "scroll",
      function () {
        if (!heroTick) {
          heroTick = true;
          requestAnimationFrame(heroScroll);
        }
      },
      { passive: true },
    );
  }

  /* Stagger siblings so groups arrive as a wave */
  document
    .querySelectorAll(
      ".days, .cards, .bento, .master, .speakers, .adinkra, .facts, .regalia, .invite, .tickets",
    )
    .forEach(function (g) {
      Array.prototype.forEach.call(g.children, function (c, i) {
        c.style.setProperty("--i", i % 6);
      });
    });

  /* Swipe galleries on phones, with Apple style paddle dots */
  document.querySelectorAll(".days, .master").forEach(function (g) {
    var dots = document.createElement("div");
    dots.className = "dots";
    dots.setAttribute("aria-hidden", "true");
    Array.prototype.forEach.call(g.children, function () {
      dots.appendChild(document.createElement("i"));
    });
    g.after(dots);
    var upd = function () {
      var kids = g.children,
        best = 0,
        bd = 1e9,
        mid = g.scrollLeft + g.clientWidth / 2;
      for (var i = 0; i < kids.length; i++) {
        var c = kids[i].offsetLeft + kids[i].offsetWidth / 2,
          d = Math.abs(c - mid);
        if (d < bd) {
          bd = d;
          best = i;
        }
      }
      Array.prototype.forEach.call(dots.children, function (d, i) {
        d.classList.toggle("on", i === best);
      });
    };
    g.addEventListener(
      "scroll",
      function () {
        requestAnimationFrame(upd);
      },
      { passive: true },
    );
    upd();
  });

  /* Sticky local nav on each day page */
  var local = document.querySelector("[data-localnav]"),
    ph = document.querySelector(".page-head");
  if (local && ph) {
    var ln = function () {
      local.classList.toggle("show", ph.getBoundingClientRect().bottom < 70);
    };
    window.addEventListener("scroll", ln, { passive: true });
    ln();
  }

  /* Page heads recede gently as you scroll */
  if (ph && !reduceMotion) {
    var phIn = ph.querySelector(".ph-inner"),
      phW = ph.querySelector(".watermark"),
      phTick = false;
    window.addEventListener(
      "scroll",
      function () {
        if (phTick) return;
        phTick = true;
        requestAnimationFrame(function () {
          phTick = false;
          var p = Math.max(0, Math.min(1, window.scrollY / ph.offsetHeight));
          if (phIn) {
            phIn.style.transform = "translate3d(0," + (p * 70).toFixed(1) + "px,0)";
            phIn.style.opacity = (1 - p * 0.6).toFixed(3);
          }
          if (phW)
            phW.style.transform =
              "translateY(-50%) rotate(" +
              (p * 40).toFixed(1) +
              "deg) scale(" +
              (1 + p * 0.15).toFixed(3) +
              ")";
        });
      },
      { passive: true },
    );
  }

  /* Share with family over WhatsApp */
  document.querySelectorAll("[data-share]").forEach(function (a) {
    a.href =
      "https://wa.me/?text=" +
      encodeURIComponent(
        document.title.split("|")[0].trim() +
          ", Ghana at 70 UK in London. Book your tickets: " +
          location.href.split("#")[0],
      );
    a.target = "_blank";
    a.rel = "noopener";
  });

  /* ===== Heading and panel motion ===== */
  if (hasIO) {
    var once = function (sel, opts) {
      var io = new IntersectionObserver(
        function (es) {
          es.forEach(function (e) {
            if (e.isIntersecting) {
              e.target.classList.add("in");
              io.unobserve(e.target);
            }
          });
        },
        opts || { rootMargin: "0px 0px -12% 0px" },
      );
      document.querySelectorAll(sel).forEach(function (el) {
        io.observe(el);
      });
    };
    /* Split headings into masked words */
    document.querySelectorAll(".section-head h2, .page-head h1").forEach(function (h) {
      var w = 0;
      var walk = function (node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (n) {
          if (n.nodeType === 3) {
            var frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach(function (part) {
              if (!part) return;
              if (/^\s+$/.test(part)) {
                frag.appendChild(document.createTextNode(" "));
                return;
              }
              var o = document.createElement("span");
              o.className = "mw";
              var i = document.createElement("span");
              i.textContent = part;
              i.style.setProperty("--w", w++);
              o.appendChild(i);
              frag.appendChild(o);
            });
            n.parentNode.replaceChild(frag, n);
          } else if (n.nodeType === 1 && n.tagName !== "BR") walk(n);
        });
      };
      walk(h);
      h.classList.add("split-h");
      if (h.getBoundingClientRect().top < innerHeight * 0.9)
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            h.classList.add("in");
          });
        });
    });
    once(".split-h:not(.in)");
    once(".wipe");
  }
  /* Forms */
  document.querySelectorAll("form[data-register]").forEach(function (form) {
    var status = form.querySelector(".form-status");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "form-status";
      status.textContent = "";
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      var data = {};
      new FormData(form).forEach(function (v, k) {
        if (data[k]) {
          data[k] = [].concat(data[k], v);
        } else {
          data[k] = v;
        }
      });
      data.page = location.pathname;
      var src = window.__ga70src ? window.__ga70src() : {};
      for (var sk in src) data[sk] = src[sk];
      var btn = form.querySelector("button[type=submit]");
      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = "Sending";
      fetch(SITE_CONFIG.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
        .then(function (r) {
          return r
            .json()
            .catch(function () {
              return {};
            })
            .then(function (j) {
              return { ok: r.ok, body: j };
            });
        })
        .then(function (res) {
          if (!res.ok) throw new Error(res.body && res.body.error ? res.body.error : "Request failed");
          var done = form.parentElement.querySelector(".form-done");
          document.dispatchEvent(new Event("ga70:registered"));
          if (done) {
            form.hidden = true;
            done.hidden = false;
            if (!form.closest(".capture")) done.scrollIntoView({ behavior: "smooth", block: "center" });
          } else {
            status.className = "form-status ok";
            status.textContent = "Thank you. Your details are with us.";
            form.reset();
          }
        })
        .catch(function (err) {
          status.className = "form-status err";
          var msg = err && err.message && err.message !== "Request failed" && err.message.indexOf("fetch") < 0 ? err.message + " " : "";
          status.textContent = msg
            ? msg
            : "We could not send your details just now. Please try again in a moment, or email " + SITE_CONFIG.contactEmail + ".";
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = label;
        });
    });
  });

  /* ===== Measurement =====
     1. Cookieless counts for every visitor from the first page: Cloudflare Web Analytics and GA4 in Consent Mode (no cookies until Accept).
     2. Advertising pixels and Clarity only after Accept. Equal Accept and Reject, and a Cookie settings link in the footer. */
  var T = SITE_CONFIG.tracking || {};
  var hasTracking = !!(
    T.ga4 ||
    T.googleAds ||
    T.metaPixel ||
    T.tiktok ||
    T.linkedin ||
    T.snapchat ||
    T.clarity
  );
  var consent = null;
  try {
    consent = localStorage.getItem("ga70-consent");
  } catch {}
  var add = function (src) {
    var sc = document.createElement("script");
    sc.async = true;
    sc.src = src;
    document.head.appendChild(sc);
    return sc;
  };
  var gaOn = false;
  var startGA = function () {
    if (gaOn || !(T.ga4 || T.googleAds)) return;
    gaOn = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      dataLayer.push(arguments);
    };
    var g = consent === "yes" ? "granted" : "denied";
    gtag("consent", "default", {
      analytics_storage: g,
      ad_storage: g,
      ad_user_data: g,
      ad_personalization: g,
      wait_for_update: 500,
    });
    gtag("set", "url_passthrough", true);
    gtag("set", "ads_data_redaction", consent !== "yes");
    gtag("js", new Date());
    if (T.ga4) gtag("config", T.ga4, { allow_google_signals: consent === "yes" });
    if (T.googleAds) gtag("config", T.googleAds);
    add("https://www.googletagmanager.com/gtag/js?id=" + (T.ga4 || T.googleAds));
  };
  startGA();
  var loadTags = function () {
    if (window.gtag)
      gtag("consent", "update", {
        analytics_storage: "granted",
        ad_storage: "granted",
        ad_user_data: "granted",
        ad_personalization: "granted",
      });
    if (T.metaPixel && !window.fbq) {
      !(function (f, b, e, v, n, t, s) {
        if (f.fbq) return;
        n = f.fbq = function () {
          n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
        };
        if (!f._fbq) f._fbq = n;
        n.push = n;
        n.loaded = !0;
        n.version = "2.0";
        n.queue = [];
        t = b.createElement(e);
        t.async = !0;
        t.src = v;
        s = b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t, s);
      })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
      fbq("init", T.metaPixel);
      fbq("track", "PageView");
    }
    if (T.tiktok && !window.ttq) {
      !(function (w, d, t) {
        w.TiktokAnalyticsObject = t;
        var ttq = (w[t] = w[t] || []);
        ttq.methods = ["page", "track", "identify"];
        ttq.setAndDefer = function (t, e) {
          t[e] = function () {
            t.push([e].concat(Array.prototype.slice.call(arguments, 0)));
          };
        };
        for (var i = 0; i < ttq.methods.length; i++) ttq.setAndDefer(ttq, ttq.methods[i]);
        ttq.load = function (e) {
          var s = d.createElement("script");
          s.async = true;
          s.src = "https://analytics.tiktok.com/i18n/pixel/events.js?sdkid=" + e + "&lib=" + t;
          d.head.appendChild(s);
        };
        ttq.load(T.tiktok);
        ttq.page();
      })(window, document, "ttq");
    }
    if (T.linkedin && !window._linkedin_data_partner_ids) {
      window._linkedin_partner_id = T.linkedin;
      window._linkedin_data_partner_ids = [T.linkedin];
      window.lintrk =
        window.lintrk ||
        function (a, b) {
          (window.lintrk.q = window.lintrk.q || []).push([a, b]);
        };
      add("https://snap.licdn.com/li.lms-analytics/insight.min.js");
    }
    if (T.snapchat && !window.snaptr) {
      var sn = (window.snaptr = function () {
        sn.handleRequest ? sn.handleRequest.apply(sn, arguments) : sn.queue.push(arguments);
      });
      sn.queue = [];
      add("https://sc-static.net/scevent.min.js");
      snaptr("init", T.snapchat);
      snaptr("track", "PAGE_VIEW");
    }
    if (T.clarity && !window.clarity) {
      window.clarity = function () {
        (window.clarity.q = window.clarity.q || []).push(arguments);
      };
      add("https://www.clarity.ms/tag/" + T.clarity);
    }
  };
  if (hasTracking && consent === "yes") loadTags();
  var showBar = function () {
    if (document.querySelector(".consent-bar")) return;
    var cb = document.createElement("div");
    cb.className = "consent-bar";
    cb.setAttribute("role", "region");
    cb.setAttribute("aria-label", "Cookie choice");
    cb.innerHTML =
      '<p>We count visits without cookies so we can improve this site. With your permission we also use cookies from Google, Meta, TikTok, LinkedIn, Snapchat and Microsoft to measure our adverts and how the site is used. <a href="privacy.html#cookies">Details</a></p><div class="btn-row"><button class="btn gold small" type="button" data-cy>Accept all</button><button class="btn gold small" type="button" data-cn>Reject all</button></div>';
    document.body.appendChild(cb);
    cb.addEventListener("click", function (e) {
      var yes = e.target.closest("[data-cy]"),
        no = e.target.closest("[data-cn]");
      if (!yes && !no) return;
      var was = consent;
      try {
        localStorage.setItem("ga70-consent", yes ? "yes" : "no");
      } catch {}
      consent = yes ? "yes" : "no";
      cb.remove();
      if (yes) loadTags();
      else {
        if (window.gtag)
          gtag("consent", "update", {
            analytics_storage: "denied",
            ad_storage: "denied",
            ad_user_data: "denied",
            ad_personalization: "denied",
          });
        if (was === "yes") location.reload();
      }
    });
  };
  if (hasTracking && !consent) showBar();
  document.querySelectorAll("[data-cookie-settings]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      showBar();
    });
  });

  /* Engagement events: GA4 receives them cookieless before Accept, in full after */
  var ga = function (ev, p) {
    try {
      if (window.gtag) gtag("event", ev, p || {});
    } catch {}
  };
  document.addEventListener(
    "click",
    function (e) {
      var a = e.target.closest("a, button");
      if (!a) return;
      var href = a.getAttribute("href") || "";
      if (/^tel:/.test(href)) ga("click_phone", { link_url: href });
      else if (/^mailto:/.test(href)) ga("click_email", { link_url: href });
      else if (/^https?:/.test(href) && href.indexOf(location.hostname) === -1)
        ga("click_outbound", { link_url: href });
      if (a.hasAttribute("data-pay"))
        ga("click_book", { day: a.getAttribute("data-pay"), page: location.pathname });
      if (a.hasAttribute("data-gi-full")) ga("gallery_open", { image: a.getAttribute("data-gi-full") });
      if (a.hasAttribute("data-copy")) ga("press_copy", { item: a.getAttribute("data-copy") });
    },
    true,
  );
  (function () {
    var marks = [25, 50, 75, 90],
      hit = {};
    window.addEventListener(
      "scroll",
      function () {
        var h = document.documentElement,
          pct = Math.round(((h.scrollTop + innerHeight) / h.scrollHeight) * 100);
        marks.forEach(function (m) {
          if (pct >= m && !hit[m]) {
            hit[m] = 1;
            ga("scroll_depth", { percent: m, page: location.pathname });
          }
        });
      },
      { passive: true },
    );
  })();
  setTimeout(function () {
    ga("engaged_30s", { page: location.pathname });
  }, 30000);
  var track = function (ev, p) {
    p = p || {};
    if (ev === "share" || ev === "add_to_calendar" || ev === "join_priority_from_book") {
      try {
        if (window.gtag) gtag("event", ev, { method: p.method, item_id: p.day });
      } catch {}
      return;
    }
    var gaMap = {
      view_item: "view_item",
      begin_checkout: "begin_checkout",
      lead: "generate_lead",
      purchase: "purchase",
    };
    var fbMap = {
      view_item: "ViewContent",
      begin_checkout: "InitiateCheckout",
      lead: "Lead",
      purchase: "Purchase",
    };
    var ttMap = {
      view_item: "ViewContent",
      begin_checkout: "InitiateCheckout",
      lead: "SubmitForm",
      purchase: "CompletePayment",
    };
    try {
      if (window.gtag)
        gtag("event", gaMap[ev], {
          currency: "GBP",
          value: p.value || 0,
          items: [{ item_id: p.day, item_name: p.name, price: p.price, quantity: p.qty }],
        });
    } catch {}
    if (consent !== "yes") return;
    try {
      if (window.lintrk && ev === "lead") lintrk("track", { conversion_id: 0 });
    } catch {}
    try {
      if (window.snaptr)
        snaptr(
          "track",
          {
            view_item: "VIEW_CONTENT",
            begin_checkout: "START_CHECKOUT",
            lead: "SIGN_UP",
            purchase: "PURCHASE",
          }[ev],
          { price: p.value || 0, currency: "GBP" },
        );
    } catch {}
    try {
      if (window.fbq)
        fbq("track", fbMap[ev], {
          currency: "GBP",
          value: p.value || 0,
          content_ids: [p.day],
          content_type: "product",
          num_items: p.qty,
        });
    } catch {}
    try {
      if (window.ttq)
        ttq.track(ttMap[ev], { currency: "GBP", value: p.value || 0, content_id: p.day, quantity: p.qty });
    } catch {}
  };
  window.__ga70track = track;
  /* Ad signals: ViewContent on each day page, InitiateCheckout when a Book now opens the Ticket Tailor box office */
  var PRICE = {
      gala: SITE_CONFIG.firstRelease && SITE_CONFIG.firstRelease.on ? SITE_CONFIG.prices.firstRelease : SITE_CONFIG.prices.gala,
      ghanaday: SITE_CONFIG.prices.ghanaday,
      sunday: SITE_CONFIG.prices.sunday,
      weekend: SITE_CONFIG.prices.weekend,
    },
    NAMES = {
      gala: "The Royal Jubilee Gala",
      ghanaday: "Ghana Day Festival",
      sunday: "Women of the Motherland",
      weekend: "Weekend Pass",
    };
  var PAGEDAY = { "royal-gala": "gala", "ghana-day": "ghanaday", "women-of-the-motherland": "sunday" };
  var slug = (location.pathname.split("/").pop() || "").replace(/\.html$/, "");
  if (PAGEDAY[slug]) {
    var vd = PAGEDAY[slug];
    setTimeout(function () {
      track("view_item", { day: vd, name: NAMES[vd], price: PRICE[vd], qty: 1, value: PRICE[vd] });
    }, 1200);
  }
  if (slug === "tickets")
    setTimeout(function () {
      track("view_item", { day: "weekend", name: "All tickets", price: 0, qty: 1, value: 0 });
    }, 1200);
  document.addEventListener(
    "click",
    function (e) {
      var a = e.target.closest && e.target.closest("[data-pay]");
      if (!a || !window.GA70TT || !window.GA70TT.any) return;
      var d = a.getAttribute("data-pay");
      if (d === "pick") d = PAGEDAY[slug] || "weekend";
      track("begin_checkout", {
        day: d,
        name: NAMES[d] || d,
        price: PRICE[d] || 0,
        qty: 1,
        value: PRICE[d] || 0,
      });
    },
    true,
  );
  document.addEventListener("ga70:lead", function () {
    track("lead", {});
  });

  /* ===== True social proof and real deadlines, shown only when set in SITE_CONFIG ===== */
  if (typeof SITE_CONFIG.booked === "number" && SITE_CONFIG.booked > 0)
    document.querySelectorAll("[data-booked]").forEach(function (el) {
      el.textContent = SITE_CONFIG.booked.toLocaleString("en-GB") + " guests have booked";
      el.hidden = false;
    });
  if (SITE_CONFIG.priorityCloses) {
    var dl = new Date(SITE_CONFIG.priorityCloses),
      dd = Math.ceil((dl - Date.now()) / 86400000);
    if (dd > 0)
      document.querySelectorAll("[data-deadline]").forEach(function (el) {
        el.textContent =
          (SITE_CONFIG.priorityLabel || "Priority release closes") +
          " in " +
          dd +
          (dd === 1 ? " day" : " days");
        el.hidden = false;
      });
  }

  /* ===== Checkout: two calm steps. 1 your day, 2 your details, 3 secure payment ===== */
  var DAYS = {
    gala: {
      name: "The Royal Jubilee Gala",
      short: "Fri 5 March",
      tab: "Gala",
      when: "Friday 5 March 2027 · 18:30 to 00:30",
      price: SITE_CONFIG.prices.gala,
      field: "Royal Jubilee Gala",
      valid: "This ticket is for The Royal Jubilee Gala only: Friday 5 March 2027, 18:30 to 00:30, Banking Hall, London. It does not include the Ghana Day Festival or Women of the Motherland, which are separate events with their own tickets.",
      tone: "black",
      line: "Banking Hall, City of London · The Ghanaian inspired dinner, the band and the midnight toast · Black Tie, ball gown or Kente",
      presets: [
        [1, "1"],
        [2, "2"],
        [4, "4"],
        [10, "Table of ten"],
      ],
      cal: "https://calendar.google.com/calendar/render?action=TEMPLATE&text=Ghana%20at%2070%20UK%3A%20The%20Royal%20Jubilee%20Gala&dates=20270305T183000Z/20270306T003000Z&details=Doors%2018%3A30.%20We%20start%20on%20time.%20Your%20golden%20ticket%20arrives%20by%20email.&location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND",
    },
    ghanaday: {
      name: "Ghana Day Festival",
      short: "Sat 6 March",
      tab: "Festival",
      when: "Saturday 6 March 2027 · 11:00 to 18:00",
      price: SITE_CONFIG.prices.ghanaday,
      field: "Ghana Day",
      valid: "This ticket is for the Ghana Day Festival only: Saturday 6 March 2027, 11:00 to 18:00, Banking Hall, London. It does not include The Royal Jubilee Gala or Women of the Motherland, which are separate events with their own tickets.",
      tone: "green",
      line: "Banking Hall · Independence Day · DJ and dancing · All ages welcome, children with an adult",
      presets: [
        [1, "1"],
        [2, "2"],
        [4, "4"],
        [6, "Quiz team, 6 tickets"],
      ],
      cal: "https://calendar.google.com/calendar/render?action=TEMPLATE&text=Ghana%20at%2070%20UK%3A%20Ghana%20Day%20Festival&dates=20270306T110000Z/20270306T180000Z&details=Independence%20Day%20at%20Banking%20Hall.%20Your%20golden%20ticket%20arrives%20by%20email.&location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND",
    },
    sunday: {
      name: "Women of the Motherland",
      short: "Sun 7 March",
      tab: "Women",
      when: "Sunday 7 March 2027 · 11:00 to 18:30",
      price: SITE_CONFIG.prices.sunday,
      field: "Women of the Motherland",
      valid: "This ticket is for Women of the Motherland only: Sunday 7 March 2027, 11:00 to 18:30, Banking Hall, London. It does not include The Royal Jubilee Gala or the Ghana Day Festival, which are separate events with their own tickets.",
      tone: "gold",
      line: "Mothering Sunday · Family afternoon tea, one sitting, a full day · Her name on the Wall of Mothers",
      presets: [
        [1, "1"],
        [2, "2"],
        [3, "3"],
        [5, "Family table, 5 tickets"],
      ],
      cal: "https://calendar.google.com/calendar/render?action=TEMPLATE&text=Ghana%20at%2070%20UK%3A%20Women%20of%20the%20Motherland&dates=20270307T110000Z/20270307T183000Z&details=Mothering%20Sunday%20at%20Banking%20Hall.%20Doors%2011%3A00.%20Your%20golden%20ticket%20arrives%20by%20email.&location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND",
    },
    weekend: {
      name: "The Weekend Pass",
      short: "All three",
      tab: "Weekend Pass",
      when: "Friday 5 to Sunday 7 March 2027",
      price: SITE_CONFIG.prices.weekend,
      field: "Weekend Pass",
      valid: "This pass gives one entry to each of three separate events, each on its own date: The Royal Jubilee Gala on Friday 5 March 2027, 18:30 to 00:30, the Ghana Day Festival on Saturday 6 March 2027, 11:00 to 18:00, and Women of the Motherland on Sunday 7 March 2027, 11:00 to 18:30, all at Banking Hall, London.",
      tone: "black",
      line: "",
      presets: [
        [1, "1"],
        [2, "2"],
        [4, "4"],
      ],
      cal: "",
    },
  };
  var fmt = function (n) {
    return "GBP " + n.toLocaleString("en-GB");
  };
  var P = SITE_CONFIG.prices,
    FR = SITE_CONFIG.firstRelease || {},
    frOn = !!FR.on,
    frMax = FR.perOrder || 2;
  /* Gala booking card line, from the one first release switch */
  DAYS.gala.line =
    (frOn ? "First release " + fmt(P.firstRelease) + ", up to " + frMax + " per order · " : "") +
    "Table of ten " + fmt(P.table) + ", ten guests for the price of nine (9 x " + fmt(P.gala) + ") · " +
    DAYS.gala.line;
  DAYS.weekend.line =
    "All three days, for one guest. " +
    (frOn
      ? "Always less than three separate tickets: " + fmt(P.firstRelease + P.ghanaday + P.sunday) + " at first release prices, " + fmt(P.gala + P.ghanaday + P.sunday) + " after."
      : "Less than three separate tickets: " + fmt(P.gala) + " + " + fmt(P.ghanaday) + " + " + fmt(P.sunday) + " = " + fmt(P.gala + P.ghanaday + P.sunday) + ".");
  /* Every total the site works out itself. The guest always pays the lower of two prices, never both offers together.
     Gala option A: first release on up to frMax seats, the rest at the Gala price.
     Gala option B: every tenth seat free (a table of ten is the price of nine).
     Returns the total, the working shown to the guest, and a hint when one more guest would be free. */
  var quote = function (day, n) {
    var d = DAYS[day],
      unit = d.price;
    if (day !== "gala") return { total: n * unit, unit: unit, working: n + " x " + fmt(unit), offer: "" };
    var free = Math.floor(n / 10),
      bTotal = (n - free) * P.gala,
      bWork = free ? n - free + " x " + fmt(P.gala) + " (every tenth seat free)" : n + " x " + fmt(P.gala);
    var best = { total: bTotal, unit: P.gala, working: bWork, offer: free ? "Table of ten" : "" };
    if (frOn) {
      var fr = Math.min(n, frMax),
        aTotal = fr * P.firstRelease + (n - fr) * P.gala,
        aWork = fr + " x " + fmt(P.firstRelease) + (n > fr ? " + " + (n - fr) + " x " + fmt(P.gala) : "");
      if (aTotal < bTotal) best = { total: aTotal, unit: P.firstRelease, working: aWork, offer: "First release" };
    }
    if (n % 10 === 9 && !(frOn && best.offer === "First release")) best.hint = "Add one more guest: the next seat is free.";
    return best;
  };
  window.__ga70days = DAYS;
  window.__ga70quote = quote;
  var co = document.createElement("div");
  co.className = "co";
  co.hidden = true;
  co.innerHTML =
    '<div class="co-back" data-co-close></div><div class="co-panel" role="dialog" aria-modal="true" aria-labelledby="co-title">' +
    '<button class="co-x" type="button" data-co-close aria-label="Close">×</button>' +
    '<ol class="co-steps" aria-label="Booking steps"><li data-co-s="1">Your event</li><li data-co-s="2">Your details</li><li data-co-s="3">Secure payment</li></ol>' +
    '<div class="co-tabs" role="tablist" aria-label="Choose your event">' +
    Object.keys(DAYS)
      .filter(function (k) {
        return !DAYS[k].hiddenTab;
      })
      .map(function (k) {
        return (
          '<button type="button" role="tab" data-co-day="' +
          k +
          '"><b>' +
          DAYS[k].tab +
          "</b><small>" +
          DAYS[k].short +
          "</small><span>" +
          fmt(DAYS[k].price) +
          "</span></button>"
        );
      })
      .join("") +
    "</div>" +
    '<span class="eyebrow" data-co-when></span><h2 id="co-title" data-co-name></h2><p class="co-line" data-co-line></p><p class="co-valid" data-co-valid></p>' +
    '<form class="co-form" novalidate>' +
    '<div class="co-step" data-step="1">' +
    '<div class="co-qty"><span>Guests</span><div class="stepper"><button type="button" data-co-dec aria-label="One fewer guest">−</button><output data-co-n>2</output><button type="button" data-co-inc aria-label="One more guest">+</button></div></div>' +
    '<div class="co-presets" data-co-presets></div>' +
    '<div class="co-sun" data-co-sun hidden>' +
    '<div class="field"><label for="co-mother">The Wall of Mothers (optional)</label><input id="co-mother" name="motherName" placeholder="For example, Auntie Ama Mensah, Kumasi"></div></div>' +
    '<p class="co-total" data-co-total></p>' +
    '<p class="co-pre" data-co-pre hidden>Tickets are on sale now.</p>' +
    '<button class="btn gold co-pay" type="button" data-co-next>Continue</button>' +
    '<p class="reassure c">No booking fees added · Alcohol not included · Transferable tickets</p>' +
    "</div>" +
    '<div class="co-step" data-step="2" hidden>' +
    '<p class="co-sum" data-co-sum></p>' +
    '<div class="row2"><div class="field"><label for="co-first">First name</label><input id="co-first" name="firstName" autocomplete="given-name" required></div>' +
    '<div class="field"><label for="co-last">Last name</label><input id="co-last" name="lastName" autocomplete="family-name" required></div></div>' +
    '<div class="row2"><div class="field"><label for="co-email">Email</label><input id="co-email" type="email" name="email" autocomplete="email" inputmode="email" required></div>' +
    '<div class="field"><label for="co-tel">Mobile</label><input id="co-tel" type="tel" name="phone" autocomplete="tel" inputmode="tel" required></div></div>' +
    '<fieldset class="co-payby"><legend>How would you like to pay?</legend><label class="check"><input type="radio" name="payBy" value="card" checked><span data-co-cardlbl>Card, Apple Pay or Google Pay</span></label><label class="check"><input type="radio" name="payBy" value="bank"><span>Bank transfer</span></label></fieldset>' +
    '<div class="field"><label for="co-inv">Who invited you? (optional)</label><input id="co-inv" name="invitedBy" autocomplete="off"></div>' +
    '<div class="co-opts">' +
    '<label class="check"><input type="checkbox" name="gift" value="yes" data-co-gift><span>This is a gift</span></label>' +
    '<label class="check"><input type="checkbox" name="company" value="yes" data-co-co><span>Booking for a company, invoice needed</span></label>' +
    '<label class="check"><input type="checkbox" name="hotel" value="yes"><span>Help me book my hotel stay</span></label></div>' +
    '<div class="field" data-co-giftf hidden><label for="co-gname">Gift for (name on the golden ticket)</label><input id="co-gname" name="giftFor"></div>' +
    '<div class="field" data-co-cof hidden><label for="co-org">Company name</label><input id="co-org" name="organisation" autocomplete="organization"></div>' +
    '<div class="co-final"><b>All sales are final.</b><span>No refunds. If you cannot attend, transfer your ticket to another guest at no extra cost. If we cancel, you are refunded in full.</span></div>' +
    '<input type="hidden" name="finalSale" value="I understand all sales are final, tickets cannot be refunded and may only be transferred">' +
    '<label class="consent co-must"><input type="checkbox" name="consent" value="yes" required><span>I understand <b>all sales are final</b> and tickets are transferable, and I agree to the <a href="terms.html#final-sale" target="_blank" rel="noopener">ticket terms</a> and the <a href="privacy.html" target="_blank" rel="noopener">privacy notice</a>.</span></label>' +
    '<label class="consent"><input type="checkbox" name="news" value="yes"><span>Send me news of the line up and releases. Unsubscribe at any time.</span></label>' +
    '<details class="co-more"><summary>Optional: tell us a little more</summary>' +
    '<div class="field"><label for="co-sector">Your sector</label><select id="co-sector" name="sector"><option value="">Prefer not to say</option><option>Finance and banking</option><option>Law</option><option>Medicine and health</option><option>Property</option><option>Technology</option><option>Business owner</option><option>Public sector</option><option>Education</option><option>Creative and media</option><option>Other</option></select></div>' +
    '<label class="consent"><input type="checkbox" name="partnerIntro" value="yes"><span>Optional: I am happy to hear from Ghana at 70 UK partners about banking, property or money transfer across the UK and Ghana. We never share your details without this tick.</span></label></details>' +
    '<div class="hp" aria-hidden="true"><label for="co-web">Leave blank</label><input id="co-web" name="website" tabindex="-1" autocomplete="off"></div>' +
    '<div class="form-status" role="status" aria-live="polite"></div>' +
    '<button class="btn gold co-pay" type="submit" data-co-pay></button>' +
    '<button class="co-backlink" type="button" data-co-prev>Back to your event</button>' +
    '<p class="reassure c" data-co-note></p>' +
    '<p class="co-help">Questions before you book? Call Asantewaa on <span data-phone></span></p>' +
    "</div></form>" +
    '<div class="co-done" hidden><span class="eyebrow">Almost there</span><h3 data-cd-h></h3><p class="cd-line" data-cd-line></p>' +
    '<div class="cd-card"><span class="cd-when" data-cd-when></span><b class="cd-name" data-cd-name></b><span class="cd-sum" data-co-done></span><span class="cd-valid" data-cd-valid></span></div>' +
    '<ol class="cd-next" data-cd-next></ol>' +
    '<div class="btn-row cd-acts"><a class="btn gold" data-cd-cal href="#">Add to calendar</a><a class="btn emerald" data-cd-share href="#" target="_blank" rel="noopener">Tell your people</a></div>' +
    '<div class="co-x-sell" data-co-xsell></div><button class="co-backlink" type="button" data-co-close>Close</button></div></div>';
  document.body.appendChild(co);
  co.querySelectorAll("[data-phone]").forEach(function (el) {
    el.textContent = SITE_CONFIG.contactPhone;
  });
  var cur = "gala",
    qty = 2,
    lastFocus = null;
  var form = co.querySelector(".co-form"),
    done = co.querySelector(".co-done");
  var remember = function (on) {
    try {
      if (on) localStorage.setItem("ga70-basket", JSON.stringify({ day: cur, qty: qty, t: Date.now() }));
      else localStorage.removeItem("ga70-basket");
    } catch {}
  };
  var payload = function () {
    var d = DAYS[cur];
    var q = quote(cur, qty);
    return { day: cur, name: d.name, price: q.unit, qty: qty, value: q.total };
  };
  var step = function (n) {
    co.querySelectorAll(".co-step").forEach(function (el) {
      el.hidden = el.getAttribute("data-step") !== String(n);
    });
    co.querySelectorAll("[data-co-s]").forEach(function (li) {
      var k = +li.getAttribute("data-co-s");
      li.className = k < n ? "done" : k === n ? "on" : "";
    });
    co.querySelector(".co-tabs").hidden = n !== 1;
    var f = co.querySelector(n === 1 ? "[data-co-inc]" : "#co-first");
    if (f)
      setTimeout(function () {
        f.focus();
      }, 60);
    if (n === 2) {
      remember(true);
      track("begin_checkout", payload());
    }
  };
  var preSale = function () {
    var t = Date.parse(SITE_CONFIG.salesOpen || "");
    var anyPay =
      SITE_CONFIG.pay &&
      Object.keys(SITE_CONFIG.pay).some(function (k) {
        return SITE_CONFIG.pay[k];
      });
    return !anyPay && !isNaN(t) && Date.now() < t;
  };
  var render = function () {
    var d = DAYS[cur],
      link = SITE_CONFIG.pay && SITE_CONFIG.pay[cur],
      q = quote(cur, qty),
      total = q.total;
    co.className = "co co-" + d.tone;
    co.querySelectorAll("[data-co-day]").forEach(function (b) {
      var on = b.getAttribute("data-co-day") === cur;
      b.setAttribute("aria-selected", on ? "true" : "false");
      b.classList.toggle("on", on);
    });
    co.querySelector("[data-co-when]").textContent = d.when;
    co.querySelector("[data-co-name]").textContent = d.name;
    co.querySelector("[data-co-line]").textContent = d.line;
    co.querySelector("[data-co-valid]").textContent = d.valid || "";
    co.querySelector("[data-co-sun]").hidden = !(cur === "sunday" || cur === "weekend");
    co.querySelector("[data-co-presets]").innerHTML = d.presets
      .map(function (p) {
        return (
          '<button type="button" data-q="' +
          p[0] +
          '"' +
          (p[0] === qty ? ' class="on"' : "") +
          ">" +
          p[1] +
          (p[0] >= 5
            ? "<small>" + quote(cur, p[0]).working + " = " + fmt(quote(cur, p[0]).total) + "</small>"
            : "") +
          "</button>"
        );
      })
      .join("");
    co.querySelector("[data-co-n]").textContent = qty;
    var pre = preSale();
    co.querySelector("[data-co-pre]").hidden = !pre;
    co.querySelector("[data-co-next]").textContent = "Continue";
    co.querySelector("[data-co-total]").innerHTML =
      q.working + " = <b>" + fmt(total) + "</b>" + (q.offer ? "<small>" + q.offer + "</small>" : "") + (q.hint ? "<small>" + q.hint + "</small>" : "");
    co.querySelector("[data-co-sum]").innerHTML =
      "<b>" + d.name + "</b> · " + d.when + " · " + q.working + " = <b>" + fmt(total) + "</b>";
    var bk = (form.querySelector('input[name="payBy"]:checked') || {}).value === "bank";
    if (bk) link = "";
    co.querySelector("[data-co-pay]").textContent = link
      ? "Pay " + fmt(total) + " securely"
      : bk
        ? "Book and pay " + fmt(total) + " by bank transfer"
        : "Book and pay " + fmt(total);
    var cl = co.querySelector("[data-co-cardlbl]");
    if (cl) cl.textContent = link ? "Card, Apple Pay or Google Pay" : "Card, by secure payment link";
    co.querySelector("[data-co-note]").textContent = link
      ? "Card, Apple Pay or Google Pay · Golden tickets by email · Transferable" +
        (SITE_CONFIG.instalments ? " · Pay in instalments available" : "")
      : bk
        ? "Pay within 24 hours to confirm. Unpaid bookings are released"
        : "We send your secure card payment link by email the same day. Your places are confirmed when paid";
  };
  var open = function (key, q) {
    if (key === "pick") key = cur;
    if (!DAYS[key]) return;
    cur = key;
    qty = q ? Math.max(1, Math.min(20, +q)) : 2;
    lastFocus = document.activeElement;
    form.hidden = false;
    done.hidden = true;
    co.querySelector(".co-panel").classList.remove("is-done");
    co.hidden = false;
    var inv = form.querySelector("#co-inv"),
      refName = window.__ga70ref ? window.__ga70ref() : "";
    if (inv && !inv.value && refName) inv.value = refName.replace(/-/g, " ");
    render();
    step(1);
    document.documentElement.classList.add("co-open");
    if (window.__ga70lenis) window.__ga70lenis.stop();
    track("view_item", payload());
    var pill = document.querySelector(".resume");
    if (pill) pill.hidden = true;
  };
  window.__ga70open = open;
  var close = function () {
    co.hidden = true;
    document.documentElement.classList.remove("co-open");
    if (window.__ga70lenis) window.__ga70lenis.start();
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    showResume();
  };
  co.addEventListener("click", function (e) {
    if (e.target.closest("[data-co-close]")) {
      close();
      return;
    }
    var t = e.target.closest("[data-co-day]");
    if (t) {
      cur = t.getAttribute("data-co-day");
      render();
      return;
    }
    var ti = e.target.closest("[data-tier]");
    if (ti) {
      cur = ti.getAttribute("data-tier");
      render();
      return;
    }
    var q = e.target.closest("[data-q]");
    if (q) {
      qty = +q.getAttribute("data-q");
      render();
    }
  });
  co.addEventListener("change", function (e) {
    if (e.target.matches("[data-co-gift]")) co.querySelector("[data-co-giftf]").hidden = !e.target.checked;
    if (e.target.matches("[data-co-co]")) co.querySelector("[data-co-cof]").hidden = !e.target.checked;
    if (e.target.name === "payBy") render();
  });
  document.addEventListener("keydown", function (e) {
    if (!co.hidden && e.key === "Escape") close();
  });
  co.querySelector("[data-co-dec]").addEventListener("click", function () {
    if (qty > 1) {
      qty--;
      render();
    }
  });
  co.querySelector("[data-co-inc]").addEventListener("click", function () {
    if (qty < 20) {
      qty++;
      render();
    }
  });
  co.querySelector("[data-co-next]").addEventListener("click", function () {
    if (preSale()) {
      track("join_priority_from_book", payload());
      var reg = document.querySelector("#register form");
      var x = co.querySelector("[data-co-close]");
      if (x) x.click();
      if (reg) {
        location.hash = "register";
        var f = reg.querySelector("input:not([type=hidden]):not([tabindex='-1'])");
        if (f)
          setTimeout(function () {
            f.focus();
          }, 300);
      } else location.href = "index.html#register";
      return;
    }
    step(2);
  });
  co.querySelector("[data-co-prev]").addEventListener("click", function () {
    step(1);
  });
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-buy], [data-pay]");
    if (!t || co.contains(t)) return;
    e.preventDefault();
    open(t.getAttribute("data-buy") || t.getAttribute("data-pay"), t.getAttribute("data-qty"));
  });
  document.addEventListener("keydown", function (e) {
    var t = e.target.closest && e.target.closest("[data-buy]");
    if (t && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      open(t.getAttribute("data-buy"));
    }
  });

  /* Finish your booking: a quiet reminder of an unfinished basket, for 7 days */
  var showResume = function () {
    var b = null;
    try {
      b = JSON.parse(localStorage.getItem("ga70-basket") || "null");
    } catch {}
    var old = document.querySelector(".resume");
    if (old) old.remove();
    if (!b || !DAYS[b.day] || Date.now() - b.t > 7 * 86400000) return;
    var dismissed = false;
    try {
      dismissed = sessionStorage.getItem("ga70-resume-x") === "1";
    } catch {}
    var go = function (e) {
      if (e) e.preventDefault();
      open(b.day, b.qty);
      setTimeout(function () {
        step(2);
      }, 50);
    };
    /* Phones: the bottom bar becomes the reminder, so nothing extra floats over the page */
    var bar = document.querySelector(".mobile-cta .btn");
    if (bar && !bar.dataset.orig) bar.dataset.orig = bar.textContent;
    if (bar) {
      bar.textContent =
        "Finish your booking · " +
        b.qty +
        " x " +
        (DAYS[b.day].tab);
      bar.classList.add("is-resume");
      bar.addEventListener(
        "click",
        function (e) {
          if (bar.classList.contains("is-resume") && matchMedia("(max-width: 700px)").matches) {
            e.stopPropagation();
            go(e);
          }
        },
        true,
      );
    }
    if (dismissed) return;
    var p = document.createElement("div");
    p.className = "resume";
    p.innerHTML =
      '<button type="button" class="resume-go"><span>Finish your booking</span><b>' +
      b.qty +
      " x " +
      DAYS[b.day].name +
      '</b></button><button type="button" class="resume-x" aria-label="Hide this reminder">\u00d7</button>';
    p.querySelector(".resume-go").addEventListener("click", function () {
      go();
    });
    p.querySelector(".resume-x").addEventListener("click", function () {
      p.remove();
      try {
        sessionStorage.setItem("ga70-resume-x", "1");
      } catch {}
    });
    document.body.appendChild(p);
  };
  showResume();

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var st = form.querySelector(".form-status");
    st.className = "form-status";
    st.textContent = "";
    var req = form.querySelectorAll('[data-step="2"] [required]');
    for (var r = 0; r < req.length; r++) {
      if (!req[r].checkValidity()) {
        req[r].reportValidity();
        return;
      }
    }
    var d = DAYS[cur],
      bank = (form.querySelector('input[name="payBy"]:checked') || {}).value === "bank";
    var link = !bank && SITE_CONFIG.pay && SITE_CONFIG.pay[cur],
      q = quote(cur, qty),
      total = q.total;
    var data = {
      type: "checkout",
      source: "checkout",
      day: cur,
      quantity: qty,
      unitPrice: q.unit,
      value: total,
      offer: q.offer,
      interests: [d.field],
      partySize: String(qty),
      basket: qty + " x " + d.name + (q.offer ? ", " + q.offer.toLowerCase() : "") + ": " + q.working + " = " + fmt(total),
      page: location.pathname,
    };
    new FormData(form).forEach(function (v, k) {
      data[k] = v;
    });
    data.termsVersion = "Ticket terms, 15 November 2026";
    data.termsAgreedAt = new Date().toISOString();
    data.finalSaleAgreed = data.finalSale ? "yes" : "no";
    if (!(cur === "sunday" || cur === "weekend")) {
      delete data.sitting;
      delete data.masterclass;
      delete data.motherName;
    }
    if (bank) data.interests.push("Bank transfer");
    if (data.hotel === "yes") data.interests.push("Accommodation");
    if (data.gift === "yes") data.interests.push("Gift");
    if (data.company === "yes") data.interests.push("Company booking");
    var src = window.__ga70src ? window.__ga70src() : {};
    for (var sk in src) data[sk] = src[sk];
    var payUrl = link
      ? link +
        (link.indexOf("?") > -1 ? "&" : "?") +
        "quantity=" +
        qty +
        "&email=" +
        encodeURIComponent(data.email) +
        "&phone=" +
        encodeURIComponent(data.phone || "") +
        "&first_name=" +
        encodeURIComponent(data.firstName) +
        "&last_name=" +
        encodeURIComponent(data.lastName || "")
      : "";
    data.checkoutUrl = payUrl;
    var btn = form.querySelector("[data-co-pay]"),
      label = btn.textContent;
    btn.disabled = true;
    btn.textContent = link ? "Opening secure checkout" : "Reserving";
    var go = function () {
      track("lead", payload());
      try {
        sessionStorage.setItem("ga70-order", JSON.stringify(payload()));
      } catch {}
      remember(false);
      if (payUrl) {
        step(3);
        location.href = payUrl;
        return;
      }
      form.hidden = true;
      done.hidden = false;
      co.querySelector(".co-panel").classList.add("is-done");
      co.querySelector(".co-panel").scrollTop = 0;
      co.querySelectorAll("[data-co-s]").forEach(function (li) {
        li.className = "done";
      });
      var who = (data.firstName || "").replace(/[<>&"]/g, "");
      var SEE = {
        gala: "The drums will be waiting at the door. Come as royalty, and we will see you in the hall.",
        sunday: "The tea will be poured and her name will be read. We will see you there.",
        ghanaday: "Seventy years to the day, and you will be in the room. We will see you there.",
        weekend: "Three days, and we will see you at every one of them.",
      };
      done.querySelector("[data-cd-h]").textContent =
        "Medaase" + (who ? ", " + who : "") + ". Your booking is received.";
      done.querySelector("[data-cd-line]").textContent = SEE[cur] || SEE.gala;
      done.querySelector("[data-cd-when]").textContent = d.when;
      done.querySelector("[data-cd-name]").textContent = d.name;
      done.querySelector("[data-cd-valid]").textContent = d.valid || "";
      done.querySelector("[data-co-done]").textContent =
        (qty === 1 ? "1 guest" : qty + " guests") + ": " + q.working + " = " + fmt(total);
      done.querySelector("[data-cd-next]").innerHTML =
        "<li>A confirmation of this booking follows by email.</li>" +
        (bank
          ? "<li>Our bank details and your booking reference follow by email. Pay within 24 hours, or the booking is released.</li>"
          : "<li>Your secure card payment link follows by email the same day. Your places are confirmed when paid.</li>") +
        "<li>Your golden ticket, with your QR code for the door, arrives once paid.</li>";
      var cal = done.querySelector("[data-cd-cal]");
      if (d.cal) {
        cal.href = d.cal;
        cal.hidden = false;
      } else cal.hidden = true;
      var shareTxt =
        "I am going to " +
        d.name +
        ", " +
        d.when.split(" · ")[0] +
        ", London. Come with me: " +
        location.origin +
        "/" +
        ({
          gala: "royal-gala",
          ghanaday: "ghana-day",
          sunday: "women-of-the-motherland",
        }[cur] || "");
      done.querySelector("[data-cd-share]").href = "https://wa.me/?text=" + encodeURIComponent(shareTxt);
      var others = ["gala", "ghanaday", "sunday"].filter(function (k) {
        return k !== cur && cur !== "weekend";
      });
      done.querySelector("[data-co-xsell]").innerHTML = others.length
        ? '<span class="eyebrow">While you are with us, make it a weekend</span>' +
          others
            .map(function (k) {
              return (
                '<button type="button" class="xs" data-xs="' +
                k +
                '"><b>' +
                DAYS[k].name +
                "</b><span>" +
                DAYS[k].when +
                " · " +
                fmt(DAYS[k].price) +
                "</span></button>"
              );
            })
            .join("")
        : "";
      document.dispatchEvent(new Event("ga70:registered"));
    };
    var preview =
      !/^https?:$/.test(location.protocol) ||
      /claude|localhost|127\.0\.0\.1|usercontent/.test(location.hostname);
    var send = function () {
      return fetch(SITE_CONFIG.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }).then(function (r) {
        if (!r.ok) throw new Error("x");
      });
    };
    send()
      .catch(function () {
        return new Promise(function (ok) {
          setTimeout(ok, 1200);
        }).then(send);
      })
      .then(go)
      .catch(function () {
        if (link || preview) {
          go();
          return;
        }
        st.className = "form-status err";
        st.textContent =
          "Your booking has not gone through. Please tap again in a moment, or call Asantewaa on " +
          SITE_CONFIG.contactPhone +
          " and we will book you by phone.";
      })
      .finally(function () {
        btn.disabled = false;
        btn.textContent = label;
      });
  });
  done.addEventListener("click", function (e) {
    var x = e.target.closest("[data-xs]");
    if (x) {
      var keep = {
        f: form.querySelector("#co-first").value,
        l: form.querySelector("#co-last").value,
        m: form.querySelector("#co-email").value,
        p: form.querySelector("#co-tel").value,
      };
      open(x.getAttribute("data-xs"), qty);
      form.querySelector("#co-first").value = keep.f;
      form.querySelector("#co-last").value = keep.l;
      form.querySelector("#co-email").value = keep.m;
      form.querySelector("#co-tel").value = keep.p;
    }
  });

  /* Thank you page: confirm, measure the sale once, offer the other days */
  var ty = document.querySelector("[data-thanks]");
  if (ty) {
    var qp = new URLSearchParams(location.search),
      o = null;
    try {
      o = JSON.parse(sessionStorage.getItem("ga70-order") || "null");
    } catch {}
    var day = qp.get("day") || (o && o.day),
      tyQty = +(qp.get("qty") || (o && o.qty) || 0);
    if (DAYS[day]) {
      var dd2 = DAYS[day],
        tq = tyQty ? window.__ga70quote(day, tyQty) : null,
        val = +(qp.get("value") || (tq ? tq.total : 0));
      ty.querySelector("[data-ty-what]").textContent =
        (tyQty ? tyQty + " x " : "") + dd2.name + (tq ? ": " + tq.working + " = " + fmt(val) : "");
      var tv = ty.querySelector("[data-ty-valid]");
      if (tv && dd2.valid) {
        tv.textContent = dd2.valid;
        tv.hidden = false;
      }
      var bought = null;
      try {
        bought = sessionStorage.getItem("ga70-purchased");
      } catch {}
      if (!bought) {
        track("purchase", { day: day, name: dd2.name, price: tq ? tq.unit : dd2.price, qty: tyQty, value: val });
        try {
          sessionStorage.setItem("ga70-purchased", "1");
        } catch {}
      }
      document.querySelectorAll("[data-ty-x]").forEach(function (c) {
        if (
          c.getAttribute("data-ty-x") === day ||
          day === "weekend"
        )
          c.hidden = true;
      });
    }
  }

  /* Copy buttons on the press kit */
  document.querySelectorAll("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var el = document.querySelector(b.getAttribute("data-copy"));
      if (!el) return;
      var band = b.closest("section"),
        ok = band && band.querySelector("[data-copy-ok]");
      var say = function (t) {
        if (ok) {
          ok.textContent = t;
          setTimeout(function () {
            ok.textContent = "";
          }, 4000);
        }
      };
      var sel = function () {
        var r = document.createRange();
        r.selectNodeContents(el);
        var s = window.getSelection();
        s.removeAllRanges();
        s.addRange(r);
        say("Selected. Copy it with your keyboard.");
      };
      try {
        navigator.clipboard.writeText(el.innerText.trim()).then(function () {
          say("Copied.");
        }, sel);
      } catch {
        sel();
      }
    });
  });
  /* ===== Save the date: calendar, invitation and sharing ===== */
  document.querySelectorAll("[data-sd]").forEach(function (sec) {
    var d;
    try {
      d = JSON.parse(sec.getAttribute("data-sd"));
    } catch {
      return;
    }
    var link = function (src) {
      return d.url + "?utm_source=" + src + "&utm_medium=share&utm_campaign=save_the_date";
    };
    var msg = function (src) {
      return d.share + ".\n\nBook your golden ticket: " + link(src);
    };
    var box = sec.querySelector("[data-sd-msg]"),
      ok = sec.querySelector("[data-sd-ok]");
    var say = function (t) {
      if (ok) {
        ok.textContent = t;
        setTimeout(function () {
          ok.textContent = "";
        }, 4000);
      }
    };
    if (box) box.value = msg("copy");
    var sh = sec.querySelector("[data-sd-share]");
    if (sh)
      sh.addEventListener("click", function () {
        var t = msg("share");
        var copy = function () {
          var fallback = function () {
            if (box) {
              box.hidden = false;
              box.focus();
              box.select();
            }
            say("Selected. Copy it and send it on.");
          };
          try {
            navigator.clipboard.writeText(t).then(function () {
              say("Copied. Paste it into WhatsApp, email or any chat.");
            }, fallback);
          } catch {
            fallback();
          }
        };
        if (navigator.share) {
          navigator.share({ title: d.title, text: d.share + ".", url: link("native") }).then(
            function () {
              track("share", { day: d.k, method: "native" });
            },
            function (err) {
              if (!err || err.name !== "AbortError") copy();
            },
          );
        } else {
          copy();
          track("share", { day: d.k, method: "copy" });
        }
      });
    var ics = sec.querySelector("[data-sd-ics]");
    if (ics)
      ics.addEventListener("click", function (e) {
        /* Build the calendar file on the device, so it works on any host */
        try {
          var esc = function (t) {
            return String(t)
              .replace(/\\/g, "\\\\")
              .replace(/;/g, ";")
              .replace(/,/g, "\\,")
              .replace(/\n/g, "\\n");
          };
          var lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Ghana at 70 UK//Save the date//EN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            "UID:" + d.k + "-2027@ghanaat70",
            "DTSTAMP:20261116T120000Z",
            "DTSTART:" + d.s,
            "DTEND:" + d.e,
            "SUMMARY:" + esc(d.title),
            "LOCATION:" + esc(d.loc),
            "DESCRIPTION:" + esc(d.body),
            "URL:" + d.url,
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:" + esc(d.title + " is tomorrow"),
            "TRIGGER:-P1D",
            "END:VALARM",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:" + esc(d.title + ". Nearest Tube: Bank"),
            "TRIGGER:-PT2H",
            "END:VALARM",
            "END:VEVENT",
            "END:VCALENDAR",
          ];
          var blob = new Blob([lines.join("\r\n")], { type: "text/calendar;charset=utf-8" });
          var a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = d.title.replace(/[^A-Za-z0-9]+/g, "-") + ".ics";
          document.body.appendChild(a);
          a.click();
          a.remove();
          e.preventDefault();
          say("Calendar file ready. Open it to add the event.");
        } catch {
          /* fall back to the hosted file */
        }
        track("add_to_calendar", { day: d.k, method: "apple" });
      });
  });
  /* Thank you page: show the save the date card for the day booked */
  (function () {
    var ty = document.querySelector("[data-thanks]");
    if (!ty) return;
    var qp = new URLSearchParams(location.search),
      o = null;
    try {
      o = JSON.parse(sessionStorage.getItem("ga70-order") || "null");
    } catch {}
    var day = qp.get("day") || (o && o.day) || "gala";
    var ids = day === "weekend" ? ["gala", "ghanaday", "sunday"] : [day];
    ids.forEach(function (k) {
      var s = document.getElementById("save-date-" + k);
      if (s) s.hidden = false;
    });
    var cl = ty.querySelector("[data-ty-cal]");
    if (cl) cl.href = "#save-date-" + ids[0];
  })();
  /* ===== Proof film: plays muted when seen, sound on request ===== */
  document.querySelectorAll("[data-film]").forEach(function (f) {
    var v = f.querySelector("video"),
      b = f.querySelector("[data-film-sound]");
    var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
    if ("IntersectionObserver" in window && !reduce) {
      new IntersectionObserver(
        function (es) {
          es.forEach(function (e) {
            if (e.isIntersecting) {
              var p = v.play();
              if (p && p.catch) p.catch(function () {});
            } else v.pause();
          });
        },
        { threshold: 0.35 },
      ).observe(f);
    } else v.controls = true;
    b.addEventListener("click", function () {
      v.muted = !v.muted;
      if (!v.muted) {
        v.currentTime = 0;
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
      }
      b.textContent = v.muted ? "Sound on" : "Sound off";
      b.setAttribute("aria-pressed", v.muted ? "false" : "true");
    });
  });

  /* ===== Exhibitor carousel: seven worlds, calm, swipeable ===== */
  document.querySelectorAll("[data-xc]").forEach(function (xc) {
    var track = xc.querySelector("[data-xc-track]"),
      slides = [].slice.call(track.children),
      tabs = [].slice.call(xc.querySelectorAll("[data-xc-go]")),
      bar = xc.querySelector("[data-xc-bar]"),
      cur = 0;
    var go = function (i, smooth) {
      i = (i + slides.length) % slides.length;
      mark(i);
      track.scrollTo({
        left: track.scrollLeft + slides[i].getBoundingClientRect().left - track.getBoundingClientRect().left,
        behavior: smooth === false ? "auto" : "smooth",
      });
    };
    var mark = function (i) {
      cur = i;
      tabs.forEach(function (t, k) {
        t.classList.toggle("on", k === i);
        t.setAttribute("aria-selected", k === i ? "true" : "false");
      });
      if (bar) bar.style.width = ((i + 1) / slides.length) * 100 + "%";
      var at = tabs[i];
      if (at && at.parentNode.scrollTo)
        at.parentNode.scrollTo({ left: at.offsetLeft - 24, behavior: "smooth" });
    };
    var t0 = null;
    track.addEventListener(
      "scroll",
      function () {
        clearTimeout(t0);
        t0 = setTimeout(function () {
          var w = track.clientWidth,
            i = Math.round(track.scrollLeft / w);
          if (i !== cur) mark(Math.max(0, Math.min(slides.length - 1, i)));
        }, 60);
      },
      { passive: true },
    );
    tabs.forEach(function (t) {
      t.addEventListener("click", function () {
        go(+t.getAttribute("data-xc-go"));
      });
    });
    xc.querySelector("[data-xc-prev]").addEventListener("click", function () {
      go(cur - 1);
    });
    xc.querySelector("[data-xc-next]").addEventListener("click", function () {
      go(cur + 1);
    });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") {
        e.preventDefault();
        go(cur + 1);
      }
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        go(cur - 1);
      }
    });
    mark(0);
    /* autoplay where asked for, paused while the guest is reading or touching */
    var auto = +xc.getAttribute("data-xc-auto") || 0,
      hold = false;
    if (auto && !(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches)) {
      ["mouseenter", "focusin", "touchstart"].forEach(function (ev) {
        xc.addEventListener(
          ev,
          function () {
            hold = true;
          },
          { passive: true },
        );
      });
      ["mouseleave", "focusout"].forEach(function (ev) {
        xc.addEventListener(ev, function () {
          hold = false;
        });
      });
      setInterval(function () {
        if (!hold && !document.hidden) {
          var r = xc.getBoundingClientRect();
          if (r.bottom > 0 && r.top < innerHeight) go(cur + 1);
        }
      }, auto);
    }
    /* a link to a slide (for example #saturday) opens that slide */
    var bySlide = function (id) {
      var k = slides.findIndex(function (sl) {
        return sl.id === id;
      });
      if (k > -1) {
        go(k, false);
        var y = xc.getBoundingClientRect().top + window.pageYOffset - 110;
        if (window.__ga70lenis) window.__ga70lenis.scrollTo(y);
        else window.scrollTo({ top: y, behavior: "smooth" });
        return true;
      }
      return false;
    };
    document.addEventListener("click", function (e) {
      var a = e.target.closest('a[href^="#"]');
      if (a && bySlide(a.getAttribute("href").slice(1))) e.preventDefault();
    });
    if (location.hash)
      setTimeout(function () {
        bySlide(location.hash.slice(1));
      }, 300);
  });

  /* ===== Your royal name: Akan day names, drawn as a shareable invitation. Nothing leaves the device ===== */
  var rn = document.querySelector("[data-rn]");
  if (rn) {
    var AKAN = [
      ["Kwasi", "Akosua", "Sunday"],
      ["Kwadwo", "Adwoa", "Monday"],
      ["Kwabena", "Abena", "Tuesday"],
      ["Kwaku", "Akua", "Wednesday"],
      ["Yaw", "Yaa", "Thursday"],
      ["Kofi", "Afua", "Friday"],
      ["Kwame", "Ama", "Saturday"],
    ];
    var outBox = document.querySelector("[data-rn-out]"),
      cv = outBox.querySelector("canvas"),
      blobUrl = "";
    /* Live preview in the shape of Ghana */
    var MEAN = [
      "The day of the leader. Born to guide.",
      "The day of peace. The calm in every storm.",
      "The day of compassion. Deep as the ocean.",
      "The day of the champion. Wise as Ananse.",
      "The day of courage. Strong as the earth.",
      "The day of the explorer. Restless and bold.",
      "The day of wisdom. The old soul of the family.",
    ];
    var pT = document.querySelector("[data-rnp-t]"),
      pN = document.querySelector("[data-rnp-n]"),
      pB = document.querySelector("[data-rnp-b]");
    var pF = document.querySelector("[data-rnp-f]");
    var rnDay = rn.querySelector("#rn-dd"),
      mm = rn.querySelector("#rn-mm"),
      yy = rn.querySelector("#rn-yy"),
      chips = [].slice.call(rn.querySelectorAll("[data-rn-day]"));
    var rv = rn.querySelector("[data-rn-reveal]"),
      err = rn.querySelector("[data-rn-err]"),
      picked = null,
      lastIdx = null;
    /* The weekday from the three selects, null when incomplete, -1 when the date does not exist */
    function fromDate() {
      if (!rnDay.value || !mm.value || !yy.value) return null;
      var y = +yy.value,
        m = +mm.value - 1,
        d = +rnDay.value,
        dt = new Date(Date.UTC(y, m, d));
      return dt.getUTCMonth() === m ? dt.getUTCDay() : -1;
    }
    function dayIdx() {
      var f = fromDate();
      return f !== null && f > -1 ? f : picked;
    }
    function queen() {
      return (rn.querySelector('input[name="k"]:checked') || {}).value === "queen";
    }
    function livePreview() {
      var f = rn.querySelector("#rn-name").value.trim().split(/\s+/)[0] || "",
        q = queen(),
        fd = fromDate(),
        idx = dayIdx(),
        has = idx !== null && idx !== undefined;
      err.textContent = fd === -1 ? "That date does not exist. Check the day and the month." : "";
      chips.forEach(function (c) {
        var on = has && +c.getAttribute("data-rn-day") === idx;
        c.setAttribute("aria-pressed", on ? "true" : "false");
      });
      var st = [f ? 1 : 0, has ? 1 : 0, has ? 1 : 0];
      [].forEach.call(rn.querySelectorAll("[data-rn-step]"), function (li, i) {
        li.classList.toggle("on", !!st[i]);
      });
      var show = has ? idx : q ? 4 : 6,
        dn = AKAN[show][q ? 1 : 0];
      if (has) {
        rv.hidden = false;
        rn.querySelector("[data-rn-rk]").textContent = "Born on a " + AKAN[idx][2] + ", you are";
        rn.querySelector("[data-rn-rn]").textContent = dn;
        rn.querySelector("[data-rn-rm]").textContent = MEAN[idx];
        if (idx !== lastIdx) {
          rv.classList.remove("pop");
          void rv.offsetWidth;
          rv.classList.add("pop");
          lastIdx = idx;
        }
      } else rv.hidden = true;
      if (!pT) return;
      if (!f && !has) f = q ? "Asantewaa" : "";
      if (f && f.toLowerCase() === dn.toLowerCase()) f = "";
      pT.textContent = q ? "Her Royal Highness" : "His Royal Highness";
      pN.textContent = "Nana " + dn;
      if (pF) {
        pF.textContent = f ? f.charAt(0).toUpperCase() + f.slice(1) : "";
        pF.hidden = !f;
      }
      pB.textContent = "born on a " + AKAN[show][2];
    }
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        picked = +c.getAttribute("data-rn-day");
        rnDay.value = mm.value = yy.value = "";
        livePreview();
      });
    });
    [rnDay, mm, yy].forEach(function (el) {
      el.addEventListener("change", function () {
        if (fromDate() !== null) picked = null;
      });
    });
    rn.addEventListener("input", livePreview);
    rn.addEventListener("change", livePreview);

    var star = function (c, x, y, r, fill, stroke) {
      c.beginPath();
      for (var i = 0; i < 10; i++) {
        var a = -Math.PI / 2 + (i * Math.PI) / 5,
          rr = i % 2 ? r * 0.4 : r;
        c.lineTo(x + rr * Math.cos(a), y + rr * Math.sin(a));
      }
      c.closePath();
      if (fill) {
        c.fillStyle = fill;
        c.fill();
      }
      if (stroke) {
        c.strokeStyle = stroke;
        c.lineWidth = 3;
        c.stroke();
      }
    };
    var fit = function (c, text, max, size, font) {
      var s2 = size;
      do {
        c.font = font.replace("{s}", s2);
        s2 -= 4;
      } while (c.measureText(text).width > max && s2 > 30);
    };
    var GH = (cv.getAttribute("data-gh") || "")
      .split(/\s+/)
      .filter(Boolean)
      .map(function (p) {
        var a = p.split(",");
        return [+a[0], +a[1]];
      });
    var ghPath = function (c, x, y, w, h) {
      c.beginPath();
      GH.forEach(function (p, i) {
        var px = x + p[0] * w,
          py = y + p[1] * h;
        if (i) c.lineTo(px, py);
        else c.moveTo(px, py);
      });
      c.closePath();
    };
    var draw = function (first, day, queen) {
      var c = cv.getContext("2d"),
        W = cv.width,
        H = cv.height,
        nm = AKAN[day],
        dn = queen ? nm[1] : nm[0];
      if (first && first.toLowerCase() === dn.toLowerCase()) first = "";
      var g = c.createRadialGradient(W / 2, H * 0.35, 80, W / 2, H * 0.5, H * 0.85);
      g.addColorStop(0, "#0F4A35");
      g.addColorStop(1, "#04190F");
      c.fillStyle = g;
      c.fillRect(0, 0, W, H);
      var foil = c.createLinearGradient(0, 0, W, H);
      foil.addColorStop(0, "#A8781F");
      foil.addColorStop(0.45, "#F6DE95");
      foil.addColorStop(0.7, "#C9962E");
      foil.addColorStop(1, "#8C6416");
      var mh = 1170,
        mw = (mh * 279) / 397.5,
        mx = (W - mw) / 2,
        my = 60;
      var ink = "#0B0A08",
        brown = "#8A6A1C",
        green = "#0B3D2C";
      if (GH.length > 10) {
        c.save();
        c.shadowColor = "rgba(0,0,0,.55)";
        c.shadowBlur = 50;
        c.shadowOffsetY = 26;
        ghPath(c, mx, my, mw, mh);
        var pg = c.createRadialGradient(
          mx + mw * 0.4,
          my + mh * 0.25,
          30,
          mx + mw * 0.5,
          my + mh * 0.5,
          mh * 0.75,
        );
        pg.addColorStop(0, "#FFFDF7");
        pg.addColorStop(0.6, "#F8F0DE");
        pg.addColorStop(1, "#EADBB8");
        c.fillStyle = pg;
        c.fill();
        c.restore();
        ghPath(c, mx, my, mw, mh);
        c.strokeStyle = foil;
        c.lineWidth = 8;
        c.stroke();
        ghPath(c, mx, my, mw, mh);
        c.strokeStyle = "rgba(255,248,225,.9)";
        c.lineWidth = 1.5;
        c.stroke();
      } else {
        c.fillStyle = "#F8F0DE";
        c.fillRect(60, 60, W - 120, H - 120);
        c.strokeStyle = foil;
        c.lineWidth = 6;
        c.strokeRect(60, 60, W - 120, H - 120);
      }
      var cx = mx + mw * 0.455,
        mt = 410;
      c.textAlign = "center";
      c.fillStyle = "#5B4A1E";
      c.font = "500 20px Jost, Arial, sans-serif";
      c.fillText("G H A N A   A T   7 0", cx, 318);
      star(c, cx, 372, 22, "#B8891F", "#B8891F");
      c.fillStyle = brown;
      c.font = "italic 400 44px 'Cormorant Garamond', Georgia, serif";
      c.fillText(queen ? "Her Royal Highness" : "His Royal Highness", cx, 470);
      c.fillStyle = ink;
      fit(c, "Nana " + dn, mt, 112, "500 {s}px 'Cormorant Garamond', Georgia, serif");
      c.fillText("Nana " + dn, cx, 590);
      var y = 590;
      if (first) {
        y += 92;
        fit(c, first, mt, 84, "italic 500 {s}px 'Cormorant Garamond', Georgia, serif");
        c.fillText(first, cx, y);
      }
      c.fillStyle = "#5B4A1E";
      c.font = "500 22px Jost, Arial, sans-serif";
      c.fillText(("born on a " + nm[2]).toUpperCase().split("").join(" "), cx, y + 66);
      c.strokeStyle = "#C9A14A";
      c.lineWidth = 1.5;
      c.beginPath();
      c.moveTo(cx - 110, y + 102);
      c.lineTo(cx + 110, y + 102);
      c.stroke();
      c.fillStyle = brown;
      c.font = "italic 400 40px 'Cormorant Garamond', Georgia, serif";
      c.fillText("is invited to", cx, y + 164);
      c.fillStyle = green;
      fit(c, "The Royal Jubilee Gala", 460, 56, "600 {s}px 'Cormorant Garamond', Georgia, serif");
      c.fillText("The Royal Jubilee Gala", cx, y + 238);
      c.fillStyle = "#4A3A14";
      c.font = "500 21px Jost, Arial, sans-serif";
      c.fillText("FRIDAY 5 MARCH 2027", cx, y + 290);
      c.fillText("BANKING HALL  ·  LONDON", cx, y + 322);
      var sx = mx + mw * 0.62,
        sy = my + mh * 0.9,
        sr = 42;
      var sg = c.createRadialGradient(sx - 12, sy - 14, 4, sx, sy, sr);
      sg.addColorStop(0, "#C8352B");
      sg.addColorStop(1, "#8E1B15");
      c.save();
      c.shadowColor = "rgba(0,0,0,.4)";
      c.shadowBlur = 16;
      c.shadowOffsetY = 6;
      c.beginPath();
      c.arc(sx, sy, sr, 0, Math.PI * 2);
      c.fillStyle = sg;
      c.fill();
      c.restore();
      c.beginPath();
      c.arc(sx, sy, sr - 5, 0, Math.PI * 2);
      c.strokeStyle = "#D4A62A";
      c.lineWidth = 2.5;
      c.stroke();
      star(c, sx, sy, 20, "#F3D27A", "#F3D27A");
      c.fillStyle = "#D9C68F";
      c.font = "400 22px Jost, Arial, sans-serif";
      c.fillText("What is your royal name?", W / 2, H - 46);
      return dn;
    };
    rn.addEventListener("submit", function (e) {
      e.preventDefault();
      var nmIn = rn.querySelector("#rn-name"),
        day = dayIdx();
      if (fromDate() === -1) {
        err.textContent = "That date does not exist. Check the day and the month.";
        rnDay.focus();
        return;
      }
      if (day === null || day === undefined) {
        err.textContent = "Choose your birthday, or tap the day you were born.";
        rnDay.focus();
        return;
      }
      var first = nmIn.value
        .trim()
        .replace(/[^\p{L}\p{M} '\-]/gu, "")
        .slice(0, 24);
      first = first.charAt(0).toUpperCase() + first.slice(1);
      var queen = (rn.querySelector('input[name="k"]:checked') || {}).value === "queen";
      var go2 = function () {
        var dn = draw(first, day, queen);
        outBox.hidden = false;
        outBox.querySelector("[data-rn-says]").textContent =
          "Born on a " +
          AKAN[day][2] +
          ", you are " +
          dn +
          ". " +
          MEAN[day] +
          " Your royal seat is waiting.";
        outBox.querySelector("[data-rn-share]").href =
          "https://wa.me/?text=" +
          encodeURIComponent(
            "I am Nana " +
              dn +
              (first && first.toLowerCase() !== dn.toLowerCase() ? " " + first : "") +
              ", and I am invited to the Royal Jubilee Gala, Friday 5 March 2027 in London. What is your royal name? " +
              location.origin +
              "/#royal-name",
          );
        if (blobUrl) URL.revokeObjectURL(blobUrl);
        blobUrl = "";
        if (window.__ga70track)
          window.__ga70track("lead", { day: "gala", name: "Royal name", price: 0, qty: 0, value: 0 });
        outBox.scrollIntoView({ behavior: "smooth", block: "center" });
      };
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(go2);
      else go2();
    });
    outBox.querySelector("[data-rn-save]").addEventListener("click", function () {
      cv.toBlob(function (b) {
        if (!b) return;
        var f = null;
        try {
          f = new window.File([b], "my-royal-invitation.png", { type: "image/png" });
        } catch {}
        if (f && navigator.canShare && navigator.canShare({ files: [f] })) {
          navigator.share({ files: [f], title: "My royal invitation" }).catch(function () {});
          return;
        }
        blobUrl = URL.createObjectURL(b);
        var a = document.createElement("a");
        a.href = blobUrl;
        a.download = "my-royal-invitation.png";
        document.body.appendChild(a);
        a.click();
        a.remove();
      }, "image/png");
    });
  }
})();

/* Black star cursor with a gold edge, desktop only */
(function () {
  if (!window.matchMedia || !matchMedia("(pointer: fine)").matches) return;
  var svg = function (fill, size) {
    return (
      'url("data:image/svg+xml,' +
      encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="' +
          size +
          '" height="' +
          size +
          '" viewBox="0 0 100 100"><polygon points="50,6 61,38 95,38 67,58 78,92 50,71 22,92 33,58 5,38 39,38" fill="' +
          fill +
          '" stroke="#D4A62A" stroke-width="7" stroke-linejoin="round"/></svg>',
      ) +
      '") ' +
      size / 2 +
      " " +
      size / 2
    );
  };
  var st = document.createElement("style");
  st.textContent =
    "html,body{cursor:" +
    svg("#0B0A08", 26) +
    ",auto}a,button,[role=button],label,select,summary,[data-pay],[data-buy]{cursor:" +
    svg("#0B0A08", 32) +
    ",pointer}input,textarea{cursor:text}";
  document.head.appendChild(st);
})();

/* Exhibitor form: Gala seats only count when ticked */
(function () {
  var cb = document.querySelector('input[name="galaWanted"]'),
    sel = document.getElementById("ex-gala");
  if (!cb || !sel) return;
  var sync = function () {
    sel.disabled = !cb.checked;
  };
  cb.addEventListener("change", sync);
  sync();
})();

/* Back to the top, one tap */
(function () {
  var b = document.createElement("button");
  b.type = "button";
  b.className = "to-top";
  b.setAttribute("aria-label", "Back to the top");
  b.innerHTML =
    '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  document.body.appendChild(b);
  var show = function () {
    b.classList.toggle("on", window.scrollY > window.innerHeight * 1.2);
  };
  window.addEventListener("scroll", show, { passive: true });
  show();
  b.addEventListener("click", function () {
    if (window.__ga70lenis) window.__ga70lenis.scrollTo(0, { duration: 1.2 });
    else window.scrollTo({ top: 0, behavior: "smooth" });
  });
  /* the logo always returns to the top when you are already on the home page */
  var logo = document.querySelector(
    ".site-header a.brand, .site-header .logo, .site-header a[href='index.html']",
  );
  if (logo)
    logo.addEventListener("click", function (e) {
      var here = (location.pathname.split("/").pop() || "index.html").replace(/\.html$/, "") || "index";
      if (here === "index" || here === "") {
        e.preventDefault();
        b.click();
      }
    });
})();

/* Gallery: filters and lightbox */
(function () {
  var grid = document.querySelector("#gallery");
  if (!grid || !document.querySelector("[data-lb]")) return;
  var items = [].slice.call(grid.querySelectorAll(".gi"));
  var lb = document.querySelector("[data-lb]"),
    img = lb.querySelector("[data-lb-img]"),
    cap = lb.querySelector("[data-lb-cap]"),
    book = lb.querySelector("[data-lb-book]"),
    cur = 0;
  var vis = function () {
    return items
      .filter(function (it) {
        return !it.hidden;
      })
      .map(function (it) {
        return it.querySelector(".gi-btn");
      });
  };
  function show(btn) {
    var src = btn.getAttribute("data-gi-full"),
      alt = btn.querySelector("img").getAttribute("alt");
    img.src = src;
    img.alt = alt;
    cap.textContent = btn.getAttribute("data-gi-cap");
    book.href = btn.getAttribute("data-gi-href");
    book.setAttribute("data-pay", btn.getAttribute("data-gi-day"));
    cur = vis().indexOf(btn);
  }
  function step(d) {
    var v = vis();
    if (!v.length) return;
    show(v[(cur + d + v.length) % v.length]);
  }
  grid.addEventListener("click", function (e) {
    var b = e.target.closest(".gi-btn");
    if (!b) return;
    show(b);
    if (lb.showModal) lb.showModal();
    else lb.setAttribute("open", "");
  });
  lb.querySelector("[data-lb-x]").addEventListener("click", function () {
    lb.close();
  });
  lb.querySelector("[data-lb-prev]").addEventListener("click", function () {
    step(-1);
  });
  lb.querySelector("[data-lb-next]").addEventListener("click", function () {
    step(1);
  });
  lb.addEventListener("click", function (e) {
    if (e.target === lb) lb.close();
  });
  lb.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") step(1);
    if (e.key === "ArrowLeft") step(-1);
  });
  var sx = 0;
  lb.addEventListener(
    "touchstart",
    function (e) {
      sx = e.touches[0].clientX;
    },
    { passive: true },
  );
  lb.addEventListener("touchend", function (e) {
    var dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1);
  });
})();

/* See yourself there: carousel buttons */
(function () {
  var t = document.querySelector("[data-sy-track]");
  if (!t) return;
  [].forEach.call(document.querySelectorAll("[data-sy]"), function (b) {
    b.addEventListener("click", function () {
      var card = t.querySelector(".sy-card");
      var step = card ? card.getBoundingClientRect().width + 14 : 300;
      var d = +b.getAttribute("data-sy"),
        max = t.scrollWidth - t.clientWidth;
      var to = t.scrollLeft + d * step * 2;
      if (d > 0 && t.scrollLeft >= max - 4) to = 0;
      else if (d < 0 && t.scrollLeft <= 4) to = max;
      t.scrollTo({ left: to, behavior: "smooth" });
    });
  });
})();

/* Gallery filmstrips: an eased glide every five seconds, pausing for the guest */
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var ease = function (k) {
    return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
  };
  [].forEach.call(document.querySelectorAll("[data-gfs]"), function (g) {
    var t = g.querySelector("[data-gfs-track]"),
      n = g.querySelector("[data-gfs-n]"),
      p = g.querySelector("[data-gfs-p]"),
      pl = g.querySelector("[data-gfs-play]");
    var lis = [].slice.call(t.children),
      bs = g.querySelectorAll("[data-gfs-d]");
    var cur = 0,
      timer = null,
      anim = null,
      hold = false,
      seen = false,
      stopped = reduce;
    var left = function (li) {
      return li.offsetLeft - t.offsetLeft;
    };
    var max = function () {
      return t.scrollWidth - t.clientWidth;
    };
    function idx() {
      var x = t.scrollLeft,
        i = 0;
      lis.forEach(function (li, k) {
        if (left(li) <= x + 8) i = k;
      });
      if (max() > 0 && x >= max() - 4) i = lis.length - 1;
      return i;
    }
    function upd() {
      var x = t.scrollLeft,
        m = max();
      cur = idx();
      n.textContent = (cur + 1 < 10 ? "0" : "") + (cur + 1);
      p.style.width = (m > 0 ? Math.min(100, ((x + t.clientWidth) / t.scrollWidth) * 100) : 100) + "%";
      lis.forEach(function (li, k) {
        li.classList.toggle("is-on", k === cur);
      });
      if (bs.length) {
        bs[0].disabled = x <= 4;
        bs[1].disabled = x >= m - 4;
      }
    }
    function glide(to, ms) {
      to = Math.max(0, Math.min(to, max()));
      if (anim) cancelAnimationFrame(anim);
      if (reduce) {
        t.scrollLeft = to;
        upd();
        return;
      }
      var from = t.scrollLeft,
        d = to - from,
        t0 = null;
      if (Math.abs(d) < 2) return;
      t.classList.add("is-gliding");
      (function f(ts) {
        if (t0 === null) t0 = ts;
        var k = Math.min(1, (ts - t0) / ms);
        t.scrollLeft = from + d * ease(k);
        if (k < 1) anim = requestAnimationFrame(f);
        else {
          anim = null;
          t.classList.remove("is-gliding");
          upd();
        }
      })(performance.now());
      requestAnimationFrame(function (ts) {
        t0 = ts;
      });
    }
    function next() {
      if (t.scrollLeft >= max() - 4) {
        glide(0, 1800);
        return;
      }
      var x = t.scrollLeft,
        to = null;
      lis.some(function (li) {
        if (left(li) > x + 8) {
          to = left(li);
          return true;
        }
      });
      glide(to === null ? max() : to, 1400);
    }
    function run() {
      clearInterval(timer);
      timer = null;
      if (!stopped && !hold && seen) timer = setInterval(next, 5000);
    }
    function setStop(v) {
      stopped = v;
      pl.setAttribute("aria-pressed", v ? "true" : "false");
      pl.setAttribute("aria-label", v ? "Play the slideshow" : "Pause the slideshow");
      run();
    }
    pl.addEventListener("click", function () {
      setStop(!stopped);
    });
    if (reduce) setStop(true);
    [].forEach.call(bs, function (b) {
      b.addEventListener("click", function () {
        var d = +b.getAttribute("data-gfs-d"),
          x = t.scrollLeft,
          w = t.clientWidth,
          to = null;
        if (d > 0) {
          lis.some(function (li) {
            if (left(li) + li.offsetWidth > x + w + 2) {
              to = left(li);
              return true;
            }
          });
          if (to === null) to = max();
        } else {
          for (var k = lis.length - 1; k >= 0; k--) {
            var l = left(lis[k]);
            if (l < x - 2 && l <= x - w + lis[k].offsetWidth) to = l;
            if (l < x - w) break;
          }
          if (to === null) to = 0;
        }
        glide(to, 1100);
        run();
      });
    });
    var on = function () {
        hold = true;
        run();
      },
      off = function () {
        hold = false;
        run();
      };
    g.addEventListener("mouseenter", on);
    g.addEventListener("mouseleave", off);
    g.addEventListener("focusin", on);
    g.addEventListener("focusout", function (e) {
      if (!g.contains(e.relatedTarget)) off();
    });
    t.addEventListener(
      "touchstart",
      function () {
        if (anim) {
          cancelAnimationFrame(anim);
          anim = null;
          t.classList.remove("is-gliding");
        }
        on();
      },
      { passive: true },
    );
    t.addEventListener(
      "touchend",
      function () {
        setTimeout(off, 4000);
      },
      { passive: true },
    );
    t.addEventListener(
      "scroll",
      function () {
        requestAnimationFrame(upd);
      },
      { passive: true },
    );
    if ("IntersectionObserver" in window)
      new IntersectionObserver(
        function (es) {
          seen = es[0].isIntersecting;
          run();
        },
        { threshold: 0.35 },
      ).observe(t);
    else {
      seen = true;
    }
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) {
        clearInterval(timer);
        timer = null;
      } else run();
    });
    window.addEventListener("resize", upd);
    upd();
    run();
  });
})();

/* Cinematic photographs settle into place as they arrive */
(function () {
  var c = document.querySelectorAll(".cine");
  if (!c.length) return;
  if (!("IntersectionObserver" in window)) {
    [].forEach.call(c, function (e) {
      e.classList.add("is-in");
    });
    return;
  }
  var io = new IntersectionObserver(
    function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("is-in");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.2 },
  );
  [].forEach.call(c, function (e) {
    io.observe(e);
  });
})();
/* Footer clear: hide floating bars while the footer is on screen */
(function () {
  var f = document.querySelector(".site-footer");
  if (!f || !("IntersectionObserver" in window)) return;
  new IntersectionObserver(
    function (e) {
      document.documentElement.classList.toggle("ft-in", e[0].isIntersecting);
    },
    { rootMargin: "0px 0px -35% 0px" },
  ).observe(f);
})();

/* RSVP envelope opens as it comes into view, or on a tap of the seal */
(function () {
  var els = document.querySelectorAll("[data-rsvp]");
  if (!els.length) return;
  function open(el) {
    el.classList.add("open");
  }
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) {
    els.forEach(open);
    return;
  }
  var io = new IntersectionObserver(
    function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          var t = e.target;
          setTimeout(function () {
            open(t);
          }, 350);
          io.unobserve(t);
        }
      });
    },
    { threshold: 0.35 },
  );
  els.forEach(function (el) {
    io.observe(el);
    var s = el.querySelector(".rsvp-seal");
    if (s)
      s.addEventListener("click", function () {
        open(el);
      });
  });
})();

/* Heads stay in frame: every cropped photo with people is positioned from its detected faces, at every width.
   Each face counts: a head cut by the edge costs far more than a face left out, and a cut across the top of a head costs most. */
(function () {
  var best = function (faces, ax, v, top) {
    if (v >= 0.999) return 50;
    var a0 = 1, a1 = 0;
    faces.forEach(function (f) {
      a0 = Math.min(a0, f[ax]);
      a1 = Math.max(a1, f[ax + 2]);
    });
    var span = a1 - a0,
      target = top ? (span > v ? a0 : a0 - (v - span) * 0.3) : (a0 + a1) / 2 - v / 2;
    target = Math.max(0, Math.min(1 - v, target));
    var bestS = target,
      bestC = Infinity;
    for (var st = 0; st <= 1 - v + 1e-9; st += 0.005) {
      var c = 0,
        e = st + v;
      faces.forEach(function (f) {
        var lo = f[ax],
          hi = f[ax + 2];
        if (lo >= st - 0.004 && hi <= e + 0.004) return;
        if (hi <= st || lo >= e) {
          c += 1;
          return;
        }
        c += top && lo < st ? 40 : 12;
      });
      c += Math.abs(st - target) * 0.5;
      if (c < bestC) {
        bestC = c;
        bestS = st;
      }
    }
    return (bestS / (1 - v)) * 100;
  };
  var fit = function (img) {
    var faces = (img.getAttribute("data-face") || "")
      .split(";")
      .map(function (t) {
        return t.split(",").map(Number);
      })
      .filter(function (f) {
        return f.length === 4;
      });
    if (!faces.length || !img.naturalWidth) return;
    if (getComputedStyle(img).objectFit !== "cover") return;
    var W = img.clientWidth,
      H = img.clientHeight,
      w = img.naturalWidth,
      h = img.naturalHeight;
    if (!W || !H) return;
    var s = Math.max(W / w, H / h);
    img.style.objectPosition = best(faces, 0, W / (w * s), false).toFixed(1) + "% " + best(faces, 1, H / (h * s), true).toFixed(1) + "%";
  };
  var imgs = [].slice.call(document.querySelectorAll("img[data-face]"));
  imgs.forEach(function (i) {
    if (i.complete) fit(i);
    else i.addEventListener("load", function () { fit(i); }, { once: true });
  });
  if (window.ResizeObserver) {
    var ro = new ResizeObserver(function (es) {
      es.forEach(function (e) { fit(e.target); });
    });
    imgs.forEach(function (i) { ro.observe(i); });
  } else
    window.addEventListener("resize", function () {
      imgs.forEach(fit);
    });
})();

/* Never cut a head. Every photo carries the position of its heads (data-heads, set at build).
   For each cropped photo the crop is moved to keep every head whole. If the frame is too
   narrow or too short to hold them all, the whole photo is shown, on a soft blurred copy of itself. */
(function () {
  var imgs = [].slice.call(document.querySelectorAll("img[data-heads]"));
  if (!imgs.length) return;
  var parse = function (s) {
    return s.split(";").map(function (b) {
      return b.split(",").map(Number);
    });
  };
  var place = function (im) {
    var cs = getComputedStyle(im);
    if (cs.objectFit !== "cover") return;
    var w = im.clientWidth,
      h = im.clientHeight,
      nw = im.naturalWidth,
      nh = im.naturalHeight;
    if (!w || !h || !nw || !nh) return;
    var boxes = im._heads || (im._heads = parse(im.getAttribute("data-heads")));
    var s = Math.max(w / nw, h / nh),
      vw = w / s / nw,
      vh = h / s / nh;
    var fit = function (b) {
      return b[2] - b[0] <= vw + 0.001 && b[3] - b[1] <= vh + 0.001;
    };
    var b = fit(boxes[0]) ? boxes[0] : fit(boxes[1]) ? boxes[1] : null;
    var fig = im.parentElement;
    if (!b) {
      im.classList.add("heads-safe");
      if (fig) {
        fig.classList.add("heads-safe-wrap");
        fig.style.setProperty("--heads-bg", 'url("' + (im.currentSrc || im.src) + '")');
      }
      return;
    }
    im.classList.remove("heads-safe");
    if (fig) fig.classList.remove("heads-safe-wrap");
    var pos = function (lo, hi, v) {
      if (v >= 0.999) return 50;
      var centre = (lo + hi) / 2,
        start = Math.min(Math.max(centre - v / 2, hi - v), lo);
      start = Math.min(Math.max(start, 0), 1 - v);
      return (start / (1 - v)) * 100;
    };
    /* keep the heads nearer the top third when there is room, so faces sit naturally */
    var py = pos(b[1], b[3], vh);
    var top = Math.max(0, b[1] - vh * 0.12);
    if (b[3] <= top + vh) py = Math.min(py, (Math.min(top, 1 - vh) / (1 - vh || 1)) * 100);
    im.style.objectPosition = pos(b[0], b[2], vw).toFixed(1) + "% " + (vh >= 0.999 ? 50 : py).toFixed(1) + "%";
  };
  var run = function () {
    imgs.forEach(function (im) {
      if (im.complete && im.naturalWidth) place(im);
      else im.addEventListener("load", function () { place(im); }, { once: true });
    });
  };
  run();
  var t;
  window.addEventListener("resize", function () {
    clearTimeout(t);
    t = setTimeout(run, 120);
  });
  if (window.ResizeObserver) {
    var ro = new ResizeObserver(function (es) {
      es.forEach(function (e) {
        if (e.target.complete) place(e.target);
      });
    });
    imgs.forEach(function (im) { ro.observe(im); });
  }
})();

/* Never a soft photo. Each image tells the browser the width it really fills,
   so the browser always picks a file sharp enough for the screen. Browsers that
   read sizes="auto" do this already; this covers the rest and the eager images. */
(function () {
  var imgs = [].slice.call(document.querySelectorAll("img[srcset]"));
  if (!imgs.length) return;
  function size(im) {
    var w = Math.ceil(im.getBoundingClientRect().width);
    if (w > 0) im.sizes = w + "px";
  }
  imgs.forEach(size);
  if ("ResizeObserver" in window) {
    var ro = new ResizeObserver(function (es) {
      es.forEach(function (e) { size(e.target); });
    });
    imgs.forEach(function (im) { ro.observe(im); });
  } else
    window.addEventListener("resize", function () {
      imgs.forEach(size);
    });
})();
