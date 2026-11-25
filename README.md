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
scripts/check_site.py       the release checks, also run on every pull request
serve.py                    local server with a stand in form handler: python serve.py
vercel.json                 serve site/ with clean URLs and security headers
```

## Change something: the release rhythm

Two releases a week, Tuesday and Friday. One release branch and one pull request each time.

1. Every change is a commit on the open release branch, never on `main`, never a new pull request.
2. Each commit adds one numbered line to the pull request list. The list always matches the branch.
3. Cut off: 18:00 the evening before release day (Monday for Tuesday, Thursday for Friday).
4. Release day: the developer reviews the one list, checks the Vercel preview, merges once.
5. After the merge the next release branch starts from the new `main`, so nothing conflicts.
6. Anything waiting for a decision sits in its own pull request titled HOLD. It is never mixed into a release.
7. Before a commit: `python scripts/check_site.py`, then `python serve.py` and look at the page on phone and desktop.

## Automatic checks

Every pull request runs `scripts/check_site.py` on GitHub (`.github/workflows/checks.yml`). A red cross means do not merge.
It fails on: Reserve wording, Sobolo, capacity or scarcity claims, selling the venue, the pound sign, dashes,
apostrophes, exclamation marks, wrong fixed times (carriages 00:30, drums and DJ 11:00, Ghana Day 08:30 to 17:00),
broken links, missing images, links to missing sections, ids used twice, invalid structured data, missing titles
or descriptions, unused images (dead files) and anything that looks like a secret key. It lists, without failing,
any change to api, functions, vercel.json or SITE_CONFIG.ticketTailor so the developer reviews it.

Prices appear in two places: `earlyBird` and the event prices in `SITE_CONFIG` in `site/site.js` (used by the
booking panel), and in the page text. Change both together.

## Settings in Vercel

1. `GHL_WEBHOOK_URL`: the GoHighLevel inbound webhook. Every form posts there.
2. Optional email copies: `RESEND_API_KEY`, `FROM_EMAIL`, `NOTIFY_EMAIL`.
3. Domains: `ghanaat70uk.com` as the main domain, with `www` and `ghanaat70uk.co.uk` redirecting to it.

## Ticket Tailor

`SITE_CONFIG.ticketTailor` in `site/site.js` holds the box office `interopa` and the event IDs:
Gala 2542641, Ghana Day Festival 2542611, Women of the Motherland 2542630. Book now opens the Ticket Tailor
checkout in a pop up on the site, with the event page as the fallback. There is no Weekend Pass.

## Forms

Every form posts JSON to `/api/register` with a `type`. Each type has its pipeline, stage and tag in
`api/register.js`. Any field the handler does not name is still sent to GoHighLevel, in `details` and
`detailsText`, so nothing a guest types is lost.
