// Cloudflare Pages Function: receives every form and booking at /api/register.
// Configure in Cloudflare > Workers and Pages > the project > Settings > Variables and Secrets:
//   GHL_WEBHOOK_URL   GoHighLevel inbound webhook URL (adds the contact to your CRM)
//   RESEND_API_KEY    Resend API key for email notifications (optional)
//   NOTIFY_EMAIL      Inbox that receives each new registration (optional, with Resend)
//   FROM_EMAIL        Verified sender, for example Ghana at 70 UK <hello@yourdomain.com> (optional, with Resend)
// At least one of GHL_WEBHOOK_URL or RESEND_API_KEY must be set.

const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const TYPES = {
  guest: { pipeline: "GA70 Tickets", stage: "Registered interest", tag: "GA70 Priority List", reply: "Thank you. You are on the Ghana at 70 UK list, so you hear the programme, the speakers and every announcement first. Tickets are on sale now on our official website." },
  partner: { pipeline: "GA70 Partnerships", stage: "Enquiry received", tag: "GA70 Partner Enquiry", reply: "Thank you for your interest in partnering with Ghana at 70 UK. Our partnerships team will reply within one working day with a proposal shaped around your objectives." },
  pack: { pipeline: "GA70 Partnerships", stage: "Pack requested", tag: "GA70 Pack Requested", reply: "Thank you for requesting the Ghana at 70 UK sponsorship pack. It follows in a separate email today, and our partnerships team will be in touch to arrange a call." },
  speaker: { pipeline: "GA70 Speakers", stage: "Submission received", tag: "GA70 Speaker", reply: "Thank you for registering to speak at Ghana at 70 UK. Our programme team reviews every submission and will be in touch if there is a fit." },
  volunteer: { pipeline: "GA70 Volunteers", stage: "Application received", tag: "GA70 Volunteer", reply: "Medaase for volunteering with Ghana at 70 UK. Briefings and shift options follow in January 2027." },
  question: { pipeline: "GA70 Questions", stage: "Anonymous question", tag: "GA70 Anonymous Question", reply: "" },
  stay: { pipeline: "GA70 Accommodation", stage: "Accommodation request", tag: "GA70 Accommodation", reply: "Thank you for your accommodation request for Ghana at 70 UK. Our team will send hotel options and rates within one working day. Nothing is booked until you approve it." },
  "ghana-travel": { pipeline: "GA70 Accommodation", stage: "Travel from Ghana", tag: "GA70 Ghana Travel", reply: "Thank you. Adansi Travels, our travel partner in Ghana, will contact you about your visa application and flights. Their services are at your own cost and are arranged directly with them." },
  exhibitor: { pipeline: "GA70 Exhibitors", stage: "Applied", tag: "GA70 Exhibitor Application", reply: "Thank you for applying to exhibit at the Ghana Day Festival. You will hear from our exhibitions team within five working days, with the exhibitor pack and next steps." },
  press: { pipeline: "GA70 Press", stage: "Accreditation requested", tag: "GA70 Press", reply: "Thank you for your press accreditation request for Ghana at 70 UK. Accreditation is confirmed by email, usually within three working days." },
  village: { pipeline: "GA70 Partnerships", stage: "Resource Village application", tag: "GA70 Resource Village", reply: "Thank you for applying to join the Resource Village at Women of the Motherland. Our partnership team will reply within one working day." },
  contact: { pipeline: "GA70 Enquiries", stage: "New enquiry", tag: "GA70 Enquiry", reply: "Thank you for contacting Ghana at 70 UK. A member of our team will reply within one working day." },
  checkout: { pipeline: "GA70 Tickets", stage: "Checkout started", tag: "GA70 Checkout", reply: "Thank you for choosing Ghana at 70 UK. If you completed payment, your golden tickets follow by email. If you have not paid yet, nothing is reserved until payment is made, and your secure payment link follows shortly." },
  sessions: { pipeline: "GA70 Tickets", stage: "Registered interest", tag: "GA70 Session Interest", reply: "Medaase. Your ideas for Women of the Motherland are with our programme team. We tell you first when talks and masterclasses are confirmed. Registering does not reserve a place." },
  alliance: { pipeline: "GA70 Partnerships", stage: "Alliance request", tag: "GA70 Alliance Partner", reply: "Thank you for asking to become an alliance partner of Ghana at 70 UK. Your one page agreement and personal booking link follow within one working day." },
  connect: { pipeline: "GA70 Partnerships", stage: "Diaspora connection request", tag: "GA70 Connect", reply: "Thank you for getting in touch with Ghana at 70 UK about reaching the diaspora. Our partnerships team will reply within one working day." },
  draw: { pipeline: "GA70 Tickets", stage: "Hamper draw entry", tag: "GA70 Hamper Draw", reply: "You are entered in the free Ghana at 70 UK hamper draw. The winner is drawn on Independence Day, Saturday 6 March 2027, and told by email within 3 working days." },
  exinterest: { pipeline: "GA70 Exhibitors", stage: "Registered interest", tag: "GA70 Exhibitor Interest", reply: "Thank you for registering your interest in exhibiting at Ghana at 70 UK. Our exhibitions team will be in touch with the details." },
  quophi: { pipeline: "GA70 Enquiries", stage: "Quophi Akotuah interest", tag: "GA70 Quophi Akotuah", reply: "Thank you for registering your interest with Quophi Akotuah, Fashion Partner of Ghana at 70 UK. You will hear from us soon." },
  interest: { pipeline: "GA70 Tickets", stage: "Registered interest", tag: "GA70 Ghana Day Interest", reply: "Thank you for registering your interest in the Ghana Day Festival on Saturday 6 March 2027. Tickets go on sale in the New Year, and you hear first, before anyone else. A person reads every word." },
  sunint: { pipeline: "GA70 Tickets", stage: "Registered interest", tag: "GA70 Sunday Interest", reply: "Thank you for registering your interest in Women of the Motherland on Mothering Sunday, 7 March 2027. Tickets go on sale in the New Year, and you hear first, before anyone else. Her seat is in our thoughts." },
  compete: { pipeline: "GA70 Competitions", stage: "Entered", tag: "GA70 Competitor", reply: "You are entered for the Ghana Day Festival games. Rules and your call times arrive by email in February 2027." }
};
const clip = (s, n) => String(s == null ? "" : s).slice(0, n);

