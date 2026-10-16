"""Builds every page of the site.
- Hand-written pages: src/*.html (start with <!--meta {...} -->)
- Treatment pages, services hub, FAQ page, sitemap.xml and llms.txt: generated from tools/content.py
Run: python3 tools/build.py"""
import json, re, pathlib, datetime, html
from content import SERVICES, SERVICE_BY_PATH, BLURB, REVIEWED
from faqs import FAQ_GROUPS

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.colleyvillechiropractic.com/"
JANE = "https://colleyvillechiropractic.janeapp.com/"
NAME = "Colleyville Chiropractic | CVC Spine"
TODAY = datetime.date.today().isoformat()
ARROW = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>'

CLINIC = {
  "@type": "Chiropractor", "@id": SITE + "#clinic",
  "name": NAME, "alternateName": ["Colleyville Chiropractic", "CVC Spine"],
  "url": SITE, "logo": SITE + "assets/logo-olive.png", "image": SITE + "assets/og.jpg",
  "telephone": "+1-817-420-7696", "faxNumber": "+1-866-499-4260",
  "priceRange": "$$", "currenciesAccepted": "USD",
  "paymentAccepted": "Cash, Credit Card, Debit Card, HSA, FSA, CareCredit, Cherry",
  "address": {"@type": "PostalAddress", "streetAddress": "1001 Glade Rd, Suite 120", "addressLocality": "Colleyville", "addressRegion": "TX", "postalCode": "76034", "addressCountry": "US"},
  "hasMap": "https://www.google.com/maps/search/?api=1&query=1001+Glade+Rd+Suite+120+Colleyville+TX+76034",
  "areaServed": [{"@type": "City", "name": c} for c in ["Colleyville", "Southlake", "Keller", "North Richland Hills", "Grapevine", "Hurst", "Euless", "Bedford"]],
  "knowsLanguage": ["en", "es"], "availableLanguage": ["English", "Spanish"],
  "medicalSpecialty": "Chiropractic",
  "openingHoursSpecification": [
    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Wednesday"], "opens": "09:00", "closes": "18:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Tuesday", "opens": "14:00", "closes": "18:00"},
    {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "09:00", "closes": "12:00"}],
  "employee": {"@id": SITE + "team/#dr-rudy"},
  "potentialAction": {"@type": "ReserveAction", "target": JANE, "name": "Book an appointment"},
}
DOCTOR = {"@type": "Person", "@id": SITE + "team/#dr-rudy", "name": "Dr. Jon \"Rudy\" Urrutia", "honorificSuffix": "DC",
          "jobTitle": "Chiropractor", "worksFor": {"@id": SITE + "#clinic"}, "knowsLanguage": ["en", "es"], "url": SITE + "team/",
          "alumniOf": {"@type": "CollegeOrUniversity", "name": "Parker University", "address": {"@type": "PostalAddress", "addressLocality": "Dallas", "addressRegion": "TX"}},
          "hasCredential": [{"@type": "EducationalOccupationalCredential", "credentialCategory": "degree", "name": "Doctor of Chiropractic", "recognizedBy": {"@type": "CollegeOrUniversity", "name": "Parker University"}},
                            {"@type": "EducationalOccupationalCredential", "credentialCategory": "certification", "name": "Advanced Activator Certification"}],
          "description": "U.S. Coast Guard veteran (10 years active duty). Doctor of Chiropractic, Parker University, 2022. Advanced Activator certified."}

