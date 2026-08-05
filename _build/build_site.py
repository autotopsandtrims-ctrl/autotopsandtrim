"""Static site generator for autotopsandtrim.com.

Emits real HTML pages (no client-side framework, no 14MB bundle). Every image
path is read from images.json, so filenames are never hand-typed.
Mobile-first: CSS-only nav (works with JS disabled), responsive srcset,
sticky tap-to-call bar, 44px touch targets.
"""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = REPO
SCRATCH = HERE


PHONE_DISPLAY = "(980) 385-8101"
PHONE_TEL = "+19803858101"
SITE = "https://www.autotopsandtrim.com"
EMAIL = "contact@autotopsandtrim.com"
FORM_ENDPOINT = "https://formspree.io/f/mrpzzdgz"   # TODO: swap for the shop's own form

with open(os.path.join(HERE, "images.json"), encoding="utf-8") as fh:
    IMAGES = json.load(fh)


# ---------------------------------------------------------------- images
def img(base, alt, sizes="100vw", cls="", eager=False, ratio=None):
    """Render a responsive <img> from the catalog. Raises if base is unknown."""
    if base not in IMAGES:
        raise KeyError(f"unknown photo: {base}")
    meta = IMAGES[base]
    variants = meta["variants"]
    srcset = ", ".join(f"assets/{v['file']} {v['w']}w" for v in variants)
    largest = variants[-1]
    style = f' style="aspect-ratio:{meta["w"]}/{meta["h"]}"' if ratio is None else f' style="aspect-ratio:{ratio}"'
    loading = "" if eager else ' loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (
        f'<img src="assets/{largest["file"]}" srcset="{srcset}" sizes="{sizes}" '
        f'width="{meta["w"]}" height="{meta["h"]}" alt="{alt}"{c}{loading}{style}>'
    )


def has(base):
    return base in IMAGES


# ---------------------------------------------------------------- chrome
NAV = [
    ("index.html", "Home"),
    ("services.html", "Services"),
    ("gallery.html", "Gallery"),
    ("process.html", "Our Process"),
    ("about.html", "About"),
    ("blog.html", "Blog"),
    ("contact.html", "Contact"),
]

SERVICES = [
    ("convertible-tops.html", "Convertible Tops"),
    ("auto-upholstery.html", "Auto Upholstery"),
    ("marine-upholstery.html", "Marine Upholstery"),
    ("aviation-upholstery.html", "Aviation Upholstery"),
    ("motorcycle-seats.html", "Motorcycle Seats"),
]

SCHEMA = {
    "@context": "https://schema.org",
    "@type": "AutoRepair",
    "name": "Auto Tops and Trim",
    "description": ("Custom automotive, marine, aviation and motorcycle upholstery in "
                    "Monroe, NC. Convertible tops, seats, headliners, carpet and marine canvas."),
    "url": SITE,
    "telephone": PHONE_DISPLAY,
    "email": EMAIL,
    "foundingDate": "1989",
    "priceRange": "$$",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "4209 W Hwy 74",
        "addressLocality": "Monroe",
        "addressRegion": "NC",
        "postalCode": "28110",
        "addressCountry": "US",
    },
    "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "5.0",
        "reviewCount": "9",
    },
    "areaServed": ["Monroe NC", "Charlotte NC", "Union County NC"],
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification",
         "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
         "opens": "09:00", "closes": "17:30"},
        {"@type": "OpeningHoursSpecification",
         "dayOfWeek": "Saturday", "opens": "11:00", "closes": "17:00"},
    ],
    "makesOffer": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}}
        for n in ["Automotive Upholstery", "Convertible Tops", "Marine Upholstery",
                  "Aviation Upholstery", "Motorcycle Upholstery"]
    ],
}


