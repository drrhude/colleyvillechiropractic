"""Builds every page from src/*.html into the site folders.
Each src file starts with <!--meta {...} --> holding path, title, desc.
Run: python3 tools/build.py"""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.colleyvillechiropractic.com/"
JANE = "https://colleyvillechiropractic.janeapp.com/"

SCHEMA = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Chiropractor","name":"Colleyville Chiropractic | CVC Spine & Sport","url":"https://www.colleyvillechiropractic.com/","telephone":"+1-817-420-7696","faxNumber":"+1-866-499-4260","address":{"@type":"PostalAddress","streetAddress":"1001 Glade Rd, Suite 120","addressLocality":"Colleyville","addressRegion":"TX","postalCode":"76034","addressCountry":"US"},"areaServed":["Colleyville","Southlake","Keller","North Richland Hills","Grapevine","Hurst","Euless","Bedford"],"availableLanguage":["English","Spanish"],"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Wednesday"],"opens":"09:00","closes":"18:00"},{"@type":"OpeningHoursSpecification","dayOfWeek":"Tuesday","opens":"14:00","closes":"18:00"},{"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"09:00","closes":"12:00"}],"medicalSpecialty":"Chiropractic"}
</script>"""

def head(m, r):
    url = SITE + (m["path"] + "/" if m["path"] else "")
    extra = SCHEMA if m.get("schema") else ""
    extra += m.get("jsonld", "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{m['title']}</title>
<meta name="description" content="{m['desc']}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{m['title']}">
<meta property="og:description" content="{m['desc']}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta name="theme-color" content="#1F2A23">
<link rel="icon" href="{r}assets/cc-mark-olive.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400&family=Hanken+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/site.css">
{extra}
</head>"""

def header(r, active):
    def a(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""<body class="home-page">
<a class="skip" href="#main">Skip to content</a>
<!-- Confirm the $47 offer is live before launch -->
<div class="offer">New patients: first visit and exam for $47. <a href="{JANE}" data-jane="special">Claim it</a></div>
<header class="site" id="top">
  <div class="wrap bar">
    <a class="brand" href="{r}" aria-label="Colleyville Chiropractic home">
      <img class="cc" src="{r}assets/cc-mark-cream.png" alt="" width="34" height="44">
      <span class="name">Colleyville Chiropractic<small>CVC Spine + Sport</small></span>
    </a>
    <nav class="main" id="nav" aria-label="Main">
      {a(r, "Home", "home")}
      {a(r + "#services", "Services", "services")}
      {a(r + "pricing/", "Pricing + Insurance", "pricing")}
      {a(r + "team/", "About", "team")}
      <a href="https://resethybridrecovery.com/" target="_blank" rel="noopener">RESET online</a>
    </nav>
    <a class="btn btn-primary header-cta" href="{JANE}" data-jane="newPatient">Book a visit</a>
    <button class="menu-btn" aria-label="Open menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
  </div>
</header>"""

def footer(r):
    return f"""<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <a href="{r}" aria-label="Colleyville Chiropractic home"><img class="foot-logo" src="{r}assets/logo-cream.png" alt="Colleyville Chiropractic" width="150" height="141"></a>
        <p style="margin-top:18px;max-width:34ch">1001 Glade Rd, Suite 120<br>Colleyville, TX 76034</p>
      </div>
      <div><h4>Services</h4><ul><li><a href="{r}services/">Chiropractic</a></li><li><a href="{r}shockwavetherapy/">Shockwave</a></li><li><a href="{r}neuropath/">NeuroPath</a></li><li><a href="{r}functionalrehab/">Functional rehab</a></li><li><a href="{r}massagetherapy/">Massage</a></li><li><a href="{r}guthealth/">Gut health</a></li></ul></div>
      <div><h4>Clinic</h4><ul><li><a href="{r}team/">Team</a></li><li><a href="{r}pricing/">Pricing + Insurance</a></li><li><a href="{r}faqs/">FAQs</a></li><li><a href="{r}affiliate/">Affiliate form</a></li><li><a href="{r}contact/">Contact</a></li></ul></div>
      <div><h4>Connect</h4><ul><li><a href="tel:+18174207696">(817) 420-7696</a></li><li><a href="sms:+18174207696">Text us</a></li><li><a href="https://resethybridrecovery.com/" target="_blank" rel="noopener">RESET online</a></li><li><a href="#" data-portal>Member login</a></li></ul></div>
    </div>
    <div class="legal"><span>© 2026 Colleyville Chiropractic | CVC Spine + Sport</span><span>Se habla español</span></div>
  </div>
</footer>
<div class="dock" aria-label="Quick actions">
  <a class="btn btn-ghost" href="tel:+18174207696">Call</a>
  <a class="btn btn-primary" href="{JANE}" data-jane="newPatient">Book a visit</a>
</div>
<!-- GHL text widget goes here (paste the existing chat widget script) -->
<script src="{r}assets/site.js"></script>
</body>
</html>
"""

built = []
for src in sorted((ROOT / "src").glob("*.html")):
    text = src.read_text()
    m = json.loads(re.match(r"<!--meta (.*?) -->\n", text, re.S).group(1))
    body = text.split("-->\n", 1)[1]
    r = m["root"] if "root" in m else ("" if m["path"] == "" else "../" * m["path"].count("/") + "../")
    body = body.replace("{{root}}", r).replace("{{jane}}", JANE)
    page = head(m, r) + "\n" + header(r, m.get("nav", "")) + "\n<main id=\"main\">\n" + body + "\n</main>\n" + footer(r)
    out = ROOT / (m["file"] if "file" in m else (m["path"] + "/index.html" if m["path"] else "index.html"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    built.append(str(out.relative_to(ROOT)))
print("\n".join(built))