# ---------------------------------------------------------------- title case
SMALL = {"a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "by", "in", "of", "as", "vs", "with", "from", "per", "via"}
def _tc_word(w, first):
    m = re.match(r"^([^A-Za-z]*)([A-Za-z][A-Za-z'’-]*)(.*)$", w)
    if not m: return w
    pre, core, post = m.groups()
    if any(ch.isupper() for ch in core[1:]) and core[0].isupper(): return w
    if core[0].isupper() and '-' not in core: return w
    if core.lower() in SMALL and not first: return w
    parts = core.split("-")
    return pre + "-".join(p[:1].upper() + p[1:] for p in parts) + post

def title_case_heading(inner):
    out, first = [], True
    for chunk in re.split(r"(<[^>]+>)", inner):
        if chunk.startswith("<"):
            out.append(chunk); continue
        words = re.split(r"(\s+)", chunk)
        for i, w in enumerate(words):
            if w.strip() and not w.isspace():
                words[i] = _tc_word(w, first); first = False
        out.append("".join(words))
    return "".join(out)

def apply_title_case(page):
    return re.sub(r"(<(h[1-3]|caption)\b[^>]*>)(.*?)(</\2>)",
                  lambda m: m.group(1) + title_case_heading(m.group(3)) + m.group(4), page, flags=re.S)

# ---------------------------------------------------------------- shell
def crumbs_ld(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(trail)]}

def head(m, r):
    url = SITE + (m["path"] + "/" if m["path"] else "")
    graph = [CLINIC, {"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": NAME, "inLanguage": "en-US", "publisher": {"@id": SITE + "#clinic"}}]
    page_type = m.get("page_type", "WebPage")
    webpage = {"@type": page_type, "@id": url + "#page", "url": url, "name": m["title"], "description": m["desc"],
               "isPartOf": {"@id": SITE + "#site"}, "about": {"@id": SITE + "#clinic"}, "inLanguage": "en-US", "dateModified": TODAY}
    if m.get("doctor"): graph.append(DOCTOR)
    if m.get("reviewed"):
        webpage["reviewedBy"] = {"@id": SITE + "team/#dr-rudy"}; webpage["lastReviewed"] = m["reviewed"]
        graph.append(DOCTOR)
    graph.append(webpage)
    if m.get("trail"): graph.append(crumbs_ld(m["trail"]))
    graph += m.get("ld", [])
    ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>"
    robots = '<meta name="robots" content="noindex">\n' if m.get("noindex") else '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">\n'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(m['title'])}</title>
<meta name="description" content="{html.escape(m['desc'])}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{html.escape(m['title'])}">
<meta property="og:description" content="{html.escape(m['desc'])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}assets/og.jpg">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="US-TX">
<meta name="geo.placename" content="Colleyville">
<meta name="theme-color" content="#22281F">
<link rel="icon" href="{r}assets/cc-mark-olive.png">
<link rel="apple-touch-icon" href="{r}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400&family=Hanken+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/site.css">
{ld}
</head>"""

def mega(r):
    t = "".join(f'<li><a href="{r}{s["path"]}/">{s["short"]}</a></li>' for s in SERVICES if s["group"] == "treatments")
    p = "".join(f'<li><a href="{r}{s["path"]}/">{s["short"]}</a></li>' for s in SERVICES if s["group"] == "people")
    return f"""<div class="has-menu">
        <button aria-expanded="false" aria-controls="mega">Services <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M1.5 3.5 5 7l3.5-3.5"/></svg></button>
        <div class="mega" id="mega">
          <div><h4>Treatments</h4><ul class="cols">{t}</ul></div>
          <div><h4>Who We Care For</h4><ul>{p}<li><a href="https://resethybridrecovery.com/" target="_blank" rel="noopener">Online Programs (RESET)</a></li></ul></div>
          <div class="all"><a href="{r}treatments/">See All Services</a></div>
        </div>
      </div>"""

def header(r, active):
    def a(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""<body class="home-page">
<a class="skip" href="#main">Skip to content</a>
<!-- Confirm the $47 offer is live before launch -->
<div class="offer">New patients: first visit and exam for $47. <a href="{JANE}" data-jane="special">Claim It</a></div>
<header class="site" id="top">
  <div class="wrap bar">
    <a class="brand" href="{r}" aria-label="Colleyville Chiropractic home">
      <img class="cc" src="{r}assets/cc-mark-cream.png" alt="" width="34" height="44">
      <span class="name">Colleyville Chiropractic<small>CVC Spine</small></span>
    </a>
    <nav class="main" id="nav" aria-label="Main">
      {a(r, "Home", "home")}
      {mega(r)}
      {a(r + "our-approach/", "Our Approach", "approach")}
      {a(r + "pricing/", "Pricing + Insurance", "pricing")}
      {a(r + "team/", "Team", "team")}
      {a(r + "faqs/", "FAQs", "faqs")}
    </nav>
    <a class="btn btn-primary header-cta" href="{JANE}" data-jane="newPatient">Book a Visit</a>
    <button class="menu-btn" aria-label="Open menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
  </div>
</header>"""

