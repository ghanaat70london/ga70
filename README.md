# Ghana at 70 UK website

The UK celebration of the Ghana 70th Platinum Jubilee, Banking Hall, London, 5 to 7 March 2027.
Live address: https://ghanaat70uk.com

## Start here

1. Open `DEPLOY.md`. It takes the site live in 15 minutes on Cloudflare Pages.
2. To look at the site on your computer first: `python3 -m pip install -r src/requirements.txt`, then `python3 src/serve.py`, then open http://localhost:8000.
3. Full reference, including every form field sent to GoHighLevel: `src/README.md`.

## What you need to do

1. Push this folder to a private GitHub repository on the business account.
2. Connect it to Cloudflare Pages with the settings in `DEPLOY.md`.
3. Add one secret: `GHL_WEBHOOK_URL`.
4. Point `ghanaat70uk.com` at Cloudflare from GoDaddy.
5. When the Ticket Tailor events exist, paste their embed values into `src/site.js` and test one real payment per event.

Everything else is done: the pages, the photos, the forms, the booking flow, the Ticket Tailor wiring, the search and share tags, and the security headers.

## Why hosting is free

| Need | Cloudflare Pages free plan | This site |
| --- | --- | --- |
| Commercial site selling tickets | No personal use only rule, unlike Vercel Hobby | Promotes paid tickets |
| Visitors | Static requests free and unlimited | Every page, photo and file is static |
| Forms | 100,000 function requests a day | One request per form sent |
| Builds | 500 a month | One per commit |
| Files | 20,000 per site, 25 MiB each | About 320 files, largest 7 MB |
| Domains | 100 per project | ghanaat70uk.com and www |

Payment fees are separate: Ticket Tailor and Stripe charge per ticket sold. No booking fee is added for guests.

## Layout

```
functions/api/register.js   form handler, runs on Cloudflare at /api/register
src/build.py                builds every page into ghana-at-70/
src/site.js                 shared script, SITE_CONFIG at the top holds every setting
src/site.css                shared styles
src/serve.py                local server with a stand in form handler
src/images/                 photos, logos, venue and film stills
.python-version             Python 3.12 for the Cloudflare build
DEPLOY.md                   the 15 minute go live plan
```