const json = (status, obj, extra) => new Response(JSON.stringify(obj), { status, headers: Object.assign({ "Content-Type": "application/json" }, extra || {}) });

export async function onRequest(context) {
  const { request, env } = context;
  if (request.method !== "POST") return json(405, { error: "Method not allowed" }, { Allow: "POST" });
  let body = {};
  try { body = await request.json(); } catch { body = {}; }
  body = body && typeof body === "object" ? body : {};

  // Honeypot: bots fill the hidden field. Pretend success.
  if (body.website) return json(200, { ok: true });

  const isQuestion = body.type === "question";
  const email = clip(body.email, 200).trim();
  const firstName = clip(body.firstName, 100).trim();
  if (isQuestion && !clip(body.message, 10).trim()) return json(400, { error: "Please write your question." });
  if (!isQuestion && (!firstName || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))) return json(400, { error: "Please give your name and a valid email." });
  if (body.consent !== "yes") return json(400, { error: "Please tick the consent box." });
  if (body.type === "checkout" && !clip(body.phone, 40).trim()) return json(400, { error: "Please add your mobile, so we can send your tickets and timings." });

  const interests = [].concat(body.interests || []).map((x) => clip(x, 80));
  // Alliance partner links: who invited this guest, from the form field or the ?ref= the visit arrived with
  const invitedBy = clip(String(body.invitedBy || "").trim() || String(body.ref || "").trim(), 120).trim();
  const cf = request.cf || {};
  const country = String(cf.country || request.headers.get("cf-ipcountry") || "");
  const record = {
    type: TYPES[body.type] ? body.type : "guest",
    pipeline: (TYPES[body.type] || TYPES.guest).pipeline,
    stage: (TYPES[body.type] || TYPES.guest).stage,
    title: clip(body.title, 20).trim(),
    firstName,
    lastName: clip(body.lastName, 100).trim(),
    email,
    phone: clip(body.phone, 40).trim(),
    organisation: clip(body.organisation, 160).trim(),
    interests,
    partySize: clip(body.partySize, 40),
    category: clip(body.category, 80),
    standType: clip(body.standType, 60),
    galaWanted: body.galaWanted === "yes",
    galaSeats: body.galaWanted === "yes" ? clip(body.galaSeats, 20) : "",
    heardFrom: clip(body.heardFrom, 60),
    message: clip(body.message, 3000),
    motherName: clip(body.motherName, 160),
    basket: clip(body.basket, 300),
    day: clip(body.day, 20),
    quantity: Number(body.quantity) || 0,
    unitPrice: Number(body.unitPrice) || 0,
    value: Number(body.value) || 0,
    sitting: clip(body.sitting, 40),
    masterclass: clip(body.masterclass, 40),
    checkoutUrl: clip(body.checkoutUrl, 600),
    payBy: clip(body.payBy, 10),
    giftFor: clip(body.giftFor, 160),
    newsOptIn: body.news === "yes" || body.type === "guest",
    organisationUrl: clip(body.organisationUrl, 200),
    invitedBy,
    ref: clip(body.ref, 120),
    source: clip(body.source || body.page, 80),
    consent: true,
    utmSource: clip(body.utm_source, 80), utmMedium: clip(body.utm_medium, 80), utmCampaign: clip(body.utm_campaign, 120),
    utmTerm: clip(body.utm_term, 120), utmContent: clip(body.utm_content, 120),
    clickId: clip(body.gclid || body.fbclid || body.ttclid || body.li_fat_id, 200),
    clickSource: body.gclid ? "Google Ads" : body.fbclid ? "Meta" : body.ttclid ? "TikTok" : body.li_fat_id ? "LinkedIn" : "",
    country: clip(country, 4), region: clip(cf.regionCode, 10),
    city: clip(cf.city, 80),
    device: clip(body.device, 20), language: clip(body.language, 20), screen: clip(body.screen, 20), timezone: clip(body.timezone, 60),
    referrer: clip(body.referrer, 300), landingPage: clip(body.landing, 300),
    tags: ["Ghana at 70 UK", (TYPES[body.type] || TYPES.guest).tag].concat(interests.map((i) => "GA70 " + i), body.category ? ["GA70 " + clip(body.category, 60)] : [], body.galaWanted === "yes" ? ["GA70 Exhibitor Gala seats"] : [], body.news === "yes" ? ["GA70 News opt in"] : [], country ? ["GA70 Country " + clip(country, 4)] : [], body.utm_source ? ["GA70 Source " + clip(body.utm_source, 40)] : [], invitedBy ? ["GA70 Invited by " + clip(invitedBy, 60)] : []),
    submittedAt: new Date().toISOString()
  };

  // Every other field the form sent (dates, rooms, what an exhibitor sells and so on), so nothing is lost on the way to the CRM
  const NAMED = new Set(["website", "consent", "type", "page", "source", "email", "firstName", "lastName", "title", "phone", "organisation", "interests",
    "partySize", "category", "standType", "galaWanted", "galaSeats", "heardFrom", "message", "motherName", "basket", "day", "quantity", "unitPrice",
    "value", "sitting", "masterclass", "checkoutUrl", "payBy", "giftFor", "news", "organisationUrl", "invitedBy", "ref", "utm_source", "utm_medium",
    "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid", "ttclid", "li_fat_id", "device", "language", "screen", "timezone", "referrer", "landing"]);
  const details = {};
  Object.keys(body).forEach((k) => {
    if (NAMED.has(k) || Object.keys(details).length >= 40) return;
    const v = body[k];
    if (v == null || v === "") return;
    details[clip(k, 40)] = Array.isArray(v) ? v.map((x) => clip(x, 200)).join(", ") : clip(typeof v === "object" ? JSON.stringify(v) : v, 500);
  });
  record.details = details;
  record.detailsText = Object.entries(details).map(([k, v]) => k + ": " + v).join("\n").slice(0, 4000);

  const tasks = [];
  const ghl = env.GHL_WEBHOOK_URL;
  const resendKey = env.RESEND_API_KEY;
  if (!ghl && !resendKey) return json(500, { error: "Registration is not configured yet." });

  if (ghl) {
    tasks.push(fetch(ghl, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(record), signal: AbortSignal.timeout(8000) })
      .then((r) => { if (!r.ok) throw new Error("CRM " + r.status); }));
  }

  if (resendKey && env.FROM_EMAIL) {
    const send = (payload) => fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: "Bearer " + resendKey, "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(8000)
    }).then((r) => { if (!r.ok) throw new Error("Email " + r.status); });

    if (env.NOTIFY_EMAIL) {
      const rows = Object.entries(record).filter(([k]) => k !== "tags" && k !== "details")
        .map(([k, v]) => `<tr><td style="padding:4px 12px 4px 0;color:#4A5A52">${esc(k)}</td><td style="padding:4px 0">${esc(Array.isArray(v) ? v.join(", ") : v)}</td></tr>`).join("");
      tasks.push(send({
        from: env.FROM_EMAIL,
        to: env.NOTIFY_EMAIL.split(",").map((s) => s.trim()),
        reply_to: email || undefined,
        subject: `Ghana at 70 UK ${record.stage}: ${firstName} ${record.lastName}`.trim(),
        html: `<table style="font-family:Arial,sans-serif;font-size:14px">${rows}</table>`
      }));
    }

    if (!isQuestion) tasks.push(send({
      from: env.FROM_EMAIL,
      to: email,
      subject: record.type === "checkout" ? "Ghana at 70 UK: your booking" : "Ghana at 70 UK: we have received your details",
      html: `<div style="font-family:Georgia,serif;font-size:16px;line-height:1.6;color:#16201B;max-width:560px">
<p>Dear ${esc(firstName)},</p>
<p>${TYPES[record.type].reply}</p>${record.type === "checkout" ? `<p><b>${esc(record.basket)}</b></p><p>We look forward to seeing you there.</p>` : ""}
<p><b>Friday 5 March 2027</b> to <b>Sunday 7 March 2027</b>, London.</p>
<p>With warm regards,<br>The Ghana at 70 UK team</p></div>`
    }));
  }

  // The CRM record is what matters. An email that fails must not make the guest submit twice.
  const results = await Promise.allSettled(tasks);
  results.forEach((r) => { if (r.status === "rejected") console.error("register task failed", r.reason); });
  const crmFailed = ghl && results[0] && results[0].status === "rejected";
  const allFailed = results.length > 0 && results.every((r) => r.status === "rejected");
  if (crmFailed || allFailed) return json(502, { error: "We could not save your details. Please try again, or call Asantewaa on 07824 555307." });
  return json(200, { ok: true });
}
