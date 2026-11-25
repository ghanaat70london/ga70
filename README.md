# Ghana at 70 UK website

The Platinum Jubilee of Ghana, Banking Hall, London, 5 to 7 March 2027.
Live at https://ghanaat70uk.com. Hosted on Vercel from `main`. No build step.

## Who does what

1. **Claude builds and ships the website.** Every change goes through a pull request, passes the automatic Site checks, is merged and confirmed live on Vercel. Nothing waits for review.
2. **The developer does set up only:** Vercel settings, keys, domains, and anything that needs a login Claude cannot use. Open setup jobs are GitHub issues titled for the developer. Do the issue, comment Live, close it.
3. **Gigi decides.** Her standing decisions are in the project docs.

## Where things are

```
site/                     the website: 25 pages, site.css, site.js, images
site/site.js              SITE_CONFIG at the top: contacts, Ticket Tailor event ids, prices, tracking ids
api/register.js           every form posts here, then to GoHighLevel and the hello@ inbox
api/tt-webhook.js         Ticket Tailor order webhook
scripts/check_site.py     the automatic checks, run on every pull request
scripts/bump_version.py   refreshes the ?v= cache versions on site.css and site.js
serve.py                  local preview with a stand in form handler: python serve.py
vercel.json               clean URLs, security headers, cache rules
```

## Signatures: never remove, never flatten

1. The golden tickets: black for the Gala, green for Ghana Day, ruby for Women of the Motherland.
2. The RSVP envelope with its wax seal, with full depth and shadow, on each event page.
3. The royal envelope on the home page: the seal breaks, the Kente flap opens, the invitation comes forward once.
4. What is your royal name? on the home page: the Akan day name invitation in the shape of Ghana.
5. The Kente drapes on the home hero, the woven Kente bands, the tricolour bars, the diamond dividers and the countdown.
6. The Banking Hall gallery and the GHANA name mark in the footer.
7. The dates above the days in the header: 5 March, 6 March, 7 March.

Each one is marked SIGNATURE in `site/site.css`.

## The site today

1. Only the Gala is on sale. Every Book your tickets button opens the Gala booking.
2. Ghana Day and Women of the Motherland show their tickets and register your interest only, with no price.
3. Readability: reading text 17.5px regular, no label under 13px, display type Cormorant 400 and 500.
   The READABILITY block is last in `site/site.css` on purpose, so it wins.
4. Adinkra symbols on the home envelope come from adinkra-icons (Apache License 2.0), credited in
   `site/images/brand/adinkra-tile.svg`.

## Rules that keep the site safe

1. Never commit to `main`. One branch and one pull request per release.
2. Run `python scripts/bump_version.py` then `python scripts/check_site.py` before every commit.
3. Do not delete repeated CSS rules automatically. Order matters, and it breaks the header menu.
4. No stock photographs, no white clothing, Quophi Akotuah images only on the fashion page and his partner card.
5. Women of the Motherland and Ghana Day are register your interest only. Only the Gala is on sale.
6. No keys, tokens or passwords in any file.

## Automatic checks

`scripts/check_site.py` fails a pull request on: Reserve wording, Sobolo, capacity or scarcity claims, the pound
sign, dashes, apostrophes, exclamation marks, wrong fixed times, broken links, missing images, links to missing
sections, ids used twice, invalid structured data, missing titles or descriptions, unused images, stale cache
versions and anything that looks like a secret. A red cross means do not merge.

## Settings in Vercel (developer)

1. `GHL_WEBHOOK_URL`: the GoHighLevel inbound webhook. Every form posts there.
2. `RESEND_API_KEY`, `FROM_EMAIL`, `NOTIFY_EMAIL` (hello@ghanaat70uk.com): email copies of every registration.
3. Domains: `ghanaat70uk.com` main, `www` and `ghanaat70uk.co.uk` redirect to it.

## Ticket Tailor

Box office `interopa`. Gala 2542641, Ghana Day Festival 2542611, Women of the Motherland 2542630.
Only the Gala links to Ticket Tailor. Ghana Day and Sunday route to their register your interest forms through
`SITE_CONFIG.register`.

## Forms

Every form posts JSON to `/api/register` with a `type`. Each type has its pipeline, stage, tag and reply in
`api/register.js`. Any field the handler does not name is still sent to GoHighLevel in `details` and
`detailsText`, so nothing a guest types is lost.
