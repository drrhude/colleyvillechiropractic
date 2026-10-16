# Colleyville Chiropractic | CVC Spine & Sport

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
Page content lives in `src/*.html`. Shared header, footer and styles are in `tools/build.py` and `assets/`. After editing, run `python3 tools/build.py` and commit the output.

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
