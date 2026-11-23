# Ghana at 70 UK website

The UK celebration of the Ghana 70th Platinum Jubilee, Banking Hall, London, 5 to 7 March 2027.
Main address: https://ghanaat70uk.com

## How the site works now

Since 24 November 2026 the website is the `site/` folder: finished HTML pages, `site.css`, `site.js` and
the images, taken from Gigi's approved preview. Vercel serves that folder as it is. There is no build step.

```
site/                       the website: every page, site.css, site.js, images, calendar files
site/site.js                SITE_CONFIG at the top: contact details, Ticket Tailor, prices, tracking
api/register.js             form handler on Vercel at /api/register, posts each form to GoHighLevel
functions/api/register.js   the same handler for Cloudflare Pages, kept in step
serve.py                    local server with a stand in form handler: python serve.py
vercel.json                 serve site/ with clean URLs and security headers
src/                        the old build (build.py), no longer used for the live site
```

## Change something

1. Edit the page in `site/` directly, for example `site/tickets.html`.
2. Check it: `python serve.py`, then open http://localhost:8000.
3. Commit and push. Vercel puts it live in about a minute.

Prices appear in two places: `earlyBird` and the event prices in `SITE_CONFIG` in `site/site.js` (used by the
booking panel), and in the page text. Change both together.

## Settings in Vercel

1. `GHL_WEBHOOK_URL`: the GoHighLevel inbound webhook. Every form posts there.
2. Optional email copies: `RESEND_API_KEY`, `FROM_EMAIL`, `NOTIFY_EMAIL`.
3. Domains: `ghanaat70uk.com` as the main domain, with `www` and `ghanaat70uk.co.uk` redirecting to it.

## Ticket Tailor

`SITE_CONFIG.ticketTailor` in `site/site.js` holds the box office `interopa` and the event IDs:
Gala 2542641, Ghana Day Festival 2542611, Women of the Motherland 2542630. Book now opens the Ticket Tailor
checkout in a pop up on the site, with the event page as the fallback. The Weekend Pass ID is left empty
until its price and the Saturday event are confirmed.

## Forms

Every form posts JSON to `/api/register` with a `type`. Each type has its pipeline, stage and tag in
`api/register.js`. Any field the handler does not name is still sent to GoHighLevel, in `details` and
`detailsText`, so nothing a guest types is lost.
