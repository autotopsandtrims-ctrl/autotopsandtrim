"""Page content for autotopsandtrim.com. Run this to emit the whole site."""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_site import (  # noqa: E402
    IMAGES, SITE, PHONE_DISPLAY, PHONE_TEL, OUT,
    img, has, head, header, footer, cta, shead, quote_form, write, NAV, SERVICES, SCHEMA,
    preload_image, public_path,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = REPO
SCRATCH = HERE


HALF = "(min-width:900px) 50vw, 100vw"
THIRD = "(min-width:960px) 33vw, (min-width:640px) 50vw, 100vw"
QUARTER = "(min-width:960px) 25vw, 50vw"

pages = []

MASONRY_SIZES = "(min-width:1100px) 25vw, (min-width:760px) 33vw, 50vw"

# Verbatim Google reviews (5.0 average, 9 reviews). Transcribed from the profile —
# do not paraphrase, and never add one that isn't real.
# Two further 5-star reviews (Amani Roberts, Coby Wright) carry no written text.
# (quote, name, sub-label, when, avatar colour)
REVIEWS = [
    ("I had Auto Tops and Trim replace the headliner and center console leather in my 2008 "
     "Honda Accord. I was very happy with the quality of the work and would recommend using them.",
     "Robert Danneman", "2 reviews", "5 days ago", "#3E7D5A"),
    # SECOND ON PURPOSE. This is the only review carrying photos, and they are a
    # headliner before/after — the strongest evidence on the site. Placing it
    # second means it slides into view almost immediately in the marquee and is
    # one swipe away on the mobile rail. Do not bury it further down the list.
    #
    # Charles Monk's review is truncated by Google's "More" link; only the complete
    # sentences visible on the profile are quoted here. The profile shows one
    # further sentence beginning "He made sure to do it right and took the time to
    # redo some of it when he didn't like the way it turned…" — still cut off, so
    # it stays out until someone expands "More" and transcribes it in full.
    #
    # The two photos are HIS, attached to his own review — not shop photos. Never
    # substitute anything from assets/originals/ here.
    ("Fantastic service. The job was done quickly, while I waited. The price was cheaper than "
     "what most people were charging here locally.",
     "Charles Monk", "Local Guide &middot; 8 reviews", "a month ago", "#B5732E",
     ["review-charles-monk-headliner-before", "review-charles-monk-headliner-after"]),
    ("Mr. Hopton restored my sunroof shade back to new condition. He even allowed me to watch "
     "the process. I recommend him 100% for all of your reupholstery needs. Thank you!",
     "Ozzie Pagan", "Local Guide &middot; 15 reviews", "8 months ago", "#2F6FB0"),
    ("Excellent work. We drove an hour to get our sunroof fixed and we were very happy with "
     "the service. Highly recommend!",
     "Lauren Corgan", "15 reviews", "11 months ago", "#8A5FA6"),
    ("Excellent service and great prices I'll take back my car all the time",
     "charmaine sealey", "3 reviews", "a month ago", "#8C6B63"),
    ("Great auto shop", "Tj L", "2 reviews", "6 months ago", "#4A6B8A"),
    ("Good work", "Mark Zuck", "2 reviews", "a year ago", "#3E7D5A"),
]

RATING = "5.0"
REVIEW_COUNT = 9
GOOGLE_REVIEWS_URL = "https://share.google/T8GTbx9cswkCKF3PI"


# Every page collects the lightboxes its photos need, flushed before the footer.
_lightboxes = []


def _lb_reset():
    _lightboxes.clear()


def _lb_add(base, caption, cat=""):
    """Register a full-size lightbox for a photo; returns its anchor id."""
    lb_id = f"v-{base}"
    if any(x[0] == lb_id for x in _lightboxes):
        return lb_id
    _lightboxes.append((lb_id, base, caption, cat))
    return lb_id


def lightbox_markup():
    """CSS-only :target lightboxes with prev/next. No JavaScript."""
    if not _lightboxes:
        return ""
    out = []
    n = len(_lightboxes)
    for i, (lb_id, base, caption, cat) in enumerate(_lightboxes):
        prev_id = _lightboxes[(i - 1) % n][0]
        next_id = _lightboxes[(i + 1) % n][0]
        catline = f'<span class="cat">{cat}</span>' if cat else ""
        nav = ""
        if n > 1:
            nav = (f'<a class="lb-nav lb-prev" href="#{prev_id}" aria-label="Previous photo">&#8249;</a>'
                   f'<a class="lb-nav lb-next" href="#{next_id}" aria-label="Next photo">&#8250;</a>')
        out.append(
            f'<div class="lb" id="{lb_id}" role="dialog" aria-label="{caption}">'
            f'<a class="lb-close" href="#{lb_id}-x" aria-label="Close">Close</a>'
            f'<a class="lb-x" href="#{lb_id}-x" aria-label="Close">&times;</a>'
            f'{nav}'
            f'<div class="lb-inner">{img(base, caption, "(min-width:1200px) 1200px, 96vw")}'
            f'<p class="lb-cap">{caption}{catline}</p></div></div>')
    return "".join(out)


def masonry_tiles(items):
    """Photos at their natural aspect ratio — nothing cropped. Each opens a lightbox."""
    out = []
    for base, caption, cat in items:
        if not has(base):
            continue
        lb = _lb_add(base, caption, cat)
        out.append(
            f'<figure><a class="lb-open" href="#{lb}">{img(base, caption, MASONRY_SIZES)}'
            f'<figcaption>{caption}<span class="cat">{cat}</span></figcaption></a></figure>')
    return "".join(out)


def stars(n=5):
    return (f'<p class="stars" aria-label="{n} out of 5 stars">'
            + "&#9733;" * n + f'<span>{n} out of 5</span></p>')


def review_card(q, who, sub, when, colour, photos=None):
    """One Google review. `photos` is an optional list of image basenames that the
    reviewer attached to their own review.

    Only pass photos that came from THAT reviewer's Google review. Never put a
    shop photo here — the card presents these as the customer's own, and dressing
    a stock or shop image up as a customer upload is exactly the kind of invented
    claim the review rules above exist to prevent. Files go through
    make_responsive.py like any other image so they get srcset variants.

    Anything up to three reads well; beyond that the card gets taller than its
    neighbours in the marquee."""
    initial = who.strip()[0].upper()
    shots = ""
    if photos:
        live = [p for p in photos if has(p)]
        if live:
            tiles = "".join(
                f'<a class="lb-open" href="#{_lb_add(p, f"Photo from {who}s review")}">'
                f'{img(p, f"Photo attached to {who}s Google review", "(min-width:900px) 200px, 44vw")}</a>'
                for p in live)
            shots = f'<div class="rev-shots" data-n="{len(live)}">{tiles}</div>'
    return (f'<div class="review">'
            f'<div class="rev-top">'
            f'<span class="avatar" style="background:{colour}" aria-hidden="true">{initial}</span>'
            f'<span class="rev-id"><span class="rev-name">{who}</span>'
            f'<span class="rev-sub">{sub}</span></span></div>'
            f'<div class="rev-line">{stars()}<span class="rev-date">{when}</span></div>'
            f'<blockquote>{q}</blockquote>{shots}</div>')


def reviews_block(num="03", label="Testimonials",
                  heading="Trusted by customers for craftsmanship that lasts"):
    card = review_card
    cards = "".join(card(*r) for r in REVIEWS)
    # duplicated once, hidden from screen readers, so the loop is seamless
    dupe = f'<div class="revtrack">{cards}{cards}</div>'
    link = (f'<p style="text-align:center"><a class="googlelink" href="{GOOGLE_REVIEWS_URL}" '
            f'target="_blank" rel="noopener">Read all {REVIEW_COUNT} reviews on Google</a></p>'
            if GOOGLE_REVIEWS_URL else "")
    return f"""<section class="band dark">
  <div class="wrap stack">
    <div class="center stack">
      {shead(num, label, center=True)}
      <h2>{heading}</h2>
      <div class="ratingbadge">
        {stars()}
        <span class="line"><span class="score">{RATING}</span>
          <span class="cnt">from <b>{REVIEW_COUNT}</b> Google reviews</span></span>
      </div>
    </div>
  </div>
  <div class="revmarquee" style="margin-top:clamp(34px,4.5vw,58px)">{dupe}</div>
  <div class="wrap" style="margin-top:clamp(26px,3.5vw,44px)">{link}</div>
</section>
"""


# ============================================================== HOME
def build_home():
    _lb_reset()
    p = "index.html"
    h = head(
        "Auto Tops and Trim | Custom Upholstery in Monroe, NC Since 1989",
        "Custom upholstery in Monroe, NC. Convertible tops, seats, headliners, carpet "
        "and marine canvas for automotive, marine, aviation and motorcycle interiors. "
        "Free estimates — call (980) 385-8101.", p,
        preload=preload_image("g16-cadillac-convertible-red-interior",
                              "(min-width:900px) 52vw, 100vw"))
    h += header(p)

    # Hero slideshow. Still no per-slide captions — the slideshow makes no claim
    # about any individual photo. The four basenames below are now the canonical
    # copy of each image (see the verified-content map above GALLERY) and none of
    # them is reused anywhere else on this page, so the home page never shows the
    # same photograph twice.
    # Slide 1 must stay first: it is the LCP preload target set in head() above.
    # Reorder the rest freely, but if you change slide 1, change preload_image too
    # or the browser preloads a photo it never shows.
    hero_slides = [
        "g16-cadillac-convertible-red-interior",
        # NEW slide 2 (owner-supplied 2026-08-07): a silver convertible with a
        # full red vinyl interior - dash, door cards, front and rear benches.
        "convertible-red-vinyl-interior-full",
        # was slide 2, pushed down one on the owner's instruction
        "gallery-header-photo-wide",
        # NEW slide 4 (owner-supplied): red pickup cab, black seat, new carpet.
        # Portrait 0.75, same ratio as the portrait slide it replaces.
        "red-pickup-cab-black-seat-and-carpet",
    ]
    n_slides = len(hero_slides)
    # Must equal the `slidefade` / `doton` durations in assets/site.css. Two
    # seconds a slide across four slides = an 8s cycle. If you change the count,
    # change the CSS duration too or the dots drift out of step with the photos.
    SLIDESHOW_SECONDS = 8
    slides = "".join(
        f'<figure style="animation-delay:{i * (SLIDESHOW_SECONDS / n_slides):.1f}s">'
        f'{img(b, "Upholstery work by Auto Tops and Trim in Monroe, NC", "(min-width:900px) 52vw, 100vw", eager=(i == 0), priority=(i == 0))}'
        f"</figure>"
        for i, b in enumerate(hero_slides)
    )
    dots = "".join(f'<span style="animation-delay:{i * (SLIDESHOW_SECONDS / n_slides):.1f}s"></span>'
                   for i in range(n_slides))

    h += f"""<section class="hero">
  <div class="wrap">
    <div class="stack">
      {shead("", "Monroe, NC &middot; Since 1989")}
      <h1>Custom upholstery, expertly crafted</h1>
      <p class="lead">Convertible tops, seats, headliners and marine canvas for
        automotive, marine, aviation and motorcycle interiors &mdash; handcrafted
        in Monroe since 1989.</p>
      <div class="btnrow">
        <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn-ghost" href="contact.html">Request a Quote Online</a>
      </div>
      <p class="microline">Free estimates &nbsp;&middot;&nbsp; By photo or in person &nbsp;&middot;&nbsp; Union County</p>
    </div>
    <div class="hero-media">
      <div class="slideshow">{slides}<div class="dots" aria-hidden="true">{dots}</div></div>
    </div>
  </div>
</section>

<section class="band" id="what-we-do">
  <div class="wrap stack">
    <div class="center stack">
      {shead("01", "What we do", center=True)}
      <h2>Expert upholstery solutions for every vehicle and vessel type</h2>
      <p class="lead">Most upholstery shops do cars. We have been doing boats, aircraft
         and bikes alongside them since 1989.</p>
    </div>
    <div class="bento">
      <a class="pcard" href="auto-upholstery.html">
        {img('automotive-ford-galaxie-top-after', 'Automotive upholstery work', HALF)}
        <span class="cat">Automotive</span>
        <div class="pbody"><h3>Automotive Upholstery</h3>
          <p>Custom upholstery, convertible tops, headliners, carpet replacement and
             full interior restorations.</p>
          <span class="go">See the work</span></div>
      </a>
      <a class="pcard" href="marine-upholstery.html">
        {img('marine-seating-and-interior-upholstery', 'Runabout cockpit seating and helm trim', HALF)}
        <span class="cat">Marine</span>
        <div class="pbody"><h3>Marine Upholstery</h3>
          <p>Boat canvas tops, cushions, helm trim and weather-resistant marine materials.</p>
          <span class="go">See the work</span></div>
      </a>
      <a class="pcard" href="motorcycle-seats.html">
        {img('custom-motorcycle-seat-upholstery-close-up', 'Diamond-stitched custom motorcycle seat', HALF)}
        <span class="cat">Motorcycle</span>
        <div class="pbody"><h3>Motorcycle Upholstery</h3>
          <p>Custom seats designed for comfort, durability and performance.</p>
          <span class="go">See the work</span></div>
      </a>
      <a class="pcard" href="aviation-upholstery.html">
        {img('aircraft-interior-seat-upholstery', 'Aircraft cabin seat upholstery', HALF)}
        <span class="cat">Aviation</span>
        <div class="pbody"><h3>Aviation Upholstery</h3>
          <p>Cockpit and cabin interiors, seating, panels and carpet &mdash; a trade
             almost nobody nearby offers.</p>
          <span class="go">See the work</span></div>
      </a>
    </div>
  </div>
</section>

<section class="band tint" id="recent-work">
  <div class="wrap stack">
    <div class="center stack">
      {shead("02", "Recent work", center=True)}
      <h2>The work speaks first</h2>
      <p class="lead">A few recent jobs out of the Monroe shop.</p>
    </div>
    <!-- Every tile here is automotive on purpose. Deduplication left exactly one
         usable marine photo, one motorcycle photo and two aviation photos, and
         all four are already on this page in the bento above — putting them here
         too would show the same photograph twice under two captions, which is the
         defect this pass exists to remove. The lead no longer promises boats and
         bikes in this strip; the gallery link below carries them. -->
    <!-- ORDER IS LOad-BEARING. The masonry is CSS multi-column, which balances by
         HEIGHT, so a run of same-shape photos sends one column far past the other
         and opens a large gap. Nearly every shop photo is 1.33 portrait; only a
         handful are 0.75 landscape.

         The first six (all that show below 1100px) alternate tall/wide/tall so
         each column totals the same: 1.33 + 0.75 + 1.33 = 3.41 on both sides.
         Before this, five of the six were portrait and column two ran out after
         one tile.

         If you swap a photo here, check its ratio in _build/images.json first and
         keep the tall/wide rhythm, or the gap comes straight back. -->
    <div class="masonry">{masonry_tiles([
        ('g01-camaro-ss-new-convertible-top', 'Camaro SS — new convertible top', 'Automotive'),
        ('classic-interior-finished', 'Cadillac convertible — finished interior', 'Automotive'),
        ('g09-truck-cab-black-seat-red-stitch', 'Truck cab — black seat, red stitch', 'Automotive'),
        ('g08-cushion-and-armrest-trimmed', 'Classic Chevrolet — bench seat and door panels', 'Automotive'),
        ('g15-1969-cadillac-profile', '1969 Cadillac — profile', 'Automotive'),
        ('g12-shift-boot-and-carpet-detail', 'Shift boot and carpet detail', 'Automotive'),
        ('convertible-top-replacement-and-finish', 'Corvette — new convertible top', 'Automotive'),
        ('g13-sound-deadening-before-carpet', 'Ford F1 — headliner fitted and finished', 'Automotive'),
    ])}</div>
    <div class="btnrow" style="justify-content:center"><a class="btn btn-ghost" href="gallery.html">See the full gallery</a></div>
  </div>
</section>

""" + reviews_block() + f"""

<section class="band">
  <div class="wrap stack">
    <div class="center stack">
      {shead("04", "Why choose us", center=True)}
      <h2>Built on trust, quality, and long-term craftsmanship</h2>
      <p class="lead">Four reasons customers keep bringing their vehicles back to the
         same shop in Monroe.</p>
    </div>
    <div class="feats">
      <div class="feat"><span class="big">01</span>
        <h3>Decades of upholstery experience</h3>
        <p>From daily drivers to specialty projects, we bring proven techniques and
           detail-focused execution to every interior.</p></div>
      <div class="feat"><span class="big">02</span>
        <h3>Premium materials</h3>
        <p>We select durable, application-specific materials that hold up in real use
           while maintaining a clean, refined finish.</p></div>
      <div class="feat"><span class="big">03</span>
        <h3>Honest pricing</h3>
        <p>Clear estimates, transparent recommendations, and no unnecessary upsells so
           you can make confident project decisions.</p></div>
      <div class="feat"><span class="big">04</span>
        <h3>Custom interior solutions</h3>
        <p>Every build is tailored to your vehicle, style, and comfort goals, whether it
           is restoration work or a modern upgrade.</p></div>
    </div>
  </div>
</section>
"""
    h += cta()
    h += footer(lightbox_markup())
    pages.append(p)
    return write(p, h)


# ============================================================== SERVICE PAGES
def service_page(slug, title, desc, eyebrow, h1, intro, hero_photo, sections,
                 photos, faqs, gallery_caps=None, extra_html=""):
    _lb_reset()
    h = head(title, desc, slug, faqs=faqs)
    h += header("services.html")
    h += f"""<section class="hero">
  <div class="wrap">
    <div class="stack">
      {shead("", eyebrow)}
      <h1>{h1}</h1>
      <p class="lead">{intro}</p>
      <div class="btnrow">
        <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn-ghost" href="contact.html">Free estimate</a>
      </div>
    </div>
    {f'<div class="hero-media">{img(hero_photo, h1, HALF, eager=True)}</div>' if hero_photo else ''}
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="grid g3">
"""
    for stitle, items in sections:
        lis = "".join(f"<li>{i}</li>" for i in items)
        h += f'<div class="stack"><h3>{stitle}</h3><ul class="ticks">{lis}</ul></div>\n'
    h += """    </div>
  </div>
</section>
"""
    if photos:
        caps = gallery_caps or [""] * len(photos)
        # Same masonry + click-to-enlarge treatment as the home page recent-work
        # block, so photo sections read consistently across the site.
        tiles = masonry_tiles([(ph, cap or h1, eyebrow)
                               for ph, cap in zip(photos, caps)])
        h += f"""<section class="band tint" id="recent-work">
  <div class="wrap stack">
    <div class="stack">{shead("02","Recent work")}<h2>Jobs out of this shop</h2></div>
    <div class="masonry svc-shots">{tiles}</div>
    <div class="btnrow" style="justify-content:center"><a class="btn btn-ghost" href="gallery.html">See the full gallery</a></div>
  </div>
</section>
"""
    if faqs:
        items = "".join(
            f"<details><summary>{q}</summary><div class='ans'>{a}</div></details>"
            for q, a in faqs
        )
        h += f"""<section class="band">
  <div class="wrap narrow stack">
    <div class="stack">{shead("03","Frequently asked questions")}<h2>Answers before you call</h2></div>
    <div class="faq">{items}</div>
  </div>
</section>
"""
    h += extra_html
    h += cta()
    h += footer(lightbox_markup())
    pages.append(slug)
    return write(slug, h)


def build_services():
    _lb_reset()
    service_page(
        "convertible-tops.html",
        "Convertible Top Replacement in Monroe, NC | Auto Tops and Trim",
        "Convertible top replacement in Monroe, NC. Vinyl and canvas tops, heated glass "
        "or plastic rear windows, frame and pad repair. Free estimates — (980) 385-8101.",
        "Convertible tops", "Convertible top replacement in Monroe, NC",
        "A new top is really three jobs: the fabric, the window, and whatever needs "
        "repairing on the frame underneath. We quote all three.",
        # was `convertible-top-after`, which is a truck cab interior, not a top
        "convertible-top-replacement-and-finish",
        [("Materials", ["Quality vinyl — holds up well in Carolina sun",
                        "Canvas cloth — correct on a classic, ages gracefully",
                        "Samples shown in the shop before you decide"]),
         ("Windows", ["Heated glass rear windows",
                      "Plastic curtain replacement",
                      "Often the reason the top failed first"]),
         ("The frame underneath", ["Collapsed pad replacement",
                                   "Bent bow straightening",
                                   "Checked before we quote, not after"])],
        # Dropped g05 (it is a Cadillac front end, not a cloth top) and g17
        # (a duplicate of g16, and the top is stowed in it anyway).
        ["g01-camaro-ss-new-convertible-top", "automotive-interior-restoration-detail",
         "automotive-ford-galaxie-top-after", "g18-camaro-ss-profile"],
        [("How much does a convertible top replacement cost?",
          "It depends on three things: the material you choose, whether the rear window is "
          "heated glass or plastic, and the condition of the frame and pads underneath. Most "
          "quotes people bring us from elsewhere only cover the fabric. We give you an itemized "
          "estimate covering all three, at no cost."),
         ("Can you quote from a photo?",
          "Yes &mdash; send photos over and we will get an estimate back to you. On a convertible "
          "top we will usually want to see the car before the number is final, because a photo "
          "cannot show collapsed pads or bent bows, and a new top fitted over a bad frame will "
          "never sit right. The estimate is free either way."),
         ("Vinyl or canvas — which should I pick?",
          "Vinyl costs less up front and handles the sun here very well. Canvas cloth costs more, "
          "looks correct on a classic, and ages more gracefully. We keep both in the shop so you "
          "can see and feel the difference before deciding."),
         ("How long does it take?",
          "Most tops are a few days once the material is in hand. Frame or pad repair adds time. "
          "We will give you a realistic window with the estimate.")],
        ["Camaro SS — new convertible top", "Burgundy cloth top — rear window",
         "Ford Galaxie — top fitted", "Camaro SS — profile"])

    service_page(
        "auto-upholstery.html",
        "Auto Upholstery in Monroe, NC | Seats, Headliners, Carpet",
        "Automotive upholstery in Monroe, NC. Seat repair and rebuilds, headliners, door "
        "panels, carpet and full classic interiors. Free estimates — (980) 385-8101.",
        "Automotive upholstery", "Seats, headliners and interiors",
        "From a single torn seat to a complete classic interior built to your spec. "
        "Daily drivers, trucks, and show cars.",
        "seat-rebuild-after",
        [("Seats", ["Torn and worn seat repair", "Foam replacement and reshaping",
                    "Seat frame rebuild and structural repair", "Custom stitch and piping"]),
         ("Interior trim", ["Headliner replacement", "Door panels, pleated or plain",
                            "Carpet fitted and bound", "Shift boots and console trim"]),
         ("Full restoration", ["Period-correct or upgraded builds",
                               "Sound deadening under the carpet",
                               "Materials specified with you first"])],
        # Dropped headliner-install (a duplicate Cadillac exterior) and moved
        # automotive-interior-restoration-detail to the convertible-tops page,
        # which is what it actually shows.
        ["g06-ford-f1-cab-seat-carpet-and-trim", "g07-bench-seat-red-piping-in-the-shop",
         "g09-truck-cab-black-seat-red-stitch", "g13-sound-deadening-before-carpet",
         "g11-carpet-fitted-and-trimmed", "g19-mercedes-gla-interior-work",
         "g12-shift-boot-and-carpet-detail", "g08-cushion-and-armrest-trimmed",
         "g10-bel-air-new-carpet-going-in", "marine-canvas-cushions"],
        [("Do you repair a single seat, or only full interiors?",
          "Either. Plenty of our work is one torn driver's seat or a sagging headliner. "
          "You do not need a full restoration to come see us."),
         ("How long does a seat repair take?",
          "A straightforward seat repair is usually quick once materials are in. Bigger jobs "
          "depend on what we find under the cover — broken frames and collapsed foam add time. "
          "We will tell you what we find before we proceed."),
         ("Do you work on modern cars as well as classics?",
          "Yes. Late-model seats, headliners and trim are routine work here alongside the "
          "restoration projects."),
         ("Can you match the original material?",
          "Usually. For a classic we chase correct grain, stitch spacing and carpet weave. "
          "Where an exact original is no longer made, we will show you the closest options.")],
        ["Ford F1 cab — sound deadening down", "Cushion and armrest, trimmed on the bench",
         "Truck cab — black seat, red stitch", "Ford F1 — headliner fitted and finished",
         "Classic Chevrolet — carpet fitted", "Ford F1 cab — rebuilt seat and carpet",
         "Shift boot and carpet detail", "Classic Chevrolet — bench seat and door panels",
         "Classic Chevrolet — new carpet going in", "Classic coupe — rear bench seat"])

    service_page(
        "marine-upholstery.html",
        "Marine Upholstery in Monroe, NC | Boat Seats and Canvas",
        "Marine upholstery near Charlotte, NC. Boat seating, helm trim, cushions and canvas "
        "in UV-stabilised marine vinyl. Free estimates — (980) 385-8101.",
        "Marine upholstery", "Boat seating, cushions and canvas",
        "Leather belongs in a car, not on the water. For marine work we specify materials "
        "built for standing water, UV and salt.",
        "marine-seating-and-interior-upholstery",
        [("Seating and cushions", ["UV-stabilised, mildew-resistant marine vinyl",
                                   "Quick-dry reticulated foam that passes water through",
                                   "Thread that will not rot", "Helm and console trim"]),
         ("Canvas", ["Solution-dyed acrylic holds colour in full sun",
                     "Covers, tops and enclosures",
                     "The difference shows in year three, not year one"]),
         ("Bring one piece", ["We will tell you honestly whether it needs recovering or replacing",
                              "No charge to look"])],
        # This strip previously showed the hero photo twice more under two other
        # filenames, plus `marine-canvas-cushions`, which is a car interior.
        ["boat-upholstery-projects-at-the-shop",
         "upholstery-materials-and-marine-project-parts"],
        [("Why not leather on a boat?",
          "Leather is wonderful in a car interior. On the water it is a maintenance problem — "
          "standing water, UV and salt will dry it out and crack it within a season or two."),
         ("My cushions stay damp. Can that be fixed?",
          "Usually yes, and the foam is normally the culprit rather than the cover. Quick-dry "
          "reticulated foam lets water pass through instead of holding it against the cushion."),
         ("Do I have to bring the whole boat?",
          "No. Bring one cushion or one piece of canvas by the shop and we can tell you what "
          "you are looking at."),
         ("My canvas has gone chalky — recover or replace?",
          "Depends how far it has gone. Chalking is usually a sign of a cheaper coated fabric "
          "reaching the end of its life. We will give you an honest answer when we see it.")],
        ["Boat in for upholstery at the shop", "Project parts on the shop bench"])

    service_page(
        "aviation-upholstery.html",
        "Aviation Upholstery in Monroe, NC | Aircraft Cabin and Cockpit Interiors",
        "Aircraft interior upholstery in Monroe, NC. Cockpit and cabin seating, panels and "
        "trim, finished to a high standard. Free estimates — (980) 385-8101.",
        "Aviation upholstery", "Aircraft cabin and cockpit interiors",
        "A rare trade in this region. We have been trimming aircraft interiors alongside "
        "cars and boats for decades.",
        "aircraft-interior-seat-upholstery",
        [("Seating", ["Cockpit and cabin seats", "Foam replacement and reshaping",
                      "Stitched detail work to a high finish"]),
         ("Cabin trim", ["Side panels and trim", "Carpet and floor coverings",
                         "Consistent finish across the cabin"]),
         ("Working with you", ["Materials specified before any cutting starts",
                               "Bring the aircraft or the seats to the shop",
                               "Free, itemised estimate"])],
        # Both dropped entries were the hero photo again under other filenames.
        ["aircraft-cabin-upholstery-craftsmanship"],
        [("Do you do full cabin interiors?",
          "Yes — seating, side panels, carpet and trim, finished consistently across the cabin."),
         ("Can I bring just the seats?",
          "Absolutely, and it is often the easiest way to do it. Remove them and bring them to "
          "the shop in Monroe."),
         ("How is aviation work different from automotive?",
          "The standard of finish and the attention to weight and fit are higher, and the "
          "materials differ. It is the same craft, held to a tighter tolerance.")],
        ["Aircraft cabin — divan and club seat"])

    service_page(
        "motorcycle-seats.html",
        "Custom Motorcycle Seats in Monroe, NC | Auto Tops and Trim",
        "Custom motorcycle seat upholstery in Monroe, NC. Reshaping, recovering, diamond "
        "stitch and custom detail work. Free estimates — (980) 385-8101.",
        "Motorcycle upholstery", "Custom motorcycle seats",
        "Recovered, reshaped, or built to your own pattern — for daily riders "
        "and show bikes alike.",
        "custom-motorcycle-seat-upholstery-close-up",
        [("Seat work", ["Recovering worn or split seats", "Foam reshaping for comfort and height",
                        "Pan repair where needed"]),
         ("Custom detail", ["Diamond and pleated stitch patterns",
                            "Contrast thread and piping", "Two-tone and custom material combinations"]),
         ("Turnaround", ["Bring the seat in on its own — no need for the bike",
                         "Free estimate, no obligation"])],
        # All three tiles were removed and the "Recent work" band drops out with
        # them. Two were the hero photo again under other filenames, and
        # `custom-bike-seat` is a burgundy convertible top on a white car — no
        # motorcycle in the frame at all. The catalogue has exactly one bike
        # photo, and it is already the hero. Restore this band when the shop
        # supplies real motorcycle work.
        [],
        [("Do I need to bring the whole bike?",
          "No — take the seat off and bring it in. That is how most of these jobs start."),
         ("Can you make the seat taller or lower?",
          "Often yes. Reshaping the foam can change the height and the riding position. Tell us "
          "what is uncomfortable and we will talk through the options."),
         ("Can you do a custom stitch pattern?",
          "Yes. Diamond, pleated, contrast thread, two-tone — bring a picture of what you want "
          "and we will tell you what is achievable on your pan.")],
        [])

    # Two of the nine Google reviews are specifically about sunroof shade work.
    # Quoted verbatim — these are the only claims made about this service.
    sunroof_reviews = [r for r in REVIEWS
                       if r[1] in ("Ozzie Pagan", "Lauren Corgan")]
    sunroof_voices = f"""<section class="band dark">
  <div class="wrap stack">
    <div class="center stack">
      {shead("03", "In their words", center=True)}
      <h2>Two of our Google reviews are about this exact repair</h2>
    </div>
    <div class="grid g2" style="margin-top:clamp(30px,4vw,52px)">
      {"".join(review_card(*r) for r in sunroof_reviews)}
    </div>
    <p style="text-align:center"><a class="googlelink" href="{GOOGLE_REVIEWS_URL}"
       target="_blank" rel="noopener">Read all {REVIEW_COUNT} reviews on Google</a></p>
  </div>
</section>
"""

    service_page(
        "sunroof-shade-repair.html",
        "Sunroof Shade Repair in Monroe, NC | Auto Tops and Trim",
        "Sagging or torn sunroof shade? We recover the sliding sunshade panel in Monroe, NC "
        "instead of replacing the whole assembly. Free estimates — (980) 385-8101.",
        "Sunroof shades", "Sunroof shade repair in Monroe, NC",
        "When the sliding shade over your sunroof sags, tears or stops retracting, the fabric "
        "is usually the only thing that has failed. We recover the panel you already have.",
        None,   # no honest photo exists for this service yet — see HANDOFF
        [("What we repair", ["Sagging or drooping shade fabric",
                             "Torn, split or stained shade panels",
                             "Fabric that has come unbonded from the slider",
                             "Shades that no longer slide or retract cleanly"]),
         ("How we approach it", ["The existing panel is recovered where it is sound",
                                 "Material matched to your headliner in the shop",
                                 "You are welcome to watch the work",
                                 "Quoted from photos or in person, free of charge"]),
         ("Worth knowing", ["A dealer often quotes the whole sunroof cassette",
                            "The shade is trim work — it is what this shop does",
                            "Bring the vehicle by; we will tell you what it needs",
                            "Customers drive in from Charlotte and Union County"])],
        [],   # no sunroof photos exist in the catalogue yet — none invented
        [("My sunroof shade is sagging. Can it be fixed, or do I need a whole new sunroof?",
          "In most cases the sunroof itself is fine and only the shade fabric has failed. The "
          "fabric is bonded to a thin sliding panel, and over years of Carolina heat that bond "
          "lets go and the material droops or tears. Recovering that panel is upholstery work. "
          "Bring it by and we will tell you honestly which one you are looking at."),
         ("The dealer quoted me for the entire sunroof assembly. Why is your quote different?",
          "Because they are usually quoting a different job. Replacing the whole cassette means "
          "new hardware, glass mechanism and labour. If the mechanism still works and only the "
          "shade has failed, that is a trim repair, not an assembly replacement. We will look at "
          "it and tell you which is actually needed."),
         ("Can you match the material to the rest of my headliner?",
          "That is the goal, and we keep material in the shop so you can see and feel it against "
          "your own headliner before deciding. On an older interior that has faded, an exact match "
          "is not always possible — we will show you the closest options rather than promise one."),
         ("How long does it take, and do I need an appointment?",
          "It depends on the vehicle and how the shade is mounted, so we will give you a realistic "
          "window with the free estimate. Calling ahead on "
          f"{PHONE_DISPLAY} is the surest way to catch us with time to look at it."),
         ("Can you quote it from a photo?",
          "Yes. Send photos of the shade and we will come back to you with an estimate. We may "
          "still want to look at it in person before confirming, because a photo will not show "
          "whether the slider and the mechanism are still sound, and that is the part that "
          "decides whether this is a simple recover or a bigger job. The estimate is free "
          "either way.")],
        extra_html=sunroof_voices)


# ============================================================== SERVICES INDEX
def build_services_index():
    _lb_reset()
    p = "services.html"
    h = head("Upholstery Services | Auto Tops and Trim, Monroe NC",
             "Automotive, marine, aviation and motorcycle upholstery in Monroe, NC. Convertible "
             "tops, seats, headliners, carpet, boat canvas, sunroof shades and custom bike seats.", p)
    h += header(p)

    cards = [
        ("convertible-tops.html", "Convertible Tops", "g01-camaro-ss-new-convertible-top",
         "Vinyl and canvas tops, heated glass and plastic windows, plus the frame and pad "
         "work underneath that most quotes leave out.",
         ["Vinyl and canvas", "Heated glass windows", "Frame and pad repair"]),
        ("auto-upholstery.html", "Auto Upholstery", "seat-rebuild-after",
         "Seats, headliners, door panels and carpet, from one torn seat to a complete "
         "classic interior built to your spec.",
         ["Seat repair and rebuilds", "Headliners and door panels", "Carpet and sound deadening"]),
        ("sunroof-shade-repair.html", "Sunroof Shade Repair", None,
         "Sagging, torn or stuck sliding sunshade? We recover the panel you already have "
         "instead of replacing the whole sunroof assembly.",
         ["Sagging and torn shades", "Matched to your headliner", "Recover, not replace"]),
        ("marine-upholstery.html", "Marine Upholstery", "marine-seating-and-interior-upholstery",
         "Boat seating, helm trim, cushions and canvas in materials built for sun, "
         "standing water and salt.",
         ["UV-stabilised marine vinyl", "Quick-dry foam", "Solution-dyed canvas"]),
        ("aviation-upholstery.html", "Aviation Upholstery", "aircraft-cabin-upholstery-craftsmanship",
         "Cockpit and cabin interiors, seating, panels and carpet. A trade almost nobody "
         "else in the region offers.",
         ["Cockpit and cabin seats", "Side panels and trim", "Cabin carpet"]),
        ("motorcycle-seats.html", "Motorcycle Seats", "custom-motorcycle-seat-upholstery-close-up",
         "Recovered, reshaped or built to your own pattern, with custom stitch work and "
         "contrast detail.",
         ["Recover and reshape", "Diamond and pleated stitch", "Pan repair"]),
    ]

    rows = ""
    for i, (href, title, photo, blurb, bullets) in enumerate(cards, 1):
        lis = "".join(f"<li>{b}</li>" for b in bullets)
        rows += f"""<div class="svc{'' if photo else ' nomedia'}">
      {f'<div class="svc-media">{img(photo, title, HALF)}</div>' if photo else ''}
      <div class="svc-body">
        <span class="svc-n">0{i}</span>
        <h2>{title}</h2>
        <p class="lead">{blurb}</p>
        <ul class="ticks">{lis}</ul>
        <a class="btn btn-ghost" href="{href}">{title} &rarr;</a>
      </div>
    </div>
"""

    h += f"""<section class="band" style="padding-bottom:0">
  <div class="wrap center stack">
    {shead("01", "Services", center=True)}
    <h1>Expert upholstery for every vehicle and vessel type</h1>
    <p class="lead">Four trades under one roof in Monroe, North Carolina.
       Every job is quoted free of charge, from your photos or in person.</p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="svclist">{rows}</div>
  </div>
</section>
"""
    h += cta()
    h += footer(lightbox_markup())
    pages.append(p)
    write(p, h)

# ============================================================== GALLERY
#
# CAPTION RULE: the basenames below came out of the old bundle and DO NOT
# describe their images. Every caption here was rewritten on 2026-08-05 by
# opening each file and describing what is in the frame. Never caption one of
# these from its filename, and never reuse a caption on a photo you have not
# looked at. Nine filenames were flatly wrong — e.g. `headliner-install` is a
# Cadillac convertible exterior with no headliner in it at all.
#
# VERIFIED CONTENT of every master in assets/originals/ (43 files, 33 distinct
# images — 7 duplicate groups are marked DUP OF and are not used twice on any
# one page):
#
#   g01-camaro-ss-new-convertible-top ... black/yellow Camaro convertible, black
#       top up, parked at the shop
#   g18-camaro-ss-profile ............... same Camaro, side profile by the fence
#   convertible-top-replacement-and-finish  red C5 Corvette, new black top, at
#       the shop (the OLD phone number is legible on the sign)
#   automotive-ford-galaxie-top-after ... blue Ford Galaxie convertible, tan top
#       up, NC plate
#   services-strip-4 .................... same blue Galaxie, top down, black
#       tonneau fitted over the top well
#   automotive-interior-restoration-detail  burgundy cloth top + rear window on a
#       white car, in a garage.  NOT an interior detail.
#   custom-bike-seat .................... DUP OF automotive-interior-restoration-detail.
#       NOT a bike seat.
#   g16-cadillac-convertible-red-interior  grey '69 Cadillac convertible, top
#       down, red interior, door open, at the shop
#   headliner-install ................... DUP OF g16. NOT a headliner.
#   g17-cadillac-top-and-interior-finished  DUP OF g16.
#   hero-best-finished-vehicle-wide-full-color  DUP OF g16.
#   classic-interior-finished ........... same Cadillac, DIFFERENT angle (front
#       three-quarter, door open) — a genuinely separate photo
#   g15-1969-cadillac-profile ........... same Cadillac low/side, pink underglow
#   g05-burgundy-cloth-top-rear-window .. that Cadillac's FRONT END at dusk, pink
#       underglow, halo headlights, "1969 Cadillac" plate.  NOT a cloth top.
#   gallery-header-photo-wide ........... red Ford F1 pickup at the shop with the
#       finished black bench seat on the driveway beside it
#   g06-ford-f1-cab-seat-carpet-and-trim  that F1's cab with Siless sound
#       deadening laid down — no seat and no carpet in it yet
#   g13-sound-deadening-before-carpet ... that F1's finished black HEADLINER,
#       visors and mirror.  The opposite of its filename.
#   g19-mercedes-gla-interior-work ...... that F1's cab interior, rebuilt black
#       seat with red stitch, concert posters in the back window.  NOT a Mercedes.
#   g09-truck-cab-black-seat-red-stitch . that F1's dash, gauges and seat
#   convertible-top-after ............... DUP OF g09. NOT a convertible top.
#   g08-cushion-and-armrest-trimmed ..... mid-50s Chevrolet interior — black bench
#       with red piping, red/black door panels, tools on the floor
#   g10-bel-air-new-carpet-going-in ..... that Chevrolet's dash and new black
#       carpet (badge reads Chevrolet; the Bel Air trim claim is unverifiable)
#   g11-carpet-fitted-and-trimmed ....... that Chevrolet, door open, carpet down
#   g12-shift-boot-and-carpet-detail .... shift boot with red stitching on black
#       carpet — the one g-caption that was already correct
#   marine-canvas-cushions .............. rear bench seat inside a classic red
#       coupe, grey headliner.  A CAR. It was filed under Marine.
#   g07-bench-seat-red-piping-in-the-shop  black cushion and armrest upside down
#       on the shop bench, staples showing.  No red piping visible.
#   services-strip-1 .................... black bench cushion WITH red piping and
#       armrest on the shop table
#   services-strip-3 .................... black bench seat with red piping, mid
#       rebuild in the shop
#   seat-rebuild-after .................. finished black bench seat with red
#       stitching, outdoors by the wooden fence
#   process-header-photo-wide ........... DUP OF seat-rebuild-after
#   services-strip-2 .................... red C8 Corvette in a field
#   services-strip-5 .................... night shot at the shop, Jeep with
#       underglow (unused)
#   owner-shop-leadership-grayscale ..... the shop building at dusk with cars out
#       front.  IN COLOUR, and there is no person in it.
#   boat-upholstery-projects-at-the-shop  the shop building with a boat on a
#       trailer parked outside
#   upholstery-materials-and-marine-project-parts  weathered outdoor table with
#       trim panels and a spray can. Nothing identifies them as marine.
#
#   -- provenance unconfirmed, see HANDOFF: these four read as commercial
#      photography and carry no cue tying them to the Monroe shop --
#   marine-seating-and-interior-upholstery  varnished-wood runabout cockpit, tan
#       leather, white wheel, orange life ring
#   g22-marine-cushions-and-helm-trim ... DUP OF marine-seating-and-interior-upholstery
#   marine-boat-cushions-canvas ......... DUP OF marine-seating-and-interior-upholstery
#   aircraft-interior-seat-upholstery ... cream quilted aircraft cabin seats
#   aviation-cabin-seats ................ DUP OF aircraft-interior-seat-upholstery
#   aircraft-cabin-upholstery-craftsmanship  private-jet cabin, cream divan and
#       club seat
#   custom-motorcycle-seat-upholstery-close-up  diamond-quilted seat on a mint
#       green cafe racer
#   motorcycle-custom-seat .............. DUP OF custom-motorcycle-seat-upholstery-close-up
#
GALLERY = [
    ("g01-camaro-ss-new-convertible-top", "Camaro SS — new convertible top", "Automotive"),
    ("g18-camaro-ss-profile", "Camaro SS — profile", "Automotive"),
    ("convertible-top-replacement-and-finish", "Corvette — new convertible top", "Automotive"),
    ("automotive-ford-galaxie-top-after", "Ford Galaxie — top fitted", "Automotive"),
    ("automotive-interior-restoration-detail", "Burgundy cloth top — rear window", "Automotive"),
    ("g16-cadillac-convertible-red-interior", "Cadillac convertible — red interior, top down", "Automotive"),
    ("classic-interior-finished", "Cadillac convertible — finished interior", "Automotive"),
    ("g15-1969-cadillac-profile", "1969 Cadillac — profile", "Automotive"),
    ("g05-burgundy-cloth-top-rear-window", "1969 Cadillac — front end", "Automotive"),
    ("gallery-header-photo-wide", "Ford F1 — finished bench seat, ready to fit", "Automotive"),
    ("g06-ford-f1-cab-seat-carpet-and-trim", "Ford F1 cab — sound deadening down", "Automotive"),
    ("g13-sound-deadening-before-carpet", "Ford F1 — headliner fitted and finished", "Automotive"),
    ("g19-mercedes-gla-interior-work", "Ford F1 cab — rebuilt seat and carpet", "Automotive"),
    ("g09-truck-cab-black-seat-red-stitch", "Truck cab — black seat, red stitch", "Automotive"),
    ("g08-cushion-and-armrest-trimmed", "Classic Chevrolet — bench seat and door panels", "Automotive"),
    ("g10-bel-air-new-carpet-going-in", "Classic Chevrolet — new carpet going in", "Automotive"),
    ("g11-carpet-fitted-and-trimmed", "Classic Chevrolet — carpet fitted", "Automotive"),
    ("g12-shift-boot-and-carpet-detail", "Shift boot and carpet detail", "Automotive"),
    ("marine-canvas-cushions", "Classic coupe — rear bench seat", "Automotive"),
    ("g07-bench-seat-red-piping-in-the-shop", "Cushion and armrest, trimmed on the bench", "Automotive"),
    ("seat-rebuild-after", "Seat rebuild — finished", "Automotive"),
    ("boat-upholstery-projects-at-the-shop", "Boat in for upholstery at the shop", "Marine"),
    # REMOVED 2026-08-07: the runabout cockpit, the two aircraft cabin shots and
    # the cafe-racer seat. The owner supplied 283 photographs of his actual work
    # that day and NOT ONE is aviation or motorcycle, which settles the
    # provenance question this file has carried since 2026-08-05 - those four are
    # not his. The lead directly below this list says every piece was cut,
    # stitched and fitted in house, so they could not stay and leave it true.
    # They are still referenced by the service pages and six blog posts; that
    # rewiring is the remaining half of the job (see HANDOFF).
]


def build_gallery():
    _lb_reset()
    p = "gallery.html"
    h = head("Gallery | Auto Tops and Trim, Monroe NC",
             "Upholstery work from Auto Tops and Trim in Monroe, NC — convertible tops, "
             "seats, headliners, carpet, boat cushions, aircraft cabins and custom bike seats.", p)
    h += header(p)
    tiles = masonry_tiles(GALLERY)
    h += f"""<section class="band">
  <div class="wrap stack">
    <div class="stack">{shead("01","Gallery")}
      <h1>Work out of the Monroe shop</h1>
      <p class="lead">Every piece here was cut, stitched and fitted in house.</p></div>
    <div class="masonry">{tiles}</div>
  </div>
</section>
"""
    h += cta(num="02", label="Your project next",
             heading="See something close to your project?",
             sub="Bring the vehicle, the boat, or just the seat by the shop and we will "
                 "give you an itemised estimate at no cost.")
    h += footer(lightbox_markup())
    pages.append(p)
    write(p, h)


# ============================================================== PROCESS / ABOUT / CONTACT
def build_process():
    _lb_reset()
    p = "process.html"
    h = head("Our Process | Auto Tops and Trim, Monroe NC",
             "How a job runs at Auto Tops and Trim in Monroe, NC — from free in-person "
             "estimate through material selection, the work itself, and fitting.", p)
    h += header(p)
    # (tag, title, copy, photo) — tag is the one-line "what this costs you"
    steps = [
        ("Walk in or call ahead", "You bring it in",
         "Drive the vehicle over, trailer the boat, or carry in a single seat. "
         "We look at it with you and talk through what you want.",
         "services-strip-1"),
        ("Free, and itemised", "We quote the job",
         "We check what is under the cover — foam, frames, pads, bows — because that is "
         "where surprises live. Then you get an itemised estimate at no charge.",
         # was process-header-photo-wide, which is this page's hero photo again
         "boat-upholstery-projects-at-the-shop"),
        ("Samples in hand", "You pick the materials",
         "We keep samples in the shop. Vinyl or canvas, glass or plastic window, "
         "period-correct or upgraded — you see and feel the difference before deciding.",
         "services-strip-3"),
        ("Same hands throughout", "We do the work",
         "Disassembly, repair of what is underneath, then cutting and stitching. "
         "The same hands that quoted the job do the work.",
         "services-strip-2"),
        ("Checked with you", "Fitting and finish",
         "Nothing leaves until it fits properly. Weather sealing on marine and "
         "convertible work, and a final check with you at pickup.",
         "services-strip-4"),
    ]
    flow = "".join(
        f'<div class="flow-step"><span class="flow-n">{i:02d}</span>'
        f'<div class="flow-body"><span class="flow-tag">{tag}</span><h3>{t}</h3><p>{d}</p></div>'
        f'<div class="flow-media">{img(photo, t, HALF)}</div></div>'
        for i, (tag, t, d, photo) in enumerate(steps, 1))

    # What the free estimate actually covers — the differentiator, in the
    # signature outlined-numeral columns.
    covers = [
        ("The cover itself", "Material, colour and stitch — the part every quote includes."),
        ("What is underneath", "Foam, frames, pads and bows. This is the part most quotes leave out."),
        ("The windows and seals", "Rear windows, weather sealing and anything that will let water in."),
        ("The realistic timing", "How long it will actually take, told to you before you commit."),
    ]
    covercols = "".join(
        f'<div class="feat"><span class="big">{i:02d}</span><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(covers, 1))

    h += f"""<section class="hero">
  <div class="wrap">
    <div class="stack">{shead("","How it works")}
      <h1>What happens after you call</h1>
      <p class="lead">No mystery and no deposit to find out what a job costs.
         Here is the whole sequence, start to finish.</p>
      <div class="btnrow">
        <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn-ghost" href="contact.html">Request a quote</a>
      </div></div>
    <div class="hero-media">{img('seat-rebuild-after', 'A rebuilt bench seat, finished and ready to fit', HALF, eager=True)}</div>
  </div>
</section>

<section class="band">
  <div class="wrap stack">
    <div class="stack">{shead("01", "Step by step")}
      <h2>Five steps, and you are told the price before step three</h2></div>
    <div class="flow">{flow}</div>
  </div>
</section>

<section class="band tint">
  <div class="wrap stack">
    <div class="stack">{shead("02", "The estimate")}
      <h2>What the free estimate actually covers</h2>
      <p class="lead">An estimate that only prices the fabric is not an estimate.
         Here is everything we look at before we give you a number.</p></div>
    <div class="feats">{covercols}</div>
  </div>
</section>

{reviews_block(num="03", label="Testimonials",
               heading="What it is like to actually work with us")}
"""
    h += cta(num="04")
    h += footer(lightbox_markup())
    pages.append(p)
    write(p, h)


def build_about():
    _lb_reset()
    p = "about.html"
    h = head("About | Auto Tops and Trim, Monroe NC Since 1989",
             "Auto Tops and Trim has been trimming automotive, marine, aviation and "
             "motorcycle interiors in Monroe, North Carolina since 1989.", p)
    h += header(p)
    h += f"""<section class="hero">
  <div class="wrap">
    <div class="stack">{shead("","About the shop")}
      <h1>Trimming interiors in Monroe since 1989</h1>
      <p class="lead">What began as a focused automotive upholstery shop grew into a
         multi-disciplinary interior restoration business — cars, boats, aircraft and bikes.</p></div>
    <div class="hero-media">{img('owner-shop-leadership-grayscale', 'The Auto Tops and Trim shop on West Highway 74 in Monroe', HALF, eager=True)}</div>
  </div>
</section>

<section class="band">
  <div class="wrap narrow stack">
    <div class="stack">{shead("01", "The craft")}<h2>A trade you learn by doing</h2></div>
    <p class="lead">Upholstery is not a job you can rush or fake. A top fitted over collapsed
       pads will never sit right. Foam that is wrong for a boat will hold water against the
       cushion. Knowing the difference is what over three decades buys you.</p>
    <p class="lead">Send photos and we will get an estimate back to you. It is also why some
       jobs need a look before the number is final &mdash; a photograph cannot show a bent bow
       or a rusted seat frame, and on that kind of work we would rather confirm it with the
       vehicle in front of us than revise the price later.</p>
  </div>
</section>

<section class="band tint">
  <div class="wrap stack">
    <div class="stack">{shead("02","Inside the shop")}<h2>How the work gets done</h2></div>
    <div class="grid g4 swiperow">
      <figure class="tile">{img('services-strip-1', 'A bench seat cushion with red piping on the shop table', QUARTER)}</figure>
      <figure class="tile">{img('services-strip-3', 'A bench seat part way through a rebuild in the shop', QUARTER)}</figure>
      <figure class="tile">{img('services-strip-4', 'A Ford Galaxie with the tonneau cover fitted over the top well', QUARTER)}</figure>
      <figure class="tile">{img('services-strip-2', 'A Corvette outside the shop', QUARTER)}</figure>
    </div>
  </div>
</section>

<section class="band dark">
  <div class="wrap stack">
    <div class="center stack">
      {shead("03", "By the numbers", center=True)}
      <h2>Four trades, one roof, since 1989</h2>
      <p class="lead">Cars, boats, aircraft and bikes are four different crafts.
         Most shops pick one. We kept all four in the same building in Monroe.</p>
    </div>
    <div class="stats" style="margin-top:clamp(30px,4vw,52px)">
      <div class="stat"><b>1989</b><span>Trimming since</span></div>
      <div class="stat"><b>4</b><span>Trades under one roof</span></div>
      <div class="stat"><b>35+</b><span>Years in Union County</span></div>
      <div class="stat"><b>Free</b><span>Estimates on every job</span></div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack">
    <div class="stack">{shead("04", "What we take in")}
      <h2>If it has a seat, a top or a panel, bring it</h2></div>
    <div class="grid g2">
      <a class="card" href="convertible-tops.html"><div class="card-body">
        <h3>Convertible tops</h3>
        <p>Vinyl and canvas, heated glass and plastic windows, and the frame and
           pad work underneath that most quotes leave out.</p>
        <span class="card-link">Convertible tops</span></div></a>
      <a class="card" href="auto-upholstery.html"><div class="card-body">
        <h3>Seats, headliners and interiors</h3>
        <p>One torn seat or a complete classic interior built to your spec, for
           daily drivers, trucks and show cars alike.</p>
        <span class="card-link">Auto upholstery</span></div></a>
      <a class="card" href="marine-upholstery.html"><div class="card-body">
        <h3>Boats</h3>
        <p>Seating, helm trim, cushions and canvas in materials chosen for sun,
           standing water and salt.</p>
        <span class="card-link">Marine upholstery</span></div></a>
      <a class="card" href="aviation-upholstery.html"><div class="card-body">
        <h3>Aircraft</h3>
        <p>Cockpit and cabin interiors, seating, side panels and carpet &mdash; a
           trade almost nobody else in the region offers.</p>
        <span class="card-link">Aviation upholstery</span></div></a>
    </div>
  </div>
</section>

{reviews_block(num="05", label="Testimonials",
               heading="Thirty-seven years of this, in their words")}
"""
    h += cta(num="06")
    h += footer(lightbox_markup())
    pages.append(p)
    write(p, h)


def build_contact():
    _lb_reset()
    p = "contact.html"
    # General questions — the ones that come before you have picked a service.
    # Service-specific questions stay on their own pages.
    general_faqs = [
        ("Do I need an appointment?",
         "You are welcome to bring it by during opening hours &mdash; Monday to Friday 9:00 to "
         "7:00, and Saturday 11:00 to 5:00. Calling ahead on "
         f"{PHONE_DISPLAY} is worth doing, because it means someone is free to come out and "
         "look at the job properly rather than between other work."),
        ("What does an estimate cost?",
         "Nothing. Estimates are free whether we work from your photos or look at the job in "
         "person, and they are itemised so you can see what each part of the job costs rather "
         "than one number at the bottom."),
        ("Can you quote from a photo?",
         "Yes. Email photos to contact@autotopsandtrim.com or text them to "
         f"{PHONE_DISPLAY} and we will come back to you with an estimate. On some jobs we will "
         "still want to see it in person before that number is final &mdash; collapsed pads, a "
         "bent bow, a rusted seat frame or foam that has gone hard do not always show up in a "
         "picture. We would rather find that at the shop than surprise you with it later. The "
         "estimate costs nothing either way."),
        ("What do you actually work on?",
         "Four trades under one roof: automotive, marine, aviation and motorcycle. Convertible "
         "tops, seats, headliners, door panels, carpet, sunroof shades, boat cushions and canvas, "
         "aircraft cabins and custom bike seats."),
        ("Do I have to bring the whole vehicle?",
         "Not always. If the job is a seat, a cushion or a motorcycle seat, take it off and bring "
         "it in on its own &mdash; that is how a lot of these start. Tops, headliners and interiors "
         "need the vehicle."),
        ("Do you take work from outside Monroe?",
         "Yes. We regularly see customers from Charlotte and across Union County, and people do "
         "travel for the work &mdash; one of our Google reviews is from a customer who drove an "
         "hour to get a sunroof fixed."),
    ]
    h = head("Contact | Auto Tops and Trim, Monroe NC | (980) 385-8101",
             "Contact Auto Tops and Trim at 4209 W Hwy 74, Monroe, NC. Call (980) 385-8101 or "
             "request a free upholstery estimate. Open Mon-Fri 9:00-7:00 and Saturday 11:00-5:00.",
             p, faqs=general_faqs)
    h += header(p)
    h += f"""<section class="band compact">
  <div class="wrap">
    <div class="contact-head">
      {shead("", "Monroe, NC &middot; Free project estimates")}
      <h1>Contact Auto Tops and Trim</h1>
      <p class="lead">Tell us about your project and we will send a clear recommendation
         with an estimate.</p>
    </div>
    <div class="contact-grid">
      <div class="formcard">
        <h2 class="formcard-h">Request your free estimate</h2>
        {quote_form()}
      </div>
      <div class="infocol">
        <ul class="infolist">
          <li><span class="k">Call the shop</span>
            <span class="v"><a class="big" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></span></li>
          <li><span class="k">Visit</span>
            <span class="v"><strong>4209 W Hwy 74</strong><br>Monroe, NC 28110<br>
              <a href="https://www.google.com/maps/search/?api=1&amp;query=4209+W+Hwy+74,+Monroe,+NC+28110"
                 target="_blank" rel="noopener">Get directions &rarr;</a></span></li>
          <li><span class="k">Hours</span>
            <span class="v"><table class="hours">
              <tr><th>Mon &ndash; Fri</th><td>9:00 AM &ndash; 7:00 PM</td></tr>
              <tr><th>Saturday</th><td>11:00 AM &ndash; 5:00 PM</td></tr>
              <tr><th>Sunday</th><td>Closed</td></tr>
            </table></span></li>
          <li><span class="k">Email</span>
            <span class="v"><a href="mailto:contact@autotopsandtrim.com">contact@autotopsandtrim.com</a></span></li>

        </ul>
        <div class="mapwrap">
          <iframe title="Map to Auto Tops and Trim, 4209 W Hwy 74, Monroe NC" loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            src="https://www.google.com/maps?q=4209+W+Hwy+74,+Monroe,+NC+28110&output=embed"></iframe>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="band tint">
  <div class="wrap narrow stack">
    <div class="stack">{shead("01", "Before you call")}
      <h2>The questions we get most</h2>
      <p class="lead">If yours is not here, ring the shop &mdash; we would rather talk it
         through than have you guess.</p></div>
    <div class="faq">{"".join(
        f"<details><summary>{q}</summary><div class='ans'>{a}</div></details>"
        for q, a in general_faqs)}</div>
  </div>
</section>
"""
    h += footer(lightbox_markup())
    pages.append(p)
    write(p, h)

# ============================================================== BLOG
#
# SCHEDULED PUBLISHING
# --------------------
# Every post carries `publish`, an ISO date. A post is built only when that date
# has arrived (UTC); until then it emits no page, stays off blog.html, and stays
# out of sitemap.xml — the sitemap is generated from `pages`, which only collects
# what was actually written, so the gate covers it for free.
#
# Nothing here publishes itself. The article text is written, reviewed and merged
# ahead of time with a future date; the daily job in .github/workflows/publish.yml
# only re-runs this build and pushes when the output actually changes. No robot
# ever authors content — it only flips the gate on work you already approved.
#
# `publish` is also the single source of truth for the displayed date and for
# schema.org datePublished. Do not add a separate `date` key: the two drifted
# apart before, and datePublished was hardcoded per category, so the May post
# claimed to be published in June.
#
# To schedule a post: add it with a future `publish` date and merge. That is all.
POSTS = [
    {
        "slug": "blog-convertible-top-cost-monroe-nc.html",
        "cat": "Convertible Tops", "publish": "2026-08-04", "read": "5 min read",
        "photo": "g01-camaro-ss-new-convertible-top",
        "title": "What does a convertible top replacement actually cost?",
        "seo_title": "Convertible Top Replacement Cost: What Drives the Price | Auto Tops and Trim",
        "meta": "What a convertible top replacement really costs — material, rear window type "
                "and the frame underneath. From an upholstery shop trimming tops since 1989.",
        "excerpt": "What drives the price of a new top — material, window type, and the "
                   "condition of the frame underneath — plus what a fair quote looks like.",
        "body": [
            "A convertible top replacement is really three jobs in one: the fabric or vinyl top "
            "itself, the rear window, and whatever needs repairing on the frame and pads "
            "underneath. Most quotes people bring us from elsewhere only cover the first one, "
            "which is why two estimates for the same car can look so far apart.",
            "<h2>The three things that set the price</h2>",
            "<h3>1. Material: vinyl, Stayfast or Twillfast</h3>",
            "Material is the first fork in the road, and it is worth knowing that almost every "
            "quality replacement top in the US is made by one company — the Haartz Corporation — "
            "in a handful of distinct grades. When a shop says \"vinyl or cloth\", these are "
            "usually the actual materials being discussed.",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Material</th><th>Construction</th><th>Typically OE on</th>"
            "<th>Trade-off</th></tr></thead>"
            "<tbody>"
            "<tr><th>Pinpoint vinyl</th>"
            "<td>Grained vinyl face, cloth backing</td>"
            "<td>Most American cars, 1950s&ndash;1990s</td>"
            "<td>Lowest cost, handles sun well, correct on a great many domestic classics</td></tr>"
            "<tr><th>Stayfast cloth</th>"
            "<td>Solution-dyed acrylic face, butyl rubber inner layer, cotton backing "
            "(about 1.0&nbsp;mm)</td>"
            "<td>Long-running OE specification across many makes</td>"
            "<td>Richer look and a higher wear rating than vinyl; less durable and less "
            "sound-deadening than Twillfast</td></tr>"
            "<tr><th>Twillfast RPC</th>"
            "<td>Twill-weave acrylic face with a dobby backing</td>"
            "<td>Later and higher-end European applications</td>"
            "<td>The most durable and the quietest of the three, and the most expensive</td></tr>"
            "</tbody></table></div>",
            "The honest summary: vinyl is not a downgrade on a car that came with vinyl — it is "
            "the correct answer, and it holds up very well in the Carolina sun. Cloth is worth "
            "paying for when the car came with cloth, when you want the richer look, or when you "
            "care about how quiet the car is at highway speed. We keep samples of each in the "
            "shop so you can feel the difference before you commit to it.",
            "<h3>2. The rear window</h3>",
            "A top with a heated glass rear window is a different job from one with a plastic "
            "curtain, and the two are priced differently. On older cars the window is very often "
            "the reason the top failed in the first place — a plastic curtain clouds, cracks at "
            "the fold line, then lets water in. If you are replacing the top anyway, this is the "
            "moment to decide whether glass is worth it.",
            "<h3>3. The frame, pads and bows underneath</h3>",
            "This is the part that separates a real quote from a cheap one. If the pads are "
            "collapsed or the bows are bent, a new top fitted over them will sit badly no matter "
            "how good the fabric is — and it will wear through early at every high spot. We check "
            "the frame before quoting rather than after.",
            "<h2>What a photo can and cannot tell us</h2>",
            "Send photos and we will come back to you with an estimate — pictures are genuinely "
            "useful for narrowing down material, style and rough cost. What a photograph cannot "
            "show is a collapsed pad or a bent bow, or where an old top was stretched to cover a "
            "frame problem someone chose not to fix.",
            "So on a convertible top we will usually want to see the car before the number is "
            "final. Pricing a frame nobody has looked at means either guessing high to stay safe, "
            "or guessing low and revising once the car is apart, and neither is fair to you. The "
            "estimate is free and itemised either way, so you can see which of the three jobs "
            "above each line belongs to.",
            "<h2>Signs your top needs replacing rather than repairing</h2>",
            "<ul class=\"ticks\">"
            "<li>The rear window has clouded, yellowed or split along a fold</li>"
            "<li>Seams are opening, or stitching has rotted through</li>"
            "<li>The fabric has gone chalky and stiff rather than supple</li>"
            "<li>Water is getting in even though the top latches properly</li>"
            "<li>The top no longer sits tight when raised, or bunches when lowered</li>"
            "</ul>",
            "Not all of these mean a full replacement. A seam can often be restitched and a window "
            "can sometimes be replaced on its own. Bring it by and we will tell you honestly which "
            "one you are looking at.",
            "<h2>Get an itemised estimate</h2>",
            "We have been replacing convertible tops in Monroe since 1989, on everything from "
            "daily drivers to show cars. Bring the car to the shop and we will walk it with you, "
            "show you vinyl and canvas samples side by side, and give you an itemised estimate at "
            "no cost. See more on our "
            "<a href=\"convertible-tops.html\">convertible top replacement</a> page, or look "
            "through recent work in the <a href=\"gallery.html\">gallery</a>.",
        ],
    },
    {
        "slug": "blog-marine-vinyl-vs-leather.html",
        "cat": "Marine", "publish": "2026-08-04", "read": "4 min read",
        "photo": "marine-seating-and-interior-upholstery",
        "title": "Marine vinyl vs. automotive leather: what belongs on a boat",
        "seo_title": "Marine Vinyl vs Leather: What Belongs on a Boat | Auto Tops and Trim",
        "meta": "Why marine grade vinyl outlasts leather on the water — UV, mildew and "
                "quick-dry foam explained by an upholstery shop doing boat work since 1989.",
        "excerpt": "Why the material that looks best in your car is the wrong choice on the water, "
                   "and what we specify for boat cushions and canvas instead.",
        "body": [
            "Leather is a wonderful material in a car interior. On a boat it is a maintenance "
            "problem: standing water, UV and salt will dry it out and crack it inside a season or "
            "two. This is the single most common mistake we see on boats that come in for "
            "reupholstery — a beautiful automotive material specified for an environment that "
            "will destroy it.",
            "<h2>What makes a vinyl marine grade</h2>",
            "Marine vinyl is not simply thicker upholstery vinyl. The differences that matter are "
            "in what has been engineered into it:",
            "<ul class=\"ticks\">"
            "<li><strong>UV stabilisation</strong> — so it does not go chalky and stiff in a "
            "season of full sun</li>"
            "<li><strong>Mildew resistance</strong> — the backing and topcoat are treated, "
            "because marine upholstery spends its life damp</li>"
            "<li><strong>Cold-crack resistance</strong> — it stays flexible through winter "
            "storage instead of splitting at the folds</li>"
            "<li><strong>Rot-proof thread</strong> — a perfect cover stitched with the wrong "
            "thread fails at the seams first</li>"
            "</ul>",
            "That last point gets overlooked constantly. Thread is cheap and invisible, so it is "
            "the easiest place for a shop to save money — and it is the first thing to let go.",
            "<h2>The foam matters as much as the cover</h2>",
            "If your boat cushions stay damp, the cover is usually not the culprit. Standard "
            "upholstery foam is a sponge: it holds water against the cushion and against the "
            "deck, which is how you end up with mildew and a smell that never fully leaves.",
            "Quick-dry reticulated foam has an open cell structure that lets water pass straight "
            "through instead of trapping it. It is more expensive per cushion and it is almost "
            "always the right call — it is the difference between a cushion that dries in an "
            "afternoon and one that never really does.",
            "<h2>Canvas follows the same logic</h2>",
            "Solution-dyed acrylic holds colour in full sun far longer than cheaper coated "
            "fabrics, because the colour goes through the fibre rather than sitting on top of it. "
            "The difference does not show in year one. It shows in year three, when the coated "
            "fabric has gone chalky and faded and the acrylic still looks like itself.",
            "There are four families of marine top fabric in common use, and they genuinely suit "
            "different jobs:",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Fabric</th><th>Type</th><th>Strengths</th><th>Watch for</th></tr>"
            "</thead><tbody>"
            "<tr><th>Sunbrella</th><td>Solution-dyed acrylic</td>"
            "<td>Best-in-class UV and colourfastness, breathable, carries a 10-year warranty "
            "against fading</td>"
            "<td>Water-resistant rather than fully waterproof &mdash; it relies on good design "
            "and upkeep</td></tr>"
            "<tr><th>Top Gun</th><td>Coated polyester</td>"
            "<td>Excellent abrasion resistance and strength, lower cost</td>"
            "<td>Shorter service life in punishing sun; coating quality varies a lot by "
            "grade</td></tr>"
            "<tr><th>Stamoid</th><td>Vinyl-coated</td>"
            "<td>Maximum waterproofing of the four</td>"
            "<td>Does not breathe, so trapped moisture underneath becomes the problem "
            "instead</td></tr>"
            "<tr><th>Seamark</th><td>Sunbrella with a vinyl backing</td>"
            "<td>Fully waterproof while matching Sunbrella colours &mdash; a common OE bimini "
            "and camper-top choice</td>"
            "<td>Costs more than either parent material</td></tr>"
            "</tbody></table></div>",
            "Notice the trade running through that table: <strong>waterproof and breathable pull "
            "against each other.</strong> Anyone who tells you one fabric wins on both is selling "
            "you something. The right choice depends on whether the boat lives on a lift, on a "
            "trailer, or in a slip.",
            "<h2>Recover or replace?</h2>",
            "Not everything needs replacing. A single split seam can often be restitched, and a "
            "cover in good condition over dead foam only needs the foam changed. Chalking on "
            "canvas, though, usually means a cheaper coated fabric has reached the end of its "
            "life, and no amount of cleaning brings it back.",
            "Bring one cushion or one piece of canvas by the shop — you do not need to bring the "
            "whole boat — and we will tell you honestly which one you are looking at. More on our "
            "<a href=\"marine-upholstery.html\">marine upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-period-correct-or-upgraded-classic-interior.html",
        "cat": "Restoration", "publish": "2026-08-04", "read": "5 min read",
        "photo": "classic-interior-finished",
        "title": "Period-correct or upgraded? Choosing an interior for a classic",
        "seo_title": "Classic Car Interior Restoration: Period-Correct or Upgraded? | Auto Tops and Trim",
        "meta": "How to choose between an original and an upgraded classic car interior "
                "restoration — originality, comfort and resale, from a shop trimming since 1989.",
        "excerpt": "Restoring a classic interior means deciding how faithful to be. Here is how we "
                   "think about originality, comfort, and resale.",
        "body": [
            "Every classic car interior restoration starts with one question, and it is not about "
            "colour or material. It is this: <strong>is this car going to shows, or is it going "
            "to be driven?</strong> The honest answer changes the entire material list, and it "
            "changes what the job costs.",
            "<h2>Building for originality</h2>",
            "For a show car we chase originality — correct grain patterns, correct stitch "
            "spacing, correct carpet weave, correct materials even where a modern equivalent "
            "would be easier to work with. Judges notice all of it, and so do serious buyers.",
            "The constraint is that some original materials are simply no longer made. Where that "
            "happens we will show you the closest available option and tell you plainly where it "
            "differs, rather than quietly substituting something and hoping nobody looks.",
            "<h2>Building for driving</h2>",
            "For a car that gets used, we keep the period look and quietly improve everything you "
            "cannot see:",
            "<ul class=\"ticks\">"
            "<li>Modern foam densities, so the seat still supports you after an hour</li>"
            "<li>Sound deadening under the carpet — the single biggest change to how an old car "
            "feels to drive</li>"
            "<li>Seat frames repaired properly rather than shimmed to hide a crack</li>"
            "<li>Better thread and stitch density at the wear points</li>"
            "</ul>",
            "From two feet away it reads as original. From the driver's seat it is a much better "
            "car to spend time in.",
            "<h2>Component by component: where to be faithful, where to improve</h2>",
            "The decision is rarely all-or-nothing. Most good interiors are original where it "
            "shows and modern where it does not:",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Component</th><th>Period-correct</th><th>Upgraded</th>"
            "<th>Our usual advice</th></tr></thead><tbody>"
            "<tr><th>Seat covers</th><td>Correct grain, stitch spacing and pattern</td>"
            "<td>Modern hide or vinyl, custom stitch</td>"
            "<td>Stay correct &mdash; this is the part everyone actually looks at</td></tr>"
            "<tr><th>Foam</th><td>Original densities, which were often poor when new</td>"
            "<td>Modern multi-density foam</td>"
            "<td>Upgrade almost always. Invisible, and it is the difference between a car you "
            "enjoy for an hour and one you do not</td></tr>"
            "<tr><th>Carpet</th><td>Correct weave and binding</td>"
            "<td>Modern loop or cut pile</td>"
            "<td>Stay correct on a show car; either is defensible on a driver</td></tr>"
            "<tr><th>Sound deadening</th><td>Little or none from the factory</td>"
            "<td>Full modern barrier under the carpet</td>"
            "<td>Upgrade. Nobody has ever regretted a quieter old car</td></tr>"
            "<tr><th>Seat frames</th><td>Repair to original structure</td>"
            "<td>Reinforced or rebuilt</td>"
            "<td>Repair properly either way &mdash; never shim a cracked frame</td></tr>"
            "</tbody></table></div>",
            "<h2>What this does to resale</h2>",
            "There is a real trade-off here and it is worth being clear about. A documented, "
            "period-correct interior protects value on a car whose buyers care about matching "
            "numbers and correct trim. On a driver, a tasteful upgraded interior usually widens "
            "the pool of people who want it, because most buyers want to enjoy the car rather "
            "than preserve it.",
            "Neither is the right answer universally. It depends on the car, and on what you "
            "intend to do with it.",
            "<h2>You do not have to choose blind</h2>",
            "We keep samples in the shop and can show you what period-correct and upgraded "
            "actually look and feel like side by side, on the bench, before anything is cut. Most "
            "people change their mind at least once at that table — which is exactly why we do it "
            "that way round.",
            "Bring the car to Monroe and we will build the spec with you before any cutting "
            "starts. See our <a href=\"auto-upholstery.html\">automotive upholstery</a> page for "
            "the full range of interior work, or browse finished projects in the "
            "<a href=\"gallery.html\">gallery</a>.",
        ],
    },

    # ---- BATCH 1: question-led cluster, all KD 0-2. See SEO_KEYWORDS.md ------
    # No prices anywhere in these. Every material claim is from a manufacturer or
    # supplier source, not from memory. Where a number would help and we do not
    # have one, the article says what drives the number instead of inventing it.
    {
        "slug": "blog-how-to-fix-a-sagging-headliner.html",
        "cat": "Headliners", "publish": "2026-08-06", "read": "6 min read",
        "photo": "g13-sound-deadening-before-carpet",
        "title": "How to fix a sagging headliner (and when the quick fix will not hold)",
        "seo_title": "How to Fix a Sagging Car Headliner — Honest Guide | Auto Tops and Trim",
        "meta": "Why headliners sag, which DIY fixes actually work, and how to tell when the "
                "foam has gone and the panel needs recovering. From a trim shop since 1989.",
        "excerpt": "Pins, adhesive and steam all have their place — and all of them fail on a "
                   "headliner whose foam has broken down. Here is how to tell which one you have.",
        "body": [
            "A sagging headliner is one of the most common jobs that walks into an upholstery "
            "shop, and it is also one of the most commonly mis-diagnosed. Almost everyone assumes "
            "the glue has failed. Usually it has not.",
            "<h2>What is actually happening above your head</h2>",
            "A headliner is not one layer. It is a rigid backing board, a thin layer of foam "
            "bonded to it, and the fabric bonded to the foam. The fabric is not glued to the "
            "board at all — it is glued to the foam.",
            "That foam is polyurethane, and heat and time break it down. Once it crumbles, "
            "nothing is holding the fabric up, because the thing it was attached to has turned to "
            "orange-brown dust. If you press a sagging headliner and your fingers come away with "
            "a fine powder, that is the foam, and it is the whole story.",
            "This is why headliners fail in the middle of the roof first, and why they fail on "
            "cars that live outside in the Carolina sun far sooner than on garaged ones.",
            "<h2>The DIY fixes, honestly rated</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Fix</th><th>What it does</th><th>Honest verdict</th></tr></thead>"
            "<tbody>"
            "<tr><th>Twist pins</th>"
            "<td>Pins the fabric back to the board mechanically</td>"
            "<td>Genuinely works as a holding measure, and it is reversible. It looks like what "
            "it is, and it does not stop the foam breaking down further.</td></tr>"
            "<tr><th>Spray adhesive through the fabric</th>"
            "<td>Attempts to re-bond fabric to board in place</td>"
            "<td>Almost always disappointing. There is still dead foam between the two surfaces, "
            "so you are gluing fabric to powder. It also stains the face of the fabric.</td></tr>"
            "<tr><th>Steam and roller</th>"
            "<td>Softens and re-lays the fabric</td>"
            "<td>Can buy time on a liner that is only just starting to lift at an edge. Useless "
            "once the foam is gone.</td></tr>"
            "<tr><th>Removing the board and recovering it</th>"
            "<td>Old fabric and all remaining foam scraped off, new foam-backed material bonded "
            "to the bare board</td>"
            "<td>The only fix that actually lasts, because it replaces the layer that failed.</td>"
            "</tr></tbody></table></div>",
            "<h2>The test that tells you which one you need</h2>",
            "Push up gently on the sagging area with a flat palm.",
            "<ul class=\"ticks\">"
            "<li>If it springs back and stays for a while, the bond has released at an edge and "
            "the foam is probably still intact. A careful re-lay may hold.</li>"
            "<li>If it feels soft and grainy, or your hand comes away dusty, the foam has "
            "disintegrated. No adhesive will fix that — there is nothing left to bond to.</li>"
            "<li>If the fabric has separated across most of the roof, the decision is already "
            "made for you.</li>"
            "</ul>",
            "<h2>Why we recover the board rather than glue the fabric back</h2>",
            "When we recover a headliner, the board comes out of the car, every trace of the old "
            "foam is scraped back to clean board, and new foam-backed headliner material is "
            "bonded to it. That is more work than spraying adhesive through the old fabric, and "
            "it is the reason the repair does not come back in a year.",
            "It is also the moment to deal with anything else the board has been hiding — sunroof "
            "shade tracks, wiring for interior lights, and trim clips that have gone brittle.",
            "<h2>Bring it by</h2>",
            "We have been recovering headliners in Monroe since 1989, on daily drivers and show "
            "cars alike. Bring the vehicle to the shop and we will tell you honestly whether you "
            "are looking at a re-lay or a recover, and quote it in person at no charge. More on "
            "our <a href=\"auto-upholstery.html\">automotive upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-headliner-replacement-cost.html",
        "cat": "Headliners", "publish": "2026-08-06", "read": "5 min read",
        "photo": "g19-mercedes-gla-interior-work",
        "title": "What actually drives the cost of a headliner replacement",
        "seo_title": "Headliner Replacement Cost: What Changes the Price | Auto Tops and Trim",
        "meta": "The five things that move the price of a headliner replacement — roof size, "
                "sunroof, trim removal, material and hidden damage. Free estimates.",
        "excerpt": "Two quotes for the same car can look very different. Here are the five "
                   "variables that explain the gap, and the ones a cheap quote usually leaves out.",
        "body": [
            "Headliner quotes vary more than most people expect, and the difference is rarely "
            "the fabric. It is almost always about how much has to come out of the car to get "
            "the board out, and what is found once it is out.",
            "<h2>1. How big the roof is, and what shape it is</h2>",
            "A two-door coupe headliner is a smaller, simpler panel than a long-wheelbase SUV "
            "with a third row. Curves matter too — a heavily contoured board takes more time to "
            "get material to lie down on without wrinkles at the corners.",
            "<h2>2. Whether there is a sunroof</h2>",
            "A sunroof turns one panel into a panel with a large opening, a surround, and often a "
            "sliding shade running in tracks. All of it has to come apart and go back together "
            "correctly, and the shade itself is frequently in the same condition as the headliner "
            "for the same reason. We cover that specific repair on our "
            "<a href=\"sunroof-shade-repair.html\">sunroof shade repair</a> page.",
            "<h2>3. How much trim has to come out</h2>",
            "The board cannot leave the car until the pillars, grab handles, visors, dome lights "
            "and seals are out of the way. On some vehicles that is quick. On others the seats "
            "come out first. This is usually the single biggest driver of labour, and it is "
            "entirely determined by the vehicle rather than by anything you choose.",
            "<h2>4. The material</h2>",
            "Standard replacement headliner material is a knit or suede-look fabric already "
            "bonded to a thin foam backing — the foam is what the adhesive grips. Upgrades exist, "
            "including suede-look and perforated materials, and they cost more per yard. On most "
            "jobs this is a smaller part of the total than people assume.",
            "<h2>5. What is found once the board is out</h2>",
            "<ul class=\"ticks\">"
            "<li>Boards that have absorbed water and gone soft, usually from a leaking sunroof "
            "drain or a windscreen seal</li>"
            "<li>Brittle trim clips that break on removal and have to be replaced</li>"
            "<li>Sunroof shades in the same failed state as the liner</li>"
            "<li>Wiring or dome-light housings that were previously bodged</li>"
            "</ul>",
            "A water-damaged board is the one that changes a quote materially, because a soft "
            "board will not hold new material and has to be repaired or replaced.",
            "<h2>What a photo can and cannot tell us</h2>",
            "A photo of a sagging headliner tells us the fabric has let go, and that is usually "
            "enough for us to come back with an estimate. What it cannot tell us is whether the "
            "board is sound, whether there is a sunroof shade behind it, or how much trim has to "
            "come out on your particular vehicle — and those are the three things that set the "
            "price.",
            "So we may ask to see the vehicle in Monroe before confirming the number. Either way "
            "you get an itemised estimate at no cost, with each of the five items above priced "
            "separately so you can see what you are paying for.",
        ],
    },
    {
        "slug": "blog-how-to-clean-boat-seats.html",
        "cat": "Marine", "publish": "2026-08-06", "read": "5 min read",
        "photo": "boat-upholstery-projects-at-the-shop",
        "title": "How to clean boat seats without wrecking them",
        "seo_title": "How to Clean Boat Seats (Vinyl) the Right Way | Auto Tops and Trim",
        "meta": "How to clean vinyl boat seats safely — what to use, what quietly destroys the "
                "seams and topcoat, and how to tell when a cushion is past cleaning.",
        "excerpt": "Most damaged boat seats we see were not worn out by the sun. They were "
                   "cleaned to death. Here is the method that works and the shortcuts that cost you.",
        "body": [
            "Marine vinyl is built to survive standing water, UV and salt. What it does not "
            "survive is aggressive cleaning, and a surprising share of the ruined cushions that "
            "come through the shop were damaged by the owner trying to look after them.",
            "<h2>Start with the gentlest thing that works</h2>",
            "<ul class=\"ticks\">"
            "<li>Warm water and a mild soap, applied with a soft brush or a microfibre cloth</li>"
            "<li>Work in sections and rinse before anything dries on the surface</li>"
            "<li>Get into the seams and welts, where dirt and moisture actually collect</li>"
            "<li>Dry with a towel rather than leaving it to sit wet in the sun</li>"
            "</ul>",
            "That handles the large majority of ordinary grime. Escalate only if it does not, and "
            "escalate one step at a time.",
            "<h2>What quietly destroys marine vinyl</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Avoid</th><th>Why</th></tr></thead><tbody>"
            "<tr><th>Bleach, undiluted or repeated</th>"
            "<td>Attacks the stitching thread and can strip the topcoat that gives the vinyl its "
            "UV resistance. The cover often outlives the seams — until bleach reverses that.</td>"
            "</tr>"
            "<tr><th>Stiff brushes and abrasive pads</th>"
            "<td>Scratch the topcoat. Once the surface is microscopically rough it holds dirt "
            "harder, so cleaning gets more aggressive each time — a loop that ends in "
            "replacement.</td></tr>"
            "<tr><th>Solvents, acetone, petrol</th>"
            "<td>Dissolve plasticisers. The vinyl looks clean, then goes hard and cracks at the "
            "folds a season later.</td></tr>"
            "<tr><th>Pressure washers</th>"
            "<td>Drive water straight through the seams into the foam, which is exactly the "
            "problem you were trying to avoid.</td></tr>"
            "</tbody></table></div>",
            "<h2>If the seat stays damp, the cover is not the problem</h2>",
            "A cushion that never really dries usually has standard upholstery foam inside it. "
            "That foam behaves like a sponge — it holds water against the cover and against the "
            "deck, and no amount of surface cleaning changes that.",
            "Quick-dry reticulated foam has an open cell structure that lets water pass straight "
            "through instead of trapping it. If you are having a cushion rebuilt anyway, this is "
            "the upgrade worth paying for.",
            "<h2>When cleaning is no longer the answer</h2>",
            "<ul class=\"ticks\">"
            "<li>The vinyl has gone hard and chalky rather than staying supple</li>"
            "<li>Seams are opening, or stitching pulls through when you press on it</li>"
            "<li>Cracks have appeared along the fold lines</li>"
            "<li>Staining sits under the surface rather than on it</li>"
            "</ul>",
            "At that point you are looking at recovering rather than cleaning. Bring one cushion "
            "by the shop — you do not need to bring the boat — and we will tell you honestly "
            "which one it is. More on our <a href=\"marine-upholstery.html\">marine upholstery</a> "
            "page.",
        ],
    },
    {
        "slug": "blog-mildew-on-boat-seats.html",
        "cat": "Marine", "publish": "2026-08-07", "read": "5 min read",
        "photo": "marine-seating-and-interior-upholstery",
        "title": "Mildew and mould on boat seats: what comes off and what does not",
        "seo_title": "How to Get Mildew and Mould Off Vinyl Boat Seats | Auto Tops and Trim",
        "meta": "Black spots on vinyl boat seats explained — surface mildew versus mould rooted "
                "in the foam, what removes each, and why bleach often makes it worse.",
        "excerpt": "Black spots on white vinyl are two completely different problems with the "
                   "same appearance. One wipes off. The other is growing inside the cushion.",
        "body": [
            "Black speckling on marine vinyl is the single most common complaint we hear about "
            "boat seating, and the reason it frustrates people is that half the time it comes "
            "off easily and half the time nothing touches it. Those are two different problems.",
            "<h2>Surface mildew versus mould in the foam</h2>",
            "<strong>Surface mildew</strong> grows on the dirt and body oils sitting on top of "
            "the vinyl, not on the vinyl itself. Marine vinyl is treated to resist it, so what "
            "you are usually looking at is mildew on the film of grime above the topcoat. It "
            "responds to ordinary cleaning.",
            "<strong>Mould rooted in the foam</strong> is a different matter. Once water has gone "
            "through a seam and the foam inside has stayed wet, growth happens inside the "
            "cushion and pushes staining outward. You are seeing the shadow of something you "
            "cannot reach.",
            "<h2>Which one do you have?</h2>",
            "<ul class=\"ticks\">"
            "<li>Wipe a small patch with warm soapy water. If the spots lift or fade noticeably, "
            "it is on the surface.</li>"
            "<li>Press the cushion. If it feels damp, or you smell it before you see it, the foam "
            "is holding water.</li>"
            "<li>Look at where the staining is worst. Along seams and at the base points to water "
            "getting in rather than dirt sitting on top.</li>"
            "</ul>",
            "<h2>Why reaching for bleach usually backfires</h2>",
            "Bleach does kill surface growth, which is why it feels like it works. The problems "
            "come afterwards: it attacks the stitching thread holding the cushion together, and "
            "repeated use strips the topcoat that gives marine vinyl its UV resistance.",
            "The common result is a cushion that looks better for one season and then fails at "
            "the seams — the covering outlived the thread. If mould is inside the foam, bleach "
            "on the outside never reaches it anyway.",
            "<h2>What actually fixes foam-rooted mould</h2>",
            "The cushion has to be opened. The foam is replaced — ideally with quick-dry "
            "reticulated foam that lets water pass through rather than holding it — and the cover "
            "is either cleaned properly off the cushion or replaced if the staining has gone into "
            "the material.",
            "It is worth finding out how the water got in at the same time, because a new cushion "
            "under a failed seam or a leaking canvas will do exactly the same thing again.",
            "<h2>Prevention, briefly</h2>",
            "<ul class=\"ticks\">"
            "<li>Dry cushions with a towel rather than leaving them to evaporate</li>"
            "<li>Let air move under and around them where you can</li>"
            "<li>Deal with a split seam immediately — it is the doorway</li>"
            "<li>Clean regularly and gently rather than occasionally and harshly</li>"
            "</ul>",
            "Bring one cushion by the shop in Monroe and we will tell you which of the two "
            "problems you have before you spend money on either. See our "
            "<a href=\"marine-upholstery.html\">marine upholstery</a> page for the full range of "
            "boat work.",
        ],
    },
    {
        "slug": "blog-how-to-clean-a-convertible-top.html",
        "cat": "Convertible Tops", "publish": "2026-08-07", "read": "5 min read",
        "photo": "automotive-ford-galaxie-top-after",
        "title": "How to clean a convertible top without shortening its life",
        "seo_title": "How to Clean a Convertible Top (Vinyl and Canvas) | Auto Tops and Trim",
        "meta": "Cleaning a convertible top safely — why vinyl and canvas need different "
                "treatment, what ruins the rear window, and when to re-proof the fabric.",
        "excerpt": "Vinyl and cloth tops are different materials with different failure modes, "
                   "and the cleaning that suits one will shorten the life of the other.",
        "body": [
            "The single most useful thing to know before cleaning a convertible top is which kind "
            "you have, because vinyl and cloth are not the same material and do not want the same "
            "treatment.",
            "<h2>Work out what your top is made of</h2>",
            "<strong>Vinyl</strong> has a smooth or lightly grained plastic surface — the "
            "pinpoint grain was original on most American cars from the 1950s through the 1990s. "
            "It is a sealed surface, so dirt sits on top of it.",
            "<strong>Cloth</strong> tops are woven. Haartz Stayfast, for example, is a "
            "solution-dyed acrylic face over a butyl rubber inner layer with a cotton backing, "
            "and it was specified as original equipment for decades. Because the face is woven, "
            "it holds dirt in the weave rather than on the surface, and it depends on a factory "
            "water-repellent finish that cleaning gradually removes.",
            "That last point is the one people miss: <strong>cleaning a cloth top removes its "
            "proofing, so it needs re-proofing afterwards.</strong> A vinyl top does not.",
            "<h2>The method</h2>",
            "<ul class=\"ticks\">"
            "<li>Rinse loose grit off first. Grinding sand into either material with a brush does "
            "more damage than the dirt ever would.</li>"
            "<li>Use a dedicated convertible top cleaner appropriate to your material, or a mild "
            "soap. Work in shade, never in direct sun on a hot panel.</li>"
            "<li>Use a soft brush on cloth, working with the weave. Use a cloth or sponge on "
            "vinyl.</li>"
            "<li>Rinse thoroughly. Residue left in a woven top attracts dirt and holds moisture "
            "against the fabric.</li>"
            "<li>Let it dry fully raised, then re-proof cloth with a fabric protectant.</li>"
            "</ul>",
            "<h2>Things that quietly cause damage</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Avoid</th><th>Why</th></tr></thead><tbody>"
            "<tr><th>Automatic car washes</th><td>Brushes catch seams and the rear-window "
            "surround, and high-pressure jets drive water past seals</td></tr>"
            "<tr><th>Bleach or strong household cleaners</th><td>Attack stitching thread and "
            "strip the water-repellent finish from cloth</td></tr>"
            "<tr><th>Glass cleaner on a plastic rear window</th><td>Ammonia clouds and "
            "yellows plastic curtains. Plastic is not glass and wants a plastic-specific "
            "polish</td></tr>"
            "<tr><th>Folding a damp top away</th><td>Creates mildew and sets creases along the "
            "fold lines, which is where tops split first</td></tr>"
            "<tr><th>Cleaning in direct sun</th><td>Product dries before it can be rinsed, "
            "leaving residue bonded into the weave</td></tr>"
            "</tbody></table></div>",
            "<h2>The rear window deserves its own attention</h2>",
            "On older cars the rear window is frequently the reason the top failed in the first "
            "place. A plastic curtain clouds, then cracks at the fold line, then lets water in. "
            "Never fold a top with a plastic window in cold weather if you can avoid it, and "
            "never clean it with anything containing ammonia.",
            "<h2>When cleaning has run out of road</h2>",
            "If seams are opening, the fabric has gone stiff and chalky rather than supple, or "
            "water is getting in even though the top latches properly, you are past maintenance. "
            "Bring the car to the shop in Monroe and we will tell you honestly whether it needs a "
            "repair, a new window, or a new top. See our "
            "<a href=\"convertible-tops.html\">convertible top replacement</a> page.",
        ],
    },
    {
        "slug": "blog-torn-car-seat-repair.html",
        "cat": "Seats", "publish": "2026-08-07", "read": "6 min read",
        "photo": "seat-rebuild-after",
        "title": "How to repair a torn car seat, and when a repair is the wrong answer",
        "seo_title": "How to Repair a Torn Car Seat — Repair or Recover? | Auto Tops and Trim",
        "meta": "Whether a torn car seat can be repaired or needs recovering — how the material, "
                "the location of the tear and the foam underneath decide it.",
        "excerpt": "A repair kit can be the right call or a waste of an afternoon. It depends on "
                   "three things, and the tear itself is only one of them.",
        "body": [
            "Whether a torn seat can be repaired depends on three things: what it is made of, "
            "where the damage is, and what condition the foam underneath is in. Most advice "
            "online only addresses the first.",
            "<h2>1. The material decides your options</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Material</th><th>Repairable?</th><th>Reality</th></tr></thead>"
            "<tbody>"
            "<tr><th>Cloth</th><td>Sometimes</td>"
            "<td>Small tears in a flat area can be backed and closed. Colour and weave matching "
            "on a faded seat is the hard part, and it is usually visible.</td></tr>"
            "<tr><th>Vinyl</th><td>Often</td>"
            "<td>Takes filler-and-grain repairs better than most materials. Works well on burns "
            "and small punctures, less well on long seam splits.</td></tr>"
            "<tr><th>Leather</th><td>Depends</td>"
            "<td>A clean cut can be repaired convincingly. Cracked, dried leather cannot — the "
            "surface around any repair is already failing.</td></tr>"
            "<tr><th>Seam split</th><td>Usually restitch</td>"
            "<td>This is not a tear in the material at all. The thread failed. Restitching is "
            "the correct fix and is generally the cheapest thing a trim shop does.</td></tr>"
            "</tbody></table></div>",
            "<h2>2. Where the tear is matters more than its size</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>On a flat panel</strong> — the best case. There is material around it to "
            "work with and little flex.</li>"
            "<li><strong>On a bolster or edge</strong> — the hardest. This is where you slide in "
            "and out, so the repair is loaded every time the seat is used.</li>"
            "<li><strong>On a seam</strong> — usually good news. Restitching is a proper "
            "structural fix rather than a cosmetic one.</li>"
            "<li><strong>Over a broken frame or collapsed foam</strong> — the material did not "
            "fail on its own. Fixing the cover alone guarantees a repeat.</li>"
            "</ul>",
            "<h2>3. The foam underneath is the part nobody checks</h2>",
            "Press either side of the tear. If one side sinks noticeably further, the foam has "
            "collapsed, and the cover tore because it was being stretched over a shape that no "
            "longer supports it.",
            "Repair the cover and leave the foam, and the same seat tears again in the same place "
            "— usually within a season. Foam replacement is not glamorous, but on a worn driver's "
            "seat it is frequently the actual repair.",
            "<h2>What a DIY kit is genuinely good for</h2>",
            "A vinyl or leather repair kit is a reasonable answer to a cigarette burn, a small "
            "puncture, or a clean cut on a flat panel of a car you are not precious about. It is "
            "not a good answer to a split bolster, a long tear, or anything on a vehicle whose "
            "interior you care about — the repair will be visible and it will move.",
            "<h2>What we do instead</h2>",
            "In the shop the seat comes apart. We look at the frame, the foam and the cover as "
            "three separate questions, restitch what can be restitched, replace foam that has "
            "collapsed, and recover panels rather than patch them where the finish matters. On a "
            "classic we chase correct grain, stitch spacing and thread.",
            "You do not need a full interior to come see us — plenty of our work is one torn "
            "driver's seat. Bring the vehicle, or just the seat, to the shop in Monroe for a free "
            "in-person estimate. More on our <a href=\"auto-upholstery.html\">automotive "
            "upholstery</a> page.",
        ],
    },

    # ---- BATCH 2 ------------------------------------------------------------
    {
        "slug": "blog-convertible-top-materials-compared.html",
        "cat": "Convertible Tops", "publish": "2026-08-08", "read": "7 min read",
        "photo": "automotive-interior-restoration-detail",
        "title": "Convertible top materials compared: vinyl, Stayfast and Twillfast",
        "seo_title": "Convertible Top Materials Compared: Vinyl vs Stayfast vs Twillfast",
        "meta": "Pinpoint vinyl, Stayfast cloth and Twillfast RPC compared on construction, "
                "durability, sound and correctness — and which belongs on your car.",
        "excerpt": "Nearly every quality replacement top in the US comes from one manufacturer "
                   "in a handful of grades. Here is what actually separates them.",
        "body": [
            "When a shop asks whether you want \"vinyl or cloth\", the conversation is usually "
            "about three specific materials. Almost every quality replacement top sold in the "
            "United States is made by the Haartz Corporation, and the grade you choose changes "
            "the look, the noise level, the lifespan and the price.",
            "<h2>The three grades</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Material</th><th>Construction</th><th>Typically OE on</th>"
            "<th>Relative cost</th></tr></thead><tbody>"
            "<tr><th>Pinpoint vinyl</th><td>Grained vinyl face over a cloth backing</td>"
            "<td>Most American cars, 1950s&ndash;1990s</td><td>Lowest</td></tr>"
            "<tr><th>Stayfast cloth</th>"
            "<td>Solution-dyed acrylic square-weave face, butyl rubber inner layer, cotton "
            "backing. Roughly 1.0&nbsp;mm thick, 60&nbsp;inch width.</td>"
            "<td>A long-running OE specification across many makes</td><td>Middle</td></tr>"
            "<tr><th>Twillfast RPC</th>"
            "<td>Twill-weave acrylic face with a dobby backing</td>"
            "<td>Later and higher-end applications, commonly European</td><td>Highest</td></tr>"
            "</tbody></table></div>",
            "<h2>Where each one genuinely wins</h2>",
            "<h3>Pinpoint vinyl</h3>",
            "It is not the budget option so much as the <em>correct</em> option on a great many "
            "domestic classics — the distinctive pinpoint grain is what left the factory. It "
            "handles sun well, cleans easily because the surface is sealed, and costs the least.",
            "Where it loses: it is the noisiest of the three at highway speed, and it looks like "
            "vinyl. On a car that originally wore cloth, it reads as wrong to anyone who knows.",
            "<h3>Stayfast cloth</h3>",
            "The middle ground, and the one most people upgrade to. The acrylic face is "
            "solution-dyed, meaning colour runs through the fibre rather than sitting on it, so "
            "it holds its appearance far better than a coated fabric. The butyl rubber inner "
            "layer is what makes it waterproof despite being woven.",
            "It carries a higher wear rating than vinyl and looks considerably richer. It is "
            "less durable and less sound-deadening than Twillfast, and it lacks the dobby "
            "backing found on that grade.",
            "<h3>Twillfast RPC</h3>",
            "The most durable and the quietest, with a twill weave that reads as a more expensive "
            "material because it is one. If the car came with it, replacing it with anything else "
            "is a downgrade you will hear as well as see.",
            "<h2>How we would choose</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Original American classic</strong> — pinpoint vinyl, if that is what it "
            "wore. Correctness beats upgrading on a car being judged.</li>"
            "<li><strong>Daily-driven convertible</strong> — Stayfast. The best balance of "
            "appearance, longevity and cost.</li>"
            "<li><strong>The car came with Twillfast</strong> — stay with Twillfast.</li>"
            "<li><strong>Highway miles, top up</strong> — pay for the cloth. The noise difference "
            "is real and you notice it every drive.</li>"
            "</ul>",
            "<h2>The part the material does not fix</h2>",
            "None of this matters if the frame underneath is wrong. A top of any grade fitted "
            "over collapsed pads or bent bows will sit badly and wear through early at every high "
            "spot. We check that before quoting, not after.",
            "We keep samples of each in the shop. Bring the car to Monroe, feel the difference "
            "between them in your hand, and get an itemised estimate at no cost. More on our "
            "<a href=\"convertible-tops.html\">convertible top replacement</a> page.",
        ],
    },
    {
        "slug": "blog-convertible-top-rear-window.html",
        "cat": "Convertible Tops", "publish": "2026-08-08", "read": "5 min read",
        "photo": "g05-burgundy-cloth-top-rear-window",
        "title": "Glass or plastic rear window? The choice that decides when your top fails",
        "seo_title": "Convertible Top Rear Window: Glass vs Plastic | Auto Tops and Trim",
        "meta": "Heated glass versus plastic curtain rear windows — cost, lifespan, visibility "
                "and why the window is usually what kills a convertible top first.",
        "excerpt": "On most older convertibles the fabric outlives the window. Here is how the "
                   "two options differ and when replacing just the window is the right call.",
        "body": [
            "People think of a convertible top as fabric. In practice the rear window is very "
            "often the part that fails first, and on a lot of cars it is the reason the whole top "
            "gets replaced.",
            "<h2>The two options</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th></th><th>Plastic curtain</th><th>Heated glass</th></tr></thead>"
            "<tbody>"
            "<tr><th>Clarity over time</th><td>Clouds and yellows with UV exposure</td>"
            "<td>Stays clear indefinitely</td></tr>"
            "<tr><th>Folding</th><td>Creases, and cracks along the fold line &mdash; the usual "
            "failure</td><td>Does not fold; the top is designed around it</td></tr>"
            "<tr><th>Cold weather</th><td>Becomes brittle; folding it cold is how most of them "
            "split</td><td>Unaffected</td></tr>"
            "<tr><th>Defrosting</th><td>None</td><td>Heated element clears it</td></tr>"
            "<tr><th>Weight and stack height</th><td>Lighter, folds flatter</td>"
            "<td>Heavier, needs the right frame and well</td></tr>"
            "<tr><th>Cost</th><td>Lower</td><td>Higher</td></tr>"
            "</tbody></table></div>",
            "<h2>Why the window usually goes first</h2>",
            "A plastic curtain is a sheet of flexible vinyl stitched into the fabric. Every time "
            "the top drops, it folds. Every fold works the same crease. Add Carolina summers "
            "clouding it from above and the occasional cold morning making it brittle, and the "
            "outcome is predictable: it hazes, then it cracks at the fold, then water gets in.",
            "By the time water is getting in, the fabric around the window is often still "
            "perfectly serviceable — which is exactly why it is worth asking whether you need a "
            "whole new top at all.",
            "<h2>Can you replace just the window?</h2>",
            "Frequently, yes. If the fabric is sound, the seams are intact and only the curtain "
            "has failed, replacing the window alone is a real option and costs considerably less "
            "than a full top.",
            "It stops being an option when the surrounding fabric has gone stiff and chalky, "
            "because new stitching through tired material tends to tear out, or when the seams "
            "either side of the window are already opening.",
            "<h2>Can you switch from plastic to glass?</h2>",
            "Sometimes, and it depends on the car. Glass is heavier and does not fold, so the "
            "frame, the well and the way the top stacks all have to accommodate it. On cars that "
            "were offered both ways from the factory it is usually straightforward. On cars that "
            "never were, it may not be possible at all.",
            "This is a question to ask with the car in front of us rather than over the phone.",
            "<h2>Making a plastic window last</h2>",
            "<ul class=\"ticks\">"
            "<li>Never fold the top in cold weather if you can avoid it</li>"
            "<li>Never clean it with anything containing ammonia &mdash; glass cleaner clouds "
            "plastic</li>"
            "<li>Use a plastic-specific polish, not a glass one</li>"
            "<li>Never put the top away damp</li>"
            "</ul>",
            "Bring the car to the shop in Monroe and we will tell you honestly whether you are "
            "looking at a window, a repair, or a new top. See our "
            "<a href=\"convertible-tops.html\">convertible top replacement</a> page.",
        ],
    },
    {
        "slug": "blog-why-convertible-tops-fail.html",
        "cat": "Convertible Tops", "publish": "2026-08-08", "read": "5 min read",
        "photo": "convertible-top-replacement-and-finish",
        "title": "Why convertible tops fail: it is usually the frame, not the fabric",
        "seo_title": "Why Convertible Tops Fail — Frame, Pads and Bows | Auto Tops and Trim",
        "meta": "Collapsed pads, bent bows and worn seals are why most convertible tops wear out "
                "early. What to check, and why a new top over a bad frame never sits right.",
        "excerpt": "A top that wore out in five years was almost never a bad top. It was a good "
                   "top fitted over a frame nobody looked at.",
        "body": [
            "When a top wears through early, the fabric usually gets the blame. In our experience "
            "the fabric is rarely the culprit — it is the structure underneath deciding where the "
            "fabric gets worn.",
            "<h2>The three things under the fabric</h2>",
            "<h3>Pads</h3>",
            "Pads sit over the bows and stop the metal telegraphing through the fabric. When they "
            "collapse, the fabric rests directly on the bows. Every bow becomes a hard line, and "
            "the top wears through along those lines while the panels between them are still "
            "fine. If you can see the bow lines through a raised top, the pads are gone.",
            "<h3>Bows</h3>",
            "The bows are the frame the top is stretched over. Bend one — usually by forcing a "
            "top that was frozen, jammed, or fighting a failed mechanism — and the fabric can "
            "never sit evenly again. You get a top that looks slack in one place and drum-tight "
            "in another, and it wears at the tight spot.",
            "<h3>Seals and drains</h3>",
            "Water is supposed to run off the top, down channels, and out through drains. When "
            "those drains block, water backs up and sits against the fabric and the frame, "
            "rotting stitching and rusting bows.",
            "<h2>What early failure actually looks like</h2>",
            "<ul class=\"ticks\">"
            "<li>Wear appearing in straight lines across the roof &mdash; collapsed pads</li>"
            "<li>The top sitting slack on one side and tight on the other &mdash; a bent bow or a "
            "twisted frame</li>"
            "<li>Stitching rotting while the fabric is still good &mdash; standing water, usually "
            "a blocked drain</li>"
            "<li>Rear window splitting well before the fabric ages &mdash; folding it cold</li>"
            "<li>Fabric wearing at one specific corner &mdash; something is catching it as it "
            "stacks</li>"
            "</ul>",
            "<h2>Why we insist on seeing the car</h2>",
            "Most quotes people bring us from elsewhere cover the fabric and nothing else. That "
            "is a cheaper number on paper, and it is why the same customer is back in a few "
            "years with the same problem.",
            "A photo cannot show a collapsed pad or a bent bow. Neither can a phone call. The "
            "only way to quote all three parts of the job honestly is to put the top up and down "
            "with the car in front of us — which is what the free in-person estimate is for.",
            "<h2>Getting the most out of a new top</h2>",
            "<ul class=\"ticks\">"
            "<li>Replace collapsed pads at the same time as the fabric, not later</li>"
            "<li>Keep the drains clear &mdash; it is a five-minute job that prevents a large one</li>"
            "<li>Do not fold a top that is wet or cold</li>"
            "<li>Fix a stiff or slow mechanism before it bends something</li>"
            "</ul>",
            "Bring the car to Monroe and we will walk the whole assembly with you. See our "
            "<a href=\"convertible-tops.html\">convertible top replacement</a> page.",
        ],
    },
    {
        "slug": "blog-leather-car-seat-repair.html",
        "cat": "Seats", "publish": "2026-08-09", "read": "6 min read",
        "photo": "g08-cushion-and-armrest-trimmed",
        "title": "Leather car seat repair: what can be saved and what cannot",
        "seo_title": "Leather Car Seat Repair: Repair, Recolour or Recover? | Auto Tops and Trim",
        "meta": "Cuts, cracks, wear and colour loss on leather car seats — which are genuinely "
                "repairable, which need a panel replaced, and why cracked leather rarely responds.",
        "excerpt": "A clean cut in good leather repairs beautifully. Cracking across a worn "
                   "bolster does not. The difference is whether the leather itself is still sound.",
        "body": [
            "Leather repair covers several very different jobs, and the results range from "
            "invisible to obviously patched. Which one you get depends less on the damage than on "
            "the condition of the leather surrounding it.",
            "<h2>The four kinds of damage</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Damage</th><th>Realistic outcome</th></tr></thead><tbody>"
            "<tr><th>Clean cut or puncture</th>"
            "<td>Repairs well. Backed, filled and grained, then colour-matched. On sound leather "
            "this can be genuinely hard to find afterwards.</td></tr>"
            "<tr><th>Seam split</th>"
            "<td>Not a leather problem at all &mdash; the thread failed. Restitching is the "
            "correct fix and usually the cheapest thing on this list.</td></tr>"
            "<tr><th>Colour loss and scuffing</th>"
            "<td>Responds well to cleaning and recolouring, provided the surface is still intact "
            "underneath.</td></tr>"
            "<tr><th>Cracking</th>"
            "<td>The hard one. Cracking means the leather has dried out and the surface is "
            "failing across the whole panel. Filling individual cracks leaves you with a repaired "
            "panel that cracks again beside the repair.</td></tr>"
            "</tbody></table></div>",
            "<h2>The test worth doing before you spend anything</h2>",
            "Press the leather next to the damage and flex it gently.",
            "<ul class=\"ticks\">"
            "<li>Supple, springs back, no fine lines appearing &mdash; the leather is sound and a "
            "repair has a real chance</li>"
            "<li>Stiff, or a web of fine cracks appears as you flex it &mdash; the panel is at "
            "the end of its life and a repair will be temporary</li>"
            "<li>The surface feels like plastic and is lifting &mdash; this is likely a coated "
            "or bonded material rather than full leather, and it does not repair well</li>"
            "</ul>",
            "<h2>Why bolsters fail first</h2>",
            "The outer bolster on the driver's seat takes the entire load of somebody sliding "
            "across it several times a day, plus the most sun. It is almost always the first "
            "thing to go, and it is the worst place for a surface repair because it flexes "
            "constantly and is under tension.",
            "On a bolster we would generally rather replace the panel than fill it. A new panel "
            "stitched in is a permanent answer; a filled bolster is a repair with a countdown.",
            "<h2>Colour matching, honestly</h2>",
            "Matching an aged interior is harder than matching a new one, because the leather you "
            "are matching to has faded unevenly. A repair matched perfectly to the panel it sits "
            "in can still stand out against the seat next to it.",
            "This is why recolouring a whole panel, or a whole seat, often looks better than "
            "spot-matching &mdash; consistency reads as correct even when the shade has moved.",
            "<h2>When recovering is the cheaper answer</h2>",
            "If several panels are cracking, if the foam underneath has collapsed, or if the "
            "leather has hardened across the seat, repairs stop being economical. You end up "
            "paying repeatedly for work that keeps moving to the next panel.",
            "Bring the vehicle, or just the seat, to the shop in Monroe. We will tell you plainly "
            "which of these you are looking at before you commit to anything. More on our "
            "<a href=\"auto-upholstery.html\">automotive upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-cost-to-reupholster-car-seats.html",
        "cat": "Seats", "publish": "2026-08-09", "read": "5 min read",
        "photo": "g07-bench-seat-red-piping-in-the-shop",
        "title": "What changes the cost of reupholstering car seats",
        "seo_title": "Cost to Reupholster Car Seats: What Drives the Price | Auto Tops and Trim",
        "meta": "The variables behind a seat reupholstery quote — material, number of panels, "
                "stitch pattern, foam and frame condition — and why quotes differ so much.",
        "excerpt": "Two shops can quote the same seats very differently. Almost all of the gap "
                   "comes from four things, and only one of them is the material.",
        "body": [
            "Reupholstery quotes vary widely, and the variation is rarely about the fabric. It is "
            "about how many pieces the seat breaks into, what is found underneath, and how much "
            "of the original construction is being reproduced.",
            "<h2>1. How many panels the seat has</h2>",
            "A flat bench with three panels is a fundamentally different job from a modern "
            "sports seat with contoured bolsters, separate side panels, a map pocket and a "
            "headrest. Every panel is a piece to pattern, cut, sew and fit. Panel count is the "
            "single biggest driver of labour on a seat.",
            "<h2>2. The stitch work</h2>",
            "<ul class=\"ticks\">"
            "<li>Plain panels with a single seam &mdash; fastest</li>"
            "<li>French seams, piping or welting &mdash; more time per seam, and the reason a "
            "seat looks finished rather than assembled</li>"
            "<li>Contrast thread &mdash; adds little cost but leaves no room for error, because "
            "every stitch is now visible</li>"
            "<li>Diamond, pleated or biscuit patterns &mdash; the most labour-intensive work we "
            "do, and priced accordingly</li>"
            "</ul>",
            "<h2>3. The material</h2>",
            "Cloth, vinyl and leather sit at different price points, but on most seats the "
            "material is a smaller share of the total than people expect. A seat that takes eight "
            "hours to trim takes eight hours regardless of what it is trimmed in.",
            "Where material really moves the number is on a classic, where matching a "
            "discontinued grain or weave may mean a specialist supplier.",
            "<h2>4. What is underneath</h2>",
            "This is the one that separates a real quote from an optimistic one.",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Found underneath</th><th>Effect on the job</th></tr></thead><tbody>"
            "<tr><th>Sound foam and frame</th><td>Recover and go. Best case.</td></tr>"
            "<tr><th>Collapsed or crumbling foam</th>"
            "<td>Foam replaced or rebuilt. Skipping this means the new cover sits on the wrong "
            "shape and wears early in the same place as the old one.</td></tr>"
            "<tr><th>Broken or cracked frame</th>"
            "<td>Repaired properly. Never shimmed &mdash; a shimmed frame keeps moving and takes "
            "the new cover with it.</td></tr>"
            "<tr><th>Failed springs or webbing</th>"
            "<td>Replaced. Common on older bench seats and the reason they sit low.</td></tr>"
            "</tbody></table></div>",
            "<h2>Why some seats need a look first</h2>",
            "Send photos and we will get a number back to you. That said, three of the four "
            "factors above are invisible in a photograph — you cannot see foam condition, a "
            "cracked frame or failed webbing until the cover comes off, and pricing without "
            "knowing means either padding the number to stay safe or revising it later.",
            "We take the seat apart far enough to see what we are dealing with, then give you an "
            "itemised estimate at no cost, with the cover, the foam and any frame work priced "
            "separately.",
            "You do not need a full interior. Bring one seat to the shop in Monroe. More on our "
            "<a href=\"auto-upholstery.html\">automotive upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-car-carpet-replacement.html",
        "cat": "Interiors", "publish": "2026-08-09", "read": "5 min read",
        "photo": "g10-bel-air-new-carpet-going-in",
        "title": "Car carpet replacement: moulded, cut-pile and what goes underneath",
        "seo_title": "Car Carpet Replacement: Moulded vs Cut Pile | Auto Tops and Trim",
        "meta": "Replacing car carpet — moulded versus cut-and-bound, why sound deadening goes "
                "in at the same time, and what wet carpet is usually telling you.",
        "excerpt": "New carpet is the cheapest interior change that makes an old car feel "
                   "different — provided you deal with what is under it at the same time.",
        "body": [
            "Carpet is the largest single surface in most interiors and the one that shows age "
            "fastest. It is also the only interior job where the thing underneath matters more "
            "than the thing you can see.",
            "<h2>Moulded or cut and bound?</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th></th><th>Moulded</th><th>Cut and bound</th></tr></thead><tbody>"
            "<tr><th>How it is made</th>"
            "<td>Heat-formed to the exact shape of that model's floor pan</td>"
            "<td>Cut from flat carpet to a pattern and bound at the edges</td></tr>"
            "<tr><th>Fit</th><td>Follows every contour with no bunching</td>"
            "<td>Depends entirely on the pattern and the fitter</td></tr>"
            "<tr><th>Availability</th>"
            "<td>Only for vehicles someone makes a mould for</td>"
            "<td>Any vehicle, any material</td></tr>"
            "<tr><th>Best for</th><td>Common models with good aftermarket support</td>"
            "<td>Anything unusual, modified, or where you want a specific material</td></tr>"
            "</tbody></table></div>",
            "<h2>What goes underneath is the real upgrade</h2>",
            "With the carpet out, the floor is bare and accessible &mdash; and it is the only "
            "time it will be. This is the moment for sound deadening, and it is the single "
            "biggest change you can make to how an older car feels to drive.",
            "Road noise, exhaust drone and the general tinniness of an old floor pan all drop "
            "noticeably. It costs relatively little on top of a job already being done, and "
            "doing it later means paying to pull the carpet a second time.",
            "<h2>Wet carpet is a symptom, not a problem</h2>",
            "If the carpet is damp, replacing it without finding the water is money thrown away. "
            "Common sources:",
            "<ul class=\"ticks\">"
            "<li>Blocked sunroof drains &mdash; water runs down the pillars and appears in the "
            "footwell nowhere near the roof</li>"
            "<li>Failed windscreen or door seals</li>"
            "<li>Heater matrix leaks, which usually smell sweet and fog the windscreen</li>"
            "<li>Body plugs and seam sealer that have let go underneath</li>"
            "</ul>",
            "Wet carpet also hides floor-pan rust, and that is worth knowing about before it "
            "becomes structural rather than cosmetic.",
            "<h2>Do not forget the pieces around it</h2>",
            "New carpet next to a sun-bleached kick panel or a worn shift boot draws attention to "
            "both. Carpet, boot and trim panels are usually best done together, which is why a "
            "carpet job on a classic often turns into a broader interior conversation.",
            "Bring the car to the shop in Monroe and we will look at the floor with you before "
            "quoting. More on our <a href=\"auto-upholstery.html\">automotive upholstery</a> page.",
        ],
    },

    # ---- BATCH 3: marine ----------------------------------------------------
    {
        "slug": "blog-boat-canvas-materials-compared.html",
        "cat": "Marine", "publish": "2026-08-10", "read": "7 min read",
        "photo": "boat-upholstery-projects-at-the-shop",
        "title": "Boat canvas compared: Sunbrella, Top Gun, Stamoid and Seamark",
        "seo_title": "Boat Canvas Compared: Sunbrella vs Top Gun vs Stamoid vs Seamark",
        "meta": "The four marine top fabrics compared on UV resistance, waterproofing, "
                "breathability and lifespan — and which suits a slip, a lift or a trailer.",
        "excerpt": "Waterproof and breathable pull against each other. Any shop telling you one "
                   "fabric wins on both is selling you something.",
        "body": [
            "Marine canvas comes in four broad families, and they genuinely suit different boats "
            "and different storage. The choice is not about which is best — it is about which "
            "compromise you want.",
            "<h2>The four families</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Fabric</th><th>Type</th><th>Strengths</th><th>Trade-off</th></tr>"
            "</thead><tbody>"
            "<tr><th>Sunbrella</th><td>Solution-dyed acrylic</td>"
            "<td>Best-in-class UV resistance and colourfastness, breathable, carries a 10-year "
            "warranty against fading</td>"
            "<td>Water-resistant rather than waterproof; depends on good design and upkeep</td>"
            "</tr>"
            "<tr><th>Top Gun</th><td>Coated polyester</td>"
            "<td>Excellent abrasion resistance and strength, solid UV performance, friendlier "
            "price</td>"
            "<td>Shorter service life in punishing sun, and coating quality varies widely by "
            "grade</td></tr>"
            "<tr><th>Stamoid</th><td>Vinyl-coated</td>"
            "<td>Maximum waterproofing of the four</td>"
            "<td>Does not breathe, so trapped moisture underneath becomes the new problem</td>"
            "</tr>"
            "<tr><th>Seamark</th><td>Sunbrella base with a vinyl backing</td>"
            "<td>Fully waterproof while matching Sunbrella colours; a common OE choice for "
            "bimini and camper tops</td>"
            "<td>Costs more than either material it is made from</td></tr>"
            "</tbody></table></div>",
            "<h2>Why solution-dyed matters</h2>",
            "In a solution-dyed acrylic the colour is added to the fibre while it is still "
            "liquid, so it runs all the way through. In a coated or surface-dyed fabric the "
            "colour sits on top.",
            "The difference is invisible in year one. By year three the coated fabric has gone "
            "chalky and faded while the acrylic still looks like itself. That is the entire "
            "argument for paying more up front.",
            "<h2>The trade nobody can escape</h2>",
            "Read the table again and the pattern is clear: <strong>waterproof and breathable "
            "work against each other.</strong> A fabric that lets no water in also lets no "
            "moisture out, so condensation collects underneath — on cushions, on the deck, and "
            "in any wood it can reach.",
            "This is why the right answer depends far more on how the boat is stored than on the "
            "boat itself.",
            "<h2>Choosing by how the boat lives</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>In a slip, uncovered, in full sun</strong> — UV is the enemy. Acrylic.</li>"
            "<li><strong>On a lift or mooring, exposed to rain</strong> — waterproofing matters "
            "more. Seamark or Stamoid, with ventilation designed in.</li>"
            "<li><strong>On a trailer, stored dry</strong> — abrasion from towing is the biggest "
            "load. Coated polyester earns its keep here.</li>"
            "<li><strong>Bimini or camper top you want to match existing canvas</strong> — "
            "Seamark exists precisely for this.</li>"
            "</ul>",
            "<h2>The parts that fail before the fabric</h2>",
            "On most canvas we see, the fabric is not what failed. It is the thread, the zips or "
            "the hardware. Thread that is not rot-proof gives out at the seams while the panels "
            "are still sound, and it is the cheapest place for a shop to cut a corner because "
            "nobody can see it.",
            "Bring a piece of your canvas by the shop in Monroe and we will tell you honestly "
            "whether it needs recovering, restitching, or replacing. See our "
            "<a href=\"marine-upholstery.html\">marine upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-boat-canvas-repair-or-replace.html",
        "cat": "Marine", "publish": "2026-08-10", "read": "5 min read",
        "photo": "upholstery-materials-and-marine-project-parts",
        "title": "Boat canvas: repair or replace?",
        "seo_title": "Boat Canvas Repair or Replace? How to Decide | Auto Tops and Trim",
        "meta": "When boat canvas is worth repairing and when it has reached the end — chalking, "
                "seam failure, zips and hardware explained by a marine trim shop.",
        "excerpt": "A split seam is worth fixing. Chalky fabric is not. Here is how to tell "
                   "which one you are looking at before you spend anything.",
        "body": [
            "Canvas rarely fails all at once. It fails in one specific way, and the way it failed "
            "tells you whether repairing it is sensible or throwing good money after bad.",
            "<h2>Worth repairing</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Seams opening while the panels are sound.</strong> The thread failed, "
            "not the fabric. Restitching is a proper structural fix and the cheapest thing we "
            "do to canvas.</li>"
            "<li><strong>A tear from a snag or a branch.</strong> Clean damage in good material "
            "patches or panels in well.</li>"
            "<li><strong>Failed zips.</strong> Replaceable, and usually the first component to "
            "go on an enclosure.</li>"
            "<li><strong>Pulled or missing fasteners.</strong> Snaps and hardware are "
            "consumables, not a reason to replace canvas.</li>"
            "<li><strong>One bad panel in an otherwise good set.</strong> Panels can be replaced "
            "individually.</li>"
            "</ul>",
            "<h2>Past repairing</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Chalking.</strong> A powdery residue on your hand means a coated fabric "
            "has reached the end of its life. Nothing brings it back and stitching into it tends "
            "to tear out.</li>"
            "<li><strong>Stiff, brittle fabric.</strong> It should be supple. When it crackles, "
            "it is done.</li>"
            "<li><strong>Multiple seams failing at once.</strong> The thread has aged uniformly; "
            "fixing one just moves the problem along.</li>"
            "<li><strong>Fabric tearing beside an old repair.</strong> The repair is now stronger "
            "than the material around it — a clear end-of-life signal.</li>"
            "<li><strong>Widespread staining under the surface</strong> rather than on it.</li>"
            "</ul>",
            "<h2>The chalk test</h2>",
            "Rub a dry hand firmly across a sun-exposed panel. If your palm comes away with a "
            "fine coloured powder, that is the coating breaking down. It is the single most "
            "reliable indicator that canvas is finished, and it takes five seconds.",
            "<h2>The window panels are their own decision</h2>",
            "Clear vinyl windows in an enclosure almost always fail before the canvas around "
            "them — they cloud, yellow and craze. Replacing just the windows in otherwise sound "
            "canvas is a common and worthwhile job, and much cheaper than a new enclosure.",
            "As with convertible tops: never clean them with anything containing ammonia, and "
            "never fold them cold.",
            "<h2>Making the next set last</h2>",
            "<ul class=\"ticks\">"
            "<li>Specify rot-proof thread. It is the component that usually fails first.</li>"
            "<li>Rinse salt off rather than letting it dry in the weave.</li>"
            "<li>Never put canvas away wet.</li>"
            "<li>Deal with a small tear immediately, before wind turns it into a large one.</li>"
            "</ul>",
            "Bring a piece to the shop in Monroe — you do not need to bring the boat. See our "
            "<a href=\"marine-upholstery.html\">marine upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-bimini-top-replacement.html",
        "cat": "Marine", "publish": "2026-08-10", "read": "5 min read",
        # NOT marine-boat-cushions-canvas or g22 — both are the same photograph as
        # marine-seating-and-interior-upholstery (see the duplicate map above GALLERY).
        "photo": "boat-upholstery-projects-at-the-shop",
        "title": "Bimini top replacement: measuring, bows and fabric choice",
        "seo_title": "Bimini Top Replacement: Bows, Measuring and Fabric | Auto Tops and Trim",
        "meta": "Replacing a bimini top — how bow count and frame width decide fit, which fabric "
                "suits your storage, and why replacing canvas on a tired frame disappoints.",
        "excerpt": "Most disappointing bimini replacements are not the fabric's fault. They are "
                   "a new top fitted to a frame that had already moved.",
        "body": [
            "A bimini looks like a simple piece of canvas over a frame, and the replacement goes "
            "wrong in the same two ways almost every time: the measurements were taken from the "
            "old top, or the frame was never assessed.",
            "<h2>Bow count is the first question</h2>",
            "Biminis are described by how many bows the frame has — commonly three or four. A "
            "four-bow frame supports a longer top with less sag between supports. The bow count "
            "is not something you choose when replacing the canvas; it is determined by the "
            "frame you already have.",
            "<h2>Measure the frame, not the old top</h2>",
            "This is the mistake that produces a top which never sits right. An old top has "
            "stretched, shrunk, or been fitted to a frame that has since shifted. Copy those "
            "dimensions and you reproduce the problem in new fabric.",
            "The measurements that matter:",
            "<ul class=\"ticks\">"
            "<li><strong>Width</strong> — between the mounting points, not the fabric edges</li>"
            "<li><strong>Length</strong> — front bow to rear bow along the frame</li>"
            "<li><strong>Height</strong> — deck to the top of the frame when it is up</li>"
            "<li><strong>Bow count</strong> and their spacing</li>"
            "</ul>",
            "<h2>The frame decides how the new top ages</h2>",
            "Before spending on canvas, work the frame. Bent tubing, seized joints, worn hinge "
            "pins and loose deck hinges all put uneven tension into the new fabric, and uneven "
            "tension is what wears a top out early — always at the same tight spot.",
            "It is the same principle as a convertible top over collapsed pads: the fabric gets "
            "blamed for a structural problem.",
            "<h2>Which fabric</h2>",
            "The choice follows the same logic as any other marine canvas — see our "
            "<a href=\"blog-boat-canvas-materials-compared.html\">comparison of Sunbrella, Top "
            "Gun, Stamoid and Seamark</a> for the detail. In short:",
            "<ul class=\"ticks\">"
            "<li><strong>Full sun, want it to hold colour</strong> — solution-dyed acrylic</li>"
            "<li><strong>Want genuinely waterproof and matching existing acrylic canvas</strong> "
            "— Seamark, which is Sunbrella with a vinyl backing</li>"
            "<li><strong>Trailered often, abrasion is the load</strong> — coated polyester</li>"
            "</ul>",
            "<h2>Do not skimp on thread and hardware</h2>",
            "Rot-proof thread and decent fasteners cost very little against the fabric and they "
            "are what actually determines whether you get a decade out of the top or four years. "
            "Almost every failed bimini we see failed at a seam or a fitting, not in the middle "
            "of a panel.",
            "Bring the boat, or just the frame and old top, to the shop in Monroe. See our "
            "<a href=\"marine-upholstery.html\">marine upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-boat-seat-repair.html",
        "cat": "Marine", "publish": "2026-08-11", "read": "5 min read",
        "photo": "marine-seating-and-interior-upholstery",
        "title": "Boat seat repair: tears, seams and the foam nobody checks",
        "seo_title": "Boat Seat Repair: Vinyl Tears, Seams and Foam | Auto Tops and Trim",
        "meta": "Repairing vinyl boat seats — which damage patches successfully, why seams fail "
                "first, and how to tell when the foam is the actual problem.",
        "excerpt": "Most boat seat failures start at a seam or in the foam. The vinyl itself is "
                   "usually the last thing to go.",
        "body": [
            "Marine vinyl is engineered to survive a hard life, and in most cushions that come "
            "through the shop the vinyl has done its job. What failed was the thread holding it "
            "together or the foam inside it.",
            "<h2>Start by identifying what actually failed</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Symptom</th><th>Cause</th><th>Fix</th></tr></thead><tbody>"
            "<tr><th>Seam opening, vinyl sound</th><td>Thread failed — often not rot-proof, or "
            "degraded by harsh cleaning</td><td>Restitch. The cheapest and most durable "
            "repair.</td></tr>"
            "<tr><th>Clean tear or puncture</th><td>Mechanical damage</td>"
            "<td>Patchable on a flat panel; better to replace the panel on an edge</td></tr>"
            "<tr><th>Cracking along fold lines</th><td>Plasticisers gone, usually from solvents "
            "or repeated bleach</td><td>Recover. The material is finished.</td></tr>"
            "<tr><th>Cushion stays damp, smells</th><td>Water inside the foam</td>"
            "<td>Open it and replace the foam</td></tr>"
            "<tr><th>Seat feels flat or lopsided</th><td>Foam collapsed or waterlogged</td>"
            "<td>New foam. Recovering alone will not fix the shape.</td></tr>"
            "</tbody></table></div>",
            "<h2>Why seams fail first on a boat</h2>",
            "Thread is the cheapest component in a cushion and the easiest place to save money, "
            "so it is frequently the weakest part of an otherwise well-made seat. On the water it "
            "takes UV, salt and constant damp, and thread that is not rot-proof simply will not "
            "last.",
            "Harsh cleaning accelerates it dramatically. Repeated bleach attacks the thread long "
            "before it visibly harms the vinyl, which is why so many seats fail at the seams "
            "shortly after somebody started cleaning them properly for the first time.",
            "<h2>The foam question</h2>",
            "Press the cushion and hold. If water comes up, or it feels heavier than it should, "
            "the foam is holding water against the cover and the deck.",
            "Standard upholstery foam behaves like a sponge. Quick-dry reticulated foam has an "
            "open cell structure that passes water straight through. If the cushion is being "
            "opened anyway, this is the upgrade worth taking — it is the difference between a "
            "cushion that dries in an afternoon and one that never truly does.",
            "<h2>What a repair kit is good for</h2>",
            "A vinyl repair kit is a fair answer to a small puncture on a flat panel of a boat "
            "you are not precious about. It is not an answer to a seam split, a fold-line crack, "
            "or anything on a cushion that flexes as you sit on it.",
            "<h2>Bring one piece</h2>",
            "You do not need to bring the boat. One cushion tells us what we need to know about "
            "the thread, the vinyl and the foam. Free in-person assessment at the shop in Monroe "
            "— see our <a href=\"marine-upholstery.html\">marine upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-marine-vinyl-buying-guide.html",
        "cat": "Marine", "publish": "2026-08-11", "read": "6 min read",
        # NOT marine-canvas-cushions — despite the name that photo is a classic car
        # rear bench seat, not marine at all.
        "photo": "upholstery-materials-and-marine-project-parts",
        "title": "Marine vinyl: what to look for and what the grades actually mean",
        "seo_title": "Marine Grade Vinyl: What to Look For in Boat Upholstery Fabric",
        "meta": "What makes a vinyl marine grade — UV stabilisation, mildew resistance, "
                "cold-crack rating and backing — and why the thread matters as much as the cover.",
        "excerpt": "Marine vinyl is not just thicker upholstery vinyl. Four specific properties "
                   "separate it, and only one of them is visible in a sample.",
        "body": [
            "\"Marine grade\" is not a regulated term, which is exactly why it is worth knowing "
            "what genuine marine vinyl has engineered into it. Four properties matter, and none "
            "of them can be judged by feel alone.",
            "<h2>1. UV stabilisation</h2>",
            "The single biggest difference. Untreated vinyl in full sun goes chalky and stiff "
            "within a season or two. Marine vinyl carries UV inhibitors in the topcoat that slow "
            "that dramatically.",
            "This is why a sample that feels identical to automotive vinyl in the shop behaves "
            "completely differently after one summer on the water.",
            "<h2>2. Mildew resistance</h2>",
            "Marine upholstery spends its life damp. Genuine marine vinyl has antimicrobial "
            "treatment in both the topcoat and the backing, because mildew attacks the backing "
            "from underneath where you cannot see it.",
            "<h2>3. Cold-crack rating</h2>",
            "Rarely discussed and important if the boat is stored through winter. Vinyl stiffens "
            "as it cools, and a low cold-crack rating means it splits at the folds when handled "
            "cold. If your boat winters outside, ask about this specifically.",
            "<h2>4. The backing</h2>",
            "Under the vinyl is a knit or woven backing, and it determines how the material "
            "stretches over a curved cushion. Too little stretch and it will not pull down over a "
            "bolster without wrinkling. Too much and it distorts. This is the property that "
            "decides whether a finished cushion looks factory or homemade.",
            "<h2>The component that fails first is not the vinyl</h2>",
            "It is the thread. A perfect cover stitched with the wrong thread fails at the seams "
            "while every panel is still sound, and thread is invisible in a fabric sample.",
            "Insist on rot-proof thread. It costs very little relative to the job and it is "
            "routinely the difference between a cushion that lasts a decade and one that opens up "
            "in year three.",
            "<h2>Foam belongs in the same conversation</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Foam</th><th>Behaviour</th><th>Use</th></tr></thead><tbody>"
            "<tr><th>Standard upholstery foam</th><td>Absorbs and holds water against the cover "
            "and deck</td><td>Fine in a cabin that stays dry; wrong anywhere exposed</td></tr>"
            "<tr><th>Quick-dry reticulated</th><td>Open cell structure passes water straight "
            "through</td><td>Cockpit seating, anything that gets rained on or splashed</td></tr>"
            "</tbody></table></div>",
            "<h2>Leather is the wrong answer on the water</h2>",
            "Leather is wonderful in a car. On a boat, standing water, UV and salt will dry it "
            "out and crack it inside a season or two. We cover the full comparison in "
            "<a href=\"blog-marine-vinyl-vs-leather.html\">marine vinyl vs automotive leather</a>.",
            "Bring a cushion or a sample to the shop in Monroe and we will show you the "
            "difference in hand. See our <a href=\"marine-upholstery.html\">marine upholstery</a> "
            "page.",
        ],
    },
    {
        "slug": "blog-sunroof-shade-repair-cost.html",
        "cat": "Sunroof Shades", "publish": "2026-08-11", "read": "4 min read",
        "photo": "g13-sound-deadening-before-carpet",
        "title": "Sunroof shade repair: why recovering beats replacing the assembly",
        "seo_title": "Sunroof Shade Repair Cost: Recover, Don't Replace | Auto Tops and Trim",
        "meta": "A sagging or torn sunroof sunshade rarely needs a new sunroof assembly. What "
                "recovering the panel involves and what changes the cost.",
        "excerpt": "Dealers often quote a whole sunroof assembly for a shade problem. The panel "
                   "you already have can usually be recovered instead.",
        "body": [
            "A sunroof sunshade fails for exactly the same reason a headliner does: the fabric is "
            "bonded to a thin layer of foam, the foam breaks down in heat, and the fabric lets "
            "go. It is the same failure in a smaller panel.",
            "<h2>Why the quote you were given may be for the wrong job</h2>",
            "Because the shade runs in tracks inside the sunroof cassette, it is often treated as "
            "part of the sunroof assembly rather than as a trim panel. That framing turns a "
            "modest upholstery job into a large mechanical one.",
            "In most cases the shade panel can be removed, stripped back and recovered — the "
            "sunroof mechanism itself is untouched because there is nothing wrong with it.",
            "<h2>What recovering involves</h2>",
            "<ul class=\"ticks\">"
            "<li>The shade panel comes out of its tracks</li>"
            "<li>Old fabric and every trace of the failed foam are scraped back to clean panel</li>"
            "<li>New foam-backed material is bonded down and trimmed to the exact edge profile</li>"
            "<li>It goes back in and gets tested through its full travel</li>"
            "</ul>",
            "The edges matter more than people expect. The panel has to slide in its tracks, so "
            "material thickness and how the edges are finished decide whether it moves properly "
            "afterwards.",
            "<h2>What changes the price</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>How the panel is accessed.</strong> Some come out with the headliner in "
            "place; others need the headliner dropped, which is most of the labour.</li>"
            "<li><strong>Whether the headliner is going too.</strong> If both are failing, doing "
            "them together is markedly cheaper than doing them separately, because the access "
            "work happens once.</li>"
            "<li><strong>Matching.</strong> A recovered shade should match the headliner around "
            "it. Where the headliner has aged, we will tell you honestly how close a match "
            "is achievable.</li>"
            "<li><strong>Track condition.</strong> Occasionally the slides or guides are worn "
            "and that is a separate repair.</li>"
            "</ul>",
            "<h2>Two of our Google reviews are about this exact repair</h2>",
            "This is not a service we added recently. Two of the shop's reviews are specifically "
            "about sunroof shade work, including one customer who was invited to watch the "
            "process. The full text of both is quoted on our "
            "<a href=\"sunroof-shade-repair.html\">sunroof shade repair</a> page.",
            "<h2>Bring it by</h2>",
            "If a dealer has quoted you for a sunroof assembly because the shade sags, it is "
            "worth a second opinion before you spend that. Free in-person estimate at the shop in "
            "Monroe.",
        ],
    },

    # ---- BATCH 4: the rest --------------------------------------------------
    {
        "slug": "blog-convertible-top-cost-by-model.html",
        "cat": "Convertible Tops", "publish": "2026-08-12", "read": "6 min read",
        "photo": "g18-camaro-ss-profile",
        "title": "Convertible top replacement by model: what makes some cars cost more",
        "seo_title": "Convertible Top Replacement Cost by Model | Auto Tops and Trim",
        "meta": "Mustang, Beetle, Camaro, Corvette, Miata, Sebring and more — what makes each "
                "convertible top job easy or awkward, and which factors drive the estimate.",
        "excerpt": "Deliberately one page rather than twelve near-identical ones. Here is what "
                   "changes between models, and why some cars are simply more work.",
        "body": [
            "People search for convertible top costs by model, and most sites answer with a "
            "dozen near-identical pages and a made-up number on each. We would rather do this "
            "once, properly, and be honest about what actually differs.",
            "<h2>What genuinely varies between models</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Factor</th><th>Why it moves the price</th></tr></thead><tbody>"
            "<tr><th>Original material</th><td>A car that came with cloth costs more to keep "
            "correct than one that came with pinpoint vinyl</td></tr>"
            "<tr><th>Rear window type</th><td>Heated glass is a different job from a plastic "
            "curtain, and some models offered both</td></tr>"
            "<tr><th>Number of panels</th><td>Some tops are a single skin; others have separate "
            "quarter panels and a headliner of their own</td></tr>"
            "<tr><th>Top well and trim</th><td>How much interior trim has to come out to reach "
            "the attachment points</td></tr>"
            "<tr><th>Mechanism</th><td>Manual, power, or semi-automatic with sensors that need "
            "resetting</td></tr>"
            "<tr><th>Pad and bow condition</th><td>Independent of model &mdash; this is about "
            "how the individual car has lived</td></tr>"
            "</tbody></table></div>",
            "<h2>Commonly asked-about models</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Ford Mustang</strong> — well-supported, materials readily available, "
            "and both glass and plastic rear windows exist across the generations.</li>"
            "<li><strong>Chevrolet Camaro</strong> — similar story. We have done these; there is "
            "one in the <a href=\"gallery.html\">gallery</a>.</li>"
            "<li><strong>Chevrolet Corvette (C5 era)</strong> — straightforward top, and again "
            "one we have in the gallery.</li>"
            "<li><strong>VW Beetle</strong> — the later cars have a heavily insulated multi-layer "
            "top, which is more material and more work than it looks.</li>"
            "<li><strong>Mazda Miata</strong> — one of the more accessible jobs, and a very "
            "common candidate for a glass-window upgrade where the frame allows.</li>"
            "<li><strong>Chrysler Sebring</strong> — plentiful, and the rear window is usually "
            "the reason it is in the shop.</li>"
            "<li><strong>Jeep Wrangler</strong> — a soft top rather than a convertible top in the "
            "traditional sense; different hardware, different expectations.</li>"
            "<li><strong>Porsche, BMW, Audi, Mercedes</strong> — generally cloth from the "
            "factory, frequently Twillfast grade, and the mechanisms are more involved.</li>"
            "</ul>",
            "<h2>Why we do not publish a price per model</h2>",
            "Because it would be a number we invented. Two identical cars can differ by a wide "
            "margin depending on whether the pads have collapsed, whether the bows are straight, "
            "and whether the previous top was fitted properly.",
            "A number that ignores those is the kind of quote customers bring us from elsewhere "
            "and then discover was for the fabric only. We would rather tell you the six things "
            "above and then price your actual car.",
            "<h2>Getting a real number</h2>",
            "Bring the car to Monroe. We put the top up and down, look at the pads, the bows and "
            "the window, show you material samples, and give you an itemised estimate at no "
            "charge — with the fabric, the window and any frame work listed separately. See our "
            "<a href=\"convertible-tops.html\">convertible top replacement</a> page, or read "
            "<a href=\"blog-convertible-top-materials-compared.html\">how the materials "
            "compare</a>.",
        ],
    },
    {
        "slug": "blog-soft-top-replacement-jeep-miata.html",
        "cat": "Convertible Tops", "publish": "2026-08-12", "read": "5 min read",
        "photo": "g01-camaro-ss-new-convertible-top",
        "title": "Soft top replacement: how Jeeps and roadsters differ from a classic convertible",
        "seo_title": "Jeep and Miata Soft Top Replacement — What Differs | Auto Tops and Trim",
        "meta": "Soft tops on Jeeps and small roadsters are a different job from a classic "
                "convertible top. Window types, frames, fit and what to expect.",
        "excerpt": "A Jeep soft top and a classic convertible top share a name and almost "
                   "nothing else. Different frames, different windows, different failure modes.",
        "body": [
            "\"Soft top\" and \"convertible top\" get used interchangeably, but on a Jeep or a "
            "small roadster the job is genuinely different from re-topping a classic convertible.",
            "<h2>Jeep-style soft tops</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Zip-out windows.</strong> Large clear vinyl panels that unzip, which "
            "means zips are a wear item and often the first failure.</li>"
            "<li><strong>Frame-and-fabric rather than bow-and-pad.</strong> There are no pads in "
            "the traditional sense, so the classic collapsed-pad failure does not apply.</li>"
            "<li><strong>Designed to come off entirely.</strong> That means more fasteners, and "
            "more places for a top to be fitted slightly wrong.</li>"
            "<li><strong>Fit is tension-driven.</strong> A top that seems too small is usually "
            "cold, not wrong &mdash; these fit far more easily warm.</li>"
            "</ul>",
            "The most common complaint we hear is wind noise, and it is nearly always a fit or "
            "seal issue rather than a fabric one.",
            "<h2>Small roadsters</h2>",
            "Roadster tops are compact, tightly packaged and stack into a very small well. That "
            "creates two characteristic problems:",
            "<ul class=\"ticks\">"
            "<li>The rear window folds hard every time the top drops, so plastic curtains crack "
            "at the fold early. This is the single most common reason a roadster top gets "
            "replaced.</li>"
            "<li>Because the stack space is tight, fitting a heavier or thicker material than "
            "the car was designed for can stop the top stowing correctly.</li>"
            "</ul>",
            "Where the frame allows it, converting to a heated glass window is a genuine upgrade "
            "on these cars — it removes the failure mode entirely. Whether it is possible depends "
            "on the frame and the well, which is a question for the car being in front of us.",
            "<h2>What stays the same across all of them</h2>",
            "<ul class=\"ticks\">"
            "<li>Never fold a top that is wet or cold</li>"
            "<li>Rot-proof thread outlasts the fabric; ordinary thread does not</li>"
            "<li>A top fitted over a bent or seized frame will never sit right</li>"
            "<li>Ammonia-based glass cleaner clouds plastic windows</li>"
            "</ul>",
            "<h2>Bring it by</h2>",
            "Whether it is a Wrangler, a roadster or a classic, we quote the fabric, the window "
            "and the frame as three separate questions. Free in-person estimate at the shop in "
            "Monroe. See our <a href=\"convertible-tops.html\">convertible top replacement</a> "
            "page.",
        ],
    },
    {
        "slug": "blog-cracked-leather-seats.html",
        "cat": "Seats", "publish": "2026-08-12", "read": "5 min read",
        "photo": "g09-truck-cab-black-seat-red-stitch",
        "title": "Cracked leather seats: what conditioner can and cannot do",
        "seo_title": "Cracked Leather Car Seats: Can They Be Saved? | Auto Tops and Trim",
        "meta": "Why leather car seats crack, whether conditioner reverses it, and how to tell "
                "surface crazing from structural failure that needs a panel replaced.",
        "excerpt": "Conditioner prevents cracking. It does not reverse it. Knowing which stage "
                   "you are at decides whether you are maintaining or replacing.",
        "body": [
            "Cracked leather is the most common thing people ask us to fix and the one where "
            "expectations most often need managing. The short version: conditioner is prevention, "
            "not cure.",
            "<h2>Why automotive leather cracks</h2>",
            "Most modern automotive leather is finished — it has a pigmented topcoat over the "
            "hide. That coat is what you actually touch, and it is what cracks first.",
            "Heat cycles are the driver. A car interior in a Carolina summer swings through an "
            "enormous temperature range, the hide expands and contracts under a topcoat that "
            "moves differently, and eventually the coat crazes. UV accelerates all of it, which "
            "is why the driver's seat and anything near a window goes first.",
            "<h2>The three stages, and what each responds to</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Stage</th><th>What you see</th><th>What helps</th></tr></thead>"
            "<tbody>"
            "<tr><th>1. Drying</th><td>Dull, slightly stiff, no cracks yet</td>"
            "<td>Cleaning and conditioning genuinely works here. This is the stage worth acting "
            "in.</td></tr>"
            "<tr><th>2. Surface crazing</th><td>A fine web of lines in the topcoat; the hide "
            "underneath is intact</td>"
            "<td>Cleaning and recolouring can make a real difference. Conditioner alone will "
            "not remove the lines.</td></tr>"
            "<tr><th>3. Structural cracking</th><td>Cracks through to the hide, edges lifting, "
            "possibly splitting</td>"
            "<td>Nothing topical helps. The panel needs replacing.</td></tr>"
            "</tbody></table></div>",
            "<h2>The honest problem with filling cracks</h2>",
            "You can fill and recolour cracks, and immediately afterwards it looks good. The "
            "difficulty is that cracking means the whole panel has aged the same way. The filled "
            "cracks hold, and new ones appear alongside them, because the underlying condition "
            "was never addressed.",
            "That is why we tend to steer people towards replacing a panel rather than filling a "
            "badly cracked one — it is the difference between a repair and a subscription.",
            "<h2>What conditioner is actually for</h2>",
            "Conditioning a seat that has not cracked yet is genuinely worthwhile and cheap. "
            "Clean first — conditioner over dirt drives the dirt in — then condition, and do it "
            "before summer rather than after.",
            "Parking out of direct sun and using a sunshade does more for leather longevity than "
            "any product.",
            "<h2>Replacing one panel rather than a whole interior</h2>",
            "If the outer bolster of the driver's seat has failed and everything else is sound, "
            "that panel can be replaced on its own. Matching an aged interior is the hard part, "
            "and we will tell you honestly how close we expect to get before starting.",
            "Bring the vehicle, or the seat, to the shop in Monroe. More on our "
            "<a href=\"auto-upholstery.html\">automotive upholstery</a> page, or read our guide "
            "to <a href=\"blog-leather-car-seat-repair.html\">leather seat repair</a>.",
        ],
    },
    {
        "slug": "blog-seat-foam-replacement.html",
        "cat": "Seats", "publish": "2026-08-13", "read": "5 min read",
        "photo": "services-strip-3",
        "title": "Why your seat is uncomfortable: it is almost always the foam",
        "seo_title": "Car Seat Foam Replacement: Why Old Seats Sag | Auto Tops and Trim",
        "meta": "Sagging, lopsided or uncomfortable car seats are usually collapsed foam, not a "
                "worn cover. How foam fails and why recovering without replacing it disappoints.",
        "excerpt": "A seat that looks fine and feels wrong has a foam problem. Recovering it "
                   "without addressing that gives you a beautiful seat that is still uncomfortable.",
        "body": [
            "People come to us because a seat looks worn. They stay because we point out it also "
            "<em>feels</em> wrong, and the two have different causes.",
            "<h2>How seat foam fails</h2>",
            "Automotive seat foam is polyurethane, and it does not wear evenly. It compresses "
            "where the load is — the outer bolster you slide across, and the section under your "
            "hip — while the rest stays close to original.",
            "The result is a seat that has quietly changed shape. It tips you slightly to one "
            "side, it no longer supports under the thigh, and long drives become tiring in a way "
            "that is hard to point at.",
            "<h2>The tests</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Palm test.</strong> Press either side of the seat base with equal "
            "force. If one side sinks noticeably further, the foam has collapsed there.</li>"
            "<li><strong>Sit and look.</strong> Have someone check whether you sit level. A tilt "
            "you have grown used to is very common.</li>"
            "<li><strong>Edge test.</strong> Press the front edge of the base. It should resist. "
            "If it folds away, the section carrying the most load is gone.</li>"
            "<li><strong>Height test.</strong> If you are sitting lower than you used to, that is "
            "compression, not your imagination.</li>"
            "</ul>",
            "<h2>Why recovering alone disappoints</h2>",
            "A cover is cut to fit a shape. Stretch a new cover over collapsed foam and you get "
            "two problems: it looks slightly wrong because the shape underneath is wrong, and it "
            "wears out early in exactly the same place, because the cover is being stretched "
            "over a hollow.",
            "This is the most common reason someone is disappointed by an upholstery job that was "
            "technically well executed.",
            "<h2>Rebuild or replace</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Approach</th><th>When it fits</th></tr></thead><tbody>"
            "<tr><th>Rebuild the existing foam</th>"
            "<td>Localised collapse in an otherwise sound bun — the failed section is cut out "
            "and new foam built in and shaped back to profile</td></tr>"
            "<tr><th>Replace the foam entirely</th>"
            "<td>Widespread breakdown, or a classic where the original foam has crumbled. Often "
            "the only way to get the original shape back</td></tr>"
            "<tr><th>Replace and improve</th>"
            "<td>A driver you spend real time in. Modern multi-density foam supports better than "
            "much of what was fitted originally, and nobody sees it</td></tr>"
            "</tbody></table></div>",
            "<h2>Check the frame while it is open</h2>",
            "Foam does not collapse in isolation. Broken springs, failed webbing and cracked "
            "frames all show up as \"the seat feels wrong\", and they are only visible with the "
            "cover off. A cracked frame should be repaired properly, never shimmed.",
            "Bring the seat, or the vehicle, to the shop in Monroe. More on our "
            "<a href=\"auto-upholstery.html\">automotive upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-custom-interior-ideas.html",
        "cat": "Restoration", "publish": "2026-08-13", "read": "5 min read",
        "photo": "g19-mercedes-gla-interior-work",
        "title": "Custom interior ideas that still look right in ten years",
        "seo_title": "Custom Car Interior Ideas That Age Well | Auto Tops and Trim",
        "meta": "Stitch patterns, contrast thread, two-tone and material mixing — the custom "
                "interior choices that still look good years later, and the ones that date fast.",
        "excerpt": "Anything can be done. The useful question is which choices still look "
                   "deliberate in a decade and which look like the year they were made.",
        "body": [
            "Once someone decides to go custom rather than original, the options open up "
            "completely — and that is exactly when it helps to know which choices age well.",
            "<h2>Stitch patterns</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Diamond.</strong> The classic, and the one that has never really gone "
            "out. Works on almost anything from a hot rod to a bike seat.</li>"
            "<li><strong>Pleated.</strong> Straight vertical pleats. Period-correct on a great "
            "many classics and quietly timeless.</li>"
            "<li><strong>Biscuit.</strong> Square tufting. Strong period character &mdash; right "
            "at home on the correct car, out of place on the wrong one.</li>"
            "<li><strong>Plain with a feature seam.</strong> Understated, and the choice most "
            "likely to still look considered in ten years.</li>"
            "</ul>",
            "<h2>Contrast thread</h2>",
            "The cheapest way to change how an interior reads. Red stitch on black is the "
            "obvious one and it works because it is decisive.",
            "The thing worth knowing: contrast thread is unforgiving. Every stitch becomes "
            "visible, so line spacing and consistency have to be right. It costs very little in "
            "material and it is entirely about execution.",
            "<h2>Two-tone, done properly</h2>",
            "Two-tone works when the split follows the seat's own construction lines — insert "
            "one colour, bolsters another. It looks wrong when the split ignores the panels and "
            "cuts across them arbitrarily.",
            "The safest version is a strong colour on the inserts and something restrained on "
            "the parts you climb across, which also happens to be the parts that wear.",
            "<h2>Mixing materials</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Combination</th><th>Why it works</th></tr></thead><tbody>"
            "<tr><th>Leather bolsters, cloth inserts</th>"
            "<td>Leather where you slide across it, cloth where you sit &mdash; cooler in "
            "summer and grippier. This is what many manufacturers do, for good reason.</td></tr>"
            "<tr><th>Vinyl with a leather-look grain, cloth inserts</th>"
            "<td>Most of the appearance at a fraction of the cost, and very durable</td></tr>"
            "<tr><th>Suede-look inserts</th>"
            "<td>Excellent grip and a strong period feel &mdash; but check how it cleans before "
            "committing on a daily driver</td></tr>"
            "</tbody></table></div>",
            "<h2>What we would tell you to spend on</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Foam.</strong> Invisible, and it changes every drive.</li>"
            "<li><strong>Sound deadening under the carpet.</strong> The biggest single change to "
            "how an old car feels.</li>"
            "<li><strong>Execution over ambition.</strong> A simple interior done precisely beats "
            "an elaborate one done adequately, every time.</li>"
            "</ul>",
            "<h2>See it before you commit</h2>",
            "We keep samples in the shop and can lay materials and thread together on the bench "
            "before anything is cut. Most people change their mind at least once at that table, "
            "which is exactly why we do it in that order. See our "
            "<a href=\"auto-upholstery.html\">automotive upholstery</a> page, or read about "
            "<a href=\"blog-period-correct-or-upgraded-classic-interior.html\">period-correct "
            "versus upgraded interiors</a>.",
        ],
    },
    {
        "slug": "blog-motorcycle-seat-upholstery.html",
        "cat": "Motorcycle", "publish": "2026-08-13", "read": "5 min read",
        "photo": "custom-motorcycle-seat-upholstery-close-up",
        "title": "Motorcycle seat upholstery: recovering, reshaping and stitch work",
        "seo_title": "Motorcycle Seat Upholstery: Recover, Reshape, Restitch | Auto Tops and Trim",
        "meta": "Custom motorcycle seat upholstery — recovering worn seats, reshaping foam for "
                "comfort and height, pan repair and diamond stitch patterns.",
        "excerpt": "Bring the seat, not the bike. Most of what makes a motorcycle seat "
                   "comfortable happens in the foam, not the cover.",
        "body": [
            "Motorcycle seats are one of the most satisfying jobs in the shop, because the change "
            "is dramatic and the customer feels it on the first ride. They are also one of the "
            "easiest to arrange: take the seat off and bring it in. The bike stays home.",
            "<h2>Recovering</h2>",
            "A split or faded cover is the usual reason a seat arrives. The material has to "
            "handle sun, rain and constant abrasion, so it is closer to marine specification than "
            "automotive — UV-stable, and stitched with thread that will not rot.",
            "Water getting through a split cover is not only a comfort problem. Once the foam is "
            "wet it stays wet, and you are then sitting on a sponge for the rest of the season.",
            "<h2>Reshaping is where comfort actually comes from</h2>",
            "Most people ask for a new cover. What usually fixes the discomfort is the foam "
            "underneath it.",
            "<ul class=\"ticks\">"
            "<li><strong>Lowering.</strong> Removing foam and reshaping can drop seat height "
            "measurably &mdash; often the difference between tiptoes and flat feet at a stop.</li>"
            "<li><strong>Raising.</strong> Building the foam up opens the knee angle, which "
            "matters on a long ride.</li>"
            "<li><strong>Widening the sitting area.</strong> Many stock seats taper aggressively "
            "for looks. A little more width where you actually sit changes long-distance comfort "
            "more than any material.</li>"
            "<li><strong>Firmer or softer.</strong> Counter-intuitively, a firmer foam is usually "
            "more comfortable over distance; soft foam bottoms out and you end up on the pan.</li>"
            "</ul>",
            "<h2>The pan</h2>",
            "Under the foam is the pan — steel, aluminium or plastic. Cracks, rust and broken "
            "mounting tabs all need dealing with before anything goes on top. A seat that will "
            "not sit securely is a safety problem, not a comfort one.",
            "<h2>Stitch work</h2>",
            "Diamond is the classic and the most requested. Pleated, contrast thread and two-tone "
            "combinations are all straightforward. What is achievable depends partly on the pan "
            "shape — a heavily curved seat limits how large a diamond can sit flat without "
            "distorting.",
            "Bring a picture of what you want. We will tell you honestly what will work on your "
            "pan rather than promising it and discovering otherwise halfway through.",
            "<h2>How to get it done</h2>",
            "Take the seat off and bring it to the shop in Monroe. Free estimate, no obligation, "
            "and no need to leave the bike anywhere. See our "
            "<a href=\"motorcycle-seats.html\">motorcycle seats</a> page.",
        ],
    },
    {
        "slug": "blog-aircraft-interior-refurbishment.html",
        "cat": "Aviation", "publish": "2026-08-14", "read": "5 min read",
        "photo": "aircraft-cabin-upholstery-craftsmanship",
        "title": "Aircraft interior refurbishment: what makes it different from automotive",
        "seo_title": "Aircraft Interior Refurbishment and Upholstery | Auto Tops and Trim",
        "meta": "How aircraft interior upholstery differs from automotive work — weight, fit, "
                "finish standards and materials. A rare trade in the Charlotte region.",
        "excerpt": "It is the same craft held to a tighter tolerance — and a trade almost nobody "
                   "in this region offers.",
        "body": [
            "Aviation upholstery is the part of this shop that surprises people most. We have "
            "been trimming aircraft interiors alongside cars and boats for decades, and it is a "
            "rare enough trade regionally that owners routinely travel for it.",
            "<h2>What actually differs</h2>",
            "<h3>Weight</h3>",
            "Every ounce counts in a way it simply does not in a car. Material choice, foam "
            "density and how much structure goes into a panel are all constrained by weight in "
            "aviation work.",
            "<h3>Fit and finish tolerance</h3>",
            "The standard of finish is higher and the tolerances are tighter. In a cabin you are "
            "sitting inches from every surface, in good light, often for hours. There is nowhere "
            "for a slightly wandering seam to hide.",
            "<h3>Materials</h3>",
            "Aviation materials differ from automotive ones and are specified rather than chosen "
            "casually. This is a conversation to have before anything is cut, not after — and it "
            "is one where the owner's own requirements and any applicable approvals govern the "
            "choice.",
            "<h3>Consistency across the cabin</h3>",
            "A car interior is one space. A cabin is seats, side panels, headliner, carpet and "
            "trim that all have to read as a single finished environment. Doing one element in "
            "isolation tends to make the rest look tired.",
            "<h2>What the work covers</h2>",
            "<ul class=\"ticks\">"
            "<li>Cockpit and cabin seating, including foam replacement and reshaping</li>"
            "<li>Side panels and interior trim</li>"
            "<li>Cabin carpet and floor coverings</li>"
            "<li>Stitched detail work to a high finish</li>"
            "</ul>",
            "<h2>You can bring just the seats</h2>",
            "This is often the easiest way to do it, and it is what most owners choose. Remove "
            "the seats and bring them to the shop in Monroe. It avoids the aircraft being tied up "
            "and lets us do the work without a clock running on hangar space.",
            "<h2>Talk to us first</h2>",
            "Because materials and approvals matter more here than in automotive work, aviation "
            "jobs start with a conversation rather than a quote. Tell us what the aircraft is and "
            "what you want, and we will be straight about what we can and cannot do. See our "
            "<a href=\"aviation-upholstery.html\">aviation upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-best-way-to-clean-car-upholstery.html",
        "cat": "Interiors", "publish": "2026-08-14", "read": "5 min read",
        "photo": "g11-carpet-fitted-and-trimmed",
        "title": "The best way to clean car upholstery, by material",
        "seo_title": "Best Way to Clean Car Upholstery (Cloth, Vinyl, Leather)",
        "meta": "How to clean cloth, vinyl and leather car upholstery safely — the method per "
                "material, what causes permanent damage, and when a stain is not coming out.",
        "excerpt": "Cloth, vinyl and leather want three different approaches, and the one that "
                   "suits any of them will damage the other two.",
        "body": [
            "Almost all permanent interior damage we see from cleaning comes from one mistake: "
            "using a method suited to a different material. Work out what you have first.",
            "<h2>Cloth</h2>",
            "<ul class=\"ticks\">"
            "<li>Vacuum thoroughly first. Cleaning over grit grinds it into the weave.</li>"
            "<li>Use as little moisture as will do the job. Cloth sits on foam, and soaked foam "
            "takes days to dry and can go mouldy.</li>"
            "<li>Blot rather than scrub. Scrubbing distorts the pile and leaves a visible patch "
            "even once the stain is gone.</li>"
            "<li>Work the whole panel, not just the stain, or you get a clean spot that draws the "
            "eye as much as the mark did.</li>"
            "<li>Dry with the windows open or a fan running.</li>"
            "</ul>",
            "<h2>Vinyl</h2>",
            "The most forgiving of the three. Mild soap, warm water, soft cloth or brush; rinse "
            "and dry.",
            "What to avoid: solvents and harsh degreasers, which strip plasticisers and leave "
            "the vinyl hard and prone to cracking at the folds a season later. Also avoid "
            "silicone-heavy dressings that leave a slick, shiny surface — on a seat that is a "
            "genuine safety issue.",
            "<h2>Leather</h2>",
            "<ul class=\"ticks\">"
            "<li>Clean first with a dedicated leather cleaner. Conditioner over dirt drives the "
            "dirt in.</li>"
            "<li>Then condition. Little and often beats a heavy application once a year.</li>"
            "<li>Never use household all-purpose cleaner, and never use anything with bleach.</li>"
            "<li>Test on a hidden area &mdash; a rear seat base edge is ideal.</li>"
            "</ul>",
            "Note that most modern automotive leather is finished, so you are cleaning a "
            "pigmented topcoat rather than the hide. That is why aggressive products strip colour "
            "rather than just dirt.",
            "<h2>Universal rules</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Rule</th><th>Why</th></tr></thead><tbody>"
            "<tr><th>Never clean a hot interior</th><td>Product dries before it can be removed "
            "and bonds in</td></tr>"
            "<tr><th>Test somewhere hidden first</th><td>Colourfastness varies enormously, "
            "especially on older material</td></tr>"
            "<tr><th>Less water, more patience</th><td>Everything sits on foam; soaked foam is "
            "the real damage</td></tr>"
            "<tr><th>No bleach, anywhere</th><td>Attacks stitching thread long before it visibly "
            "harms the covering</td></tr>"
            "</tbody></table></div>",
            "<h2>When it is not coming out</h2>",
            "Dye transfer from clothing, old grease, and anything that has been heat-set by "
            "sitting in a hot car are all frequently permanent. So is a mark that has soaked "
            "through into the foam &mdash; you are treating the surface of something that is "
            "stained all the way down.",
            "At that point the honest options are a replacement panel or living with it, and we "
            "will tell you which rather than selling you a cleaning that will not work. See our "
            "<a href=\"auto-upholstery.html\">automotive upholstery</a> page.",
        ],
    },
    {
        "slug": "blog-how-to-reupholster-car-seats.html",
        "cat": "Seats", "publish": "2026-08-14", "read": "6 min read",
        "photo": "services-strip-1",
        "title": "How to reupholster car seats — and an honest look at doing it yourself",
        "seo_title": "How to Reupholster Car Seats: DIY vs a Trim Shop | Auto Tops and Trim",
        "meta": "What reupholstering a car seat actually involves step by step, which jobs are "
                "realistic at home, and where DIY attempts usually come unstuck.",
        "excerpt": "The sewing is not the hard part. Patterning and getting tension right are, "
                   "and that is where most home attempts go wrong.",
        "body": [
            "Plenty of people reupholster their own seats and get a decent result. Plenty of "
            "others start and bring us the pieces. The difference is rarely sewing skill — it is "
            "usually patterning and tension.",
            "<h2>What the job actually involves</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Remove the seat.</strong> Disconnect the battery first if there are "
            "airbags or sensors in it.</li>"
            "<li><strong>Strip the cover.</strong> Hog rings, clips and sometimes glue. Photograph "
            "everything as you go, from more angles than feel necessary.</li>"
            "<li><strong>Unpick the old cover.</strong> This is your pattern. Do not cut it "
            "apart — unpick the seams so each panel stays whole.</li>"
            "<li><strong>Assess foam and frame.</strong> With everything off, this is the only "
            "chance to fix what is underneath.</li>"
            "<li><strong>Cut new panels</strong> from the old ones, allowing for seams.</li>"
            "<li><strong>Sew.</strong> Upholstery-weight thread and a machine that will pull it "
            "through several layers plus foam backing.</li>"
            "<li><strong>Fit under tension.</strong> The cover has to go on tight and even, which "
            "is far harder than it looks.</li>"
            "</ul>",
            "<h2>Where home attempts usually come unstuck</h2>",
            "<div class=\"tablewrap\"><table class=\"spectable\">"
            "<thead><tr><th>Problem</th><th>What happens</th></tr></thead><tbody>"
            "<tr><th>Cutting the old cover apart instead of unpicking</th>"
            "<td>You have destroyed your only accurate pattern</td></tr>"
            "<tr><th>Domestic sewing machine</th>"
            "<td>Will not reliably pull upholstery thread through multiple layers; skipped "
            "stitches become split seams later</td></tr>"
            "<tr><th>Ignoring the foam</th>"
            "<td>A perfect cover over a collapsed bun looks wrong and wears out early in the "
            "same place</td></tr>"
            "<tr><th>Uneven tension on fitting</th>"
            "<td>Wrinkles that never settle, and stress concentrated where it will tear</td></tr>"
            "<tr><th>Wrong thread</th>"
            "<td>The seams fail while the material is still fine</td></tr>"
            "</tbody></table></div>",
            "<h2>Which jobs are realistic at home</h2>",
            "<ul class=\"ticks\">"
            "<li><strong>Reasonable:</strong> a flat bench seat with few panels, a simple "
            "cushion, or a pre-made cover kit for a common vehicle</li>"
            "<li><strong>Difficult:</strong> contoured buckets with bolsters, anything with "
            "piping, and any pattern work</li>"
            "<li><strong>Leave it alone:</strong> seats with airbags in the bolster. The cover "
            "is part of a safety system, the seam is designed to burst in a specific way, and "
            "getting it wrong has consequences beyond appearance.</li>"
            "</ul>",
            "<h2>If you are going to try it</h2>",
            "Start with a rear seat rather than the driver's. It is simpler, less visible, and "
            "you will have learned a great deal by the time you reach the seat everybody looks "
            "at. Photograph everything. Label every piece as you unpick it.",
            "<h2>What we do differently</h2>",
            "We pattern from the old cover, replace foam that has collapsed rather than "
            "trimming over it, repair frames properly instead of shimming them, and fit under "
            "even tension with the right thread for the material. On a classic we chase correct "
            "grain, stitch spacing and weave.",
            "And if you have already started and it has gone sideways, bring us the pieces — that "
            "is a more common phone call than you would think, and it is not a problem. Free "
            "in-person estimate at the shop in Monroe. See our "
            "<a href=\"auto-upholstery.html\">automotive upholstery</a> page.",
        ],
    },
]


def _today():
    """Build date in UTC, overridable with BUILD_DATE=YYYY-MM-DD for previewing.

    Set BUILD_DATE to a future date to see exactly what the site will look like
    when a scheduled post goes out, without touching any publish date.
    """
    override = os.environ.get("BUILD_DATE", "").strip()
    if override:
        return datetime.date.fromisoformat(override)
    return datetime.datetime.now(datetime.timezone.utc).date()


def visible_posts():
    """Posts whose publish date has arrived, newest first.

    Raises on a missing or malformed `publish` rather than guessing — a post that
    silently defaults to "now" would go live the moment it is merged, which is
    the exact failure this gate exists to prevent.
    """
    today = _today()
    out = []
    for po in POSTS:
        if "publish" not in po:
            raise KeyError(f"post {po['slug']} has no `publish` date")
        when = datetime.date.fromisoformat(po["publish"])
        if when <= today:
            out.append((when, po))
    out.sort(key=lambda pair: pair[0], reverse=True)
    return [po for _, po in out]


def post_date_label(po):
    """Displayed date, always derived from `publish` so the two cannot drift."""
    return datetime.date.fromisoformat(po["publish"]).strftime("%B %Y")


def build_blog():
    _lb_reset()
    live = visible_posts()
    scheduled = len(POSTS) - len(live)
    if scheduled:
        nxt = min(p["publish"] for p in POSTS if p not in live)
        print(f"   blog: {len(live)} live, {scheduled} scheduled (next {nxt})")

    # Remove output for any post that is no longer live. The gate keeps unpublished
    # posts out of blog.html and sitemap.xml, but a file already on disk would stay
    # reachable by direct URL if a publish date were ever pushed back. Scoped to
    # slugs declared in POSTS so it can never touch a hand-managed page.
    for po in POSTS:
        if po not in live:
            stale = os.path.join(OUT, po["slug"])
            if os.path.exists(stale):
                os.remove(stale)
                print(f"   blog: withdrew {po['slug']} (publishes {po['publish']})")
    p = "blog.html"
    h = head("Blog | Auto Tops and Trim, Monroe NC",
             "Advice on convertible tops, marine upholstery and classic interiors from a "
             "Monroe, NC upholstery shop trimming interiors since 1989.", p)
    h += header(p)
    cards = "".join(f"""<a class="card" href="{po['slug']}">
      {img(po['photo'], po['title'], THIRD, ratio='16/10')}
      <div class="card-body"><span class="meta">{po['cat']} &middot; {post_date_label(po)} &middot; {po['read']}</span>
      <h3>{po['title']}</h3><p>{po['excerpt']}</p>
      <span class="card-link">Read the article</span></div></a>""" for po in live)
    h += f"""<section class="band">
  <div class="wrap stack">
    <div class="stack">{shead("01","Blog")}<h1>Notes from the shop</h1>
      <p class="lead">Straight answers to the questions we get asked most often.</p></div>
    <div class="grid g3 swiperow">{cards}</div>
  </div>
</section>
"""
    h += cta()
    h += footer(lightbox_markup())
    pages.append(p)
    write(p, h)

    for po in live:
        schema = {
            "@context": "https://schema.org", "@type": "Article",
            "headline": po["title"], "description": po["excerpt"],
            "datePublished": po["publish"],
            "author": {"@type": "Organization", "name": "Auto Tops and Trim"},
            "publisher": {"@type": "Organization", "name": "Auto Tops and Trim"},
            "mainEntityOfPage": SITE + public_path(po["slug"]),
        }
        # `seo_title` and `meta` let the search-result listing target its keyword
        # while the on-page H1 stays readable. Both fall back to the H1/excerpt.
        ph = head(po.get("seo_title") or f"{po['title']} | Auto Tops and Trim",
                  po.get("meta") or po["excerpt"], po["slug"], schema)
        ph += header("blog.html")
        # A body entry starting with "<" is emitted as-is, so posts can carry
        # H2s, lists and internal links instead of an undifferentiated wall of
        # paragraphs. Anything else is treated as prose and wrapped.
        body = "".join(t if t.lstrip().startswith("<") else f"<p>{t}</p>"
                       for t in po["body"])
        ph += f"""<section class="band">
  <div class="wrap">
    <div class="article-head">
      <span class="meta">{po['cat']} &middot; {post_date_label(po)} &middot; {po['read']}</span>
      <h1>{po['title']}</h1>
      <p class="lead">{po['excerpt']}</p>
    </div>
    <figure class="article-figure">{img(po['photo'], po['title'], "(min-width:1000px) 940px, 100vw", eager=True)}</figure>
    <article class="article">
      {body}
      <p style="margin-top:1.6em"><a href="blog.html">&larr; All articles</a></p>
    </article>
  </div>
</section>
"""
        ph += cta()
        ph += footer()
        pages.append(po["slug"])
        write(po["slug"], ph)


# ============================================================== SITEMAP / ROBOTS
def build_meta():
    _lb_reset()
    # Clean URLs here too — a sitemap listing .html would hand Google a list of
    # URLs that all redirect, and the canonicals point elsewhere.
    urls = "".join(
        f"<url><loc>{SITE}{public_path(pg)}</loc>"
        f"<changefreq>monthly</changefreq>"
        f"<priority>{'1.0' if pg == 'index.html' else '0.8'}</priority></url>"
        for pg in pages)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          f"{urls}</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    build_home()
    build_services_index()
    build_services()
    build_gallery()
    build_process()
    build_about()
    build_contact()
    build_blog()
    build_meta()
    print(f"pages written: {len(pages)}")
    for pg in pages:
        print("  ", pg)
