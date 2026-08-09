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

# The one response-time promise the site makes, written ONCE so the form, the
# call-to-action and the contact page can never drift apart from each other.
#
# Deliberately a single, keepable commitment with no "usually" attached: a
# promise the shop misses on a busy Saturday is worse than no promise at all.
# If the owner wants to commit to something faster, change it HERE and nowhere
# else — every place it appears is generated from this string.
# CHANGED 2026-08-09 from "one business day" to one hour, at the owner's request.
# Speed-to-lead is the single biggest conversion lever in local services and this
# now backs the paid campaign, where it is an advertised claim rather than a hope.
#
# SCOPED TO SHOP HOURS DELIBERATELY. Unqualified, this promise breaks every Sunday
# and every evening, and a missed advertised promise is worse than a slower kept
# one. The hours sit directly under it on the contact page and the landing pages.
# To make it unqualified, drop the trailing clause here and nowhere else.
REPLY_PROMISE = "We reply to every request within one hour during shop hours"
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
FORM_ACCEPTS_FILES = True   # ON 2026-08-07: the user confirms the endpoint is
                            # theirs and the plan is the paid one that accepts
                            # attachments. A live submission was fired at it to
                            # confirm it answers before this was switched on.

with open(os.path.join(HERE, "images.json"), encoding="utf-8") as fh:
    IMAGES = json.load(fh)


# ---------------------------------------------------------------- images
def img(base, alt, sizes="100vw", cls="", eager=False, ratio=None, priority=False,
        style_extra=""):
    """Render a responsive <img> from the catalog. Raises if base is unknown.

    `ratio=False` emits NO aspect-ratio at all. That is for images whose box is
    sized by their container instead — the landing-page step cards are a fixed
    250px-tall crop with object-fit, and an aspect-ratio on the <img> fights the
    height:100% those cards depend on.

    `style_extra` appends declarations to the same style attribute, which is how
    those cards carry a per-photo `object-position`: these are phone photos and
    the subject is rarely dead centre, so each crop has to be aimed individually.
    """
    if base not in IMAGES:
        raise KeyError(f"unknown photo: {base}")
    meta = IMAGES[base]
    variants = meta["variants"]
    srcset = ", ".join(f"assets/{v['file']} {v['w']}w" for v in variants)
    largest = variants[-1]
    if ratio is False:
        decls = ""
    elif ratio is None:
        decls = f'aspect-ratio:{meta["w"]}/{meta["h"]}'
    else:
        decls = f"aspect-ratio:{ratio}"
    if style_extra:
        decls = f"{decls};{style_extra}" if decls else style_extra
    style = f' style="{decls}"' if decls else ""
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
    ("careers.html", "Careers"),
    ("contact.html", "Contact"),
]

# ORDER IS THE OWNER'S BUSINESS CARD: convertible tops, vinyl tops, sunroofs,
# vehicle interiors. The photo counts back it up (62 convertible tops, 115
# interior, 14 vinyl, 2 sunroof), and it is what the shop actually sells. The
# old "four trades under one roof — automotive, marine, aviation, motorcycle"
# framing was the outlier and is gone from the ordering everywhere.
#
# Marine, aviation and motorcycle stay live and stay listed, but LAST — they are
# demoted into a "We also work on" band on the home page and the services index.
#
# URLS ARE FROZEN. `auto-upholstery.html` is labelled "Vehicle Interiors" and
# keeps its filename: it is indexed, internally linked from a dozen blog posts,
# and renaming the file would 404 every one of them for no SEO gain.
SERVICES = [
    ("convertible-tops.html", "Convertible Tops"),
    ("vinyl-tops.html", "Vinyl Tops"),
    # LABEL IS "SUNROOFS" — the word on the business card. The file name stays
    # sunroof-shade-repair.html: it is indexed and "sunroof shade repair" is the
    # phrase people actually search, so the page keeps it in its own title.
    ("sunroof-shade-repair.html", "Sunroofs"),
    ("auto-upholstery.html", "Vehicle Interiors"),
    # Headliners sit directly under Vehicle Interiors, not alongside the four
    # card services. It is interior work with its own page because it is the
    # least-contested search cluster the shop has, not a fifth trade.
    ("headliner-replacement.html", "Headliner Replacement"),
    ("marine-upholstery.html", "Marine Upholstery"),
    ("aviation-upholstery.html", "Aviation Upholstery"),
    ("motorcycle-seats.html", "Motorcycle Seats"),
]

