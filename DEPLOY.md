# Ghana at 70 UK website: live in 15 minutes on Cloudflare Pages

Host: Cloudflare Pages, free plan. Unlike Vercel Hobby, it has no personal use only rule, and visitor traffic is free and unlimited. Domain: `ghanaat70uk.com`, registered at GoDaddy. Forms: the Pages Function in `functions/api/register.js` posts every form and booking to GoHighLevel. Twelve minutes of work plus a three minute buffer.

Before you start, have these from Gigi:
1. Access to the business GitHub account, or a new private repository there.
2. Access to the business Cloudflare account. A free account is enough.
3. The GoHighLevel inbound webhook URL.
4. Access to the GoDaddy account that holds `ghanaat70uk.com`.

## The 15 minutes

| Clock | Task | Done when |
| --- | --- | --- |
| 00:00 | Unzip. In the `GA70UK_website` folder run the git commands below. Do not use the GitHub web upload: it stops at 100 files. | The repository shows `functions`, `src` and `DEPLOY.md` at the top |
| 00:03 | Cloudflare: Workers and Pages, Create, Pages, Connect to Git, pick the repository. Framework preset: None. Build command: `pip install -r src/requirements.txt && python3 src/build.py`. Build output directory: `ghana-at-70`. Root directory: leave empty. Save and Deploy. | The build log ends with `built` and a `pages.dev` address appears |
| 00:06 | The Pages project, Settings, Variables and Secrets: add `GHL_WEBHOOK_URL` as a secret, for Production and Preview. Deployments, the latest one, Retry deployment. | The redeploy has finished |
| 00:08 | Open the `pages.dev` address on a phone. Home page, Tickets page, one Book now. Send one enquiry from the Contact page. | Every page opens and the enquiry appears in GoHighLevel |
| 00:10 | Domain, see below. | The domain is added in Cloudflare and the nameservers are changed in GoDaddy |
| 00:12 | Buffer, then tell Gigi it is live. | |

```
git init -b main
git add .
git commit -m "Ghana at 70 UK website"
git remote add origin https://github.com/BUSINESS-ACCOUNT/ghana-at-70.git
git push -u origin main
```

Python: the repository holds `.python-version` set to 3.12, which the Cloudflare build reads. If the build ever reports the wrong Python, add the variable `PYTHON_VERSION` = `3.12` and retry.

## Connect ghanaat70uk.com

1. Cloudflare home, Add a domain, `ghanaat70uk.com`, Free plan. Cloudflare copies the existing DNS records from GoDaddy.
2. Check the copied list before going on. If the domain has email, the MX records and any TXT records (SPF, DKIM, verification) must be there, exactly as in GoDaddy. Add any that are missing.
3. Cloudflare shows two nameservers. In GoDaddy: My Products, the domain, DNS, Nameservers, Change, Enter my own nameservers, paste the two, Save.
4. Back in the Pages project: Custom domains, Set up a custom domain, `ghanaat70uk.com`. Then again for `www.ghanaat70uk.com`.
5. The switch usually takes under an hour, up to 24 hours. The `pages.dev` address works meanwhile.

The site already uses `https://ghanaat70uk.com` in every canonical tag, share tag, `sitemap.xml` and `robots.txt`. Nothing to change.

## Ticket Tailor, once the four events exist

1. In Ticket Tailor, open each event, Share event, Website embed code, the pop out button code.
2. Copy the values exactly into `SITE_CONFIG.ticketTailor` at the top of `src/site.js`: `widgetScript`, `boxOffice`, the four event IDs and the four public event links, plus the box office link. Never type an ID from memory.
3. Commit. Cloudflare redeploys in about a minute. Every Book now button then opens the Ticket Tailor checkout for that event.
4. Make one real card payment per event and refund it. Check that the ticket email and QR code name the right event and date.

Until then, Book now runs the built in booking form: it takes the booking, sends it to GoHighLevel and tells the guest how payment follows. Integration is complete only after step 4 passes on the live account.

### The four events to create in Ticket Tailor

Venue for all four: Banking Hall, 14 Cornhill, London EC3V 3ND.

| Event name | Date and time | Ticket types and prices |
| --- | --- | --- |
| The Royal Jubilee Gala | Friday 5 March 2027, 18:30 to 00:30 | Gala Early bird, GBP 250, quantity as Gigi sets it. Gala, GBP 275 |
| Ghana Day Festival | Saturday 6 March 2027, 11:00 to 18:00 | Festival, GBP 50 |
| Women of the Motherland | Sunday 7 March 2027, 11:00 to 18:30 | Women of the Motherland, GBP 150 |
| The Weekend Pass | Friday 5 to Sunday 7 March 2027 | Weekend Pass, GBP 435. One entry to each of the three events |

In the Gala Early bird ticket settings, switch off Show remaining tickets. Ghana at 70 never publishes how many early bird tickets exist. Each ticket description says: This ticket is valid for [event name] on [date] only. The Weekend Pass description says: One entry to each of three separate events, each on its own date. GoHighLevel reads the ticket type names, so keep them exact.

## Optional settings

1. Email copies of each form: add `RESEND_API_KEY`, `FROM_EMAIL` and `NOTIFY_EMAIL` next to `GHL_WEBHOOK_URL`.
2. Visitor counts without cookies: the Pages project, Metrics, Web Analytics, Enable.

## Run it on your own computer first

`python3 -m pip install -r src/requirements.txt`, then `python3 src/serve.py` and open http://localhost:8000. Forms work locally and print what they would send to GoHighLevel. To run the real Cloudflare function locally: `python3 src/build.py`, then `npx wrangler pages dev ghana-at-70`.

## Before launch, check these are true

1. `SITE_CONFIG.earlyBird.on` in `src/site.js` is true while the early bird is on sale. Set it to false when the early bird closes, so the site shows GBP 275. The site never shows how many early bird tickets exist.
2. `SITE_CONFIG.left` stays empty unless the numbers are real. Never invent scarcity.

## Updates after launch

Every commit rebuilds the site in about a minute. The team can edit these files on GitHub in the browser:

1. Announce a partner: `src/partners.json`, with the logo in `src/images/partners/`. The steps are at the top of that file. The build stops with a plain message if anything is missing, so nothing broken goes live.
2. Contact details, Ticket Tailor values, early bird on or off: `src/site.js`, the `SITE_CONFIG` block at the top.
3. Prices and ticket names: the `T_GALA`, `T_DAY` and `T_SUN` lines in `src/build.py`, and the `DAYS` prices in `src/site.js`.
4. A new photo of people: add it, run `python3 src/faces.py`, commit `src/faces.json` with the photo.

## Rules

1. Accounts belong to the business. Rishit is a collaborator on GitHub, Cloudflare and Ticket Tailor, never the owner.
2. No keys in browser code. Server keys live only in the Cloudflare project variables.
3. No card details on the website. Ticket Tailor and Stripe take payment.
4. Do not edit the built `ghana-at-70` folder. It is rebuilt on every deploy.
