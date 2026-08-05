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
        "gallery-header-photo-wide",
        "g19-mercedes-gla-interior-work",
        "g18-camaro-ss-profile",
    ]
    n_slides = len(hero_slides)
    slides = "".join(
        f'<figure style="animation-delay:{i * (20 / n_slides):.1f}s">'
        f'{img(b, "Upholstery work by Auto Tops and Trim in Monroe, NC", "(min-width:900px) 52vw, 100vw", eager=(i == 0), priority=(i == 0))}'
        f"</figure>"
        for i, b in enumerate(hero_slides)
    )
    dots = "".join(f'<span style="animation-delay:{i * (20 / n_slides):.1f}s"></span>'
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
      <p class="microline">Free estimates &nbsp;&middot;&nbsp; In-person quotes &nbsp;&middot;&nbsp; Union County</p>
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
          "We would rather not, and it is in your interest too. A photo cannot show collapsed "
          "pads or bent bows, and a new top fitted over a bad frame will never sit right. Bring "
          "the car by and we will walk it with you."),
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
                                 "Quoted in person, free of charge"]),
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
          "We would rather see it. A photo will not show whether the slider and the mechanism are "
          "still sound, and that is the part that decides whether this is a simple recover or a "
          "bigger job. The estimate is free either way.")],
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
       Every job is quoted in person and free of charge.</p>
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
    ("marine-seating-and-interior-upholstery", "Runabout — cockpit seating and helm trim", "Marine"),
    ("boat-upholstery-projects-at-the-shop", "Boat in for upholstery at the shop", "Marine"),
    ("aircraft-interior-seat-upholstery", "Aircraft cabin seating", "Aviation"),
    ("aircraft-cabin-upholstery-craftsmanship", "Aircraft cabin — divan and club seat", "Aviation"),
    ("custom-motorcycle-seat-upholstery-close-up", "Diamond-stitched motorcycle seat", "Motorcycle"),
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
        ("Free, and itemised", "We quote in person",
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
    <p class="lead">That is also why we quote in person. A photograph cannot show a bent bow
       or a rusted seat frame, and a number given without seeing those is not a real number.</p>
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
      <div class="stat"><b>Free</b><span>In-person estimates</span></div>
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
         "5:30, and Saturday 11:00 to 5:00. Calling ahead on "
         f"{PHONE_DISPLAY} is worth doing, because it means someone is free to come out and "
         "look at the job properly rather than between other work."),
        ("What does an estimate cost?",
         "Nothing. Estimates are free and given in person, and they are itemised so you can see "
         "what each part of the job costs rather than one number at the bottom."),
        ("Why will you not quote from a photo?",
         "Because a photo cannot show the things that decide the price. Collapsed pads, a bent "
         "bow, a rusted seat frame, foam that has gone hard &mdash; none of that is visible in a "
         "picture, and a number given without seeing it is not a real number. It protects you as "
         "much as us."),
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
             "request a free upholstery estimate. Open Mon-Fri 9:00-5:30 and Saturday 11:00-5:00.",
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
              <tr><th>Mon &ndash; Fri</th><td>9:00 AM &ndash; 5:30 PM</td></tr>
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
            "<h2>Why we will not quote a convertible top from a photo</h2>",
            "A photograph cannot show a collapsed pad or a bent bow. It cannot show you where the "
            "old top was stretched to cover a frame problem someone chose not to fix. Quoting from "
            "a picture means either guessing high to stay safe, or guessing low and revising the "
            "number once the car is apart. Neither is fair to you.",
            "That is why every estimate here is done in person, in the shop, with the car in front "
            "of us — and why it is free and itemised, so you can see which of the three jobs above "
            "each line belongs to.",
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
                "sunroof, trim removal, material and hidden damage. Free in-person estimates.",
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
            "<h2>Why we will not quote this from a photo</h2>",
            "A photo of a sagging headliner tells us the fabric has let go. It cannot tell us "
            "whether the board is sound, whether there is a sunroof shade behind it, or how much "
            "trim has to come out on your particular vehicle — and those are the three things "
            "that set the price.",
            "Bring the vehicle to the shop in Monroe and you will get an itemised estimate, in "
            "person, at no cost, with each of the five items above priced separately so you can "
            "see what you are paying for.",
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