# Social accounts, all on the same handle. In the footer and in the schema's
# `sameAs`, which is how Google ties the profiles to the business. Icons are
# inline SVG paths — no icon font, no external request, and they inherit
# currentColor so they sit on any background.
SOCIALS = [
    ("Facebook", "https://www.facebook.com/autotopsandtrim",
     "M13.5 22v-8h2.7l.4-3.1h-3.1V8.9c0-.9.25-1.5 1.55-1.5H16.7V4.6a22 22 0 0 0-2.4-.12c-2.4 0-4 1.46-4 4.14v2.3H7.6V14h2.7v8h3.2Z"),
    ("Instagram", "https://www.instagram.com/autotopsandtrim",
     "M12 2.2c3.2 0 3.6 0 4.85.07 1.17.05 1.8.25 2.23.42.56.22.96.48 1.38.9.42.42.68.82.9 1.38.17.42.37 1.06.42 2.23.06 1.25.07 1.62.07 4.8s-.01 3.55-.07 4.8c-.05 1.17-.25 1.8-.42 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.17-1.06.37-2.23.42-1.25.06-1.62.07-4.85.07s-3.6-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.42-.56-.22-.96-.48-1.38-.9-.42-.42-.68-.82-.9-1.38-.17-.42-.37-1.06-.42-2.23C2.21 15.55 2.2 15.18 2.2 12s.01-3.55.07-4.8c.05-1.17.25-1.8.42-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.17 1.06-.37 2.23-.42C8.45 2.21 8.82 2.2 12 2.2Zm0 1.98c-3.13 0-3.5.01-4.73.07-1.14.05-1.76.24-2.17.4-.55.21-.94.47-1.35.88-.41.41-.67.8-.88 1.35-.16.41-.35 1.03-.4 2.17-.06 1.23-.07 1.6-.07 4.73s.01 3.5.07 4.73c.05 1.14.24 1.76.4 2.17.21.55.47.94.88 1.35.41.41.8.67 1.35.88.41.16 1.03.35 2.17.4 1.23.06 1.6.07 4.73.07s3.5-.01 4.73-.07c1.14-.05 1.76-.24 2.17-.4.55-.21.94-.47 1.35-.88.41-.41.67-.8.88-1.35.16-.41.35-1.03.4-2.17.06-1.23.07-1.6.07-4.73s-.01-3.5-.07-4.73c-.05-1.14-.24-1.76-.4-2.17a3.6 3.6 0 0 0-.88-1.35 3.6 3.6 0 0 0-1.35-.88c-.41-.16-1.03-.35-2.17-.4-1.23-.06-1.6-.07-4.73-.07Zm0 3.37a4.45 4.45 0 1 1 0 8.9 4.45 4.45 0 0 1 0-8.9Zm0 7.34a2.89 2.89 0 1 0 0-5.78 2.89 2.89 0 0 0 0 5.78Zm5.67-7.53a1.04 1.04 0 1 1-2.08 0 1.04 1.04 0 0 1 2.08 0Z"),
    ("TikTok", "https://www.tiktok.com/@autotopsandtrim",
     "M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 0 1-2.59 2.5 2.59 2.59 0 1 1 .77-5.06v-3.1a5.66 5.66 0 0 0-.77-.05A5.68 5.68 0 1 0 15.54 15.4V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3a4.3 4.3 0 0 1-3.24-1.48Z"),
    ("X", "https://x.com/autotopsandtrim",
     "M17.53 3h3.03l-6.62 7.57L21.75 21h-5.9l-4.62-6.04L5.94 21H2.9l7.08-8.09L2.5 3h6.05l4.18 5.52L17.53 3Zm-1.06 16.2h1.68L7.6 4.7H5.8l10.67 14.5Z"),
]

