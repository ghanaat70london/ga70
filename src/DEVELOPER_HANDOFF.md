# Ghana at 70 UK website: developer handoff

For: Rishit Thakkar
From: Gigi, Ghana at 70 UK
Updated: 19 November 2026

## 1. The job

1. Deploy the site to Cloudflare Pages on the business account and connect `ghanaat70uk.com` from GoDaddy. `DEPLOY.md` does it in 15 minutes.
2. Connect the forms to GoHighLevel with `GHL_WEBHOOK_URL`.
3. Switch on Ticket Tailor by pasting the official embed values for the four events into `SITE_CONFIG.ticketTailor`.
4. Prove it with one real card payment per event, then refund it.

Do not build a ticketing system. Ticket Tailor and Stripe handle tickets, payment and QR codes.

## 2. State of the code on handover

Checked on 19 November 2026 at phone, tablet and desktop width:
1. 20 pages, W3C HTML validator: no errors.
2. `site.js` and `api/register.js`, ESLint: no errors.
3. No script errors, no failed requests, no broken links or anchors, no sideways scrolling.
4. Accessibility, axe WCAG 2.1 AA: no violations.
5. All 32 forms submitted through the real `api/register.js` with a mock GoHighLevel: every record correct.
6. Booking for all four events, by card and by bank transfer: correct quantity x price.
7. Ticket Tailor simulated with test values: every Book now button opens the right event, Weekend Pass included.
8. Clean build from the zip in a fresh Python environment, with the exact Cloudflare build command: identical output.
9. The Cloudflare Pages Function tested with a mock GoHighLevel: success, refusal, wrong method, bad JSON and bot cases all correct.

Fixed in the final sweep:
1. The Weekend Pass had no checkout once Ticket Tailor was on. It is now its own event (`weekend`).
2. Canonical tags, sitemap and robots pointed at a guessed address. They now use `https://ghanaat70uk.com`.
3. The build published source files as static files. It no longer does. It writes a Cloudflare `_headers` file for security headers and caching instead.
4. Four script variables were declared twice in one scope (`q`, `once`, `NAMES`, `dd`), so a later block could overwrite an earlier one. Renamed.
5. A duplicate `id="midnight"` on the Royal Gala page.
6. The face map tool wrote an old format the build could not read. Replaced.
7. Forms now show the server reason when a submission is refused. Gala early bird bookings are marked early bird in GoHighLevel.

## 3. How the site is built

1. `src/build.py` generates every page into `ghana-at-70/`. Edit the source, never the output.
2. Python 3.12 or later with Pillow and fontTools. The build stops with a plain message if either is missing.
3. `src/serve.py` runs the whole site locally with a stand in form handler.
4. `functions/api/register.js` is the only server code, a Cloudflare Pages Function. Its keys come from the Cloudflare project variables only.
5. Build settings live in the Cloudflare project (see `DEPLOY.md`). There is no Content Security Policy. If you add one, allow `https://*.tickettailor.com` for script, style, frame and connect.

## 4. Ticket Tailor, waiting for real values

1. `src/site.js`, `SITE_CONFIG.ticketTailor`: `widgetScript` (src of the script tag), `boxOffice` (first value in `TTWidget.loadEvent`), the four numeric event IDs and their public links, and the box office link. Copy from Ticket Tailor: event, Share event, Website embed code, pop out button code.
2. `src/tt/boxoffice.html`: the official box office widget code. `src/tt/cart.html`: the cart widget code, only once multi checkout is on.
3. Once filled, every `data-pay="gala|ghanaday|sunday|weekend"` element opens `TTWidget.loadEvent(boxOffice, eventId, "website")`. If the widget fails, the click goes to that event's Ticket Tailor page. Every button also carries the real link as its `href`.
4. `data-pay="pick"` scrolls to all events on `tickets.html`, or opens the box office from other pages.
5. While any value is empty, that event keeps the built in booking form. Do not remove it until Ticket Tailor is tested live.
6. Never invent an event ID, script URL or link.

The four events, ticket type names and descriptions are in `DEPLOY.md`. GoHighLevel reads the ticket type names, so keep them exact.

## 5. Ads and measurement

1. `SITE_CONFIG.tracking`: paste the IDs. Advertising tools load only after the visitor accepts cookies.
2. Events: view_item on each event page, click_book and begin_checkout on Book now, lead on every form, purchase on the thank you page, plus add_to_calendar and share. Each carries day, GBP value and quantity.
3. Paste the same Meta Pixel and GA4 IDs into Ticket Tailor (Box office settings, Tracking), where the payment happens.
4. Meta domain verification: `META_DOMAIN_VERIFY` at the top of `src/build.py`.

## 6. Facts you must not change

1. Ghana at 70 UK, The Platinum Jubilee Celebrations. Three separate events, each ticket valid for its event on its date only.
2. Gala GBP 275, early bird GBP 250. Never state how many early bird tickets exist. Festival GBP 50. Women of the Motherland GBP 150. Weekend Pass GBP 435.
3. Venue: Banking Hall, 14 Cornhill, London EC3V 3ND, moments from the Bank of England.
4. No booking fees. Bar is card only.
5. Gala dress: Royalty Kente or Black Tie, long gowns, no short dresses, black always welcome.
6. Photos never cut a head and are never low resolution.
7. British spelling, no dashes, no apostrophes, no exclamation marks. Write Ghana by name, never she or it.

## 7. Ground rules

1. Accounts belong to the business. You are a collaborator on GitHub, Cloudflare and Ticket Tailor.
2. No keys in browser code. No card details on the website.
3. One writer at a time. Tell Gigi before you push.
4. Before every deploy: `python3 src/build.py` ends with "built", `tickets.html` has no sideways scroll at 360 px, every Book now opens the right event.

## 8. Done means

1. Live on the business Cloudflare account, on `ghanaat70uk.com`.
2. Every form arrives in GoHighLevel.
3. One real payment and refund per event, with the right event and date on the ticket.
4. Gigi holds all access. Hand back what you no longer need.