def head(title, desc, path, extra_schema=None):
    canonical = f"{SITE}/{path}" if path != "index.html" else f"{SITE}/"
    schema = json.dumps(extra_schema or SCHEMA, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta name="theme-color" content="#12354F">
<link rel="stylesheet" href="assets/site.css">
<script type="application/ld+json">{schema}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(active):
    links = "".join(
        f'<li><a href="{href}"{" class=\'on\'" if href == active else ""}>{label}</a></li>'
        for href, label in NAV
    )
    return f"""<header class="site-head">
  <div class="head-in">
    <a class="brand" href="index.html">
      <span class="brand-name">AUTO TOPS <em>&amp;</em> TRIM</span>
      <span class="brand-sub">Monroe, NC &middot; Since 1989</span>
    </a>
    <input type="checkbox" id="navtoggle" class="navtoggle" aria-hidden="true">
    <label for="navtoggle" class="burger" aria-label="Menu"><span></span><span></span><span></span></label>
    <nav class="nav" aria-label="Main">
      <ul>{links}</ul>
    </nav>
    <a class="head-call" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
  </div>
</header>
<main id="main">
"""


def footer():
    svc = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in SERVICES)
    nav = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in NAV)
    return f"""</main>
<footer class="site-foot">
  <div class="foot-in">
    <div class="foot-col">
      <p class="foot-brand">AUTO TOPS <em>&amp;</em> TRIM</p>
      <p>Custom upholstery in Monroe, North Carolina since 1989. Automotive, marine,
         aviation and motorcycle interiors.</p>
      <p><a class="foot-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
    <div class="foot-col">
      <p class="foot-h">Services</p>
      <ul>{svc}</ul>
    </div>
    <div class="foot-col">
      <p class="foot-h">Pages</p>
      <ul>{nav}</ul>
    </div>
    <div class="foot-col">
      <p class="foot-h">Hours</p>
      <table class="hours">
        <tr><th>Mon &ndash; Fri</th><td>9:00 AM &ndash; 5:30 PM</td></tr>
        <tr><th>Saturday</th><td>11:00 AM &ndash; 5:00 PM</td></tr>
        <tr><th>Sunday</th><td>Closed</td></tr>
      </table>
      <p class="foot-area">4209 W Hwy 74, Monroe, NC 28110</p>
    </div>
  </div>
  <div class="foot-bar">
    <p>&copy; 2026 Auto Tops and Trim. All rights reserved.</p>
  </div>
</footer>
<a class="callbar" href="tel:{PHONE_TEL}">
  <span class="callbar-ic" aria-hidden="true">&#9742;</span>
  Call {PHONE_DISPLAY} &middot; Free Estimate
</a>
</body>
</html>
"""


def shead(num, label, center=False):
    """The site's section header: 01 — LABEL"""
    mid = " mid" if center else ""
    return (f'<div class="shead{mid}"><span class="n">{num}</span>'
            f'<span class="dash"></span><span class="lab">{label}</span></div>')


def cta(num="05", label="Ready when you are",
        heading="Ready to transform your interior?",
        sub="Bring new life to your seats, tops, and trim with work built for "
            "comfort, durability, and long-term pride of ownership."):
    return f"""<section class="band tint2">
  <div class="wrap narrow center stack">
    {shead(num, label, center=True)}
    <h2>{heading}</h2>
    <p class="lead">{sub}</p>
    <div class="btnrow">
      <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
      <a class="btn btn-ghost" href="contact.html">Request a Quote Online</a>
    </div>
    <p class="microline">Free estimates &nbsp;&middot;&nbsp; In-person quotes &nbsp;&middot;&nbsp; Monroe, NC since 1989</p>
  </div>
</section>
"""


def quote_form(which="contact"):
    return f"""<form class="quote" action="{FORM_ENDPOINT}" method="post">
  <input type="hidden" name="_subject" value="New estimate request from autotopsandtrim.com">
  <div class="f2">
    <label>First name <input type="text" name="First name" required autocomplete="given-name"></label>
    <label>Last name <input type="text" name="Last name" required autocomplete="family-name"></label>
  </div>
  <div class="f2">
    <label>Phone <input type="tel" name="Phone" required autocomplete="tel" inputmode="tel"></label>
    <label>Email <input type="email" name="Email" required autocomplete="email" inputmode="email"></label>
  </div>
  <div class="f3">
    <label>Year <input type="text" name="Year" inputmode="numeric"></label>
    <label>Make <input type="text" name="Make"></label>
    <label>Model <input type="text" name="Model"></label>
  </div>
  <label>What do you need? <textarea name="Project description" rows="5" required
    placeholder="Convertible top, seats, headliner, boat cushions&hellip;"></textarea></label>
  <button type="submit" class="btn btn-primary wide">Send my request</button>
  <p class="formnote">Prefer to talk? Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
     &mdash; Mon&ndash;Fri 9&ndash;5:30, Sat 11&ndash;5.</p>
</form>
"""


def write(path, html):
    with open(os.path.join(OUT, path), "w", encoding="utf-8") as fh:
        fh.write(html)
    return path
