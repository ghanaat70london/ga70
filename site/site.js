try {
  document.querySelectorAll("[data-pl]").forEach(function (e) {
    e.setAttribute("pathLength", e.getAttribute("data-pl"));
  });
} catch {}
var SITE_CONFIG = {
  contactEmail: "hello@ghanaat70uk.com",
  contactPhone: "+44 7824 555307",
  endpoint: "/api/register",
  anniversary: "2027-03-06T00:00:00Z",
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
      boxoffice: "",
    },
  },
  earlyBird: { gala: 150, full: 200, on: true, perOrder: 2 },
  tableFree: { gala: 10 },
  tracking: {
    ga4: "",
    googleAds: "",
    metaPixel: "29226830343650795",
    tiktok: "",
    linkedin: "",
    snapchat: "",
    clarity: "",
    adsLeadLabel: "",
    adsPartnerLabel: "",
    adsPurchaseLabel: "",
    linkedinLead: "",
    linkedinPartner: "",
  },
};
/* Days that register interest instead of selling. Remove a line to put that day on sale. */
SITE_CONFIG.register = { ghanaday: "ghana-day.html#interest", sunday: "women-of-the-motherland.html#sunday-interest" };
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
    /* A day that registers interest (SITE_CONFIG.register) never links to its Ticket Tailor page,
       even on a long press or open in new tab */
    var reg = SITE_CONFIG.register || {};
    if (reg[d]) return reg[d];
    return ln[d] || (live(d) ? ln.boxoffice : "") || "";
  };
  var any = DAYS.some(live) || !!ln.boxoffice;
  window.GA70TT = { live: live, any: any };
  if (!any) return;
  document.documentElement.classList.add("tt-on");
  /* Pop-up checkout: a dialog on this site holding the official Ticket Tailor inline widget for the chosen event.
     The widget code is exactly what Ticket Tailor gives under Promote > Website embed code > Event listing widget,
     with that event's ID. Ticket Tailor takes the payment inside its own frame. */
  var NAMES = {
    gala: "The Royal Jubilee Gala",
    ghanaday: "Ghana Day Festival",
    sunday: "Women of the Motherland",
    weekend: "The Weekend Pass",
  };
  var ttUrl = function (d) {
    return (
      "https://www.tickettailor.com/events/" +
      encodeURIComponent(TT.boxOffice) +
      "/" +
      encodeURIComponent(ev[d]) +
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
      "data-inline-ref":
        (function () {
          try {
            return (new URLSearchParams(location.search).get("ref") || sessionStorage.getItem("ref") || "")
              .replace(/[^\w .'-]/g, "")
              .slice(0, 120);
          } catch (e) {
            return "";
          }
        })() || "website_widget",
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
        if (wait)
          wait.textContent = "The checkout is slow to open. Use the link below to book on the Ticket Tailor page.";
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
  /* Phones and tablets go straight to the Ticket Tailor page in the same tab: a checkout inside a pop-up frame
     can lose its session on iPhone Safari, and the full page gives Apple Pay and Google Pay without a frame. */
  var phone = function () {
    try {
      return window.matchMedia("(max-width: 820px), (pointer: coarse)").matches;
    } catch (e) {
      return false;
    }
  };
  /* The golden ticket cards (data-buy) book exactly like Book now (data-pay), never through the old enquiry panel */
  document.addEventListener(
    "keydown",
    function (e) {
      var a = e.target.closest && e.target.closest("[data-buy]");
      if (!a || (e.key !== "Enter" && e.key !== " ")) return;
      var d = a.getAttribute("data-buy");
      if (DAYS.indexOf(d) < 0 || !(link(d) || (SITE_CONFIG.register || {})[d])) return;
      e.preventDefault();
      e.stopImmediatePropagation();
      a.click();
    },
    true,
  );
  document.addEventListener(
    "click",
    function (e) {
      var a = e.target.closest && e.target.closest("[data-pay], [data-buy]");
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      var d = a.getAttribute("data-pay") || a.getAttribute("data-buy");
      /* Only the Gala is on sale: Book now opens the Gala checkout in one click */
      if (d === "pick" && link("gala")) d = "gala";
      /* Ghana Day and Sunday register interest (SITE_CONFIG.register) until they go on sale */
      var reg = (SITE_CONFIG.register || {})[d];
      if (reg) {
        e.preventDefault();
        e.stopImmediatePropagation();
        var parts = reg.split("#"),
          here = (location.pathname.split("/").pop() || "index.html").replace(/^$/, "index.html");
        if (here === parts[0] || here + ".html" === parts[0]) {
          var t = document.getElementById(parts[1]);
          if (t) t.scrollIntoView({ block: "start" });
        } else location.href = reg;
        return;
      }
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
      if (phone() && link(d)) {
        e.preventDefault();
        location.href = link(d);
        return;
      }
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
      if (hd) document.documentElement.style.setProperty("--hdr", Math.round(hd.getBoundingClientRect().bottom) + "px");
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
  if (toggle)
    toggle.addEventListener("click", function () {
      var h = document.querySelector(".dd.here");
      if (h && !desktop.matches && links.classList.contains("open")) {
        h.classList.add("open");
        h.querySelector(".dd-btn").setAttribute("aria-expanded", "true");
      }
    });
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
  var reduceMotion =
    (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) ||
    document.documentElement.classList.contains("comfort");
  var hasIO = "IntersectionObserver" in window;
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
  var pageName = function (u) {
    var n = (u || "")
      .split("?")[0]
      .split("/")
      .pop()
      .replace(/\.html$/, "");
    return n || "index";
  };
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
  var headerEl = document.querySelector(".site-header");
  var compact = function () {
    if (headerEl) headerEl.classList.toggle("compact", window.scrollY > 60);
  };
  window.addEventListener("scroll", compact, { passive: true });
  compact();
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
  document
    .querySelectorAll(".days, .cards, .bento, .master, .speakers, .adinkra, .facts, .regalia, .invite, .tickets")
    .forEach(function (g) {
      Array.prototype.forEach.call(g.children, function (c, i) {
        c.style.setProperty("--i", i % 6);
      });
    });
  var local = document.querySelector("[data-localnav]"),
    ph = document.querySelector(".page-head");
  if (local && ph) {
    var ln = function () {
      local.classList.toggle("show", ph.getBoundingClientRect().bottom < 70);
    };
    window.addEventListener("scroll", ln, { passive: true });
    ln();
  }
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
              "translateY(-50%) rotate(" + (p * 40).toFixed(1) + "deg) scale(" + (1 + p * 0.15).toFixed(3) + ")";
        });
      },
      { passive: true },
    );
  }
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
  document.querySelectorAll("form[data-register]").forEach(function (form) {
    var status = form.querySelector(".form-status");
    var groups = function () {
      form.querySelectorAll("[data-req-group]").forEach(function (g) {
        var bx = g.querySelectorAll("input[type=checkbox]");
        var any = [].some.call(bx, function (x) {
          return x.checked;
        });
        if (bx[0]) bx[0].setCustomValidity(any ? "" : "Please tick at least one.");
      });
      form.querySelectorAll("[data-show-when]").forEach(function (f) {
        var rule = f.getAttribute("data-show-when").split(":");
        var el = form.querySelector('[name="' + rule[0] + '"]');
        f.hidden = !(el && rule[1].split("|").indexOf(el.value) > -1);
      });
    };
    form.addEventListener("change", groups);
    groups();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "form-status";
      status.textContent = "";
      groups();
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
          try {
            var _t = form.querySelector("[name=type]");
            document.dispatchEvent(
              new CustomEvent("ga70:lead", {
                detail: {
                  type: _t ? _t.value : "guest",
                  category: (form.querySelector("[name=category]") || {}).value || "",
                },
              }),
            );
          } catch (e) {}
          if (done) {
            try {
              var fn = ((form.querySelector("[name=firstName]") || {}).value || "").trim().split(/\s+/)[0];
              if (fn)
                done.querySelectorAll("[data-first]").forEach(function (el) {
                  el.textContent = "Akwaaba, " + fn + ".";
                });
              var mn = ((form.querySelector("[name=motherName]") || {}).value || "").trim();
              if (mn)
                done.querySelectorAll("[data-mother]").forEach(function (el) {
                  el.textContent = "A seat for " + mn + " is in our thoughts.";
                });
              var td = done.querySelector("[data-today]");
              if (td)
                td.textContent =
                  "Received · " +
                  new Date().toLocaleDateString("en-GB", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                    timeZone: "Europe/London",
                  });
            } catch (e) {}
            form.hidden = true;
            done.hidden = false;
            if (!form.closest(".capture"))
              done.scrollIntoView({
                behavior: "smooth",
                block: done.classList.contains("inv-done") ? "start" : "center",
              });
          } else {
            status.className = "form-status ok";
            status.textContent = "Thank you. Your details are with us.";
            form.reset();
          }
        })
        .catch(function (err) {
          status.className = "form-status err";
          status.textContent =
            "Thank you. We could not receive this just now. Please email " +
            SITE_CONFIG.contactEmail +
            " and we will add you by hand.";
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = label;
        });
    });
  });
  var T = SITE_CONFIG.tracking || {};
  var hasTracking = !!(T.ga4 || T.googleAds || T.metaPixel || T.tiktok || T.linkedin || T.snapchat || T.clarity);
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
      if (a.hasAttribute("data-pay")) ga("click_book", { day: a.getAttribute("data-pay"), page: location.pathname });
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
    var fbMap = { view_item: "ViewContent", begin_checkout: "InitiateCheckout", lead: "Lead", purchase: "Purchase" };
    var ttMap = {
      view_item: "ViewContent",
      begin_checkout: "InitiateCheckout",
      lead: "SubmitForm",
      purchase: "CompletePayment",
    };
    var B2B = { partner: 1, pack: 1, connect: 1, exhibitor: 1, village: 1, press: 0 };
    var isB2B = ev === "lead" && B2B[p.leadType] === 1;
    try {
      if (window.gtag && ev === "lead") {
        gtag("event", isB2B ? "partner_enquiry" : "guest_signup", { lead_type: p.leadType, sector: p.sector });
        if (T.googleAds) {
          var lab = isB2B ? T.adsPartnerLabel || T.adsLeadLabel : T.adsLeadLabel;
          if (lab) gtag("event", "conversion", { send_to: T.googleAds + "/" + lab });
        }
      }
      if (window.gtag && ev === "purchase" && T.googleAds && T.adsPurchaseLabel)
        gtag("event", "conversion", {
          send_to: T.googleAds + "/" + T.adsPurchaseLabel,
          value: p.value || 0,
          currency: "GBP",
        });
    } catch {}
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
      if (window.lintrk && ev === "lead") {
        var lid = isB2B ? T.linkedinPartner || T.linkedinLead : T.linkedinLead;
        if (lid) lintrk("track", { conversion_id: Number(lid) });
      }
      if (window.fbq && isB2B) fbq("trackCustom", "PartnerEnquiry", { lead_type: p.leadType, sector: p.sector });
    } catch {}
    try {
      if (window.snaptr)
        snaptr(
          "track",
          { view_item: "VIEW_CONTENT", begin_checkout: "START_CHECKOUT", lead: "SIGN_UP", purchase: "PURCHASE" }[ev],
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
  var PRICE = { gala: 200, ghanaday: 50, sunday: 150, weekend: 330 },
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
      if (d === "pick") d = PAGEDAY[slug] || "gala";
      track("begin_checkout", { day: d, name: NAMES[d] || d, price: PRICE[d] || 0, qty: 1, value: PRICE[d] || 0 });
    },
    true,
  );
  document.addEventListener("ga70:lead", function (e) {
    var d = (e && e.detail) || {};
    track("lead", { leadType: d.type || "guest", sector: d.category || "" });
  });
  if (/^(partners|exhibit|contact)$/.test(slug)) {
    try {
      if (window.gtag) gtag("event", "view_partnership", { page: slug });
    } catch (e) {}
    if (consent === "yes")
      setTimeout(function () {
        try {
          if (window.fbq) fbq("trackCustom", "ViewPartnership", { page: slug });
        } catch (e) {}
        try {
          if (window.ttq) ttq.track("ViewContent", { content_id: "partnership", content_type: "product" });
        } catch (e) {}
      }, 1200);
  }
  var DAYS = {
    gala: {
      name: "The Royal Jubilee Gala",
      short: "Fri 5 March",
      tab: "Gala",
      when: "Friday 5 March 2027 · 18:30 to 00:30",
      price: 200,
      field: "Royal Jubilee Gala",
      valid:
        "This ticket is for The Royal Jubilee Gala only: Friday 5 March 2027, 18:30 to 00:30, Banking Hall, London. It does not include the Ghana Day Festival or Women of the Motherland, which are separate events with their own tickets.",
      tone: "black",
      line: "Banking Hall · Tables of ten · The Ghanaian inspired dinner, the band and the midnight toast · Black Tie, ball gown or Kente",
      presets: [
        [1, "1"],
        [2, "2"],
        [4, "4"],
        [10, "Table of ten, GBP 1,800"],
      ],
      cal: "https://calendar.google.com/calendar/render?action=TEMPLATE&text=Ghana%20at%2070%20UK%3A%20The%20Royal%20Jubilee%20Gala&dates=20270305T183000Z/20270306T003000Z&details=Doors%2018%3A30.%20We%20start%20on%20time.%20Your%20ticket%20arrives%20by%20email.&location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND",
    },
    ghanaday: {
      name: "Ghana Day Festival",
      short: "Sat 6 March",
      tab: "Festival",
      when: "Saturday 6 March 2027 · 08:30 to 17:00",
      price: 50,
      hidePrice: false,
      hiddenTab: false,
      field: "Ghana Day",
      valid:
        "This ticket is for the Ghana Day Festival only: Saturday 6 March 2027, 08:30 to 17:00, Banking Hall, London. It does not include The Royal Jubilee Gala or Women of the Motherland, which are separate events with their own tickets.",
      tone: "green",
      line: "Banking Hall · Independence Day · Art, fashion and business · All ages welcome, no pushchairs",
      presets: [
        [1, "1"],
        [2, "2"],
        [4, "4"],
        [6, "Group of six"],
      ],
      cal: "https://calendar.google.com/calendar/render?action=TEMPLATE&text=Ghana%20at%2070%20UK%3A%20Ghana%20Day%20Festival&dates=20270306T083000Z/20270306T170000Z&details=Independence%20Day%20at%20Banking%20Hall.%20Your%20ticket%20arrives%20by%20email.&location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND",
    },
    sunday: {
      name: "Women of the Motherland",
      short: "Sun 7 March",
      tab: "Women",
      hidePrice: false,
      hiddenTab: false,
      when: "Sunday 7 March 2027 · 11:00 to 18:30",
      price: 150,
      field: "Women of the Motherland",
      valid:
        "This ticket is for Women of the Motherland only: Sunday 7 March 2027, 11:00 to 18:30, Banking Hall, London. It does not include The Royal Jubilee Gala or the Ghana Day Festival, which are separate events with their own tickets.",
      tone: "gold",
      line: "Mothering Sunday · Family afternoon tea, one sitting, a full day · Her name on the Wall of Mothers",
      presets: [
        [1, "1"],
        [2, "2"],
        [3, "3"],
        [5, "Family table, 5 tickets"],
      ],
      cal: "https://calendar.google.com/calendar/render?action=TEMPLATE&text=Ghana%20at%2070%20UK%3A%20Women%20of%20the%20Motherland&dates=20270307T110000Z/20270307T183000Z&details=Mothering%20Sunday%20at%20Banking%20Hall.%20Doors%2011%3A00.%20Your%20ticket%20arrives%20by%20email.&location=Banking%20Hall%2C%2014%20Cornhill%2C%20London%20EC3V%203ND",
    },
    weekend: {
      name: "The Weekend Pass",
      short: "All three",
      tab: "Weekend Pass",
      hiddenTab: true,
      when: "Friday 5 to Sunday 7 March 2027",
      price: 330,
      field: "Weekend Pass",
      valid:
        "This pass gives one entry to each of three separate events, each on its own date: The Royal Jubilee Gala on Friday 5 March 2027, 18:30 to 00:30, the Ghana Day Festival on Saturday 6 March 2027, 08:30 to 17:00, and Women of the Motherland on Sunday 7 March 2027, 11:00 to 18:30, all at Banking Hall, London.",
      tone: "black",
      line: "Banking Hall · All three days · One entry to each event",
      presets: [
        [1, "1"],
        [2, "2"],
        [4, "4"],
      ],
      cal: "",
    },
  };
  var gbp = function (n) {
    return "GBP " + n.toLocaleString("en-GB");
  };
  var eb = SITE_CONFIG.earlyBird,
    ebOn = !!(eb && eb.on);
  if (eb) {
    DAYS.gala.price = ebOn ? eb.gala : eb.full;
    if (ebOn)
      DAYS.gala.line =
        "First release " +
        gbp(eb.gala) +
        ", up to " +
        (eb.perOrder || 2) +
        " per order" +
        ", then " +
        gbp(eb.full) +
        " · " +
        DAYS.gala.line;
  }
  window.__ga70days = DAYS;
  var fmt = function (n) {
    return "GBP " + n.toLocaleString("en-GB");
  };
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
        val = +(qp.get("value") || tyQty * dd2.price);
      ty.querySelector("[data-ty-what]").textContent =
        (tyQty ? tyQty + " x " : "") +
        dd2.name +
        (tyQty ? ": " + tyQty + " x " + fmt(dd2.price) + " = " + fmt(val) : "");
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
        track("purchase", { day: day, name: dd2.name, price: dd2.price, qty: tyQty, value: val });
        try {
          sessionStorage.setItem("ga70-purchased", "1");
        } catch {}
      }
      document.querySelectorAll("[data-ty-x]").forEach(function (c) {
        if (c.getAttribute("data-ty-x") === day || day === "weekend") c.hidden = true;
      });
    }
  }
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
      return d.share + ".\n\nBook your ticket: " + link(src);
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
        try {
          var esc = function (t) {
            return String(t).replace(/\\/g, "\\\\").replace(/;/g, ";").replace(/,/g, "\\,").replace(/\n/g, "\\n");
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
        } catch {}
        track("add_to_calendar", { day: d.k, method: "apple" });
      });
  });
  (function () {
    var ty = document.querySelector("[data-thanks]");
    if (!ty) return;
    var qp = new URLSearchParams(location.search),
      o = null;
    try {
      o = JSON.parse(sessionStorage.getItem("ga70-order") || "null");
    } catch {}
    var day = qp.get("day") || (o && o.day) || "gala";
    if (day === "royal") day = "gala";
    var ids = day === "weekend" ? ["gala", "ghanaday", "sunday"] : [day];
    ids.forEach(function (k) {
      var s = document.getElementById("save-date-" + k);
      if (s) s.hidden = false;
    });
    var cl = ty.querySelector("[data-ty-cal]");
    if (cl) cl.href = "#save-date-" + ids[0];
  })();
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
      if (at && at.parentNode.scrollTo) at.parentNode.scrollTo({ left: at.offsetLeft - 24, behavior: "smooth" });
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
})();
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
  var logo = document.querySelector(".site-header a.brand, .site-header .logo, .site-header a[href='index.html']");
  if (logo)
    logo.addEventListener("click", function (e) {
      var here = (location.pathname.split("/").pop() || "index.html").replace(/\.html$/, "") || "index";
      if (here === "index" || here === "") {
        e.preventDefault();
        b.click();
      }
    });
})();
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
    var py = pos(b[1], b[3], vh);
    var top = Math.max(0, b[1] - vh * 0.12);
    if (b[3] <= top + vh) py = Math.min(py, (Math.min(top, 1 - vh) / (1 - vh || 1)) * 100);
    im.style.objectPosition = pos(b[0], b[2], vw).toFixed(1) + "% " + (vh >= 0.999 ? 50 : py).toFixed(1) + "%";
  };
  var run = function () {
    imgs.forEach(function (im) {
      if (im.complete && im.naturalWidth) place(im);
      else
        im.addEventListener(
          "load",
          function () {
            place(im);
          },
          { once: true },
        );
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
    imgs.forEach(function (im) {
      ro.observe(im);
    });
  }
})();
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
      es.forEach(function (e) {
        size(e.target);
      });
    });
    imgs.forEach(function (im) {
      ro.observe(im);
    });
  } else
    window.addEventListener("resize", function () {
      imgs.forEach(size);
    });
})();
(function () {
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-spotify-play]");
    if (!b) return;
    var box = b.closest("[data-spotify]");
    var id = box && box.getAttribute("data-spotify");
    if (!id || !/^[A-Za-z0-9]{10,40}$/.test(id)) return;
    var f = document.createElement("iframe");
    f.src = "https://open.spotify.com/embed/playlist/" + id + "?utm_source=generator&theme=0";
    f.width = "100%";
    f.height = "452";
    f.loading = "lazy";
    f.title = "Seventy years, seventy songs on Spotify";
    f.setAttribute("allow", "autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture");
    f.style.border = "0";
    f.style.borderRadius = "14px";
    box.innerHTML = "";
    box.appendChild(f);
  });
})();
(function () {
  document.querySelectorAll("[data-copytext]").forEach(function (b) {
    b.addEventListener("click", function () {
      var t = b.getAttribute("data-copytext"),
        label = b.textContent;
      function done() {
        b.textContent = "Address copied";
        setTimeout(function () {
          b.textContent = label;
        }, 2200);
      }
      try {
        navigator.clipboard.writeText(t).then(done, function () {
          b.textContent = t;
        });
      } catch (e) {
        b.textContent = t;
      }
    });
  });
})();
(function () {
  var sel = document.getElementById("c-ind");
  document.querySelectorAll("[data-industry]").forEach(function (b) {
    b.setAttribute("aria-pressed", "false");
    b.addEventListener("click", function () {
      document.querySelectorAll("[data-industry]").forEach(function (x) {
        x.setAttribute("aria-pressed", "false");
      });
      b.setAttribute("aria-pressed", "true");
      if (sel) sel.value = b.getAttribute("data-industry");
      var f = document.getElementById("connect-form");
      if (f) {
        f.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(function () {
          var n = document.getElementById("c-name");
          if (n) n.focus({ preventScroll: true });
        }, 600);
      }
    });
  });
})();
(function () {
  var form = document.querySelector("form[data-listing]");
  if (!form) return;
  var items = [].slice.call(form.querySelectorAll("[data-ls-item]"));
  var addBtn = form.querySelector("[data-ls-add]");
  var count = form.querySelector("[data-ls-count]");
  var status = form.querySelector("[data-ls-status]");
  var submit = form.querySelector("[data-ls-submit]");
  var shrunk = {};
  function shown() {
    return items.filter(function (el) {
      return !el.hidden;
    }).length;
  }
  function refresh() {
    var n = shown();
    if (count) count.textContent = n + " of 15";
    if (addBtn) addBtn.hidden = n >= 15;
  }
  if (addBtn)
    addBtn.addEventListener("click", function () {
      var next = items.filter(function (el) {
        return el.hidden;
      })[0];
      if (next) {
        next.hidden = false;
        var f = next.querySelector("input[type=text], input:not([type])");
        refresh();
        if (f) f.focus({ preventScroll: true });
        next.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  refresh();
  function shrink(file) {
    return new Promise(function (resolve) {
      if (!file || !/^image\//.test(file.type) || !window.createImageBitmap) return resolve(file);
      createImageBitmap(file)
        .then(function (bmp) {
          var max = 1600,
            s = Math.min(1, max / Math.max(bmp.width, bmp.height));
          var c = document.createElement("canvas");
          c.width = Math.round(bmp.width * s);
          c.height = Math.round(bmp.height * s);
          c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
          c.toBlob(
            function (b) {
              resolve(b ? new File([b], "piece.jpg", { type: "image/jpeg" }) : file);
            },
            "image/jpeg",
            0.84,
          );
        })
        .catch(function () {
          resolve(file);
        });
    });
  }
  items.forEach(function (el) {
    var input = el.querySelector("[data-ls-photo]"),
      prev = el.querySelector("[data-ls-prev]"),
      drop = el.querySelector("[data-ls-drop]");
    input.addEventListener("change", function () {
      var f = input.files && input.files[0];
      if (!f) return;
      shrink(f).then(function (small) {
        shrunk[input.name] = small;
        try {
          prev.src = URL.createObjectURL(small);
          prev.hidden = false;
          drop.classList.add("has");
        } catch (e) {}
      });
    });
  });
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    status.textContent = "";
    var fd = new FormData(form);
    if (!fd.get("firstName") || !fd.get("label") || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(fd.get("email") || "")) {
      status.textContent = "Please give your name, your label and a valid email.";
      return;
    }
    if (fd.get("consent") !== "yes") {
      status.textContent = "Please tick the box to confirm.";
      return;
    }
    Object.keys(shrunk).forEach(function (k) {
      fd.set(k, shrunk[k], "piece.jpg");
    });
    var any = false;
    for (var i = 1; i <= 15; i++) {
      var nm = (fd.get("item" + i + "_name") || "").trim(),
        ph = fd.get("item" + i + "_photo");
      var hasPh = ph && ph.size,
        pr = String(fd.get("item" + i + "_price") || "").replace(/[^0-9.]/g, "");
      if (!nm && !hasPh) {
        fd.delete("item" + i + "_photo");
        continue;
      }
      if (!nm || !hasPh || !Number(pr)) {
        status.textContent = "Piece " + i + " needs a photo, a name and a price.";
        return;
      }
      any = true;
    }
    if (!any) {
      status.textContent = "Please add at least one piece, with a photo, a name and a price.";
      return;
    }
    submit.disabled = true;
    status.textContent = "Sending your pieces. Please keep this page open.";
    fetch("/api/listing", { method: "POST", body: fd })
      .then(function (r) {
        return r
          .json()
          .catch(function () {
            return {};
          })
          .then(function (j) {
            return { ok: r.ok, j: j };
          });
      })
      .then(function (res) {
        if (res.ok) {
          form.reset();
          shrunk = {};
          form.querySelectorAll("[data-ls-prev]").forEach(function (p) {
            p.hidden = true;
          });
          form.querySelectorAll("[data-ls-drop]").forEach(function (d) {
            d.classList.remove("has");
          });
          var n = res.j.pieces || 0;
          status.textContent =
            "Medaase. Your " +
            (n === 1 ? "piece has" : n + " pieces have") +
            " arrived. We confirm by email before anything goes online.";
        } else
          status.textContent =
            (res.j && res.j.error) ||
            "We could not send your pieces. Please try again, or email hello@ghanaat70uk.com.";
      })
      .catch(function () {
        status.textContent = "We could not send your pieces. Please check your connection and try again.";
      })
      .then(function () {
        submit.disabled = false;
      });
  });
})();
document.addEventListener("click", function (e) {
  var a = e.target.closest && e.target.closest("[data-qa-piece]");
  if (!a) return;
  var form = document.querySelector("#qa-connect form");
  if (!form) return;
  var sel = form.querySelector("select[name=interests]"),
    msg = form.querySelector("textarea[name=message]");
  if (sel) sel.value = "A piece from the collection";
  if (msg && msg.value.indexOf(a.getAttribute("data-qa-piece")) < 0)
    msg.value = "I would like to order: " + a.getAttribute("data-qa-piece") + (msg.value ? "\n" + msg.value : "");
});
(function () {
  var ids = ["list-your-pieces", "plan", "from-ghana", "interest"];
  function openFor(h) {
    var id = (h || "").replace("#", "");
    if (ids.indexOf(id) < 0) return;
    var el = document.getElementById(id);
    if (el)
      el.querySelectorAll("details.more").forEach(function (d) {
        d.open = true;
      });
  }
  openFor(location.hash);
  window.addEventListener("hashchange", function () {
    openFor(location.hash);
  });
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href*="#"]');
    if (a) openFor(a.getAttribute("href").split("#")[1]);
  });
})();
(function () {
  document.querySelectorAll("[data-spl]").forEach(function (root) {
    var track = root.querySelector(".spl-track");
    var slides = root.querySelectorAll(".spl-slide");
    if (!track || slides.length < 2) return;
    var dots = root.querySelectorAll(".spl-dot");
    var cur = 0,
      timer = null,
      hold = false;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    function go(i) {
      cur = (i + slides.length) % slides.length;
      track.scrollTo({ left: cur * track.clientWidth, behavior: reduce ? "auto" : "smooth" });
      mark();
    }
    function mark() {
      dots.forEach(function (d, k) {
        d.setAttribute("aria-current", k === cur ? "true" : "false");
      });
    }
    root.querySelector(".spl-prev").addEventListener("click", function () {
      go(cur - 1);
      restart();
    });
    root.querySelector(".spl-next").addEventListener("click", function () {
      go(cur + 1);
      restart();
    });
    dots.forEach(function (d, k) {
      d.addEventListener("click", function () {
        go(k);
        restart();
      });
    });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") {
        go(cur + 1);
        e.preventDefault();
      }
      if (e.key === "ArrowLeft") {
        go(cur - 1);
        e.preventDefault();
      }
    });
    var t;
    track.addEventListener("scroll", function () {
      clearTimeout(t);
      t = setTimeout(function () {
        var w = track.clientWidth || 1;
        cur = Math.round(track.scrollLeft / w);
        mark();
      }, 80);
    });
    function restart() {
      if (timer) clearInterval(timer);
      if (reduce) return;
      timer = setInterval(function () {
        if (!hold && !document.hidden) go(cur + 1);
      }, 7000);
    }
    root.addEventListener("mouseenter", function () {
      hold = true;
    });
    root.addEventListener("mouseleave", function () {
      hold = false;
    });
    root.addEventListener("focusin", function () {
      hold = true;
    });
    root.addEventListener("focusout", function () {
      hold = false;
    });
    mark();
    restart();
  });
})();
(function () {
  var rows = [].slice.call(document.querySelectorAll(".kl-row"));
  if (!rows.length) return;
  function wake(row) {
    row.querySelectorAll('img[loading="lazy"]').forEach(function (im) {
      im.loading = "eager";
    });
  }
  if (!("IntersectionObserver" in window)) {
    rows.forEach(wake);
    return;
  }
  var io = new IntersectionObserver(
    function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          wake(e.target);
          io.unobserve(e.target);
        }
      });
    },
    { rootMargin: "100% 0px" },
  );
  rows.forEach(function (r) {
    io.observe(r);
  });
})();
(function () {
  var hd = document.querySelector(".site-header");
  if (!hd) return;
  function set() {
    document.documentElement.style.setProperty("--hdr", Math.round(hd.getBoundingClientRect().bottom) + "px");
  }
  set();
  if ("ResizeObserver" in window) new ResizeObserver(set).observe(hd);
  else window.addEventListener("resize", set);
})();
/* Register your interest forms (data-steps): the bottom bar steps aside, appointments rest when declined, at most five */
(function () {
  document.querySelectorAll("form[data-steps]").forEach(function (form) {
    /* While the form is on screen, the bottom Register bar steps aside */
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(
        function (es) {
          document.documentElement.classList.toggle("in-reg", es[0].isIntersecting);
        },
        { rootMargin: "-80px 0px -80px 0px" },
      ).observe(form.closest(".invite") || form);
    }
    /* No appointments wanted: the appointment cards rest, and nothing is sent from them */
    var appt = form.querySelector(".appts");
    var syncAppt = function () {
      var no = form.querySelector('input[name="appointments"]:checked');
      if (!appt || !no) return;
      var off = /^No/.test(no.value);
      appt.classList.toggle("is-off", off);
      appt.querySelectorAll("input").forEach(function (x) {
        if (off) x.checked = false;
        x.disabled = off;
      });
    };
    form.addEventListener("change", function (e) {
      if (e.target.name === "appointments") syncAppt();
    });
    syncAppt();
    form.querySelectorAll("[data-max]").forEach(function (box) {
      var max = +box.getAttribute("data-max");
      box.addEventListener("change", function () {
        var all = box.querySelectorAll("input[type=checkbox]"),
          on = box.querySelectorAll("input:checked").length;
        all.forEach(function (x) {
          x.disabled = !x.checked && on >= max;
        });
      });
    });
  });
})();

/* Signature moment: the royal envelope opens once, when it comes into view */
(function () {
  var env = document.querySelector("[data-envelope]");
  if (!env || !("IntersectionObserver" in window)) return;
  document.documentElement.classList.add("sm-js");
  function open() {
    env.classList.remove("is-open");
    void env.offsetWidth;
    env.classList.add("is-open");
  }
  var io = new IntersectionObserver(
    function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          setTimeout(open, 300);
          io.disconnect();
        }
      });
    },
    { threshold: 0.5 },
  );
  io.observe(env);
  var again = document.querySelector("[data-envelope-again]");
  if (again) again.addEventListener("click", open);
})();

(function () {
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
