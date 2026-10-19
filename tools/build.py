"""Builds every page of the site.
- Hand-written pages: src/*.html (start with <!--meta {...} -->)
- Treatment pages, services hub, FAQ page, sitemap.xml and llms.txt: generated from tools/content.py
Run: python3 tools/build.py"""
import json, re, pathlib, datetime, html
from content import SERVICES, SERVICE_BY_PATH, BLURB, REVIEWED
from content_es import ES, BLURB_ES, REVIEWED_ES
from faqs import FAQ_GROUPS

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.colleyvillechiropractic.com/"
JANE = "https://colleyvillechiropractic.janeapp.com/"
NAME = "Colleyville Chiropractic | CVC Spine"
# Analytics: paste your GA4 Measurement ID (looks like G-XXXXXXXXXX). Leave blank to load no tracking.
GA4_ID = ""
HOME_FAQ = ["What happens at my first visit?", "How much is the first visit?", "Do you take insurance?",
            "Do I need a referral to see a chiropractor?", "Do adjustments hurt?", "How many visits will I need?"]
# Social profiles: add a URL to show its icon in the footer and in Google's business data (schema sameAs). Blank = hidden.
SOCIAL = {
  "Instagram": "https://www.instagram.com/cvcspinetx/",
  "Instagram (Español)": "https://www.instagram.com/cvc.health/",
  "Facebook": "",
  "TikTok": "",
  "YouTube": "",
}
ICONS = {
  "Instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
  "Facebook": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-7.5H16l.4-3H13.5V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4A21 21 0 0 0 14.3 4.3c-2.3 0-3.8 1.4-3.8 3.9v2.3H8v3h2.5V21z"/></svg>',
  "TikTok": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 3c.3 2.2 1.6 3.6 3.9 3.8v3a7 7 0 0 1-3.9-1.2v6.2a5.8 5.8 0 1 1-5.8-5.8c.3 0 .6 0 .9.1v3.1a2.7 2.7 0 1 0 1.9 2.6V3z"/></svg>',
  "YouTube": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3z"/></svg>',
}
def social_html():
    links = []
    for name, url in SOCIAL.items():
        if url:
            links.append(f'<a href="{url}" target="_blank" rel="noopener" aria-label="{name}">{ICONS[name.split(" ")[0]]}</a>')
    return '<div class="social">' + "".join(links) + "</div>" if links else ""
HERO_VARIANTS = ["", "hv-olive", "hv-forest", "hv-earth"]

# Real photos for treatment pages (assets/img/<name>-<width>.webp). Pages without one get a branded panel instead.
PHOTOS = {
  "services": ("adjustment-side-posture", [700, 1200], 1542/1200, "Dr. Rudy giving a side-posture chiropractic adjustment"),
  "sports-chiropractic": ("adjustment-lumbar", [540, 900], 1094/900, "Dr. Rudy treating a patient's low back"),
  "functionalrehab": ("vibration-plates", [600, 1000], 1.333, "Vibration plates at Colleyville Chiropractic"),
  "senior-chiropractic": ("dr-rudy-spine", [540, 900], 1353/900, "Dr. Rudy holding a spine model"),
}
TODAY = datetime.date.today().isoformat()
ARROW = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>'

