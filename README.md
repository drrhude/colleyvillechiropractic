# Colleyville Chiropractic | CVC Spine

Static site for www.colleyvillechiropractic.com. Booking runs through Jane; online programs and member login run through RESET (resethybridrecovery.com) and GoHighLevel.

## Status: not live yet
The domain still points to Squarespace. Do not switch DNS until every page below exists here.

## URL map (keep these paths to protect Google rankings)
| Current URL | New site |
| --- | --- |
| / | index.html (built) |
| /services | Chiropractic page (built) |
| /shockwavetherapy | built |
| /neuropath | built |
| /functionalrehab | built |
| /massagetherapy | built |
| /guthealth | built |
| /team | built |
| /pricing | built |
| /faqs | built |
| /contact | built |
| /affiliate | built |
| /shop | redirect to RESET programs |
| /npmc | redirect to RESET neck |
| /spmc-1 | redirect to RESET shoulder |
| /gpmc | redirect to RESET golf |
| /pfmc | redirect to RESET programs (no pelvic floor program yet) |
| /account/login | redirect to member portal |

## Editing pages
- Treatment pages (15): edit `tools/content.py`
- FAQ page: edit `tools/faqs.py`
- Home, Our Approach, Team, Pricing, Contact, Affiliate, 404: edit `src/*.html`
- Header, footer, schema, sitemap.xml and llms.txt: `tools/build.py`
- Styles and animation: `assets/site.css`, `assets/site.js`

After any edit run `python3 tools/build.py` and commit the output. Headings are converted to Title Case automatically.

## New pages (no redirect needed, they didn't exist before)
/treatments/ (services hub), /our-approach/, /cupping-therapy/, /myofascial-release/, /red-light-therapy/,
/electrical-stimulation/, /therapeutic-ultrasound/, /pediatric-chiropractic/, /prenatal-chiropractic/,
/sports-chiropractic/, /senior-chiropractic/

## SEO / AEO
- Schema.org graph on every page: Chiropractor (clinic), WebSite, WebPage or MedicalWebPage, BreadcrumbList
- Treatment pages: MedicalTherapy or MedicalProcedure, FAQPage, reviewed by Dr. Rudy with a review date
- Answer-first "What is ...?" definitions on every treatment page
- robots.txt welcomes Google, Bing and AI assistants; llms.txt summarizes the clinic for AI search
- sitemap.xml regenerates with lastmod on every build

## Hosting
Recommended: Cloudflare Pages connected to this repo, so `_redirects` gives true 301s.
GitHub Pages also works: each redirected path has an index.html stub. Add a CNAME file
containing `www.colleyvillechiropractic.com` only on launch day.

## Launch checklist
1. Build the remaining pages above.
2. Add assets (see assets/README.md).
3. Fill the Jane treatment links in index.html (`const JANE`).
4. Point DNS, submit sitemap.xml in Google Search Console.
5. Keep Squarespace active 30 days as a rollback.

## Analytics + conversion tracking
- Paste your GA4 Measurement ID into `GA4_ID` at the top of `tools/build.py`, then run `python3 tools/build.py`. Blank = no tracking loads.
- Events sent automatically (assets/site.js): `book_click` (every Jane button, with `booking_type`), `call_click`, `text_click`, `generate_lead` (partner form).
- In GA4, mark `book_click`, `call_click` and `generate_lead` as key events.
- Actual appointment completions happen inside Jane, so they can't be tracked from this site. Use Jane's reports for booked appointments.

## Staff Product Desk (/staff/)
Password-locked BPA product lookup + program builder with a patient PDF (no costs on it).
Not linked from the site, `noindex`, and not in the sitemap.
- `staff/data.enc.json` is the product database, AES-256-GCM encrypted (PBKDF2-SHA256, 310k rounds).
  The repo is public, so **never commit the plaintext products file**. Without the password the file is unreadable.
- Markup, custom costs and saved programs are stored per browser, encrypted with the same password.
- To update costs or change the password: open /staff/ > Settings > "Download data.enc.json", then replace
  `staff/data.enc.json` here with the downloaded file. Or from a plaintext copy:
  `node tools/staff_encrypt.mjs products.json "password"`.

## Photos
- Web-ready images live in `assets/img/` as `<name>-<width>.webp`. Treatment-page photos are mapped in `PHOTOS` in `tools/build.py`; pages without one show a branded "At a Glance" panel.
- Hero video: `assets/hero.mp4` (trimmed, captions cropped, no audio) with `assets/hero-poster.webp`.
