// Ghana at 70 UK · Ticket Tailor to GoHighLevel bridge. Cloudflare Pages Function.
// Address: https://ghanaat70uk.com/api/tt-webhook?key=YOUR_SECRET
// Open it in a browser: it answers "Bridge ready" when deployed. Ticket Tailor posts every order to it.
// It sends one clean message to GoHighLevel: T1 for new orders, T2 for cancellations.
// Kept in step with api/tt-webhook.js (the live Vercel version).
// Variables in Cloudflare Pages: TT_BRIDGE_KEY, GHL_TT_CREATED_URL, GHL_TT_CANCELLED_URL
// Optional, for adverts: META_PIXEL_ID and META_CAPI_TOKEN send each paid order to Meta as a Purchase from the server.
// Use this OR the Meta pixel inside Ticket Tailor for purchases, never both, or every sale counts twice.
// META_TEST_CODE (optional) sends the events to Test Events in Meta Events Manager while testing.

const kindOf = (d) => {
  const s = String(d || "").toLowerCase();
  if (s.includes("weekend")) return "weekend";
  if (/party of (10|ten)|table of (10|ten)/.test(s) && !s.includes("family")) return "gala";
  if (s.includes("gala")) return (s.includes("early") || s.includes("first release")) ? "earlybird" : "gala";
  if (s.includes("festival") || s.includes("ghana day")) return "festival";
  if (s.includes("women") || s.includes("motherland") || s.includes("sunday")) return "women";
  return "other";
};

const yes = (v) => /^(yes|true|1|on|y)/i.test(String(v || "").trim()) || /send me news/i.test(String(v || ""));

const sha256 = async (v) => {
  if (!v) return undefined;
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(String(v).trim().toLowerCase()));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
};
const ukPhone = (p) => { let d = String(p || "").replace(/\D/g, ""); if (d.startsWith("0")) d = "44" + d.slice(1); return d; };

async function metaPurchase(env, out) {
  if (!env.META_PIXEL_ID || !env.META_CAPI_TOKEN || out.event !== "created" || out.tags.includes("SYS_TEST") && !env.META_TEST_CODE) return null;
  const user = { em: [await sha256(out.email)], ph: [await sha256(ukPhone(out.phone))], fn: [await sha256(out.firstName)], ln: [await sha256(out.lastName)], country: [await sha256("gb")], external_id: [await sha256(out.email)] };
  Object.keys(user).forEach((k) => { if (!user[k][0]) delete user[k]; });
  const body = { data: [{ event_name: "Purchase", event_time: Math.floor(Date.now() / 1000), event_id: "tt_" + out.orderId, action_source: "website", event_source_url: "https://ghanaat70uk.com/tickets", user_data: user, custom_data: { currency: "GBP", value: out.totalGBP, num_items: out.seats } }] };
  if (env.META_TEST_CODE) body.test_event_code = env.META_TEST_CODE;
  const r = await fetch("https://graph.facebook.com/v22.0/" + env.META_PIXEL_ID + "/events?access_token=" + encodeURIComponent(env.META_CAPI_TOKEN), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) console.error("Meta answered", r.status, await r.text());
  return r.ok;
}

const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "Content-Type": "application/json" } });
const titleCase = (s) => String(s || "").trim().replace(/\s+/g, " ").toLowerCase().replace(/(^|\s)\S/g, (c) => c.toUpperCase());

export async function onRequestGet() {
  return new Response("Bridge ready", { status: 200 });
}