CLINIC = {
  "@type": "Chiropractor", "@id": SITE + "#clinic",
  "name": NAME, "alternateName": ["Colleyville Chiropractic", "CVC Spine"],
  "url": SITE, "logo": SITE + "assets/logo-olive.png", "image": [SITE + "assets/og.jpg", SITE + "assets/img/front-desk-1000.webp", SITE + "assets/img/reception-1000.webp"],
  "telephone": "+1-817-420-7696", "faxNumber": "+1-866-499-4260",
  "foundingDate": "1999", "priceRange": "$$", "currenciesAccepted": "USD",
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
CLINIC["sameAs"] = [u for u in SOCIAL.values() if u]
DOCTOR = {"@type": "Person", "@id": SITE + "team/#dr-rudy", "name": "Dr. Jon \"Rudy\" Urrutia", "honorificSuffix": "DC",
          "jobTitle": "Chiropractor", "worksFor": {"@id": SITE + "#clinic"}, "knowsLanguage": ["en", "es"], "url": SITE + "team/",
          "alumniOf": {"@type": "CollegeOrUniversity", "name": "Parker University", "address": {"@type": "PostalAddress", "addressLocality": "Dallas", "addressRegion": "TX"}},
          "hasCredential": [{"@type": "EducationalOccupationalCredential", "credentialCategory": "degree", "name": "Doctor of Chiropractic", "recognizedBy": {"@type": "CollegeOrUniversity", "name": "Parker University"}},
                            {"@type": "EducationalOccupationalCredential", "credentialCategory": "certification", "name": "Advanced Activator Certification"}],
          "description": "U.S. Coast Guard veteran (10 years active duty). Doctor of Chiropractic, Parker University, 2022. Advanced Activator certified."}

# ---------------------------------------------------------------- languages
# English page path -> Spanish page path. Used for hreflang tags and the language switch.
ES_PAIRS = {"": "es", "pricing": "es/precios", "contact": "es/contacto", "treatments": "es/servicios"}
ES_PAIRS.update({k: v["slug"] for k, v in ES.items()})
EN_OF = {v: k for k, v in ES_PAIRS.items()}
def lang_of(m): return m.get("lang", "en")

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
    # Capitalize a small word when it ends the heading ("What Brings You In?")
    inner = re.sub(r"\b(in|on|to|for|of|at|by|up)(\?|\.|!)?$", lambda m: m.group(1).capitalize() + (m.group(2) or ""), inner)
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
    lang = lang_of(m); locale = "es-US" if lang == "es" else "en-US"
    graph = [CLINIC, {"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": NAME, "inLanguage": ["en-US", "es-US"], "publisher": {"@id": SITE + "#clinic"}}]
    page_type = m.get("page_type", "WebPage")
    webpage = {"@type": page_type, "@id": url + "#page", "url": url, "name": m["title"], "description": m["desc"],
               "isPartOf": {"@id": SITE + "#site"}, "about": {"@id": SITE + "#clinic"}, "inLanguage": locale, "dateModified": TODAY}
    if m.get("doctor"): graph.append(DOCTOR)
    if m.get("reviewed"):
        webpage["reviewedBy"] = {"@id": SITE + "team/#dr-rudy"}; webpage["lastReviewed"] = m["reviewed"]
        graph.append(DOCTOR)
    graph.append(webpage)
    if m.get("trail"): graph.append(crumbs_ld(m["trail"]))
    graph += m.get("ld", [])
    ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>"
    preload = f'<link rel="preload" as="image" href="{r}{m["preload"]}" fetchpriority="high">\n' if m.get("preload") else ""
    ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>\n'
          f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>\n") if GA4_ID else ""
    en_path = EN_OF.get(m["path"], m["path"]) if lang == "es" else m["path"]
    es_path = ES_PAIRS.get(en_path)
    alts = ""
    if es_path is not None:
        u = lambda p: SITE + (p + "/" if p else "")
        alts = (f'<link rel="alternate" hreflang="en" href="{u(en_path)}">\n<link rel="alternate" hreflang="es" href="{u(es_path)}">\n'
                f'<link rel="alternate" hreflang="x-default" href="{u(en_path)}">\n')
    robots = '<meta name="robots" content="noindex">\n' if m.get("noindex") else '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">\n'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(m['title'])}</title>
<meta name="description" content="{html.escape(m['desc'])}">
{robots}<link rel="canonical" href="{url}">
{alts}
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{html.escape(m['title'])}">
<meta property="og:description" content="{html.escape(m['desc'])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}assets/og.jpg">
<meta property="og:locale" content="{'es_US' if lang == 'es' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="US-TX">
<meta name="geo.placename" content="Colleyville">
<meta name="theme-color" content="#1F251D">
<link rel="icon" href="{r}assets/cc-mark-olive.png">
<link rel="apple-touch-icon" href="{r}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400&family=Hanken+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/site.css">
{preload}{ga}{ld}
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