def footer(r):
    t = "".join(f'<li><a href="{r}{s["path"]}/">{s["short"]}</a></li>' for s in SERVICES if s["group"] == "treatments")
    p = "".join(f'<li><a href="{r}{s["path"]}/">{s["short"]}</a></li>' for s in SERVICES if s["group"] == "people")
    return f"""<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <a href="{r}" aria-label="Colleyville Chiropractic home"><img class="foot-logo" src="{r}assets/logo-cream.png" alt="Colleyville Chiropractic logo" width="150" height="141"></a>
        <p style="margin-top:18px;max-width:34ch">1001 Glade Rd, Suite 120<br>Colleyville, TX 76034<br><a href="tel:+18174207696">(817) 420-7696</a></p>
        <p style="margin-top:12px">Mon + Wed 9 to 6 · Tue 2 to 6<br>Thu by appointment · Sat 9 to 12</p>
      </div>
      <div><h4>Treatments</h4><ul class="cols">{t}</ul></div>
      <div><h4>Who We Care For</h4><ul>{p}</ul><h4 style="margin-top:28px">Clinic</h4><ul><li><a href="{r}our-approach/">Our Approach</a></li><li><a href="{r}team/">Team</a></li><li><a href="{r}pricing/">Pricing + Insurance</a></li><li><a href="{r}faqs/">FAQs</a></li><li><a href="{r}contact/">Contact</a></li><li><a href="{r}affiliate/">Partner With Us</a></li></ul></div>
      <div><h4>Connect</h4><ul><li><a href="tel:+18174207696">Call (817) 420-7696</a></li><li><a href="sms:+18174207696">Text Us</a></li><li><a href="https://resethybridrecovery.com/" target="_blank" rel="noopener">RESET Online Programs</a></li><li><a href="#" data-portal>Member Login</a></li></ul></div>
    </div>
    <div class="legal"><span>© 2026 {NAME}</span><span>Se habla español · In-network with BCBS of Texas</span></div>
  </div>
</footer>
<div class="dock" aria-label="Quick actions">
  <a class="btn btn-ghost" href="tel:+18174207696">Call</a>
  <a class="btn btn-primary" href="{JANE}" data-jane="newPatient">Book a Visit</a>
</div>
<!-- GHL text widget goes here (paste the existing chat widget script) -->
<script src="{r}assets/site.js"></script>
</body>
</html>
"""