SCHEMA = {
    "@context": "https://schema.org",
    "@type": "AutoRepair",
    "name": "Auto Tops and Trim",
    "description": ("Convertible tops, vinyl tops, sunroofs and vehicle interiors in "
                    "Monroe, NC since 1989. Boat, aircraft and motorcycle upholstery too."),
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
    # How Google ties the social profiles to this business
    "sameAs": [url for _, url, _ in SOCIALS],
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification",
         "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
         "opens": "09:00", "closes": "19:00"},
        {"@type": "OpeningHoursSpecification",
         "dayOfWeek": "Saturday", "opens": "11:00", "closes": "17:00"},
    ],
    "makesOffer": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}}
        # Same order as SERVICES, for the same reason: the card first, the three
        # secondary trades last.
        for n in ["Convertible Tops", "Vinyl Tops",
                  "Sunroof Shade Repair", "Vehicle Interiors",
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


def head(title, desc, path, extra_schema=None, faqs=None, preload="", extra_head=""):
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
{extra_head}</head>
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


# Pages that belong in the footer but NOT in the header. Empty right now —
# Careers went into the main nav on 2026-08-07 because a footer-only link was
# not findable.
FOOT_EXTRA = []


def footer(lightbox="", callbar=None):
    """Closes <main>, then the footer.

    `callbar` replaces the sticky mobile bar's MARKUP only. It keeps the
    `.callbar` class, so site.css keeps owning the bar's position, z-index, the
    hide-above-1000px rule and the .site-foot padding that clears it — a landing
    page that invented its own fixed bar would have to re-derive all four and
    would drift the day any of them changes. The landing pages pass a two-button
    call/text split; everything else gets the single call link below.

    `lightbox` is emitted AFTER </main> on purpose. <main> carries the `pagein`
    animation, and an ancestor running a transform-affecting animation becomes the
    containing block for position:fixed descendants — which made the fixed overlay
    size itself to the full height of <main> instead of the viewport, so photos
    opened far down the page. Kept outside <main>, `.lb` centres on the viewport.
    """
    svc = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in SERVICES)
    nav = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in NAV + FOOT_EXTRA)
    # The same row of icons is emitted twice and one copy is hidden per width:
    # on a desktop it belongs under Hours, on a phone under the address, and the
    # footer's four columns collapse into one centred stack in between. Two
    # copies plus a display rule is the honest way to do that in pure CSS — the
    # alternative is reordering a grid and hoping the source order still reads
    # correctly to a screen reader.
    socials_row = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener" aria-label="{name}">'
        f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{path}"/></svg>'
        f'</a></li>' for name, url, path in SOCIALS)
    # SPLIT CALL / TEXT, sitewide, 2026-08-09.
    #
    # (980) 385-8101 receives picture messages — confirmed by the owner. The
    # whole site's ask is "send us a photo of the job", and until now the only
    # way to do that was an eight-field form. Someone reading this on a phone is
    # standing next to the car with the camera already open; a text is a few
    # seconds, the form is not.
    #
    # `.callbar` is kept on the WRAPPER so site.css keeps owning position,
    # z-index, the hide-above-1000px rule, the safe-area padding and the
    # .site-foot clearance. `.split` only changes the internal layout.
    #
    # Call stays the wider half: it is the only conversion Google can track, so
    # it should not lose the emphasis. sms: carries no body param on purpose —
    # iOS wants &body=, Android wants ?body=, and one syntax breaks the other.
    bar = callbar if callbar is not None else f"""<div class="callbar split">
  <a class="cb cb-call" href="tel:{PHONE_TEL}">
    <span class="callbar-ic" aria-hidden="true">&#9742;</span>Call {PHONE_DISPLAY}</a>
  <a class="cb cb-text" href="sms:{PHONE_TEL}">
    <span class="callbar-ic" aria-hidden="true">&#9993;</span>Text a photo</a>
</div>"""
    return f"""</main>
{lightbox}
<footer class="site-foot">
  <div class="foot-in">
    <div class="foot-col">
      <p class="foot-brand">{img('logo-badge-warm', 'Auto Tops and Trim', '190px')}</p>
      <p>Custom upholstery in Monroe, North Carolina since 1989. Convertible tops,
         vinyl tops, sunroofs and vehicle interiors.</p>
      <p><a class="foot-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="foot-area"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path
        d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/>
        </svg>4209 W Hwy 74, Monroe, NC 28110</p>
      <ul class="socials sc-mob">{socials_row}</ul>
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
      <ul class="socials sc-desk">{socials_row}</ul>
    </div>
  </div>
  <div class="foot-bar">
    <p>&copy; 2026 Auto Tops and Trim. All rights reserved.</p>
  </div>
</footer>
{bar}
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
    <p class="microline">Free estimates &nbsp;&middot;&nbsp; By photo or in person
       &nbsp;&middot;&nbsp; Reply within one hour &nbsp;&middot;&nbsp; Monroe, NC since 1989</p>
  </div>
</section>
"""