export async function onRequestPost({ request, env }) {
  const key = new URL(request.url).searchParams.get("key");
  if (!env.TT_BRIDGE_KEY || key !== env.TT_BRIDGE_KEY) return json({ ok: false, error: "bad key" }, 401);

  let body = {};
  try { body = await request.json(); } catch (e) { return json({ ok: false, error: "not JSON" }, 400); }
  const o = body.payload || body.data || body;
  const eventName = String(body.event || body.type || "").toUpperCase();
  const cancelled = /CANCEL/.test(eventName) || String(o.status || "").toLowerCase() === "cancelled";
  const created = !cancelled && /CREATE/.test(eventName);
  if (!cancelled && !created) return json({ ok: true, ignored: eventName || "no event" });

  const buyer = o.buyer_details || o.buyer || {};
  const fullName = String(buyer.name || "").trim();
  const firstName = buyer.first_name || fullName.split(" ")[0] || "";
  const lastName = buyer.last_name || fullName.split(" ").slice(1).join(" ") || "";
  const email = String(buyer.email || o.email || "").trim().toLowerCase();

  const counts = { gala: 0, earlybird: 0, festival: 0, women: 0, weekend: 0, other: 0 };
  const issued = Array.isArray(o.issued_tickets) ? o.issued_tickets : [];
  if (issued.length) {
    for (const t of issued) counts[kindOf(t.description || t.ticket_type_name)] += 1;
  } else {
    for (const li of (Array.isArray(o.line_items) ? o.line_items : [])) {
      if (li.type && li.type !== "ticket") continue;
      counts[kindOf(li.description)] += Number(li.quantity || 1);
    }
  }

  const questions = [].concat(buyer.custom_questions || [], o.custom_questions || []);
  const answer = (re) => {
    const q = questions.find((x) => re.test(String(x.question || x.label || "")));
    return q ? String(q.answer || q.value || "") : "";
  };
  const newsOptIn = yes(answer(/news/i));
  const dietary = answer(/dietary/i);
  const motherName = answer(/wall of mothers/i);
  const giftFor = answer(/gift/i);
  const invitedBy = titleCase(answer(/who invited/i));
  const meetPartners = yes(answer(/meet our partners|partners/i));
  const lookingFor = answer(/looking for/i);

  const galaQty = counts.gala + counts.earlybird;
  let galaSeats = galaQty + counts.weekend;
  const totalRaw = Number(o.total || o.total_paid || 0);
  const totalGBP = Math.round(totalRaw) / 100;

  const tags = [];
  if (created) tags.push("GA70 Paid");
  if (galaQty || counts.weekend) tags.push("GA70 Gala");
  if (counts.festival || counts.weekend) tags.push("GA70 Festival");
  if (counts.women || counts.weekend) tags.push("GA70 Women");
  if (counts.weekend) tags.push("GA70 Weekend");
  if (counts.earlybird) tags.push("GA70 First release");
  if (created && galaSeats >= 10) tags.push("GA70 Table host");
  if (created && newsOptIn) tags.push("GA70 News opt in");
  if (created && invitedBy) tags.push("GA70 Sold by " + invitedBy);
  // Offer and draw tags, read from the ticket type names
  const names = (issued.length ? issued : (Array.isArray(o.line_items) ? o.line_items : [])).map((t) => String(t.description || t.ticket_type_name || "").toLowerCase());
  const tableHits = names.filter((n) => /party of (10|ten)|table of (10|ten)|group ticket/.test(n) && !n.includes("family")).length;
  const tableQty = tableHits >= 10 ? Math.round(tableHits / 10) : tableHits;
  if (tableQty && galaSeats < 10 * tableQty) galaSeats = 10 * tableQty;
  if (created && tableQty && !tags.includes("GA70 Table host")) tags.push("GA70 Table host");
  if (created && tableQty) tags.push("GA70 Table of ten");
  const quizTeam = names.some((n) => n.includes("quiz")) ? 1 : 0;
  const familyTable = names.some((n) => n.includes("family")) ? 1 : 0;
  if (created && quizTeam) tags.push("GA70 Quiz team");
  if (created && familyTable) tags.push("GA70 Family table");
  if (created && meetPartners) tags.push("GA70 Meet partners yes");
  // Mefie free prize draw: every lead booker with a paid order placed before 23:59 Sunday 28 February 2027 (London, GMT)
  if (created && Date.now() < Date.parse("2027-03-01T00:00:00Z")) tags.push("GA70 Mefie Draw");
  if (email.includes("+ga70test")) tags.push("SYS_TEST");
  const seats = Object.values(counts).reduce((a, b) => a + b, 0);

  const out = {
    event: cancelled ? "cancelled" : "created",
    orderId: o.id || o.order_id || "",
    firstName, lastName, email,
    phone: buyer.phone || "",
    galaQty, earlyBirdQty: counts.earlybird, festivalQty: counts.festival,
    womenQty: counts.women, weekendQty: counts.weekend, galaSeats,
    totalGBP, currency: (o.currency && o.currency.code) || o.currency || "GBP",
    seats, tableQty, quizTeam, familyTable, meetPartners, lookingFor, newsOptIn, dietary, motherName, giftFor, invitedBy,
    tags: tags.join(", "),
    galaDate: (galaQty || counts.weekend) ? "2027-03-05" : "",
    festivalDate: (counts.festival || counts.weekend) ? "2027-03-06" : "",
    womenDate: (counts.women || counts.weekend) ? "2027-03-07" : ""
  };

  const url = cancelled ? env.GHL_TT_CANCELLED_URL : env.GHL_TT_CREATED_URL;
  if (!url) {
    console.error("Missing GoHighLevel URL for", out.event);
    return json({ ok: false, error: "missing GoHighLevel URL" }, 500);
  }
  let ghlOk = false, ghlStatus = 0;
  try {
    const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(out), signal: AbortSignal.timeout(8000) });
    ghlOk = r.ok; ghlStatus = r.status;
    if (!r.ok) console.error("GoHighLevel answered", r.status, "for order", out.orderId);
  } catch (e) { console.error("GoHighLevel unreachable for order", out.orderId, e); }
  let meta = null;
  if (ghlOk) { try { meta = await metaPurchase(env, out); } catch (e) { console.error("Meta error", e); } }
  // 502 when GoHighLevel did not take the order, so Ticket Tailor retries the webhook
  return json({ ok: ghlOk, sent: out.event, orderId: out.orderId, tags: out.tags, ghlStatus, meta }, ghlOk ? 200 : 502);
}