def header(r, active, m=None):
    m = m or {"path": ""}
    def a(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    if lang_of(m) == "es":
        en = EN_OF.get(m["path"], "")
        return f"""<body class="home-page" lang="es">
<a class="skip" href="#main">Saltar al contenido</a>
<div class="offer">Pacientes nuevos: su primera visita cuesta $47. <a href="{JANE}" data-jane="special">Reserve en línea</a></div>
<header class="site" id="top">
  <div class="wrap bar">
    <a class="brand" href="{r}es/" aria-label="Colleyville Chiropractic, inicio">
      <img class="cc" src="{r}assets/cc-mark-cream.png" alt="" width="34" height="44">
      <span class="name">Colleyville Chiropractic<small>CVC Spine</small></span>
    </a>
    <nav class="main" id="nav" aria-label="Principal">
      {a(r + "es/", "Inicio", "home")}
      {a(r + "es/servicios/", "Servicios", "services")}
      {a(r + "es/precios/", "Precios + Seguro", "pricing")}
      {a(r + "es/contacto/", "Contacto", "contact")}
      <a class="lang-switch" href="{r}{en + '/' if en else ''}" hreflang="en" lang="en">English</a>
    </nav>
    <a class="header-phone" href="tel:+18174207696"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>(817) 420-7696</a>
    <a class="btn btn-primary header-cta" href="{JANE}" data-jane="special">Reserve su visita de $47</a>
    <button class="menu-btn" aria-label="Abrir menú" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
  </div>
</header>"""
    es = ES_PAIRS.get(m["path"], "es")
    return f"""<body class="home-page">
<a class="skip" href="#main">Skip to content</a>
<div class="offer">New patients: your first visit is $47. <a href="{JANE}" data-jane="special">Book Online</a></div>
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
      <a class="lang-switch" href="{r}{es}/" hreflang="es" lang="es">Español</a>
    </nav>
    <a class="header-phone" href="tel:+18174207696"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>(817) 420-7696</a>
    <a class="btn btn-primary header-cta" href="{JANE}" data-jane="special">Book Your $47 Visit</a>
    <button class="menu-btn" aria-label="Open menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
  </div>
</header>"""

def footer_es(r):
    return f"""<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <a href="{r}es/" aria-label="Colleyville Chiropractic, inicio"><img class="foot-logo" src="{r}assets/logo-cream.png" alt="Logotipo de Colleyville Chiropractic" width="150" height="141"></a>
        <p style="margin-top:18px;max-width:34ch">1001 Glade Rd, Suite 120<br>Colleyville, TX 76034<br><a href="tel:+18174207696">(817) 420-7696</a></p>
        <p style="margin-top:12px">Lun + Mié 9 a 6 · Mar 2 a 6<br>Jue con cita · Sáb 9 a 12</p>
      </div>
      <div><h4>En español</h4><ul><li><a href="{r}es/">Inicio</a></li><li><a href="{r}es/servicios/">Servicios</a></li><li><a href="{r}es/neuropatia/">Neuropatía (NeuroPath)</a></li><li><a href="{r}es/precios/">Precios + Seguro</a></li><li><a href="{r}es/contacto/">Contacto</a></li></ul></div>
      <div><h4>En inglés</h4><ul><li><a href="{r}team/" hreflang="en">Equipo</a></li><li><a href="{r}faqs/" hreflang="en">Preguntas frecuentes</a></li><li><a href="{r}our-approach/" hreflang="en">Nuestro enfoque</a></li></ul></div>
      <div><h4>Contacto</h4><ul><li><a href="tel:+18174207696">Llame al (817) 420-7696</a></li><li><a href="sms:+18174207696">Envíenos un mensaje</a></li><li><a href="https://resethybridrecovery.com/es/" target="_blank" rel="noopener">Programas RESET en línea</a></li></ul>{social_html()}</div>
    </div>
    <p class="disclaimer">La información de este sitio es educativa y no es un diagnóstico ni sustituye un examen. Los resultados varían de persona a persona. Si tiene una emergencia médica, llame al 911.</p>
    <div class="legal"><span>© 2026 {NAME}</span><span><a href="{r}privacy/" hreflang="en">Privacidad</a> · Hablamos español · Dentro de la red de BCBS de Texas</span></div>
  </div>
</footer>
<div class="dock" aria-label="Acciones rápidas">
  <a class="btn btn-ghost" href="tel:+18174207696">Llamar</a>
  <a class="btn btn-primary" href="{JANE}" data-jane="special">Visita de $47</a>
</div>
<script src="{r}assets/site.js"></script>
</body>
</html>
"""

def footer(r):
    t = "".join(f'<li><a href="{r}{s["path"]}/">{s["short"]}</a></li>' for s in SERVICES if s["group"] == "treatments")
    p = "".join(f'<li><a href="{r}{s["path"]}/">{s["short"]}</a></li>' for s in SERVICES if s["group"] == "people")
    c = "".join(f'<li><a href="{r}{s["path"]}/">{s["short"]}</a></li>' for s in SERVICES if s["group"] == "conditions")
    return f"""<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <a href="{r}" aria-label="Colleyville Chiropractic home"><img class="foot-logo" src="{r}assets/logo-cream.png" alt="Colleyville Chiropractic logo" width="150" height="141"></a>
        <p style="margin-top:18px;max-width:34ch">1001 Glade Rd, Suite 120<br>Colleyville, TX 76034<br><a href="tel:+18174207696">(817) 420-7696</a></p>
        <p style="margin-top:12px">Mon + Wed 9 to 6 · Tue 2 to 6<br>Thu by appointment · Sat 9 to 12</p>
      </div>
      <div><h4>Treatments</h4><ul class="cols">{t}</ul></div>
      <div><h4>Who We Care For</h4><ul>{p}</ul><h4 style="margin-top:28px">Nerve Conditions</h4><ul>{c}</ul><h4 style="margin-top:28px">Clinic</h4><ul><li><a href="{r}our-approach/">Our Approach</a></li><li><a href="{r}team/">Team</a></li><li><a href="{r}pricing/">Pricing + Insurance</a></li><li><a href="{r}faqs/">FAQs</a></li><li><a href="{r}contact/">Contact</a></li><li><a href="{r}affiliate/">Partner With Us</a></li></ul></div>
      <div><h4>Connect</h4><ul><li><a href="tel:+18174207696">Call (817) 420-7696</a></li><li><a href="sms:+18174207696">Text Us</a></li><li><a href="https://resethybridrecovery.com/" target="_blank" rel="noopener">RESET Online Programs</a></li><li><a href="#" data-portal>Member Login</a></li></ul>{social_html()}</div>
    </div>
    <p class="disclaimer">The information on this site is for education and is not a diagnosis or a substitute for an exam. Results vary from person to person. If you have a medical emergency, call 911.</p>
    <div class="legal"><span>© 2026 {NAME}</span><span><a href="{r}privacy/">Privacy</a> · <a href="{r}faqs/#insurance-payment">Cancellation Policy</a> · Se habla español · In-network with BCBS of Texas</span></div>
  </div>
</footer>
<div class="dock" aria-label="Quick actions">
  <a class="btn btn-ghost" href="tel:+18174207696">Call</a>
  <a class="btn btn-primary" href="{JANE}" data-jane="special">Book $47 Visit</a>
</div>
<!-- GHL text widget goes here (paste the existing chat widget script) -->
<script src="{r}assets/site.js"></script>
</body>
</html>
"""

def write(m, body):
    r = m["root"] if "root" in m else ("" if m["path"] == "" else "../" * (m["path"].count("/") + 1))
    if "{{home_faq}}" in body:
        qa = {q: a for _, items in FAQ_GROUPS for q, a in items}
        body = body.replace("{{home_faq}}", faq_html([(q, qa[q]) for q in HOME_FAQ]))
    body = body.replace("{{root}}", r).replace("{{jane}}", JANE)
    es = lang_of(m) == "es"
    page = head(m, r) + "\n" + header(r, m.get("nav", ""), m) + '\n<main id="main">\n' + body + "\n</main>\n" + (footer_es(r) if es else footer(r))
    if not es:  # Spanish headings use sentence case
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

# Labels for the shared page template, per language
L = {
 "en": dict(learn="Learn more", reviewed="Reviewed by", updated="Updated " + REVIEWED, ready="Ready to Get Started?",
            ready_p="Book online in under a minute, or call or text (817) 420-7696. Se habla español.", call_us="Call Us",
            call_num="Call (817) 420-7696", glance="At a Glance", used_for="Often Used For", what="What Is {}?",
            how="How {} Works", how_p="Three phases over 12 months. How fast you move through them depends on your testing, not the calendar.",
            conds="Nerve Problems We See Most", conds_p="Different causes, different plans. Start with the one that sounds like you.",
            helps="What It Helps With", symptoms="Common Symptoms", fit="Your exam tells us whether {} is the right fit for you.",
            this_care="this care", expect="What to Expect", after="After Your Visit", right="Is It Right for You?",
            tell="Tell us before treatment if any of these apply:", research="What the research says.", pricing="Pricing",
            members="Members save on most services.", see_mem="See memberships and all pricing", see_all="See all pricing",
            faq="Common Questions", faq_p="Have another question? Call or text (817) 420-7696.", paired="Often Paired With",
            paired_p="Most plans combine two or three treatments.", crumbs={"people": "Who We Care For", "conditions": "Conditions"},
            crumb_default="Services", hub="treatments/", pricing_url="pricing/"),
 "es": dict(learn="Ver más", reviewed="Revisado por", updated="Actualizado en " + REVIEWED_ES, ready="¿Listo para empezar?",
            ready_p="Reserve en línea en menos de un minuto, o llame o escriba al (817) 420-7696. Hablamos español.", call_us="Llámenos",
            call_num="Llame al (817) 420-7696", glance="En resumen", used_for="Se usa para", what="¿Qué es {}?",
            how="Cómo funciona {}", how_p="Tres fases en 12 meses. La velocidad depende de sus resultados, no del calendario.",
            conds="Problemas de nervios más comunes", conds_p="Causas distintas, planes distintos. Empiece por la que se parezca a lo que siente.",
            helps="Para qué sirve", symptoms="Síntomas comunes", fit="Su examen nos dice si {} es una buena opción para usted.",
            this_care="esta atención", expect="Qué esperar", after="Después de su visita", right="¿Es para usted?",
            tell="Avísenos antes del tratamiento si algo de esto aplica:", research="Lo que dice la investigación.", pricing="Precio",
            members="Los miembros ahorran en la mayoría de los servicios.", see_mem="Ver membresías y todos los precios", see_all="Ver todos los precios",
            faq="Preguntas frecuentes", faq_p="¿Tiene otra pregunta? Llame o escriba al (817) 420-7696. Le atendemos en español.", paired="Se combina con",
            paired_p="La mayoría de los planes combinan dos o tres tratamientos.", crumbs={"people": "Para quién", "conditions": "Condiciones"},
            crumb_default="Servicios", hub="es/servicios/", pricing_url="es/precios/"),
}

def es_service(s):
    """Spanish version of an English service dict: English settings + Spanish text + Spanish URL."""
    t = ES[s["path"]]
    m = {**s, **{k: v for k, v in t.items() if k not in ("book", "alt")}}
    m["book"] = (s["book"][0], t["book"])
    m["alt"] = (s["alt"][0], t["alt"]) if s.get("alt") and t.get("alt") else None
    m.update(path=t["slug"], en_path=s["path"], lang="es")
    if "pricing" not in t: m["pricing"] = None
    if "extra" not in t: m["extra"] = ""
    return m

def card_link(k, lang):
    if lang == "es": return ES[k]["slug"] + "/", ES[k]["name"], BLURB_ES[k]
    return k + "/", SERVICE_BY_PATH[k]["name"], BLURB[k]

def related_html(keys, lang="en"):
    cards = []
    for k in keys:
        href, name, blurb = card_link(k, lang)
        cards.append(f'<a href="{{{{root}}}}{href}" class="reveal"><h3>{esc(name)}</h3><p>{esc(blurb)}</p><span class="go">{L[lang]["learn"]} {ARROW}</span></a>')
    return '<div class="related">' + "".join(cards) + "</div>"

def byline(lang="en"):
    t = L[lang]
    return f'''<div class="byline"><span class="dot"><img src="{{{{root}}}}assets/cc-mark-olive.png" alt=""></span><span>{t["reviewed"]} <b>Dr. Jon "Rudy" Urrutia, DC</b><br>{t["updated"]}</span></div>'''

def ticks(items): return '<ul class="ticks">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"

def cta(s, lang="en"):
    k, label = s["book"]; t = L[lang]
    return f'''<section class="cta-band">
  <div class="wrap"><div class="inner reveal">
    <div><h2>{t["ready"]}</h2><p>{t["ready_p"]}</p></div>
    <div class="btns"><a class="btn btn-primary" href="{{{{jane}}}}" data-jane="{k}">{esc(label)}</a><a class="btn btn-ghost" href="tel:+18174207696">{t["call_us"]}</a></div>
  </div></div>
</section>'''

def visual(s, lang="en"):
    key = s.get("en_path", s["path"]); t = L[lang]
    if key in PHOTOS:
        n, ws, ratio, alt = PHOTOS[key]
        return (f'<div class="photo reveal"><img src="{{{{root}}}}assets/img/{n}-{ws[0]}.webp" srcset="{{{{root}}}}assets/img/{n}-{ws[0]}.webp {ws[0]}w, {{{{root}}}}assets/img/{n}-{ws[1]}.webp {ws[1]}w" '
                f'sizes="(max-width:860px) 92vw, 44vw" width="{ws[1]}" height="{round(ws[1]*ratio)}" alt="{esc(alt)}" loading="lazy" decoding="async"></div>')
    items = s["facts"][:3] if s["facts"] else []
    rows = "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a, b in items)
    helps = "".join(f"<li>{esc(h)}</li>" for h in s["helps"][:4])
    return f'''<aside class="panel-card reveal" aria-label="{esc(s["name"])}: {t["glance"]}">
      <img class="mark" src="{{{{root}}}}assets/cc-mark-cream.png" alt="" width="68" height="88">
      <p class="kicker">{t["glance"]}</p>
      <p class="pc-title">{esc(s["name"])}</p>
      {f'<ul class="pc-facts">{rows}</ul>' if rows else ''}
      <p class="kicker" style="margin-top:22px">{t["used_for"]}</p>
      <ul class="pc-helps">{helps}</ul>
    </aside>'''

def service_page(s, lang="en"):
    t = L[lang]
    lines = " ".join(f'<span class="line"><span>{esc(l)}</span></span>' for l in s["h1"])
    k, label = s["book"]
    actions = f'<a class="btn btn-primary" href="{{{{jane}}}}" data-jane="{k}">{esc(label)}</a>'
    actions += (f'<a class="btn btn-ghost" href="{{{{jane}}}}" data-jane="{s["alt"][0]}">{esc(s["alt"][1])}</a>' if s.get("alt")
                else f'<a class="btn btn-ghost" href="tel:+18174207696">{t["call_num"]}</a>')
    facts = ("<ul class=\"facts\">" + "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a, b in s["facts"]) + "</ul>") if s["facts"] else ""
    crumb_label = t["crumbs"].get(s["group"], t["crumb_default"])
    more = "".join(f"<p>{esc(p)}</p>" for p in s["more"])
    if s.get("pricing"):
        pricing = f'<div class="card reveal">{price_html(s["pricing"])}<p class="note">{t["members"]} <a href="{{{{root}}}}{t["pricing_url"]}">{t["see_mem"]}</a></p></div>'
    else:
        pricing = f'<div class="card reveal"><h3>{t["pricing"]}</h3>{s.get("extra","")}<p class="note"><a href="{{{{root}}}}{t["pricing_url"]}">{t["see_all"]}</a></p></div>'
    en_key = s.get("en_path", s["path"])
    hv = HERO_VARIANTS[[x["path"] for x in SERVICES].index(en_key) % len(HERO_VARIANTS)]
    phases = ""
    if s.get("phases"):
        ph = "".join(f'<div class="phase"><span class="when">{esc(w)}</span><h3>{esc(h)}</h3><p>{esc(d)}</p></div>' for w, h, d in s["phases"])
        phases = f'''
<section class="tint">
  <div class="wrap">
    <div class="intro reveal"><h2>{t["how"].format(esc(s["name"]))}</h2><p>{t["how_p"]}</p></div>
    <div class="phases reveal">{ph}</div>
  </div>
</section>'''
    conds = ""
    if s.get("conditions"):
        conds = f'''
<section>
  <div class="wrap">
    <div class="intro reveal"><h2>{t["conds"]}</h2><p>{t["conds_p"]}</p></div>
    {related_html(s["conditions"], lang)}
  </div>
</section>'''
    helps_h = t["symptoms"] if s["group"] == "conditions" else t["helps"]
    if s["group"] == "treatments" and lang == "en":
        who = s["short"] if s["short"] == "NeuroPath" else s["short"].lower()
    else:
        who = t["this_care"]
    return f'''<section class="page-hero {hv}">
  <div class="wrap">
    <a class="crumb" href="{{{{root}}}}{t["hub"]}">{crumb_label}</a>
    <h1>{lines}</h1>
    <p class="lede">{esc(s["lede"])}</p>
    <div class="actions">{actions}</div>
    {facts}
  </div>
</section>

<section>
  <div class="wrap split">
    <div class="reveal">
      <h2>{t["what"].format(esc(s["name"]))}</h2>
      <div class="answer"><p class="lead">{esc(s["what"])}</p></div>
      <div style="margin-top:22px">{more}</div>
      {byline(lang)}
    </div>
    {visual(s, lang)}
  </div>
</section>
{phases}{conds}
<section class="tint">
  <div class="wrap">
    <div class="intro reveal">
      <h2>{helps_h}</h2>
      <p>{t["fit"].format(esc(who))}</p>
    </div>
    <ul class="tags reveal">{"".join(f"<li>{esc(h)}</li>" for h in s["helps"])}</ul>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="cols2">
      <div class="reveal"><h3>{t["expect"]}</h3>{ticks(s["expect"])}</div>
      <div class="reveal"><h3>{t["after"]}</h3>{ticks(s["after"])}</div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap split">
    <div class="reveal">
      <h2>{t["right"]}</h2>
      <p>{t["tell"]}</p>
      {ticks(s["caution"])}
      <div class="evidence"><b>{t["research"]}</b> {esc(s["evidence"])}</div>
    </div>
    {pricing}
  </div>
</section>

<section>
  <div class="wrap">
    <div class="intro reveal"><h2>{t["faq"]}</h2><p>{t["faq_p"]}</p></div>
    <div class="reveal">{faq_html(s["faqs"])}</div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="intro reveal"><h2>{t["paired"]}</h2><p>{t["paired_p"]}</p></div>
    {related_html(s["related"], lang)}
  </div>
</section>

{cta(s, lang)}'''

def service_meta(s, lang="en"):
    t = L[lang]
    group = t["crumbs"].get(s["group"], t["crumb_default"])
    home, hub = ("Inicio", "es/") if lang == "es" else ("Home", "")
    therapy = {"@type": s["schema"], "name": s["name"], "description": s["what"], "url": SITE + s["path"] + "/",
               "provider": {"@id": SITE + "#clinic"}}
    if lang == "es": therapy["inLanguage"] = "es-US"
    m = {"path": s["path"], "nav": "services", "title": s["title"], "desc": s["desc"], "page_type": "MedicalWebPage",
         "reviewed": "2026-10-18", "trail": [(home, hub), (group, t["hub"]), (s["name"], s["path"] + "/")],
         "ld": [therapy, faq_ld(s["faqs"])]}
    if lang == "es": m["lang"] = "es"
    return m

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
    <div class="hub-group"><h2 class="reveal">Nerve Conditions</h2>{grid("conditions")}</div>
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

def hub_page_es():
    def grid(group):
        cards = "".join(f'<a href="{{{{root}}}}{ES[s["path"]]["slug"]}/" class="reveal"><h3>{esc(ES[s["path"]]["name"])}</h3><p>{esc(BLURB_ES[s["path"]])}</p><span class="go">Ver más {ARROW}</span></a>' for s in SERVICES if s["group"] == group)
        return f'<div class="related">{cards}</div>'
    body = f'''<section class="page-hero">
  <div class="wrap">
    <a class="crumb" href="{{{{root}}}}es/">Inicio</a>
    <h1><span class="line"><span>Nuestros servicios</span></span></h1>
    <p class="lede">Quiropráctica, ondas de choque, rehabilitación, terapias de recuperación y más, todo en un solo lugar en Colleyville. ¿No sabe por dónde empezar? Reserve una visita de paciente nuevo y armamos el plan juntos.</p>
    <div class="actions"><a class="btn btn-primary" href="{{{{jane}}}}" data-jane="newPatient">Reserve su visita de paciente nuevo</a><a class="btn btn-ghost" href="tel:+18174207696">Llame al (817) 420-7696</a></div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="hub-group"><h2 class="reveal">Tratamientos</h2>{grid("treatments")}</div>
    <div class="hub-group"><h2 class="reveal">Para quién</h2>{grid("people")}</div>
    <div class="hub-group"><h2 class="reveal">Problemas de nervios</h2>{grid("conditions")}</div>
  </div>
</section>
<section class="reset" aria-label="Programas RESET en línea">
  <div class="wrap"><div class="inner reveal">
    <div><h2>¿No vive cerca de Colleyville?</h2><p>RESET lleva nuestros programas de rehabilitación y entrenamiento en línea, para que siga el mismo enfoque desde cualquier lugar.</p></div>
    <a class="btn btn-primary" href="https://resethybridrecovery.com/es/" target="_blank" rel="noopener">Ver programas RESET</a>
  </div></div>
</section>'''
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + ES[s["path"]]["slug"] + "/", "name": ES[s["path"]]["name"]} for i, s in enumerate(SERVICES)]
    m = {"path": "es/servicios", "lang": "es", "nav": "services", "title": "Servicios de quiropráctica y rehabilitación en Colleyville, TX | CVC Spine",
         "desc": "Quiropráctica, ondas de choque, NeuroPath para neuropatía, rehabilitación, masaje, ventosas y luz roja en Colleyville, TX. Atención en español para niños, atletas, embarazadas y adultos mayores.",
         "page_type": "CollectionPage", "trail": [("Inicio", "es/"), ("Servicios", "es/servicios/")], "ld": [{"@type": "ItemList", "itemListElement": items}]}
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
    e = es_service(s)
    built.append(write(service_meta(e, "es"), service_page(e, "es")))
built.append(write(*hub_page_es()))
built.append(write(*hub_page()))
built.append(write(*faq_page()))

# sitemap
paths = sorted({str(p.relative_to(ROOT)).replace("index.html", "") for p in built if p.name != "404.html"})
urls = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in paths)
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')

# llms.txt (summary for AI assistants)
svc_lines = "\n".join(f"- [{s['name']}]({SITE}{s['path']}/): {s['what']}" for s in SERVICES)
(ROOT / "llms.txt").write_text(f"""# {NAME}

> Chiropractic clinic in Colleyville, Texas, serving the community since 1999. Chiropractic care, shockwave therapy, the NeuroPath neuropathy program, functional rehab, massage and recovery therapies for kids, athletes, expecting moms, seniors and everyone in between. In-network with Blue Cross Blue Shield of Texas. Bilingual (English and Spanish).

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
- [Inicio en español]({SITE}es/): Spanish homepage. [Servicios]({SITE}es/servicios/), [Neuropatía / NeuroPath]({SITE}es/neuropatia/), [Precios]({SITE}es/precios/), [Contacto]({SITE}es/contacto/)
""")
print(len(built), "pages built")