def write(m, body):
    r = m["root"] if "root" in m else ("" if m["path"] == "" else "../" * (m["path"].count("/") + 1))
    body = body.replace("{{root}}", r).replace("{{jane}}", JANE)
    page = head(m, r) + "\n" + header(r, m.get("nav", "")) + '\n<main id="main">\n' + body + "\n</main>\n" + footer(r)
    page = apply_title_case(page)
    out = ROOT / (m["file"] if "file" in m else (m["path"] + "/index.html" if m["path"] else "index.html"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    return out

# ---------------------------------------------------------------- pieces
def esc(s): return html.escape(s, quote=False)

def faq_html(items):
    return '<div class="faq">\n' + "\n".join(
        f'  <details><summary>{esc(q)}</summary><div class="a"><p>{esc(a)}</p></div></details>' for q, a in items) + "\n</div>"

def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

def price_html(p):
    cap, rows = p
    trs = "".join(f"<tr><th>{esc(a)}</th><td class=\"amt\">{esc(b)}</td></tr>" for a, b in rows)
    return f'<table class="price-table"><caption>{esc(cap)}</caption><tbody>{trs}</tbody></table>'

def related_html(keys):
    cards = []
    for k in keys:
        s = SERVICE_BY_PATH[k]
        cards.append(f'<a href="{{{{root}}}}{k}/" class="reveal"><h3>{s["name"]}</h3><p>{BLURB[k]}</p><span class="go">Learn more {ARROW}</span></a>')
    return '<div class="related">' + "".join(cards) + "</div>"

def byline():
    return f'''<div class="byline"><span class="dot"><img src="{{{{root}}}}assets/cc-mark-olive.png" alt=""></span><span>Reviewed by <b>Dr. Jon "Rudy" Urrutia, DC</b><br>Updated {REVIEWED}</span></div>'''

def ticks(items): return '<ul class="ticks">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"

def cta(s):
    k, label = s["book"]
    return f'''<section class="cta-band">
  <div class="wrap"><div class="inner reveal">
    <div><h2>Ready to Get Started?</h2><p>Book online in under a minute, or call or text (817) 420-7696. Se habla español.</p></div>
    <div class="btns"><a class="btn btn-primary" href="{{{{jane}}}}" data-jane="{k}">{label}</a><a class="btn btn-ghost" href="tel:+18174207696">Call Us</a></div>
  </div></div>
</section>'''

def service_page(s):
    lines = " ".join(f'<span class="line"><span>{esc(l)}</span></span>' for l in s["h1"])
    k, label = s["book"]
    actions = f'<a class="btn btn-primary" href="{{{{jane}}}}" data-jane="{k}">{label}</a>'
    actions += (f'<a class="btn btn-ghost" href="{{{{jane}}}}" data-jane="{s["alt"][0]}">{s["alt"][1]}</a>' if s.get("alt")
                else '<a class="btn btn-ghost" href="tel:+18174207696">Call (817) 420-7696</a>')
    facts = ("<ul class=\"facts\">" + "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in s["facts"]) + "</ul>") if s["facts"] else ""
    crumb_label = "Who We Care For" if s["group"] == "people" else "Services"
    more = "".join(f"<p>{esc(p)}</p>" for p in s["more"])
    pricing = ""
    if s.get("pricing"):
        pricing = f'<div class="card reveal">{price_html(s["pricing"])}<p class="note">Members save on most services. <a href="{{{{root}}}}pricing/">See memberships and all pricing</a></p></div>'
    else:
        pricing = f'<div class="card reveal"><h3>Pricing</h3>{s.get("extra","")}<p class="note"><a href="{{{{root}}}}pricing/">See all pricing</a></p></div>'
    return f'''<section class="page-hero">
  <div class="wrap">
    <a class="crumb" href="{{{{root}}}}treatments/">{crumb_label}</a>
    <h1>{lines}</h1>
    <p class="lede">{esc(s["lede"])}</p>
    <div class="actions">{actions}</div>
    {facts}
  </div>
</section>

<section>
  <div class="wrap split">
    <div class="reveal">
      <h2>What Is {esc(s["name"])}?</h2>
      <div class="answer"><p class="lead">{esc(s["what"])}</p></div>
      <div style="margin-top:22px">{more}</div>
      {byline()}
    </div>
    <div class="photo reveal"><span class="ph">Photo needed: {esc(s["photo"])}</span></div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="intro reveal">
      <h2>What It Helps With</h2>
      <p>Your exam tells us whether {esc(s["short"].lower() if s["group"]=="treatments" else "this care")} is the right fit for you.</p>
    </div>
    <ul class="tags reveal">{"".join(f"<li>{esc(h)}</li>" for h in s["helps"])}</ul>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="cols2">
      <div class="reveal"><h3>What to Expect</h3>{ticks(s["expect"])}</div>
      <div class="reveal"><h3>After Your Visit</h3>{ticks(s["after"])}</div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap split">
    <div class="reveal">
      <h2>Is It Right for You?</h2>
      <p>Tell us before treatment if any of these apply:</p>
      {ticks(s["caution"])}
      <div class="evidence"><b>What the research says.</b> {esc(s["evidence"])}</div>
    </div>
    {pricing}
  </div>
</section>

<section>
  <div class="wrap">
    <div class="intro reveal"><h2>Common Questions</h2><p>Have another question? Call or text (817) 420-7696.</p></div>
    <div class="reveal">{faq_html(s["faqs"])}</div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="intro reveal"><h2>Often Paired With</h2><p>Most plans combine two or three treatments.</p></div>
    {related_html(s["related"])}
  </div>
</section>

{cta(s)}'''

def service_meta(s):
    group = "Who We Care For" if s["group"] == "people" else "Services"
    therapy = {"@type": s["schema"], "name": s["name"], "description": s["what"], "url": SITE + s["path"] + "/",
               "provider": {"@id": SITE + "#clinic"}}
    return {"path": s["path"], "nav": "services", "title": s["title"], "desc": s["desc"], "page_type": "MedicalWebPage",
            "reviewed": "2026-10-16", "trail": [("Home", ""), (group, "treatments/"), (s["name"], s["path"] + "/")],
            "ld": [therapy, faq_ld(s["faqs"])]}

def hub_page():
    def grid(group):
        cards = "".join(f'<a href="{{{{root}}}}{s["path"]}/" class="reveal"><h3>{s["name"]}</h3><p>{BLURB[s["path"]]}</p><span class="go">Learn more {ARROW}</span></a>' for s in SERVICES if s["group"] == group)
        return f'<div class="related">{cards}</div>'
    body = f'''<section class="page-hero">
  <div class="wrap">
    <a class="crumb" href="{{{{root}}}}">Home</a>
    <h1><span class="line"><span>Our Services</span></span></h1>
    <p class="lede">Chiropractic care, shockwave, rehab, recovery therapies and more, all under one roof in Colleyville. Not sure where to start? Book a new patient visit and we'll build the plan with you.</p>
    <div class="actions"><a class="btn btn-primary" href="{{{{jane}}}}" data-jane="newPatient">Book a New Patient Visit</a><a class="btn btn-ghost" href="tel:+18174207696">Call (817) 420-7696</a></div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="hub-group"><h2 class="reveal">Treatments</h2>{grid("treatments")}</div>
    <div class="hub-group"><h2 class="reveal">Who We Care For</h2>{grid("people")}</div>
  </div>
</section>
<section class="reset" aria-label="RESET online programs">
  <div class="wrap"><div class="inner reveal">
    <div><h2>Not Near Colleyville?</h2><p>RESET brings our rehab and training programs online, so you can follow the same approach from anywhere.</p></div>
    <a class="btn btn-primary" href="https://resethybridrecovery.com/#programs" target="_blank" rel="noopener">Explore RESET Programs</a>
  </div></div>
</section>'''
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + s["path"] + "/", "name": s["name"]} for i, s in enumerate(SERVICES)]
    m = {"path": "treatments", "nav": "services", "title": "Chiropractic + Rehab Services in Colleyville, TX | CVC Spine",
         "desc": "Chiropractic, shockwave, NeuroPath, rehab, massage, cupping and red light therapy in Colleyville, TX. Care for kids, athletes, expecting moms and seniors.",
         "page_type": "CollectionPage", "trail": [("Home", ""), ("Services", "treatments/")], "ld": [{"@type": "ItemList", "itemListElement": items}]}
    return m, body

def faq_page():
    groups = "\n".join(f'''    <div class="faq-group reveal" id="{re.sub(r"[^a-z]+","-",g.lower()).strip("-")}">
      <h2>{esc(g)}</h2>
      {faq_html(items)}
    </div>''' for g, items in FAQ_GROUPS)
    toc = "".join(f'<li><a href="#{re.sub(r"[^a-z]+","-",g.lower()).strip("-")}">{esc(g)}</a></li>' for g, _ in FAQ_GROUPS)
    body = f'''<section class="page-hero">
  <div class="wrap">
    <a class="crumb" href="{{{{root}}}}">Home</a>
    <h1><span class="line"><span>Questions,</span></span> <span class="line"><span>Answered</span></span></h1>
    <p class="lede">Straight answers about visits, insurance, pricing, memberships and every treatment we offer. Don't see yours? Call or text (817) 420-7696.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <ul class="tags reveal" style="margin-bottom:clamp(40px,6vw,64px)">{toc}</ul>
{groups}
  </div>
</section>
<section class="cta-band">
  <div class="wrap"><div class="inner reveal">
    <div><h2>Still Have a Question?</h2><p>Call or text us. A real person answers.</p></div>
    <div class="btns"><a class="btn btn-primary" href="tel:+18174207696">Call (817) 420-7696</a><a class="btn btn-ghost" href="sms:+18174207696">Text Us</a></div>
  </div></div>
</section>'''
    allq = [qa for _, items in FAQ_GROUPS for qa in items]
    m = {"path": "faqs", "nav": "faqs", "title": "FAQs | Insurance, Pricing + Treatments | CVC Spine",
         "desc": "Answers about your first visit, BCBS insurance, pricing, memberships, shockwave therapy, adjustments, kids, pregnancy and more at Colleyville Chiropractic.",
         "page_type": "WebPage", "trail": [("Home", ""), ("FAQs", "faqs/")], "ld": [faq_ld(allq)]}
    return m, body

# ---------------------------------------------------------------- build
built = []
for src in sorted((ROOT / "src").glob("*.html")):
    text = src.read_text()
    m = json.loads(re.match(r"<!--meta (.*?) -->\n", text, re.S).group(1))
    built.append(write(m, text.split("-->\n", 1)[1]))
for s in SERVICES:
    built.append(write(service_meta(s), service_page(s)))
built.append(write(*hub_page()))
built.append(write(*faq_page()))

# sitemap
paths = sorted({str(p.relative_to(ROOT)).replace("index.html", "") for p in built if p.name != "404.html"})
urls = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in paths)
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')

