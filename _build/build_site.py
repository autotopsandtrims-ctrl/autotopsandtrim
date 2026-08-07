"""Static site generator for autotopsandtrim.com.

Emits real HTML pages (no client-side framework, no 14MB bundle). Every image
path is read from images.json, so filenames are never hand-typed.
Mobile-first: CSS-only nav (works with JS disabled), responsive srcset,
sticky tap-to-call bar, 44px touch targets.
"""
import json
import os
import re
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

# Let customers attach photos of the job to the quote request.
#
# OFF until BOTH are true, and it is one line to switch on:
#   1. The form endpoint above is an account the shop actually owns. It is not
#      today (HANDOFF open item 2). Photos of a customer's vehicle carry their
#      plate, driveway and often their house — sending those to an unverified
#      third party is materially worse than sending a name and a phone number.
#   2. That account is on a PAID Formspree plan. File uploads are not on the
#      free tier (free is 50 submissions/month, no attachments); the cheapest
#      plan that accepts files is Personal at $15/mo with 1 GB of storage.
#      Shipping the input against a free endpoint gives customers a file picker
#      whose attachment is silently dropped, which is worse than no picker.
#
# The markup itself needs no JavaScript — a file input plus the multipart
# enctype is plain HTML, so this does not touch the zero-JS guarantee.
FORM_ACCEPTS_FILES = False

with open(os.path.join(HERE, "images.json"), encoding="utf-8") as fh:
    IMAGES = json.load(fh)


# ---------------------------------------------------------------- images
def img(base, alt, sizes="100vw", cls="", eager=False, ratio=None, priority=False):
    """Render a responsive <img> from the catalog. Raises if base is unknown."""
    if base not in IMAGES:
        raise KeyError(f"unknown photo: {base}")
    meta = IMAGES[base]
    variants = meta["variants"]
    srcset = ", ".join(f"assets/{v['file']} {v['w']}w" for v in variants)
    largest = variants[-1]
    style = f' style="aspect-ratio:{meta["w"]}/{meta["h"]}"' if ratio is None else f' style="aspect-ratio:{ratio}"'
    loading = "" if eager else ' loading="lazy" decoding="async"'
    # the LCP image should not queue behind a dozen other requests
    prio = ' fetchpriority="high" decoding="async"' if priority else ""
    c = f' class="{cls}"' if cls else ""
    return (
        f'<img src="assets/{largest["file"]}" srcset="{srcset}" sizes="{sizes}" '
        f'width="{meta["w"]}" height="{meta["h"]}" alt="{alt}"{c}{loading}{prio}{style}>'
    )


def preload_image(base, sizes):
    """<link rel=preload> for the LCP image, matching the <img>'s own srcset."""
    meta = IMAGES[base]
    srcset = ", ".join(f"assets/{v['file']} {v['w']}w" for v in meta["variants"])
    return (f'<link rel="preload" as="image" href="assets/{meta["variants"][-1]["file"]}" '
            f'imagesrcset="{srcset}" imagesizes="{sizes}" fetchpriority="high">\n')


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
    ("sunroof-shade-repair.html", "Sunroof Shade Repair"),
    ("marine-upholstery.html", "Marine Upholstery"),
    ("aviation-upholstery.html", "Aviation Upholstery"),
    ("motorcycle-seats.html", "Motorcycle Seats"),
]

SCHEMA = {
    "@context": "https://schema.org",
    "@type": "AutoRepair",
    "name": "Auto Tops and Trim",
    "description": ("Custom automotive, marine, aviation and motorcycle upholstery in "
                    "Monroe, NC. Convertible tops, seats, headliners, sunroof shades, "
                    "carpet and marine canvas."),
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
         "opens": "09:00", "closes": "19:00"},
        {"@type": "OpeningHoursSpecification",
         "dayOfWeek": "Saturday", "opens": "11:00", "closes": "17:00"},
    ],
    "makesOffer": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}}
        for n in ["Automotive Upholstery", "Convertible Tops", "Sunroof Shade Repair",
                  "Marine Upholstery", "Aviation Upholstery", "Motorcycle Upholstery"]
    ],
}