def quote_form(which="contact"):
    # A file input requires the multipart enctype; without it the browser posts
    # only the filename and the photo never leaves the machine.
    enctype = ' enctype="multipart/form-data"' if FORM_ACCEPTS_FILES else ""
    # Kept to one line. The long version explained photo etiquette, what a photo
    # cannot show and what still gets quoted at the shop — all true, all already
    # said on the service pages, and all of it noise next to a file picker.
    photos = """
  <label class="filefield">Photos <span class="opt">optional</span>
    <input type="file" name="Photos" accept="image/*" multiple>
    <span class="fieldnote">Add a picture or two of what needs doing.</span>
  </label>""" if FORM_ACCEPTS_FILES else ""
    return f"""<form class="quote" action="{FORM_ENDPOINT}" method="post"{enctype}>
  <input type="hidden" name="_subject" value="New estimate request from autotopsandtrim.com">
  <!-- Honeypot. Formspree silently discards any submission where `_gotcha` is
       filled: a bot scraping the HTML fills every field it finds, a person never
       sees this one. No JavaScript, so the zero-JS guarantee holds.
       Positioned off-screen rather than display:none, because some bots skip
       display:none fields. aria-hidden + tabindex=-1 keep it away from screen
       readers and the tab order; autocomplete=off stops browsers filling it.
       Formspree also runs reCAPTCHA server-side on every form by default, so
       this is a second layer, not the only one. If spam still lands, the
       stronger move is a CUSTOM-named honeypot plus a form rule, since
       spammers know `_gotcha` by name. -->
  <div class="hp" aria-hidden="true">
    <label>Leave this field empty
      <input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label>
  </div>
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
  <!-- TCPA consent, cut to the four things it legally has to carry: who is
       texting, what about, that rates may apply, and how to stop. The long
       version buried the form under a paragraph of small print. Still not
       required and still not pre-checked. -->
  <label class="consent">
    <input type="checkbox" name="SMS consent" value="Yes, agreed to receive text messages">
    <span>Text me about my estimate. Message and data rates may apply &mdash; reply
      STOP to opt out.</span>
  </label>
  <button type="submit" class="btn btn-primary wide">Send my request</button>
  <!-- Inline SVG clock, not the &#9200; character: that codepoint renders as a
       full-colour emoji on most platforms and would be the loudest thing on the
       page. Same treatment as the footer's map pin. -->
  <p class="replynote"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path
     d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm1-13h-2v6l5 3 1-1.7-4-2.3Z"/>
     </svg>{REPLY_PROMISE}.</p>
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