# llms.txt (summary for AI assistants)
svc_lines = "\n".join(f"- [{s['name']}]({SITE}{s['path']}/): {s['what']}" for s in SERVICES)
(ROOT / "llms.txt").write_text(f"""# {NAME}

> Chiropractic clinic in Colleyville, Texas, serving the community for 25 years. Chiropractic care, shockwave therapy, the NeuroPath neuropathy program, functional rehab, massage and recovery therapies for kids, athletes, expecting moms, seniors and everyone in between. In-network with Blue Cross Blue Shield of Texas. Bilingual (English and Spanish).

- Address: 1001 Glade Rd, Suite 120, Colleyville, TX 76034
- Phone (call or text): (817) 420-7696
- Hours: Monday and Wednesday 9am to 6pm, Tuesday 2pm to 6pm, Thursday by appointment, Friday closed, Saturday 9am to 12pm, Sunday closed
- Booking: {JANE}
- Chiropractor: Dr. Jon "Rudy" Urrutia, DC. Bachelor's degree and Doctor of Chiropractic from Parker University (2022), Advanced Activator certified, 10 years active duty U.S. Coast Guard
- New patient special: $47. New patient exam $120. Follow-up visit $60 ($45 member).
- Memberships: CVC Care $49/year, CVC Wellness $89/month, CVC Complete $169/month. Wellness and Complete include 2 recovery therapies a month (cupping, vibration plate or myofascial release).
- Online programs: https://resethybridrecovery.com/

## Services
{svc_lines}

## Key pages
- [Our Approach]({SITE}our-approach/): Dr. Rudy's care philosophy, "movement is medicine"
- [Pricing and Insurance]({SITE}pricing/)
- [FAQs]({SITE}faqs/)
- [Team]({SITE}team/)
- [Contact]({SITE}contact/)
""")
print(len(built), "pages built")