def faq_schema(faqs):
    """FAQPage JSON-LD from the same (question, answer) pairs the page renders."""
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }


def head(title, desc, path, extra_schema=None, faqs=None, preload=""):
    # Canonical must point at the clean URL Vercel actually serves, not the .html
    # file, or every page would declare a canonical that immediately redirects.
    canonical = SITE + public_path(path)
    base = extra_schema or SCHEMA
    if faqs:
        # both objects in one @graph so the page keeps its LocalBusiness markup
        # AND becomes eligible for FAQ rich results
        node = {k: v for k, v in base.items() if k != "@context"}
        doc = {"@context": "https://schema.org", "@graph": [node, faq_schema(faqs)]}
    else:
        doc = base
    schema = json.dumps(doc, separators=(",", ":"))
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
<meta name="theme-color" content="#16344F">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:image" content="{SITE}/icon-512.png">
<meta property="og:site_name" content="Auto Tops and Trim">
<meta name="twitter:card" content="summary">
<link rel="preload" as="font" type="font/woff2" href="assets/fonts/font-327592e7.woff2" crossorigin>
{preload}<link rel="stylesheet" href="assets/site.css">
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
    <!-- No strapline under the brand. "Monroe, NC · Since 1989" was removed at the
         user's request 2026-08-05, ahead of dropping a logo in here: a logo with
         the wordmark already in it plus a strapline underneath makes the header
         lockup too tall and too busy. Both facts still appear in the footer, the
         home hero eyebrow, the About page and the LocalBusiness schema, so
         nothing is lost for SEO or for a reader. -->
    <!-- Text wordmark, not the logo. The logo trial was reverted 2026-08-05: the
         supplied artwork reads well on white but its linework is charcoal, which
         sinks into this header's navy, and recolouring a raster never comes out
         as crisp as type does.

         The prepared artwork is kept in assets/originals/ for when we return to
         it — logo-light.png (AUTO TOPS whitened) and logo-dark.png (as supplied,
         for white backgrounds). Both already have their drop shadow stripped and
         both generate srcset variants through make_responsive.py.

         TO PUT IT BACK: swap the span below for
           {{img('logo-light', 'Auto Tops and Trim', '210px', eager=True)}}
         The .brand img sizing rules are still in site.css and are inert until
         an <img> exists here again. -->
    <a class="brand" href="index.html" aria-label="Auto Tops and Trim, home">
      {img('logo-badge-warm', '', '190px', eager=True)}
      <span class="brand-name">AUTO TOPS <em>&amp;</em> TRIM</span>
    </a>
    <input type="checkbox" id="navtoggle" class="navtoggle" aria-hidden="true">
    <label for="navtoggle" class="burger" aria-label="Menu"><span></span><span></span><span></span></label>
    <nav class="nav" aria-label="Main">
      <ul>{links}</ul>
    </nav>
    <a class="head-call" href="tel:{PHONE_TEL}">
      <span class="hc-ic" aria-hidden="true">&#9742;</span>
      <span class="hc-num">{PHONE_DISPLAY}</span>
      <span class="hc-sub">Free estimate</span>
    </a>
  </div>
</header>
<main id="main">
"""


def footer(lightbox=""):
    """Closes <main>, then the footer.

    `lightbox` is emitted AFTER </main> on purpose. <main> carries the `pagein`
    animation, and an ancestor running a transform-affecting animation becomes the
    containing block for position:fixed descendants — which made the fixed overlay
    size itself to the full height of <main> instead of the viewport, so photos
    opened far down the page. Kept outside <main>, `.lb` centres on the viewport.
    """
    svc = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in SERVICES)
    nav = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in NAV)
    return f"""</main>
{lightbox}
<footer class="site-foot">
  <div class="foot-in">
    <div class="foot-col">
      <p class="foot-brand">{img('logo-badge-warm', 'Auto Tops and Trim', '190px')}</p>
      <p>Custom upholstery in Monroe, North Carolina since 1989. Automotive, marine,
         aviation and motorcycle interiors.</p>
      <p><a class="foot-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="foot-area"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path
        d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/>
        </svg>4209 W Hwy 74, Monroe, NC 28110</p>
    </div>
    <div class="foot-col foot-acc">
      <input type="checkbox" id="fa-svc" class="facc" aria-hidden="true">
      <label for="fa-svc" class="foot-h">Services</label>
      <ul>{svc}</ul>
    </div>
    <div class="foot-col foot-acc">
      <input type="checkbox" id="fa-nav" class="facc" aria-hidden="true">
      <label for="fa-nav" class="foot-h">Pages</label>
      <ul>{nav}</ul>
    </div>
    <div class="foot-col">
      <p class="foot-h">Hours</p>
      <table class="hours">
        <tr><th>Mon &ndash; Fri</th><td>9:00 AM &ndash; 7:00 PM</td></tr>
        <tr><th>Saturday</th><td>11:00 AM &ndash; 5:00 PM</td></tr>
        <tr><th>Sunday</th><td>Closed</td></tr>
      </table>
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
    <p class="microline">Free estimates &nbsp;&middot;&nbsp; By photo or in person &nbsp;&middot;&nbsp; Monroe, NC since 1989</p>
  </div>
</section>
"""


def quote_form(which="contact"):
    # A file input requires the multipart enctype; without it the browser posts
    # only the filename and the photo never leaves the machine.
    enctype = ' enctype="multipart/form-data"' if FORM_ACCEPTS_FILES else ""
    photos = """
  <label class="filefield">Photos of the job <span class="opt">optional</span>
    <input type="file" name="Photos" accept="image/*" multiple>
    <span class="fieldnote">A picture of the tear, the sagging shade or the whole
      vehicle helps us come back to you faster. It does not replace seeing it in
      person &mdash; we still quote the frame and foam at the shop.</span>
  </label>""" if FORM_ACCEPTS_FILES else ""
    return f"""<form class="quote" action="{FORM_ENDPOINT}" method="post"{enctype}>
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
    placeholder="Convertible top, seats, headliner, boat cushions&hellip;"></textarea></label>{photos}
  <!-- TCPA express written consent. Deliberately NOT `required` and NOT pre-checked:
       consent to marketing texts cannot lawfully be a condition of getting a quote. -->
  <label class="consent">
    <input type="checkbox" name="SMS consent" value="Yes, agreed to receive text messages">
    <span>By checking this box you agree to receive text messages from Auto Tops and
      Trim about your estimate and job. Message frequency varies. Message and data
      rates may apply. Reply STOP to opt out, HELP for help.</span>
  </label>
  <button type="submit" class="btn btn-primary wide">Send my request</button>
  <p class="formnote">Prefer to talk? Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
     <span class="fn-hrs">Mon&ndash;Fri 9:00&nbsp;AM&ndash;7:00&nbsp;PM &middot; Sat 11:00&nbsp;AM&ndash;5:00&nbsp;PM</span></p>
</form>
"""


# ---- clean URLs ------------------------------------------------------------
# The pages are still written to disk as real .html files; vercel.json sets
# cleanUrls, so Vercel serves gallery.html at /gallery and 308-redirects the .html
# form to it. Internal links therefore have to be emitted extensionless, or every
# in-site click would take a needless redirect hop.
#
# Rewriting at write() time rather than at each call site is deliberate: hrefs are
# authored inline across hundreds of f-strings, and one post-process catches all
# of them. It also keeps header()'s `href == active` comparison working, since
# that runs on the pre-rewrite filename.
_CLEAN_HREF = re.compile(r'href="([A-Za-z0-9\-_]+)\.html"')


def public_path(filename):
    """Public URL path for a generated page. index.html is the site root."""
    if filename == "index.html":
        return "/"
    return "/" + filename[:-5] if filename.endswith(".html") else "/" + filename


def _cleanify(html):
    # The character class cannot match "https://..." (no ':' or '/'), so absolute
    # URLs, tel:, mailto: and fragment links are all left alone.
    return _CLEAN_HREF.sub(
        lambda m: 'href="/"' if m.group(1) == "index" else f'href="/{m.group(1)}"',
        html)


def write(path, html):
    if path.endswith(".html"):
        html = _cleanify(html)
    with open(os.path.join(OUT, path), "w", encoding="utf-8") as fh:
        fh.write(html)
    return path
