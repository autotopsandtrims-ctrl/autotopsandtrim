"""Page content for autotopsandtrim.com. Run this to emit the whole site."""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_site import (  # noqa: E402
    IMAGES, SITE, PHONE_DISPLAY, PHONE_TEL, EMAIL, OUT, REPLY_PROMISE,
    img, has, head, header, footer, cta, shead, quote_form, write, NAV, SERVICES, SCHEMA,
    preload_image, public_path, PAUSED_SERVICES, THANKS_PAGE,
)
from build_landing import landing_page  # noqa: E402

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
    # The `reviews` class exists ONLY so the quilt override in site.css can
    # target this band. The user had the desktop quilt turned up sitewide on
    # 2026-08-09, disliked it, and asked for it back down everywhere except
    # the reviews section - so this is the one dark band that keeps .030.
    return f"""<section class="band dark reviews">
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
# The fanned deck. Five cards, alternating real shop work with the three trades
# this band is about, so the deck reads as "and all of this too" rather than as
# three lonely stock photos. Order matters: it is the left-to-right order of the
# fan. No links and no captions — see also_band().
# BOATS, AIRCRAFT AND BIKES ONLY. No cars in this deck — the whole rest of the
# site is cars, and a car here makes the band say nothing. Two marine (both real
# shop photographs), two aviation, one motorcycle.
#
# ⚠️ EVERY CARD IN THIS DECK MUST BE FINISHED WORK OR A CLEAN SUBJECT. The cards
# carry no captions by design, so a damaged piece here reads as the shop's output
# rather than as its intake. That is what removed `boat-helm-seat-white` on
# 2026-08-09 (user's call): it is a BEFORE photo — cracked, stained vinyl with a
# mismatched tan bottom cushion — and it sat on the far right of the fan with
# nothing saying so. It is still used where a caption gives it that context: the
# gallery, the marine page strip and the mildew blog post.
#
# The card count is load-bearing: `.also-col:nth-child(N)` in site.css sets the
# arc, and there is a five-card override that keeps the fan symmetric. Change the
# length of this list and the arc has to be retuned to match.
ALSO = [
    ("boat-on-the-trailer-at-the-shop", "Marine", ""),
    ("boat-cockpit-cream-and-grey", "Marine", ""),
    # NOT aircraft-cabin-upholstery-craftsmanship as the big one: that master is
    # 396x298. It is fine at this card size but this one is 1800x1201.
    ("aircraft-interior-seat-upholstery", "Aviation", ""),
    ("custom-motorcycle-seat-upholstery-close-up", "Motorcycle", ""),
    ("aircraft-cabin-upholstery-craftsmanship", "Aviation", ""),
]


def also_band(label="We also work on",
              heading="Boats, aircraft and bikes come through here too",
              lead="Boat seating, cushions, helm trim and canvas in materials chosen for "
                   "sun and standing water; cockpit and cabin interiors for aircraft; and "
                   "motorcycle seats recovered or reshaped for comfort. Same shop, same "
                   "hands, same free estimate.",
              tone=""):
    """The three secondary trades as a row of photographs.

    NOT LINKS AND NOT CLICKABLE, on the user's instruction 2026-08-07: the tiles
    are there to show the range of the shop, not to send anyone off the page.
    The three pages are still reachable from the footer's Services list.

    ⚠️ These three photographs are the unverified stock images. They were taken
    off the gallery and off every service page in the restructure because nothing
    ties them to this shop, and 283 photographs of real work contain no aviation
    and no motorcycle. They were put back HERE, decoratively, on the user's
    explicit instruction. Nothing in this band claims they are the shop's own
    jobs — no captions, no "recent work" heading, no lightbox.

    Unnumbered on purpose: every other band carries a section number, so an
    unnumbered one reads as secondary, which is what this band is.

    THIS BAND SURVIVES THE PAUSE, on the user's call 2026-08-09. Marine, aviation
    and motorcycle are in PAUSED_SERVICES — unlinked from the footer, noindexed
    and out of the sitemap — but this band stays exactly as it is, because it
    shows the shop still DOES that work. That is not a contradiction: the tiles
    are not links, so nothing here promotes a paused page or sends a visitor to
    one. What is paused is the SELECTION; what stays is the evidence of range.

    So do not "tidy" this by filtering it against PAUSED_SERVICES. That was tried
    on 2026-08-09 and reverted the same day.

    ⚠️ The card count is load-bearing — `.also-col:nth-child(N)` in site.css sets
    the arc and there is a five-card override, so all five tiles have to stay
    together or the fan needs retuning.
    """
    cols = "".join(
        f'<figure class="also-col">{img(photo, "", QUARTER)}'
        f'<figcaption><span class="also-cat">{cat}</span>'
        f'<span class="line">{line}</span></figcaption></figure>'
        for photo, cat, line in ALSO)
    # Centred heading, because the deck under it is centred. A left-aligned
    # heading over a centred row is the kind of mismatch that makes a page look
    # unfinished.
    return f"""<section class="band{f' {tone}' if tone else ''}" id="also">
  <div class="wrap stack">
    <div class="center stack">{shead("", label, center=True)}<h2>{heading}</h2>
      {f'<p class="lead">{lead}</p>' if lead else ''}</div>
    <div class="also">{cols}</div>
  </div>
</section>
"""


# (before, after, label). EVERY PAIR IS ONE JOB ON ONE VEHICLE, confirmed by
# opening both photographs and matching the car — same colour, same wheels, same
# bay. A "before and after" that is actually two different cars is worse than no
# before and after at all, so a pair that could not be confirmed was left out.
PAIRS = [
    # AFTER is the in-the-bay shot, not the rear-quarter one: the rear quarter is
    # the home page's vinyl card, and nothing on that page is shown twice. It is
    # also the better match — both frames are the whole roof, from the same side.
    ("vinyl-top-before-roof-covering-rotted", "vinyl-top-burgundy-finished-in-the-bay",
     "Vinyl top"),
    ("shot-087-old-black-top-faded", "shot-089-new-black-top-side",
     "Convertible top"),
    # supplied 2026-08-08 in the BEFORE AFTER folder, as matched pairs: `b`/`b2`
    # are the before shots, `a`/`a2` the after. These replaced the last two pairs.
    ("ba-seats-before-torn-buckets", "ba-seats-after-recovered-buckets",
     "Bucket seats"),
    ("ba-galaxie-before-frame-and-material", "ba-galaxie-after-new-top-fitted",
     "Convertible top"),
    ("shot-194-frame-and-weatherstrip", "shot-195-brown-top-on-white-car",
     "Convertible top"),
]


def pair_deck(pairs, label="Before and after", num="",
              heading="The same job, twice",
              lead="", tone="tint"):
    """Before/after cards: the two photographs SIDE BY SIDE, before left.

    Left-to-right, not stacked — that is how anyone reads a before and after,
    and stacking three of them made a very tall column on a phone. Each pair is
    one card: two photos butted together with a hairline between them and a small
    arrow sitting on the join, so the card reads as one comparison rather than
    two pictures. Deliberately NOT the fan used by the deck above — these are
    meant to be compared, and overlapping cards fight that.
    """
    cards = ""
    for before, after, cap in pairs:
        if not (has(before) and has(after)):
            continue
        cards += (
            f'<figure class="pair"><span class="pair-shots">'
            f'<span class="pair-shot"><span class="pair-tag">Before</span>'
            f'{img(before, f"{cap} before", QUARTER)}</span>'
            f'<span class="pair-shot"><span class="pair-tag after">After</span>'
            f'{img(after, f"{cap} after", QUARTER)}</span>'
            f'<span class="pair-arrow" aria-hidden="true">&rarr;</span>'
            f'</span><figcaption>{cap}</figcaption></figure>')
    return f"""<section class="band{f' {tone}' if tone else ''}" id="before-after">
  <div class="wrap stack">
    <div class="center stack">{shead(num, label, center=True)}<h2>{heading}</h2>
      {f'<p class="lead">{lead}</p>' if lead else ''}</div>
    <div class="pairs">{cards}</div>
  </div>
</section>
"""


def build_before_after():
    _lb_reset()
    p = "before-after.html"
    h = head("Before and After | Auto Tops and Trim, Monroe NC",
             "Before and after photographs of real jobs out of the Monroe, NC shop — "
             "convertible tops, vinyl tops, seats and interiors. Free estimates.", p)
    h += header("gallery.html")
    h += f"""<section class="band" style="padding-bottom:0">
  <div class="wrap center stack">
    {shead("01", "Before and after", center=True)}
    <h1>What these cars looked like when they arrived</h1>
    <p class="lead">Every pair below is one job on one vehicle, photographed on the way
       in and on the way out.</p>
  </div>
</section>
"""
    h += pair_deck(PAIRS, num="02", label="The jobs",
                   heading="Five jobs, start to finish", tone="")
    h += cta(num="03", label="Yours next",
             heading="Bring us the one you are embarrassed about",
             sub="The worse it looks now, the better the second photograph is. Free, "
                 "itemised estimates, from your photos or in person.")
    h += footer(lightbox_markup())
    pages.append(p)
    write(p, h)


def build_home():
    _lb_reset()
    p = "index.html"
    h = head(
        "Auto Tops and Trim | Custom Upholstery in Monroe, NC Since 1989",
        "Custom upholstery in Monroe, NC since 1989. Convertible tops, vinyl tops, "
        "sunroofs and vehicle interiors. Free estimates — call (980) 385-8101.", p,
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
        # BACK as slide 2 on 2026-08-08. It had moved to the Vehicle Interiors
        # card while that card had nothing better; the card now carries the red
        # pickup interior, so this is free to return to the hero where the owner
        # put it originally.
        "convertible-red-vinyl-interior-full",
        "gallery-header-photo-wide",
        # owner-supplied: red pickup cab, black seat, new carpet.
        # Portrait 0.75, same ratio as the portrait slide it replaces.
        "red-pickup-cab-black-seat-and-carpet",
    ]
    n_slides = len(hero_slides)
    # Must equal the `slidefade` / `doton` durations in assets/site.css. Two
    # seconds a slide across four slides = an 8s cycle. If you change the count,
    # change the CSS duration AND the keyframe percentages too, or the dots drift
    # out of step with the photos.
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
      <p class="lead">Convertible tops, vinyl tops, sunroofs and vehicle interiors
        &mdash; handcrafted in Monroe since 1989.</p>
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
    <!-- The four names off the owner's business card, in his order: convertible
         tops, vinyl tops, sunroofs, vehicle interiors. Blurbs stay one short
         sentence each, the length the original cards ran at — these tiles are
         photo cards, not paragraphs. -->
    <div class="bento">
      <a class="pcard" href="convertible-tops.html">
        {img('automotive-ford-galaxie-top-after', 'Convertible top fitted to a classic Ford', HALF)}
        <span class="cat">Convertible tops</span>
        <div class="pbody"><h3>Convertible Tops</h3>
          <p>Vinyl and canvas tops, heated glass and plastic windows, and the frame
             underneath.</p>
          <span class="go">See the work</span></div>
      </a>
      <a class="pcard" href="vinyl-tops.html">
        {img('vinyl-top-after-burgundy-fitted', 'A new burgundy vinyl top fitted over the roof and rear quarter', HALF)}
        <span class="cat">Vinyl tops</span>
        <div class="pbody"><h3>Vinyl Tops</h3>
          <p>Rotted, peeling or faded roof coverings stripped back and re-covered.</p>
          <span class="go">See the work</span></div>
      </a>
      <a class="pcard" href="auto-upholstery.html">
        {img('interior-red-truck-burgundy-seat', 'Burgundy interior fitted in a red pickup', HALF)}
        <span class="cat">Vehicle interiors</span>
        <div class="pbody"><h3>Vehicle Interiors</h3>
          <p>Custom upholstery, headliners, carpet replacement and full interior
             restorations.</p>
          <span class="go">See the work</span></div>
      </a>
      <a class="pcard" href="sunroof-shade-repair.html">
        {img('sunroof-glass-open-in-the-shop', 'A sunroof open on a car in the shop', HALF)}
        <span class="cat">Sunroofs</span>
        <div class="pbody"><h3>Sunroofs</h3>
          <p>Sagging, torn or stuck sliding sunshades recovered, not replaced.</p>
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
    <!-- REFRESHED 2026-08-11 with the owner's own photographs, mixing convertible
         tops and interiors so the strip shows range rather than one kind of job.
         Eight tiles became twelve.

         THE TALL/WIDE RHYTHM IS STILL LOAD-BEARING — see the note above. Only two
         photographs in the entire new set are landscape (au-shop-10 and
         au-shop-11, both 0.75); everything else the owner sent is 1.33 portrait.
         So positions 2 and 5 MUST stay landscape or the columns unbalance and the
         gap comes back. Position 5 keeps the 1969 Cadillac for exactly that
         reason — using both new landscapes at 2 and 5 would have put two similar
         red interiors opposite each other. -->
    <div class="masonry">{masonry_tiles([
        ('ct-shop-04', 'Blue classic convertible — new black top', 'Convertible tops'),
        ('au-shop-10', 'Convertible interior recovered in red', 'Interiors'),
        ('au-shop-03', 'Tan quilted leather seats and door cards', 'Interiors'),
        ('ct-shop-07', 'Camaro — tan top on black with yellow stripes', 'Convertible tops'),
        ('g15-1969-cadillac-profile', '1969 Cadillac — profile', 'Automotive'),
        ('au-shop-12', 'Bench seat in black with blue accent panels', 'Interiors'),
        ('ct-shop-01', 'Burgundy top on a cream classic', 'Convertible tops'),
        ('au-shop-04', 'Black and magenta bucket seats', 'Interiors'),
        ('ct-shop-11', 'Corvette — new black top', 'Convertible tops'),
        ('au-shop-14', 'Modern truck cab retrimmed', 'Interiors'),
        ('ct-shop-08', 'Camaro convertible — new black top', 'Convertible tops'),
        ('au-shop-17', 'Bench seat with red and blue piping', 'Interiors'),
    ])}</div>
    <div class="btnrow" style="justify-content:center"><a class="btn btn-ghost" href="gallery.html">See the full gallery</a></div>
  </div>
</section>

{pair_deck(PAIRS[:4], label="Before and after",
           heading="The same job, twice",
           lead="Four cars, photographed on the way in and on the way out.",
           tone="")}
{also_band(tone="tint")}
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
def ba_band(steps, num="02", label="Before and after",
            heading="One roof, start to finish", lead=""):
    """A staged before → during → after strip. Same lightbox as the masonry.

    `steps` is [(basename, stage, caption)]. Stage is the chip printed over the
    photo ("Before", "Stripped", "After") — it is the whole point of the band, so
    it is a separate field rather than something buried in the caption text.
    Photos are cropped to a common ratio here, unlike the masonry, because three
    portrait shots at their natural heights read as three unrelated pictures
    instead of one sequence.
    """
    figs = ""
    for base, stage, caption in steps:
        if not has(base):
            continue
        lb = _lb_add(base, caption, stage)
        figs += (f'<figure><a class="lb-open" href="#{lb}">'
                 f'<span class="ba-stage">{stage}</span>'
                 f'{img(base, caption, THIRD)}'
                 f'<figcaption>{caption}</figcaption></a></figure>')
    return f"""<section class="band tint" id="before-after">
  <div class="wrap stack">
    <div class="stack">{shead(num, label)}<h2>{heading}</h2>
      {f'<p class="lead">{lead}</p>' if lead else ''}</div>
    <div class="ba">{figs}</div>
  </div>
</section>
"""


def service_page(slug, title, desc, eyebrow, h1, intro, hero_photo, sections,
                 photos, faqs, gallery_caps=None, extra_html="", lead_html=""):
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
    # Anything that has to sit ABOVE the photo strip and the FAQ — the vinyl-top
    # before/after sequence, for one. `extra_html` lands after the FAQ, which is
    # too far down for evidence this strong.
    #
    # Section numbers are counted, not hard-coded: a page carrying a lead band
    # runs 02 / 03 / 04, and one without it still runs 02 / 03 exactly as before.
    # The lead band numbers itself (it is built by the caller), so the counter
    # only has to know that it took a number. It also owns the tint, so the strip
    # below it goes white — two tinted bands back to back read as one.
    n = 2
    if lead_html:
        h += lead_html
        n += 1
    if photos:
        caps = gallery_caps or [""] * len(photos)
        # Same masonry + click-to-enlarge treatment as the home page recent-work
        # block, so photo sections read consistently across the site.
        tiles = masonry_tiles([(ph, cap or h1, eyebrow)
                               for ph, cap in zip(photos, caps)])
        h += f"""<section class="band{'' if lead_html else ' tint'}" id="recent-work">
  <div class="wrap stack">
    <div class="stack">{shead(f"{n:02d}","Recent work")}<h2>Jobs out of this shop</h2></div>
    <div class="masonry svc-shots">{tiles}</div>
    <div class="btnrow" style="justify-content:center"><a class="btn btn-ghost" href="gallery.html">See the full gallery</a></div>
  </div>
</section>
"""
    if photos:
        n += 1
    if faqs:
        items = "".join(
            f"<details><summary>{q}</summary><div class='ans'>{a}</div></details>"
            for q, a in faqs
        )
        h += f"""<section class="band{' tint' if lead_html else ''}">
  <div class="wrap narrow stack">
    <div class="stack">{shead(f"{n:02d}","Frequently asked questions")}<h2>Answers before you call</h2></div>
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

    # VINYL TOPS — new 2026-08-07 with the services restructure. It is the second
    # item on the owner's business card and the site had no page for it at all.
    #
    # CAPTIONS: written from opening all five photos at full size, not from their
    # filenames. Two cars are involved, not one — the burgundy job (rotted →
    # stripped → fitted) is a cream sedan; the peeling-at-the-rear shot is a
    # different, pale blue car. Nothing here names a make or a model year: the
    # thumbnails those filenames came off have already been wrong twice.
    #
    # The finished covering photographs as a matte, cloth-grained material, so
    # the copy and the captions say "top" and never "vinyl" about THAT car. The
    # service is vinyl and padded tops; the photos are not used to claim a
    # material nobody has confirmed.

    # ------------------------------------------------------------------
    # auto-upholstery.html and headliner-replacement.html are NOT built here.
    #
    # Both are paid-search landing pages now, built by build_landings() from
    # the landing_page() type in build_landing.py — the `_draft-headliner.html`
    # layout the user approved at DRAFT v15. They keep their existing URLs,
    # their <title>s, their FAQ copy and their place in SERVICES and the nav;
    # only the body layout changed. Git history holds the service_page() calls
    # they replaced.
    #
    # If either page ever needs to go back to being an ordinary service page,
    # move it out of LANDINGS in build_landings() rather than adding a second
    # writer here — two builders for one slug means last-one-wins and a
    # duplicate entry in sitemap.xml.
    # ------------------------------------------------------------------
    # convertible-tops.html, vinyl-tops.html and sunroof-shade-repair.html are
    # NOT built here either — all three are paid landing pages now, built by
    # build_landings(). Same reasoning as the note above.
    #
    # The sunroof page CHANGED SCOPE when it converted. It was shade-only; the
    # owner interview established he does the whole unit — cables, motors,
    # tracks, drains — and refits the original. It is still NOT sunroof
    # installation, which he declines and which is negated campaign-wide.

    service_page(
        "marine-upholstery.html",
        "Marine Upholstery in Monroe, NC | Boat Seats and Canvas",
        "Marine upholstery near Charlotte, NC. Boat seating, helm trim, cushions and canvas "
        "in UV-stabilised marine vinyl. Free estimates — (980) 385-8101.",
        "Marine upholstery", "Boat seating, cushions and canvas",
        "Leather belongs in a car, not on the water. For marine work we specify materials "
        "built for standing water, UV and salt.",
        # Was `marine-seating-and-interior-upholstery` — a varnished-wood runabout
        # cockpit that reads as commercial photography and carries nothing tying it
        # to this shop. 283 photographs of real work confirmed it was never ours.
        # Real marine work, imported 2026-08-07: a boat cockpit at 3024x4032.
        # The old hero (shop-with-a-boat-outside) was a 297x396 master.
        "boat-cockpit-cream-and-grey",
        [("Seating and cushions", ["UV-stabilised, mildew-resistant marine vinyl",
                                   "Quick-dry reticulated foam that passes water through",
                                   "Thread that will not rot", "Helm and console trim"]),
         ("Canvas", ["Solution-dyed acrylic holds colour in full sun",
                     "Covers, tops and enclosures",
                     "The difference shows in year three, not year one"]),
         ("Bring one piece", ["We will tell you honestly whether it needs recovering or replacing",
                              "No charge to look"])],
        # This strip previously showed the OLD hero twice more under two other
        # filenames, plus `marine-canvas-cushions`, which is a car interior. The
        # boat-on-a-trailer shot moved up to the hero, so one honest tile is left.
        ["boat-helm-seat-white", "boat-upholstery-projects-at-the-shop",
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
        ["Helm seat off a boat, in for recovering",
         "Boat in for upholstery at the shop", "Project parts on the shop bench"])

    service_page(
        "aviation-upholstery.html",
        "Aviation Upholstery in Monroe, NC | Aircraft Cabin and Cockpit Interiors",
        "Aircraft interior upholstery in Monroe, NC. Cockpit and cabin seating, panels and "
        "trim, finished to a high standard. Free estimates — (980) 385-8101.",
        "Aviation upholstery", "Aircraft cabin and cockpit interiors",
        "A rare trade in this region. We have been trimming aircraft interiors alongside "
        "cars and boats for decades.",
        # NO HERO PHOTO, deliberately. Both aviation images on this site were
        # unverified stock — cream quilted cabin seats and a private-jet interior —
        # and 283 photographs of the shop's real work contain no aircraft at all.
        # A text-only hero is honest and reads as designed; an empty frame does not.
        # This becomes an ordinary hero the day the shop supplies a real photograph.
        None,
        [("Seating", ["Cockpit and cabin seats", "Foam replacement and reshaping",
                      "Stitched detail work to a high finish"]),
         ("Cabin trim", ["Side panels and trim", "Carpet and floor coverings",
                         "Consistent finish across the cabin"]),
         ("Working with you", ["Materials specified before any cutting starts",
                               "Bring the aircraft or the seats to the shop",
                               "Free, itemised estimate"])],
        # Empty for the same reason the hero is: the only two aviation photos in
        # the catalogue are unverified stock. The "Recent work" band drops out
        # with them rather than showing a picture of somebody else's aeroplane.
        [],
        [("Do you do full cabin interiors?",
          "Yes — seating, side panels, carpet and trim, finished consistently across the cabin."),
         ("Can I bring just the seats?",
          "Absolutely, and it is often the easiest way to do it. Remove them and bring them to "
          "the shop in Monroe."),
         ("How is aviation work different from automotive?",
          "The standard of finish and the attention to weight and fit are higher, and the "
          "materials differ. It is the same craft, held to a tighter tolerance.")],
        [])

    service_page(
        "motorcycle-seats.html",
        "Custom Motorcycle Seats in Monroe, NC | Auto Tops and Trim",
        "Custom motorcycle seat upholstery in Monroe, NC. Reshaping, recovering, diamond "
        "stitch and custom detail work. Free estimates — (980) 385-8101.",
        "Motorcycle upholstery", "Custom motorcycle seats",
        "Recovered, reshaped, or built to your own pattern — for daily riders "
        "and show bikes alike.",
        # NO HERO PHOTO. The one "motorcycle" image on this site was a diamond-
        # quilted seat on a mint-green cafe racer — unverified stock, and there is
        # no motorcycle anywhere in the 283 photographs of the shop's real work.
        # Text-only until the shop supplies a real one.
        None,
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



# ============================================================== SERVICES INDEX
def build_services_index():
    _lb_reset()
    p = "services.html"
    h = head("Upholstery Services | Auto Tops and Trim, Monroe NC",
             "Convertible tops, vinyl tops, sunroofs and vehicle interiors in Monroe, NC. "
             "Boat, aircraft and motorcycle upholstery too. Free estimates.", p)
    h += header(p)

    # TRUE BUSINESS-CARD ORDER, and only the four services the shop leads with.
    # Marine, aviation and motorcycle are still linked and still live — they moved
    # into the photoless "We also work on" band below this list, because the only
    # photographs the site had for them are unverified stock (see also_band).
    cards = [
        ("convertible-tops.html", "Convertible Tops", "g01-camaro-ss-new-convertible-top",
         "Vinyl and canvas tops, heated glass and plastic windows, plus the frame and pad "
         "work underneath that most quotes leave out.",
         ["Vinyl and canvas", "Heated glass windows", "Frame and pad repair"]),
        ("vinyl-tops.html", "Vinyl Tops", "vinyl-top-after-burgundy-fitted",
         "Rotted, peeling or faded roof coverings stripped back to the metal, re-padded "
         "and re-covered — including landau and padded tops.",
         ["Full, landau and half tops", "Rust checked before quoting", "Colour matched to the car"]),
        # Same photograph as the home page card, on purpose: it is the best
        # sunroof shot there is and the two cards should agree.
        ("sunroof-shade-repair.html", "Sunroofs", "sunroof-glass-open-in-the-shop",
         "Sagging, torn or stuck sliding sunshade? We recover the panel you already have "
         "instead of replacing the whole sunroof assembly.",
         ["Sagging and torn shades", "Matched to your headliner", "Recover, not replace"]),
        ("auto-upholstery.html", "Vehicle Interiors", "seat-rebuild-after",
         "Seats, headliners, door panels and carpet, from one torn seat to a complete "
         "classic interior built to your spec.",
         ["Seat repair and rebuilds", "Headliners and door panels", "Carpet and sound deadening"]),
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
    <p class="lead">Convertible tops, vinyl tops, sunroofs and vehicle interiors, out of
       one shop in Monroe, North Carolina. Every job is quoted free of charge, from your
       photos or in person.</p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="svclist">{rows}</div>
  </div>
</section>
"""
    h += also_band(tone="tint")
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
    # ---- adopted 2026-08-07 out of the 283-photo batch. Captions describe what
    # is in the frame, never the filename, and nothing here shows the retired
    # 704 number on the building (that check was made photo by photo).
    ("convertible-top-blue-galaxie-finished", "Ford Galaxie — new black top fitted", "Automotive"),
    ("convertible-top-tan-on-black-camaro", "Tan top fitted to a black convertible", "Automotive"),
    ("convertible-top-tan-side-view", "Tan top — side view", "Automotive"),
    ("vinyl-top-burgundy-finished-in-the-bay", "Vinyl top — finished in the shop bay", "Automotive"),
    ("vinyl-top-after-burgundy-fitted", "Vinyl top — new burgundy covering fitted", "Automotive"),
    ("vinyl-top-after-opera-window-detail", "Vinyl top — wrapped around the rear window", "Automotive"),
    ("vinyl-top-before-roof-covering-rotted", "Before — roof covering rotted through", "Automotive"),
    ("vinyl-top-roof-stripped-trim-removed", "Stripped — covering and mouldings off", "Automotive"),
    ("vinyl-top-before-peeling-at-rear", "Before — vinyl top peeling at the rear", "Automotive"),
    ("convertible-red-vinyl-interior-full", "Full red vinyl interior, front to back", "Automotive"),
    ("red-pickup-cab-black-seat-and-carpet", "Pickup cab — black seat and new carpet", "Automotive"),
    ("process-fitting-and-finish-cream-interior", "Cream leather interior, finished", "Automotive"),
    ("sunroof-shade-fabric-failed", "Sunroof shade — fabric broken up and flaking", "Automotive"),
    ("sunroof-shade-fabric-failed-wide", "Sunroof shade — the whole panel", "Automotive"),
    ("shop-lifting-the-top-frame", "Lifting the top frame off a car", "In the shop"),
    ("process-we-do-the-work-fitting-a-top", "Fitting a convertible top", "In the shop"),
    ("shop-seat-foam-and-jute-padding", "Foam and jute padding on the machine table", "In the shop"),
    ("shop-stitched-seam-detail", "Stitched seam detail", "In the shop"),
    ("process-materials-vinyl-and-fabric-rolls", "Vinyl and fabric roll stock", "In the shop"),
    ("process-working-at-the-bench", "Trimming work in progress at the bench", "In the shop"),
    ("boat-cockpit-cream-and-grey", "Boat cockpit — cream and grey upholstery", "Marine"),
    ("boat-helm-seat-white", "Helm seat off a boat, in for recovering", "Marine"),
    # REMOVED 2026-08-07: the runabout cockpit, the two aircraft cabin shots and
    # the cafe-racer seat. The owner supplied 283 photographs of his actual work
    # that day and NOT ONE is aviation or motorcycle, which settles the
    # provenance question this file has carried since 2026-08-05 - those four are
    # not his. The lead directly below this list says every piece was cut,
    # stitched and fitted in house, so they could not stay and leave it true.
    # They are still referenced by the service pages and six blog posts; that
    # rewiring is the remaining half of the job (see HANDOFF).
]


def batch_gallery_rows():
    """Every photo adopted out of the sorted batch, for the gallery.

    Written by the adoption pass into _build/gallery_batch.json so this file does
    not carry 250 hand-typed lines. Captions come from the descriptive tail of
    each source filename and the folder it was sorted into — the folder is
    reliable, the vehicle make/year in a filename is NOT, so that part is dropped
    and never shown. Anything already listed in GALLERY by hand is skipped, so no
    photograph appears twice.
    """
    path = os.path.join(HERE, "gallery_batch.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        rows = json.load(fh)
    seen = {b for b, _, _ in GALLERY}
    out = []
    for r in rows:
        if r["base"] in seen or not has(r["base"]):
            continue
        seen.add(r["base"])
        out.append((r["base"], r["caption"], r["cat"]))
    return out


def build_gallery():
    _lb_reset()
    p = "gallery.html"
    h = head("Gallery | Auto Tops and Trim, Monroe NC",
             "Upholstery work from Auto Tops and Trim in Monroe, NC — convertible tops, "
             "seats, headliners, carpet, boat cushions, aircraft cabins and custom bike seats.", p)
    h += header(p)
    shots = GALLERY + batch_gallery_rows()
    tiles = masonry_tiles(shots)
    h += f"""<section class="band">
  <div class="wrap stack">
    <div class="stack">{shead("01","Gallery")}
      <h1>Work out of the Monroe shop</h1>
      <p class="lead">{len(shots)} photographs of real jobs. Every piece here was cut,
         stitched and fitted in house.</p></div>
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
    # PHOTOS: supplied by the user 2026-08-07, already sorted into one folder per
    # step ("You bring it in", "We quote the job", …) — so each step now shows the
    # thing it describes instead of a generic shop photo.
    # The handshake on step 2 is licensed stock (Pexels), not a shop photograph;
    # it is the one image here that is not from Monroe.
    steps = [
        ("Walk in or call ahead", "You bring it in",
         "Drive the vehicle over, trailer the boat, or carry in a single seat. "
         "We look at it with you and talk through what you want.",
         "process-you-bring-it-in-corvette-at-the-shop"),
        ("Free, and itemised", "We quote the job",
         "We check what is under the cover — foam, frames, pads, bows — because that is "
         "where surprises live. Then you get an itemised estimate at no charge.",
         "process-we-quote-the-job-handshake"),
        ("Samples in hand", "You pick the materials",
         "We keep samples in the shop. Vinyl or canvas, glass or plastic window, "
         "period-correct or upgraded — you see and feel the difference before deciding.",
         "process-working-at-the-bench"),
        ("Same hands throughout", "We do the work",
         "Disassembly, repair of what is underneath, then cutting and stitching. "
         "The same hands that quoted the job do the work.",
         "process-we-do-the-work-fitting-a-top"),
        ("Checked with you", "Fitting and finish",
         "Nothing leaves until it fits properly. Weather sealing on marine and "
         "convertible work, and a final check with you at pickup.",
         "process-fitting-and-finish-cream-interior"),
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
    <!-- The bench shot moved down to "You pick the materials" where it belongs;
         this page opens on a car in the shop instead. -->
    <div class="hero-media">{img('shot-166-classic-in-for-top-work', 'A classic in the Monroe shop for top work', HALF, eager=True)}</div>
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


def build_careers():
    """Hiring page. Nothing here is invented.

    NO PAY, NO HOURS, NO BENEFITS and no job titles nobody has agreed to — none
    of that has been supplied, and a wrong number on a hiring page wastes both
    sides' time. What it does say is what the shop actually needs (someone who
    can sew, plus hands for everything either side of the machine) and how to
    put yourself forward. Add the specifics here the moment the owner gives them.
    """
    _lb_reset()
    p = "careers.html"
    h = head("Careers | Auto Tops and Trim, Monroe NC",
             "Auto Tops and Trim in Monroe, NC is hiring. Upholstery sewing machine "
             "operators and general shop help. Call (980) 385-8101 or stop by the shop "
             "at 4209 W Hwy 74.", p)
    h += header("contact.html")
    h += f"""<section class="hero">
  <div class="wrap">
    <div class="stack">{shead("", "Join the shop")}
      <h1>We are hiring in Monroe</h1>
      <p class="lead">This is a working trim shop, not a counter job. If you can sew, or
         you want to learn this trade properly from someone who has done it since 1989,
         come and talk to us.</p>
      <div class="btnrow">
        <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn-ghost" href="mailto:{EMAIL}?subject=Job%20enquiry">Email us</a>
      </div>
    </div>
    <div class="hero-media">{img('process-working-at-the-bench', 'Trimming work in progress at the bench', HALF, eager=True)}</div>
  </div>
</section>

<!-- EVERY heading on this page is centred, including the CTA at the bottom.
     Mixing a left-aligned band with a centred one on the same page is what made
     this look thrown together on a phone. -->
<section class="band">
  <div class="wrap stack">
    <div class="center stack">{shead("01", "Who we are looking for", center=True)}
      <h2>Sewing first &mdash; but not sewing only</h2>
      <p class="lead">The machine is the hardest seat to fill, so an experienced upholstery
         sewing machine operator can walk in tomorrow. It is not the only job here though:
         a top or an interior is stripped, repaired, patterned, cut, fitted and finished,
         and every one of those steps needs a pair of hands.</p></div>
    <div class="grid g3">
      <div class="stack"><h3>On the machine</h3><ul class="ticks">
        <li>Industrial machine experience &mdash; automotive, marine or furniture</li>
        <li>Panels, seams, piping, pleats and diamond work</li>
        <li>Working clean off a pattern</li>
      </ul></div>
      <div class="stack"><h3>Around the machine</h3><ul class="ticks">
        <li>Stripping interiors and pulling old covers</li>
        <li>Foam, frames, pads and bows &mdash; the repair underneath</li>
        <li>Fitting tops and trim on the car</li>
        <li>Keeping the shop and the benches straight</li>
      </ul></div>
      <div class="stack"><h3>What matters most</h3><ul class="ticks">
        <li>You turn up, on the days you said you would</li>
        <li>You take care with someone else&rsquo;s vehicle</li>
        <li>You would rather do it twice than hand back something crooked</li>
        <li>Willing to learn the parts you do not know yet</li>
      </ul></div>
    </div>
  </div>
</section>

<section class="band tint">
  <div class="wrap narrow stack">
    <div class="center stack">{shead("02", "How to apply", center=True)}
      <h2>There is no form for this one</h2>
      <p class="lead">Call, email, or come by &mdash; in person is best. Bring something
         you have made, or photographs of it.</p></div>
    <!-- Three centred cards rather than a label/value list: the list put a narrow
         left column against a wrapping right one, which on a phone left the
         labels stranded above ragged text. -->
    <div class="applyrow">
      <div class="applycard"><span class="k">Call</span>
        <a class="big" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
      <div class="applycard"><span class="k">Email</span>
        <a href="mailto:{EMAIL}?subject=Job%20enquiry">{EMAIL}</a></div>
      <div class="applycard"><span class="k">Come by</span>
        <strong>4209 W Hwy 74</strong>
        <span>Monroe, NC 28110</span>
        <span class="hrs">Mon&ndash;Fri 9&ndash;7 &middot; Sat 11&ndash;5</span></div>
    </div>
  </div>
</section>
"""
    h += cta(num="03", label="Come and see the place",
             heading="Not sure you have enough experience?",
             sub="Come by anyway and say so. We would rather meet someone willing to learn "
                 "the trade than wait for a perfect résumé that never turns up.")
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
      <!-- These are literally inside the shop, which is what the heading says.
           The tiles before this were parked cars and a seat on a bench, three of
           them from 249x332 masters. -->
      <figure class="tile">{img('shot-167-shop-with-convertible', 'A convertible in the shop with the benches behind it', QUARTER)}</figure>
      <figure class="tile">{img('shot-248-shop-with-white-mustang', 'A Mustang in the bay with the roller door open', QUARTER)}</figure>
      <figure class="tile">{img('shot-164-shop-floor-wide', 'The shop floor, benches and tool cart', QUARTER)}</figure>
      <figure class="tile">{img('shot-253-shop-floor-with-black-car', 'Work tables and a car in for trim work', QUARTER)}</figure>
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
      <a class="card" href="vinyl-tops.html"><div class="card-body">
        <h3>Vinyl tops</h3>
        <p>Rotted, peeling or faded roof coverings stripped back to the metal,
           re-padded and re-covered &mdash; landau and padded tops included.</p>
        <span class="card-link">Vinyl tops</span></div></a>
      <a class="card" href="sunroof-shade-repair.html"><div class="card-body">
        <h3>Sunroofs</h3>
        <p>The sliding shade recovered rather than the whole sunroof assembly
           replaced. Two of our Google reviews are about this exact repair.</p>
        <span class="card-link">Sunroofs</span></div></a>
      <a class="card" href="auto-upholstery.html"><div class="card-body">
        <h3>Seats, headliners and interiors</h3>
        <p>One torn seat or a complete classic interior built to your spec, for
           daily drivers, trucks and show cars alike.</p>
        <span class="card-link">Vehicle interiors</span></div></a>
    </div>
  </div>
</section>

{also_band(tone="tint")}

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
        ("How quickly will I hear back?",
         f"{REPLY_PROMISE} &mdash; by email or a call back, whichever you asked for. If it is "
         f"urgent, ring the shop on {PHONE_DISPLAY} during opening hours; a phone call is always "
         "the fastest route to an answer."),
        ("Can you quote from a photo?",
         "Yes. Email photos to contact@autotopsandtrim.com or text them to "
         f"{PHONE_DISPLAY} and we will come back to you with an estimate. On some jobs we will "
         "still want to see it in person before that number is final &mdash; collapsed pads, a "
         "bent bow, a rusted seat frame or foam that has gone hard do not always show up in a "
         "picture. We would rather find that at the shop than surprise you with it later. The "
         "estimate costs nothing either way."),
        ("What do you actually work on?",
         "Convertible tops, vinyl tops, sunroofs and vehicle interiors &mdash; seats, "
         "headliners, door panels and carpet. Boat cushions and canvas, aircraft cabins "
         "and custom bike seats come through as well."),
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
         with an estimate. {REPLY_PROMISE}.</p>
    </div>
    <div class="contact-grid">
      <div class="formcard">
        <h2 class="formcard-h">Request your free estimate</h2>
        {quote_form()}
      </div>
      <div class="infocol">
        <ul class="infolist">
          <!-- Deliberately NO "text a photo" link here (reverted 2026-08-09).
               On a paid landing page the alternative to a text is losing the
               visitor, so it rescues a lead. On THIS page the alternative is the
               form beside it: someone who navigated to Contact has already
               decided to reach out. A text here would trade a name, phone,
               email, year/make/model and a description for an unidentified
               photo. Cannibalisation, not incrementality.
               The sticky mobile bar still offers text, which is correct - that
               is a utility, not the designed path on this page. -->
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
        # Was the unverified runabout-cockpit stock shot — off the site entirely
        # as of the 2026-08-07 restructure.
        "photo": "shot-032-white-helm-seat-angle",
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
        "photo": "boat-cockpit-cream-and-grey",
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
        # Photo was the unverified runabout-cockpit stock shot (removed 2026-08-07).
        "slug": "blog-mildew-on-boat-seats.html",
        "cat": "Marine", "publish": "2026-08-07", "read": "5 min read",
        # NOT boat-upholstery-projects-at-the-shop — the how-to-clean-boat-seats
        # post already uses it, and both are live, so the blog index showed the
        # same photograph on two cards.
        "photo": "boat-helm-seat-white",
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
        "photo": "boat-on-the-trailer-at-the-shop",
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
        # HELD 2026-08-11. Was due to publish today and did, automatically, on the
        # date gate. Pulled back for a PHOTO reason, not a copy reason — the piece
        # itself is finished and good.
        # It shares `upholstery-materials-and-marine-project-parts` with the marine
        # buying guide and one already-published post, so three cards on the blog
        # index carried the identical thumbnail and dupcheck failed. That photo is
        # also, per the verified-content map, "a weathered outdoor table with trim
        # panels and a spray can — nothing identifies them as marine".
        # Marine is also currently in PAUSED_SERVICES.
        # TO PUBLISH: give it a photo of real marine work and set the date to today.
        "cat": "Marine", "publish": "2099-01-01", "read": "5 min read",
        # Was the unverified runabout-cockpit stock shot (removed 2026-08-07).
        "photo": "upholstery-materials-and-marine-project-parts",
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
        # HELD 2026-08-11, same reason as blog-boat-seat-repair: it is the second
        # of the three posts sharing one generic photo. Copy is finished.
        # TO PUBLISH: give it its own marine photo and set the date to today.
        "cat": "Marine", "publish": "2099-01-01", "read": "6 min read",
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
        # RELEASED 2026-08-11. Held earlier the same day because its photo was
        # `g13-sound-deadening-before-carpet`, which the verified-content map
        # records as a finished HEADLINER — "the opposite of its filename" — so a
        # sunroof-shade article was illustrated with a headliner, the same mistake
        # the 2026-08-05 caption audit corrected nine times. There was no correct
        # substitute at the time: no sunroof photograph existed in the library.
        # The owner supplied one on 2026-08-11, so it now carries an actual
        # sunroof shot instead of a borrowed headliner.
        "cat": "Sunroof Shades", "publish": "2026-08-11", "read": "4 min read",
        "photo": "ba-sunroof-shade-after",
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
        # NO PHOTO. The only "motorcycle" image the site had was unverified stock
        # (a diamond-quilted seat on a mint-green cafe racer) and there is no
        # motorcycle in the 283 photographs of the shop's real work. Text card and
        # no article hero until the shop supplies one — see build_blog.
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
        # NO PHOTO, same reason: both aviation images were unverified stock and no
        # aircraft appears in the shop's own 283 photographs.
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
    # `photo` is optional. A post about a trade the shop has no honest photograph
    # of gets a text card rather than somebody else's stock picture — the two
    # affected posts (motorcycle, aviation) lost theirs in the 2026-08-07 services
    # restructure. Give the post a `photo` again and the card illustrates itself.
    cards = "".join(f"""<a class="card{'' if po.get('photo') else ' nophoto'}" href="{po['slug']}">
      {img(po['photo'], po['title'], THIRD, ratio='16/10') if po.get('photo') else ''}
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
    {f'<figure class="article-figure">{img(po["photo"], po["title"], "(min-width:1000px) 940px, 100vw", eager=True)}</figure>' if po.get("photo") else ''}
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


# ============================================================== LANDING PAGES
#
# The paid-search pages. One per ad group in `c:\Claude Code\att_ads`, all built
# from landing_page() in build_landing.py — read that module's docstring before
# editing any of this, especially the five rules at the bottom of it.
#
# PHOTO RULE, restated because it is the one that bites: every caption and every
# alt below was written by OPENING the photograph at full size, never from its
# filename. The filenames in this repo demonstrably lie — `g13-sound-deadening-
# before-carpet` is a finished headliner, `shot-204-black-seat-torn-foam-out` and
# `shot-214-black-seat-finished` sound like a matched pair and are two different
# vehicles (204 is a GM bench torn open to the foam, 214 is a finished bucket
# seat off another car). The before/after captions say so.
LANDINGS = [
    # ---------------------------------------------------------------- HEADLINERS
    # This is `_draft-headliner.html` at DRAFT v15, unchanged in substance. The
    # <title> and meta description are the ones the page was already indexed
    # under, not the draft's placeholder.
    #
    # PHOTOS, all opened at full size: `shot-050` is a finished light-grey
    # headliner in a coupe (it IS a Porsche — the crest is on the headrest — but
    # no caption on this site names a make). `shot-152` is an SUV with the board
    # out and the bare roof showing. `shot-208-top-frame-and-headliner` was
    # REJECTED: despite the filename there is no headliner in it, it is the
    # underside of a raised convertible top. `headliner-install` is the known
    # duplicate Cadillac exterior — never use it.
    #
    # NOTHING HERE CLAIMS A TURNAROUND OR A PRICE. Neither is verified, and both
    # are still open questions with the owner.
    {
        "slug": "headliner-replacement.html",
        "title": "Headliner Replacement in Monroe, NC | Sagging Headliner Repair",
        "desc": ("Headliner replacement in Monroe, NC. Sagging and drooping headliners "
                 "recovered with new foam-backed fabric. Free estimates — (980) 385-8101."),
        "eyebrow": "Headliners",
        "h1": "Your headliner is sagging because the foam died, not the glue.",
        "lead": ("That is why pins and spray adhesive keep letting go. We take the board "
                 "out, strip the crumbling foam back, and fit new foam-backed fabric that "
                 "stays up."),
        "hero": ("shot-050-porsche-headliner-finished",
                 "A finished headliner, fitted taut across the roof of a coupe"),
        "argument": {
            "label": "Why it sags",
            "h2": "The fabric is fine. What failed is behind it.",
            "sub": ("Every headliner is fabric bonded to a thin layer of foam, and that "
                    "foam is glued to a moulded board. Heat and age turn the foam to "
                    "powder. The fabric has nothing left to hold on to, so it drops away "
                    "from the board in sheets."),
            "pull": ("Carolina summers make it happen faster.",
                     "A closed car in July gets hot enough to age that foam years ahead "
                     "of schedule."),
            "myth_title": "Why the quick fixes fail",
            "myths": [
                ("Spray adhesive", "bonds fabric to powder. There is nothing solid "
                                   "underneath for it to grip."),
                ("Twist pins", "hold the fabric up in spots and leave dimples between "
                               "them &mdash; and marks in the fabric when they come out."),
                ("Steam and re-glue", "does not stop the foam breaking down, so the same "
                                      "thing happens again."),
                ("Replacing the whole board", "is usually unnecessary. Yours is almost "
                                              "always sound."),
            ],
        },
        "steps": {
            "label": "What we do",
            "h2": "The repair that actually lasts",
            "sub": ("The board comes out of the car. That is the difference between a "
                    "headliner that is fixed and one that is patched."),
            "cards": [
                ("shot-152-rear-headliner-frame",
                 "An SUV with the headliner board removed, bare roof and wiring visible",
                 "68%", "The board comes out",
                 ["Out of the car, not worked around",
                  "Trim taken off rather than cut past",
                  "Roof left bare and checked over"]),
                ("headliner-board-out-foam-degraded",
                 "A headliner board on the shop bench, stripped back to the substrate",
                 "52%", "Stripped back on the bench",
                 ["Old fabric and dead foam scraped off",
                  "Board cleaned down to a sound surface",
                  "Sunroof and light cutouts kept true"]),
                ("headliner-old-fabric-and-foam-on-bench",
                 "New grey foam-backed fabric being laid onto the stripped headliner board",
                 "58%", "New material goes on",
                 ["Fresh foam-backed headliner fabric",
                  "Bonded across the whole board at once",
                  "Colour matched to your interior"]),
            ],
        },
        # VERIFIED 2026-08-09 by opening every photo: there is NO same-car
        # before/after in the 16-photo headliner batch. The jobs cluster into four
        # separate vehicles and not one has both ends photographed. Card 1 is
        # therefore TWO DIFFERENT CARS and its caption says so; card 2 is the only
        # genuinely matched pair in the set. Do not relabel either as one car.
        "pairs": [
            ("headliner-sagging-board-exposed",
             "A headliner come away at the rear corner, exposing the roof structure",
             "shot-050-porsche-headliner-finished",
             "A finished headliner fitted taut across the roof of a coupe",
             "Come away at the rear corner &middot; finished on another car"),
            ("headliner-board-out-foam-degraded",
             "A headliner board out of the car on the bench, stripped to the substrate",
             "headliner-old-fabric-and-foam-on-bench",
             "New grey foam-backed fabric being laid onto the same stripped board",
             "The same board &mdash; stripped, then recovered"),
        ],
        "work": {
            "label": "Out of this shop",
            "h2": "Headliners out of this shop",
            "sub": ("Real jobs, photographed on the bench and in the car at "
                    "4209 W Hwy 74."),
            "photos": [
                ("headliner-sagging-second-angle",
                 "A sagging headliner photographed from a second angle"),
                ("headliner-suv-bows-exposed",
                 "An SUV roof with the headliner out and the bows exposed"),
                ("headliner-suv-hatch-open-liner-out",
                 "An SUV with the hatch open and the headliner removed"),
                ("headliner-cream-panel-on-table",
                 "A cream headliner panel on the shop table"),
                ("headliner-finished-with-sunroof-opening",
                 "A finished headliner with the sunroof opening trimmed"),
                ("headliner-finished-sunroof-grab-handle",
                 "A finished headliner around the sunroof and grab handle"),
                ("headliner-finished-over-windscreen",
                 "A finished light grey headliner above the windscreen"),
                ("headliner-finished-rear-quarter",
                 "A finished headliner at the rear quarter and grab handle"),
            ],
        },
        "review_taglines": {
            "Robert Danneman": "Headliner replacement",
            "Charles Monk": "Headliner replacement",
            "Ozzie Pagan": "Sunroof shade",
            "Lauren Corgan": "Drove an hour",
            "charmaine sealey": "Repeat customer",
        },
        "faq": {
            "label": "Before you call",
            "h2": "Answers first",
            "items": [
                ("My headliner is sagging. Can it just be glued back up?",
                 "Almost never for long. The fabric is separating because the foam bonded "
                 "to its back has turned to powder &mdash; there is nothing solid left for "
                 "glue to hold to. Pins and spray adhesive buy a little time and usually "
                 "leave marks in the fabric. Recovering the board is the repair that lasts."),
                ("Do you replace the whole roof lining or just the fabric?",
                 "The board itself is almost always sound and gets reused. What gets "
                 "replaced is the foam-backed fabric bonded to it. We only quote a new "
                 "board if yours is warped or broken."),
                ("Can you match it to the rest of my interior?",
                 "Usually. We will show you material against your own trim before you "
                 "decide. On an interior that has faded over the years, the honest answer "
                 "is that a brand-new match can look newer than everything around it, and "
                 "we will say so."),
                ("Can you quote from a photo?",
                 "Yes. Send a photo of the sagging area along with the year, make and "
                 "model, and we will give you an estimate by email. Some jobs need an "
                 "in-person look before we commit to a number, and we will tell you if "
                 "yours is one of them."),
                ("Do you do modern cars, or only classics?",
                 "Both. Sagging headliners are common on cars from the mid-1990s onward, "
                 "and that is a lot of what comes through the shop alongside the "
                 "restoration work."),
            ],
        },
        # NO "extra" BAND. Removed 2026-08-09.
        #
        # This is a PAID landing page. Every click costs about $2.50, and this
        # band offered that visitor a button reading "How to fix a sagging
        # headliner" — paying to hand someone instructions for not hiring us.
        # It was also two heavy black buttons and a whole extra band of scroll
        # sitting between the FAQ and the form.
        #
        # The internal-link value is real but small, and those posts already
        # rank on their own; they do not need a paid page feeding them. If the
        # link is wanted for SEO it belongs inline inside a FAQ answer, not as
        # buttons competing with the form.
        #
        # The `extra` band still exists in build_landing.py for any page that
        # genuinely wants it — this page just does not pass one.
        "form": {
            "big": "Send us a photo of it",
            "p": ("A picture of the sagging area plus the year, make and model is usually "
                  "enough for an estimate by email."),
            "why": ["Free, and no obligation",
                    "Nobody will chase you afterwards",
                    "If yours needs an in-person look, we will say so"],
            "subject": "HEADLINER estimate request from autotopsandtrim.com",
            "placeholder": ("Sagging headliner, where it has come away, anything else in "
                            "the interior&hellip;"),
            "filenote": "A picture or two of the sagging area helps a lot.",
        },
    },

    # ------------------------------------------------------ AUTO UPHOLSTERY
    # THE BIG ONE: 33 keywords and 10,040 local searches a month, 60% of the whole
    # campaign's volume on one page. Keyword set is in keywords_verified.py under
    # "Auto Upholstery & Interiors".
    #
    # The intent behind those 33 terms is overwhelmingly REPAIR, not restoration:
    # "car upholstery repair near me", "fix leather car seat", "torn leather car
    # seat repair", "auto seat repair", "car seat fix". The old service page led
    # with full classic interiors, which is the smallest slice of the demand. This
    # one leads with a torn seat and keeps the restoration work as the closer.
    #
    # THE FURNITURE TRAP: bare "upholstery shop near me" and friends are FURNITURE
    # searches (Ahrefs parent_topic) — 47,500/mo of pure waste — and are in
    # REJECTED in keywords_verified.py. Never widen this page's copy toward plain
    # "upholstery" to chase them.
    #
    # PHOTOS, every one opened at full size on 2026-08-09:
    #   shot-113 ... a seat cushion stripped to the burlap over its springs, the
    #                cotton padding disintegrated, on a stool in the bay
    #   shot-176 ... a black bench seat with red piping on the shop bench, the
    #                stripped base and tools on the table in front of it
    #   shot-030 ... two finished burgundy pleated cushions resting on the body of
    #                a classic car in the shop, waiting to go back in
    #   ba-seats-* . THE ONE GENUINE MATCHED PAIR on this project: the same two
    #                bucket seats against the same wall, one split open and duct-
    #                taped, then both recovered in new burgundy vinyl
    #   shot-204 ... a GM bench with the cover split open and yellow foam exposed
    #   shot-214 ... a finished black pleated BUCKET seat — a DIFFERENT vehicle
    #                from 204. The caption says so.
    # The eight strip photos are the ones already eye-verified in the map above
    # GALLERY, with their verified captions.
    {
        "slug": "auto-upholstery.html",
        "title": "Auto Upholstery in Monroe, NC | Car Seat and Interior Repair",
        "desc": ("Auto upholstery shop in Monroe, NC. Torn and split car seats repaired, "
                 "leather and vinyl recovered, carpet, door panels and classic car "
                 "interior restoration. Free estimates — (980) 385-8101."),
        "eyebrow": "Auto upholstery",
        "h1": "A torn car seat is rarely just a torn cover.",
        "lead": ("By the time the vinyl or the leather splits, the foam under it has "
                 "already collapsed and the burlap under that has rotted. We take the "
                 "seat apart, rebuild what is holding you up, and recover it."),
        # Owner-supplied hero, 2026-08-11. Given its OWN basename rather than
        # overwriting `seat-rebuild-after`, because that photo is also used on
        # gallery, services, the blog index and blog-torn-car-seat-repair — a
        # blanket replace would have silently changed five pages to fix one.
        "hero": ("hero-auto-upholstery-f1-and-bench",
                 "A red Ford F1 pickup outside the Monroe shop with a finished black "
                 "bench seat, red stitching, on the driveway beside it"),
        "argument": {
            "label": "Why it splits",
            "h2": "The cover is the last thing to go, not the first.",
            "sub": ("Under the leather or the vinyl there is foam, and under the foam "
                    "there is burlap stretched over springs. Heat, damp and thirty years "
                    "of getting in and out break those down first. The cover then has "
                    "nothing holding its shape, so it stretches, splits along a seam and "
                    "tears open at the bolster you slide across twice a day."),
            "pull": ("It is nearly always the driver's seat, and nearly always the "
                     "outer bolster.",
                     "That is the corner your whole weight lands on, every time you "
                     "get in."),
            "myth_title": "Why the quick fixes fail",
            "myths": [
                ("Slip-on seat covers", "hide a split for a while and slide about on it. "
                                        "Nothing underneath is any better for it."),
                ("Leather repair kits", "fill a tear with a coloured compound that sits "
                                        "on foam which has already given way. It shows, "
                                        "and it goes again."),
                ("Stitching the split shut", "pulls the tear wider, because the material "
                                             "either side has stretched and there is "
                                             "nothing firm left behind it."),
                ("A used seat from a breaker", "is the same age as yours with the same "
                                               "foam in it. You have bought somebody "
                                               "else's problem."),
            ],
        },
        "steps": {
            "label": "What we do",
            "h2": "Stripped to the frame, then rebuilt",
            "sub": ("The seat comes out and it comes apart. That is the difference "
                    "between a seat that is repaired and a seat that has been covered up."),
            "cards": [
                # Owner-supplied 2026-08-11, folder "Stripped to the frame, then
                # rebuilt". Own au- basenames so they stay exclusive to this ad page.
                ("au-step-01",
                 "A seat stripped back to its frame, the rotted burlap and old padding "
                 "hanging off the springs",
                 "40%", "Stripped back to the frame",
                 ["Cover and dead padding come off",
                  "Burlap and springs uncovered and checked",
                  "Broken springs and frames repaired, not padded over"]),
                ("au-step-02",
                 "A bench seat recovered in black on the shop table, the new panels "
                 "pulled taut over the rebuilt base",
                 "35%", "Rebuilt on the bench",
                 ["New foam cut and shaped to the original profile",
                  "Panels cut and sewn to the car's own pattern",
                  "Custom stitch spacing and piping where you want it"]),
                ("au-step-03",
                 "A finished bench seat recovered in red, outside the shop",
                 "55%", "Recovered and refitted",
                 ["Leather, vinyl or cloth, chosen with you first",
                  "Fitted taut, with no pull marks at the seams",
                  "Back in the car and checked on its runners"]),
            ],
        },
        # Owner-supplied 2026-08-11, folder "before and afters". Both are genuinely
        # the SAME seats photographed twice, which the old pair 2 was not — its
        # caption had to admit "a finished seat off another car". Exclusive au-
        # basenames so the gallery and home page are untouched.
        "pairs": [
            ("au-ba-before1",
             "A red bench seat in pieces on the workbench with the old covers off",
             "au-ba-after1",
             "The same bench recovered in new red material on the shop table",
             "The same bench &mdash; stripped, then recovered in red"),
            ("au-ba-before2",
             "Two burgundy bucket seats, one split open down the side with the "
             "padding showing through",
             "au-ba-after2",
             "The same two bucket seats recovered in burgundy",
             "The same two seats &mdash; split and worn, then rebuilt"),
        ],
        "work": {
            "label": "Out of this shop",
            "h2": "Interiors out of this shop",
            "sub": ("Real jobs, photographed on the bench and in the car at "
                    "4209 W Hwy 74, Monroe."),
            # Owner-supplied 2026-08-11, folder "Interiors out of this shop".
            # Twelve of the seventeen he sent, not all of them: the strip is a
            # four-column grid, so twelve fills three clean rows where thirteen
            # leaves a single dangling tile. Ordered for VARIETY rather than by
            # filename, because mobile hides everything past the sixth tile
            # (.lp .strip figure:nth-child(n+7)) — so the first six have to carry
            # the range on their own. The whole set is exclusive to this ad page.
            "photos": [
                ("au-shop-03",
                 "Tan quilted leather seats with black inserts and matching door cards"),
                ("au-shop-01",
                 "A cream leather front seat fitted in the car"),
                ("au-shop-10",
                 "The red interior of a convertible, front and rear seats recovered"),
                ("au-shop-12",
                 "A black bench seat with blue accent panels, finished outside the shop"),
                ("au-shop-04",
                 "A pair of black and magenta bucket seats on the driveway"),
                ("au-shop-09",
                 "A black bench seat with red piping, photographed in the shop"),
                ("au-shop-07",
                 "Dark pleated door trim and seats inside a red classic"),
                ("au-shop-05",
                 "A two-tone red bench seat finished and out on the driveway"),
                ("au-shop-14",
                 "A modern truck cab with its seats and console retrimmed"),
                ("au-shop-06",
                 "Purple and black seats laid out on the bench outside"),
                ("au-shop-16",
                 "The cab of a red pickup with its rebuilt seat fitted"),
                ("au-shop-17",
                 "A black bench seat with red and blue piping on the shop table"),
            ],
        },
        # Robert Danneman's review names the two jobs it names — a headliner and
        # the centre console leather. It may not be labelled anything else.
        # Charles Monk's text does not name a job, but the two photographs he
        # attached to it are a headliner before and after, which is what the label
        # rests on. Everyone else falls through to "Google review".
        "review_taglines": {
            "Robert Danneman": "Headliner and console leather",
            "Charles Monk": "Headliner replacement",
            "Ozzie Pagan": "Sunroof shade",
            "Lauren Corgan": "Drove an hour",
            "charmaine sealey": "Repeat customer",
        },
        "faq": {
            "label": "Before you call",
            "h2": "Answers first",
            "items": [
                ("Can you repair one torn seat, or do I have to do the whole interior?",
                 "One seat is fine, and it is a great deal of what comes through the shop. "
                 "Plenty of our work is a single split driver's seat in a car that is "
                 "otherwise good. You do not need a full restoration to come and see us."),
                ("Can a leather car seat be repaired, or does it have to be recovered?",
                 "It depends where the damage is. A small burn or a split in a flat panel "
                 "can sometimes be repaired so you would not find it. A rip across the "
                 "bolster you slide over usually cannot, because that panel has stretched "
                 "and the foam under it has gone &mdash; that one gets a new panel. We "
                 "will tell you which yours is before we quote it."),
                ("Do you use leather, or vinyl?",
                 "Both, and cloth. Modern automotive vinyl wears extremely well and is "
                 "often the right call on a daily driver; leather is worth it where the "
                 "car warrants it. We put samples in front of you and tell you what each "
                 "one will do in a car that sits out in the Carolina sun."),
                ("How much does it cost to reupholster car seats?",
                 "It comes down to how many seats, the material you choose, and what we "
                 "find when the cover comes off. Repairing one panel and rebuilding a "
                 "seat with new foam and springs are very different numbers. The estimate "
                 "is free and itemised, so you can see which part of it is the cover and "
                 "which part is what was underneath it."),
                ("Do you work on modern cars, or only classics?",
                 "Both. A late-model seat with a split bolster is routine work here, and "
                 "so is a full classic car interior restoration built to your own spec. "
                 "The shop has been doing both in Monroe since 1989."),
            ],
        },
        # NO "extra" BAND — same reasoning as the headliner page above. Paid
        # traffic should not be offered three buttons out to blog posts before
        # it reaches the form.
        "form": {
            "big": "Send us a photo of it",
            "p": ("A picture of the tear or the worn panel, plus the year, make and "
                  "model, is usually enough for an estimate by email."),
            "why": ["Free, and no obligation",
                    "Nobody will chase you afterwards",
                    "If yours needs an in-person look, we will say so"],
            "subject": "AUTO UPHOLSTERY estimate request from autotopsandtrim.com",
            "placeholder": ("Torn driver's seat, worn leather, carpet, door "
                            "panels&hellip;"),
            "filenote": "A picture or two of the damage helps a lot.",
        },
    },

    # ---------------------------------------------------------- SUNROOF REPAIR
    # 17 keywords, 2,570/mo, and the highest max CPC in the account at $3.75.
    # WIDENED from the old shade-only page. The owner interview settled it: he
    # takes the whole cassette OUT of the car, rebuilds it and refits the
    # ORIGINAL — cables, motors, tracks, drains, and the sliding shade. No new
    # part is sold. That is the argument, and no competitor page says it.
    #
    # NOT INSTALLATION. He can cut a roof and fit one; he does not want to and
    # would refer it out. Those 18 keywords are held in keywords_verified.py and
    # negated campaign-wide. Nothing on this page may invite that work.
    #
    # ⚠️ PHOTO LIMIT, recorded here so nobody papers over it later: there is NO
    # photograph anywhere in the 283-photo batch of a RECOVERED sunroof shade.
    # The shade folder holds exactly two files and BOTH are before shots. So this
    # page carries NO before/after deck — a pair deck here would have to invent
    # one. It shows the mechanism open on the bench and finished interiors with
    # sound shades, and nothing is captioned as a shade this shop recovered.
    # The day a true after exists, it becomes the hero and the deck goes in.
    {
        "slug": "sunroof-shade-repair.html",
        "title": "Sunroof Repair in Monroe, NC | Leaks, Cables, Motors and Shades",
        "desc": ("Sunroof repair in Monroe, NC. Stuck, leaking or noisy sunroofs rebuilt — "
                 "cables, tracks, drains and sagging sunshades. We refit your original. "
                 "Free estimates — (980) 385-8101."),
        "eyebrow": "Sunroof repair",
        "h1": "A stuck sunroof is usually the cables, not the motor.",
        "lead": ("We take the whole unit out of the car, rebuild it on the bench and refit "
                 "the one you already have. You are not buying a new sunroof."),
        # Hero must be FINISHED work — a broken shade as the hero made the page
        # look like a picture of a bad job. This is a confirmed after: a finished
        # light-grey headliner with the sliding shade closed across the opening.
        "hero": ("shot-045-finished-with-sunroof-opening",
                 "A finished headliner with the sliding shade closed across the sunroof "
                 "opening"),
        # Added 2026-08-11. This was the ONLY landing page without a before/after
        # section — it had zero pairs while the other four had two each. Supplied
        # by the owner as before.jpg / after.jpg and placed in those slots on his
        # instruction. Wording is kept deliberately plain: it does not name the
        # vehicle, and it does not claim whether the shade was recovered or the
        # assembly replaced, because neither is established by the photographs.
        # If the owner confirms which it was, tighten the caption then — that
        # distinction is the whole argument of the sunroof blog post.
        "pairs": [
            ("ba-sunroof-shade-before",
             "A sunroof shade before the repair",
             "ba-sunroof-shade-after",
             "The sunroof shade after the repair",
             "Sunroof shade &middot; before and after"),
        ],
        "argument": {
            "label": "Why it sticks",
            "h2": "The part that fails is the cheapest part in there.",
            "sub": ("A sunroof runs on two nylon-coated cables in guide tracks, pushed by a "
                    "small motor. The cables dry out, fray and jump their track, and the "
                    "plastic shoes they run in break up. The motor is usually fine and so is "
                    "the glass. What you hear as a dead sunroof is nearly always the drive "
                    "cables and the guides."),
            "pull": ("We rebuild your unit and put it back.",
                     "Nothing is cut and no new assembly is sold. The sunroof that comes out "
                     "is the one that goes back in."),
            "myth_title": "What the quick answers get wrong",
            "myths": [
                ("A new motor", "is the usual first guess and rarely the fix. If it hums and "
                                "nothing moves, the cables have already let go."),
                ("Sealing around the glass", "does not stop most leaks. A sunroof is designed "
                                             "to let water in — it drains away down four "
                                             "tubes, and blocked tubes are what puts water on "
                                             "your headliner."),
                ("A used assembly from a breaker", "is the same age as yours with the same "
                                                   "dried-out cables in it."),
                ("Bolting it shut for good", "is what a lot of places will suggest. We would "
                                             "rather fix the mechanism."),
            ],
        },
        "steps": {
            "label": "What we do",
            "h2": "Out of the car, rebuilt on the bench",
            "sub": ("The cassette comes out so the tracks, cables, drains and shade can be "
                    "worked on properly — then your original goes back in."),
            "cards": [
                # Owner-supplied 2026-08-11, folder "Out of the car, rebuilt on the
                # bench" — the exact name of this section's h2. The photo that used
                # to sit here, `sunroof-glass-open-in-the-shop`, was not discarded:
                # it moved down into the strip below, on the owner's instruction.
                ("sr-bench-01",
                 "A sunroof assembly lifted out of the car, its frame, shade and "
                 "fixings exposed",
                 "50%", "We open it up",
                 ["Panel and trim off, not worked around",
                  "Tracks, cables and guides exposed",
                  "All four drain tubes checked and cleared"]),
                ("sr-bench-02",
                 "Looking up through the roof opening from inside the car with the "
                 "sunroof unit out and its cable hanging free",
                 "45%", "What usually turns up",
                 ["Cable sheathing dried out and frayed",
                  "Guide shoes cracked or missing",
                  "Shade fabric perished off its panel"]),
                ("shot-046-finished-sunroof-grab-handle",
                 "A finished headliner and trim around the sunroof opening and grab handle",
                 "55%", "Back in and trimmed",
                 ["Your original unit refitted, not replaced",
                  "Runs checked through the full travel",
                  "Headliner and trim put back properly"]),
            ],
        },
        # (This used to read "NO pairs KEY ON PURPOSE" — true when no sunroof
        # before/after photograph existed anywhere in the library. The owner
        # supplied one on 2026-08-11 and the pairs key above is now populated.)
        "work": {
            "label": "Out of this shop",
            "h2": "Sunroofs and shades through this shop",
            "sub": ("Photographed at 4209 W Hwy 74, Monroe. The shop has more sunroof work "
                    "than it has pictures of it — these are the jobs that got photographed."),
            # Changed 2026-08-11 on the owner's instruction. The perished-shade
            # wide shot was dropped from the head of this strip, and the sunroof
            # opened up in the shop moved down here from the first "what we do"
            # card, whose slot his own bench photograph now fills.
            "photos": [
                ("sunroof-glass-open-in-the-shop",
                 "A sunroof opened up in the shop with the panel slid back and the "
                 "guide track exposed"),
                ("headliner-finished-with-sunroof-opening",
                 "A finished headliner trimmed around the sunroof opening"),
                ("headliner-finished-sunroof-grab-handle",
                 "A finished headliner around the sunroof surround and grab handle"),
                ("headliner-finished-over-windscreen",
                 "A finished light grey headliner above the windscreen"),
            ],
        },
        # Ozzie Pagan's review IS a sunroof shade job and Lauren Corgan's names a
        # sunroof, so this page can lead with both honestly.
        "review_taglines": {
            "Ozzie Pagan": "Sunroof shade",
            "Lauren Corgan": "Drove an hour for a sunroof",
            "Robert Danneman": "Headliner and console leather",
            "Charles Monk": "Headliner replacement",
            "charmaine sealey": "Repeat customer",
        },
        "faq": {
            "label": "Before you call",
            "h2": "Answers first",
            "items": [
                ("My sunroof is stuck open. Can you get it shut today?",
                 "Usually, yes — getting it closed and safe is the first thing we do, and "
                 "that part is often quick. Whether the full repair is finished the same day "
                 "depends on what has broken. Jobs here run from about an hour to a full day."),
                ("Do you replace the whole sunroof?",
                 "No, and that is the point of bringing it here. We take your unit out, "
                 "rebuild it and refit the original — cables, guides, tracks and motor. A "
                 "dealer will often quote the entire cassette instead."),
                ("Water is coming in around my sunroof. Is the seal gone?",
                 "Probably not. A sunroof is built to let water past the glass and drain it "
                 "away through tubes in each corner. When those block, the water backs up and "
                 "comes out at the headliner. We clear the drains and find out where it is "
                 "actually getting in before quoting a seal."),
                ("Can you fix the sliding shade as well?",
                 "Yes. When the fabric on the sliding sunshade sags or breaks up, we recover "
                 "the panel you already have and match the material to your headliner. It is "
                 "trim work, which is what this shop does."),
                ("Do you install new sunroofs?",
                 "No. Cutting a roof for a sunroof that was never there is not work we take "
                 "on, and we will point you to someone who does rather than take it half-"
                 "heartedly. Repairing, rebuilding and resealing a sunroof the car already "
                 "has is very much our work."),
            ],
        },
        "form": {
            "big": "Tell us what it is doing",
            "p": ("What it does when you press the switch, plus the year, make and model, is "
                  "usually enough for us to tell you what is likely wrong."),
            "why": ["Free, and no obligation",
                    "Nobody will chase you afterwards",
                    "If it needs to come in to be diagnosed, we will say so"],
            "subject": "SUNROOF estimate request from autotopsandtrim.com",
            "placeholder": ("Stuck open, will not close, leaking at the headliner, grinding "
                            "noise, sagging shade&hellip;"),
            "filenote": "A short video of what it does is even better than a photo.",
        },
    },

    # -------------------------------------------------------- CONVERTIBLE TOPS
    # Only 600/mo, but it carries the TOP BID in the account at $4.00, because
    # the owner says tops pay most and he wants the work. Everything here is from
    # the owner interview: he BUYS AND OWNS his materials (Stayfast, vinyl,
    # cloth), the heated glass rear window comes with the top, he does frames,
    # pads and bows, he does Jeep soft tops, and he quotes by calling the top
    # manufacturer and adding his labour.
    {
        "slug": "convertible-tops.html",
        "title": "Convertible Top Replacement in Monroe, NC | Auto Tops and Trim",
        "desc": ("Convertible top replacement in Monroe, NC. Cloth and vinyl tops, heated "
                 "glass rear windows, frames, pads and bows. Jeep soft tops too. "
                 "Free estimates — (980) 385-8101."),
        "eyebrow": "Convertible tops",
        "h1": "A new top is three jobs, and most quotes only cover one.",
        "lead": ("The fabric, the rear window, and the frame underneath it. We look at all "
                 "three before we give you a number, because the frame is what decides how "
                 "long the new top lasts."),
        "hero": ("convertible-top-blue-galaxie-finished",
                 "A finished tan convertible top fitted on a blue classic, outside the shop"),
        "argument": {
            "label": "Why they fail",
            "h2": "The fabric is what you see. The frame is what killed it.",
            "sub": ("Pads collapse, bows bend and the tension goes out of the frame. Once "
                    "that happens the new fabric is stretched over a shape that is no longer "
                    "right, so it wears through at the same corners and the rear window "
                    "cracks again. Fitting a top to a tired frame is why some tops last "
                    "fifteen years and some last three."),
            "pull": ("We own the material we fit.",
                     "Stayfast cloth, vinyl and canvas bought in by this shop — not ordered "
                     "in blind against whatever a supplier has that week."),
            "myth_title": "What a cheap quote leaves out",
            "myths": [
                ("The pads and bows", "are the part nobody itemises, and the part that "
                                      "decides whether the new top sits right."),
                ("The rear window", "is often the reason the top failed first. On ours the "
                                    "heated glass window comes with the top."),
                ("Trim and mouldings", "get cut around instead of taken off, and you can see "
                                       "it afterwards at every edge."),
                ("Rust under the seals", "gets covered rather than dealt with. We will not "
                                         "put a new top over rust."),
            ],
        },
        "steps": {
            "label": "What we do",
            "h2": "Old top off, frame sorted, new top fitted",
            "sub": ("The frame gets looked at with the old material off, which is the only "
                    "point in the job where you can actually see it."),
            "cards": [
                ("shot-171-old-top-removed",
                 "A convertible with the old top off, the new top laid out on the rear deck "
                 "and the fasteners set aside",
                 "48%", "The old top comes off",
                 ["Mouldings and trim removed, not cut past",
                  "Fasteners kept and bagged, not replaced with screws",
                  "Tack strips and channels cleaned back"]),
                ("shot-060-stripped-top-frame-bare",
                 "A classic convertible with its top frame stripped down to the bare bows",
                 "42%", "The frame comes down to bare bows",
                 ["Collapsed pads replaced",
                  "Bent bows straightened and alignment checked",
                  "Corrosion dealt with before anything new goes on"]),
                ("shot-120-new-top-clamped-and-taped",
                 "A new black top fitted to the car and taped along the belt line while the "
                 "adhesive sets",
                 "52%", "New top fitted and set",
                 ["Cloth, vinyl or canvas, chosen with you first",
                  "Heated glass rear window fitted with the top",
                  "Held and taped while it sets so it pulls up tight"]),
            ],
        },
        # Owner-supplied 2026-08-11, folder "before and after". Three pairs now
        # instead of two, on exclusive ct- basenames so nothing here is shared
        # with the gallery or the home page.
        #
        # Pair 3's "after" has the top DOWN, so the new top is folded and not on
        # show. Its caption therefore does not claim you can see the new top —
        # it says the car is finished and back out, which is what the photograph
        # actually shows.
        "pairs": [
            ("ct-ba-before1",
             "A red convertible in the shop with the old top off, laid back over the "
             "rear deck",
             "ct-ba-after1",
             "A new black top fitted, seen from the rear quarter",
             "Old top off &middot; new black top fitted"),
            ("ct-ba-before2",
             "A red convertible in the bay with the top out and the frame exposed",
             "ct-ba-after2",
             "The same car finished on the driveway outside the shop",
             "Frame bare in the bay &middot; finished on the driveway"),
            ("ct-ba-before3",
             "A blue classic convertible in the shop with the top deck stripped",
             "ct-ba-after3",
             "The same blue classic back outside, finished, with the top down",
             "Stripped in the shop &middot; finished and back out"),
        ],
        "work": {
            "label": "Out of this shop",
            "h2": "Tops out of this shop",
            "sub": "Real cars, photographed in the bay and on the lot at 4209 W Hwy 74, Monroe.",
            # Owner-supplied 2026-08-11, folder "Tops out of this shop". Twelve of
            # the thirteen sent — ct-shop-06 is dropped as a near-duplicate of
            # ct-shop-05 (the same tan top, one frame apart), and two near-identical
            # tiles in a twelve-tile grid read as a mistake. Twelve also fills the
            # four-column grid in three clean rows. Mobile hides everything past
            # the sixth tile, so the first six are ordered to carry the range.
            "photos": [
                ("ct-shop-04",
                 "A blue classic convertible with its new black top, on the shop driveway"),
                ("ct-shop-07",
                 "A black Camaro with yellow stripes and a tan convertible top"),
                ("ct-shop-01",
                 "A burgundy top fitted on a cream classic, seen from the rear quarter"),
                ("ct-shop-08",
                 "A black Camaro convertible with a new black top"),
                ("ct-shop-11",
                 "A red Corvette with a new black top outside the shop"),
                ("ct-shop-12",
                 "A burgundy convertible with a black top on the driveway"),
                ("ct-shop-02",
                 "A red convertible with its new black top, photographed in the bay"),
                ("ct-shop-03",
                 "A blue Camaro convertible parked outside the Monroe shop"),
                ("ct-shop-05",
                 "A tan convertible top with its glass rear window"),
                ("ct-shop-09",
                 "The black Camaro convertible in profile"),
                ("ct-shop-10",
                 "A convertible in the bay with the new top taped while it sets"),
                ("ct-shop-13",
                 "The yellow-striped Camaro from the rear, tan top fitted"),
            ],
        },
        "review_taglines": {
            "Robert Danneman": "Headliner and console leather",
            "Charles Monk": "Headliner replacement",
            "Ozzie Pagan": "Sunroof shade",
            "Lauren Corgan": "Drove an hour",
            "charmaine sealey": "Repeat customer",
        },
        "faq": {
            "label": "Before you call",
            "h2": "Answers first",
            "items": [
                ("How much does a convertible top cost?",
                 "It comes down to three things: the material, whether the rear window is "
                 "heated glass or plastic, and what the frame and pads underneath need. We "
                 "quote by calling the top manufacturer for your exact car and adding our "
                 "labour, so the number is built from your vehicle rather than an average. "
                 "The estimate is free and itemised across all three."),
                ("Cloth or vinyl — which should I have?",
                 "Vinyl holds up well in Carolina sun and is usually the sensible choice on a "
                 "daily driver. Cloth, Stayfast in particular, is correct on most classics and "
                 "ages more gracefully. We keep material here and will put it on the car in "
                 "daylight before you decide, because colours read completely differently "
                 "outdoors."),
                ("Does the rear window come with it?",
                 "Yes. A heated glass rear window comes as part of the top on nearly "
                 "everything we fit. In years of doing this only one car — a Mercedes — has "
                 "needed a window built specially."),
                # This one exists because people genuinely ask it, and because
                # "ragtop repair" and "convertible roof repair near me" are both
                # live keywords whose words appeared nowhere on the page. It
                # answers the question honestly AND routes the fixed-roof half of
                # the confusion to the vinyl tops page, which is the other side of
                # the "vinyl top" overlap noted in campaign_spec's AMBIGUOUS list.
                ("Is a ragtop the same thing as a convertible top?",
                 "Yes. Ragtop, soft top and convertible roof all mean the same job: fabric "
                 "over a folding frame with a rear window in it. If your roof folds down, you "
                 "are on the right page. If it is a covering bonded to a fixed steel roof "
                 "that does not fold, that is a vinyl top — we do those too, and they are "
                 "priced completely differently."),
                ("Do you do Jeep soft tops?",
                 "Yes, those are routine here alongside the classics and the late-model "
                 "convertibles."),
                ("What if there is rust under the old top?",
                 "We deal with it here rather than sending it out, and we will not fit a new "
                 "top over rust. Water sits in the channels and around the seals, so that is "
                 "exactly where it turns up. You will be told what we find with the old top "
                 "off, before the new one is ordered."),
            ],
        },
        "form": {
            "big": "Send us a photo of the car",
            "p": ("A picture with the top up, plus the year, make and model, is usually "
                  "enough to get you a number."),
            "why": ["Free, and itemised across fabric, window and frame",
                    "Nobody will chase you afterwards",
                    "We will tell you if the frame needs looking at in person"],
            "subject": "CONVERTIBLE TOP estimate request from autotopsandtrim.com",
            "placeholder": ("Top up or down, the rear window, anything you have noticed about "
                            "the frame or the way it folds&hellip;"),
            "filenote": "One photo with the top up and one of the rear window helps most.",
        },
    },

    # --------------------------------------------------------------- VINYL TOPS
    # The smallest group at 30/mo. It gets a page anyway because the searches
    # that do happen are dead-specific and there is almost nothing to compete
    # with. Owner facts: the red top IS vinyl, he does all top types, he handles
    # rust himself rather than sending it out, and he will not put a top over
    # rust.
    #
    # "vinyl top" is deliberately NOT negated out of the Convertible Tops ad
    # group — see AMBIGUOUS in campaign_spec.py. A convertible top is often made
    # of vinyl, and that overlap is honest rather than a routing mistake.
    {
        "slug": "vinyl-tops.html",
        "title": "Vinyl Top Replacement in Monroe, NC | Landau and Padded Roofs",
        "desc": ("Vinyl and padded top replacement in Monroe, NC. Peeling, split or rotted "
                 "roof coverings stripped back, rust dealt with and re-covered. "
                 "Free estimates — (980) 385-8101."),
        "eyebrow": "Vinyl tops",
        "h1": "A vinyl top fails from underneath, where you cannot see it.",
        "lead": ("The padding under the covering holds water against the roof skin. By the "
                 "time the vinyl splits at a seam, the question is not the vinyl — it is what "
                 "the water has been doing to the metal."),
        "hero": ("vinyl-top-burgundy-finished-in-the-bay",
                 "A finished burgundy vinyl top fitted on a car in the shop bay"),
        "argument": {
            "label": "Why they go",
            "h2": "The covering is the symptom. The padding is the cause.",
            "sub": ("A vinyl roof is a covering bonded over padding on a steel roof. The "
                    "padding soaks up water and holds it against the metal, so the roof rots "
                    "from underneath while the top still looks passable from the pavement. "
                    "The split you can see at the seam is usually the last thing to happen, "
                    "not the first."),
            "pull": ("We will not put a new top over rust.",
                     "And we deal with the rust here rather than sending the car out and "
                     "adding somebody else's markup to your bill."),
            "myth_title": "Why patching it does not hold",
            "myths": [
                ("Re-gluing a lifting edge", "can buy a season if the material is still soft. "
                                             "Once it has gone hard, it is a recover."),
                ("A patch over the split", "hides the one place you could have seen what the "
                                           "water was doing underneath."),
                ("Leaving it because it is only cosmetic", "is how a covering problem becomes "
                                                           "a roof skin problem."),
                ("Cutting around the mouldings", "leaves an edge you will notice every time "
                                                 "you walk up to the car."),
            ],
        },
        "steps": {
            "label": "What we do",
            "h2": "Stripped to the metal, then re-covered",
            "sub": ("The same car at three stages. The middle picture is the part nobody "
                    "sees and the part that decides how long the new top lasts."),
            "cards": [
                ("vinyl-top-before-roof-covering-rotted",
                 "A vinyl roof covering rotted through to the padding underneath",
                 "50%", "What comes off",
                 ["Old covering and padding stripped back",
                  "Mouldings and trim removed, not cut around",
                  "The roof skin uncovered so it can be seen"]),
                ("vinyl-top-roof-stripped-trim-removed",
                 "The same roof stripped bare with the mouldings removed, ready for the new "
                 "top",
                 "48%", "The metal gets checked",
                 ["Rust found and dealt with here, not sent out",
                  "Skin cleaned back to a sound surface",
                  "No new top goes on until it is right"]),
                ("vinyl-top-after-opera-window-detail",
                 "The finished vinyl top wrapped around the opera window on the same car",
                 "50%", "New covering fitted",
                 ["Grained vinyl matched to your paint or interior",
                  "Wrapped properly around opera windows and quarters",
                  "Mouldings refitted once the top is on"]),
            ],
        },
        "pairs": [
            ("vinyl-top-before-roof-covering-rotted",
             "A vinyl roof covering rotted through to the padding",
             "vinyl-top-burgundy-finished-in-the-bay",
             "The same car with the finished burgundy vinyl top fitted",
             "The same car &mdash; rotted through, then re-covered"),
            ("vinyl-top-before-peeling-at-rear",
             "Another car with the vinyl covering lifting and peeling at the rear",
             "vinyl-top-after-burgundy-fitted",
             "A finished vinyl top over the roof and rear quarter",
             "Peeling at the rear &middot; a finished top on another car"),
        ],
        "work": {
            "label": "Out of this shop",
            "h2": "Vinyl and padded tops out of this shop",
            "sub": ("Photographed in the bay at 4209 W Hwy 74, Monroe. Full vinyl roofs, "
                    "landau and half tops, and padded cabriolet-style roofs."),
            # FOUR TILES, not eight. There are only six vinyl-top photographs in
            # the whole catalogue and two of them are already the step cards
            # above, so a longer strip would have to repeat one — which dupcheck
            # correctly failed on. Four fills the desktop row exactly. This is a
            # photo shortage, not a layout choice: more vinyl jobs shot means a
            # longer strip here and nothing else to change.
            "photos": [
                ("vinyl-top-after-burgundy-fitted",
                 "A finished burgundy vinyl top over the roof and rear quarter"),
                ("vinyl-top-before-peeling-at-rear",
                 "A vinyl covering lifting and peeling at the rear"),
                ("process-materials-vinyl-and-fabric-rolls",
                 "Rolls of vinyl and top material kept at the shop"),
                ("shot-275-hand-holding-vinyl-sample",
                 "A vinyl sample held up against the car before the colour is chosen"),
            ],
        },
        "review_taglines": {
            "Robert Danneman": "Headliner and console leather",
            "Charles Monk": "Headliner replacement",
            "Ozzie Pagan": "Sunroof shade",
            "Lauren Corgan": "Drove an hour",
            "charmaine sealey": "Repeat customer",
        },
        "faq": {
            "label": "Before you call",
            "h2": "Answers first",
            "items": [
                ("Is a vinyl top the same job as a convertible top?",
                 "No. A vinyl top is a covering bonded to a fixed steel roof; a convertible "
                 "top is fabric over a folding frame with a rear window in it. We do both and "
                 "they are priced completely differently. If your roof does not fold, this is "
                 "the right page — if it does, see our convertible tops page."),
                ("Is there rust under my vinyl top?",
                 "Often there is some, and it is the real reason not to leave a failed top on "
                 "the car. We strip the roof back and look at the metal before quoting the "
                 "covering, not after — and we handle the rust here rather than sending it "
                 "out. We will not fit a new top over it."),
                ("Can a vinyl top be repaired instead of replaced?",
                 "A lifting edge or an open seam can sometimes be re-bonded while the material "
                 "is still soft. Once it has gone hard, split across the top, or rotted where "
                 "water has been sitting, it is a recover. Bring it by and we will tell you "
                 "honestly which one you have."),
                ("Can you match the colour to my paint?",
                 "That is usually where the job starts. Grained vinyl comes in a wide colour "
                 "range and we will lay samples on the car in daylight before anything is "
                 "ordered, because a colour that looks right indoors can read completely "
                 "differently against your paint outside."),
                ("How long does it take?",
                 "It depends on what is under the old covering. A sound roof stripped and "
                 "re-covered is straightforward; rust or a damaged skin adds time. We will "
                 "tell you that with the old top off rather than spring it on you later."),
            ],
        },
        "form": {
            "big": "Send us a photo of the roof",
            "p": ("A picture of the roof and anywhere it has lifted or split, plus the year, "
                  "make and model, is usually enough for an estimate."),
            "why": ["Free, and no obligation",
                    "Nobody will chase you afterwards",
                    "If the metal needs looking at in person, we will say so"],
            "subject": "VINYL TOP estimate request from autotopsandtrim.com",
            "placeholder": ("Where it has lifted or split, any bubbling around the rear "
                            "window or the mouldings&hellip;"),
            "filenote": "A photo of the roof and one of the rear window edge helps most.",
        },
    },
]


def build_landings():
    for cfg in LANDINGS:
        _lb_reset()
        landing_page(cfg, REVIEWS, pages)


def build_privacy():
    """The privacy policy.

    Written from what the site ACTUALLY does, not from a template: the form
    fields in quote_form()/landing_form(), Formspree as the processor, Google
    Workspace for the mail, the Google Ads conversion tag on TRACKED_PAGES, and
    the SMS consent checkbox. If any of those change, this page changes with it —
    a policy describing things the site does not do is worse than none, because
    it is a published claim that is not true.

    Deliberately NOT in TRACKED_PAGES: a privacy policy carrying advertising
    cookies is a bad look and there is nothing to measure here.
    """
    _lb_reset()
    p = "privacy.html"
    h = head("Privacy Policy | Auto Tops and Trim, Monroe NC",
             "How Auto Tops and Trim in Monroe, NC collects, uses and protects the "
             "information you send through our website, including quote requests, "
             "photos and text message consent.", p)
    h += header("")
    h += f"""<section class="hero">
  <div class="wrap">
    <div class="stack">{shead("", "Privacy")}
      <h1>Privacy Policy</h1>
      <p class="lead">This explains what we collect when you contact us, why we
         collect it, and what we do with it. Last updated 10 August 2026.</p>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack">
    <div class="stack">{shead("01", "Who we are")}
      <p>Auto Tops and Trim, 4209 W Hwy 74, Monroe, NC 28110.
         Telephone <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.
         Email <a href="mailto:{EMAIL}">{EMAIL}</a>.
         This policy covers {SITE}.</p></div>

    <div class="stack">{shead("02", "What we collect")}
      <p>We only collect what you choose to send us. If you fill in a quote or
         estimate form on this site, that is:</p>
      <ul class="ticks">
        <li>Your first and last name</li>
        <li>Your phone number and email address</li>
        <li>Your vehicle year, make and model</li>
        <li>A description of the work you need</li>
        <li>Any photographs you choose to attach</li>
        <li>Whether you agreed to receive text messages about your estimate</li>
      </ul>
      <p>You can call the shop instead and send us nothing at all. Only the name,
         phone, email and description are required on the form &mdash; the vehicle
         details and photographs are optional, though they usually let us quote
         without you bringing the vehicle in.</p>
      <p><b>A note on photographs.</b> Pictures of a vehicle often show a licence
         plate, a driveway or a house. We use them to prepare your quote. We do not
         publish a customer's photograph on this website or anywhere else without
         asking that customer first.</p></div>

    <div class="stack">{shead("03", "Why we collect it and what we do with it")}
      <p>To reply to you with an estimate and to carry out work you ask us to do.
         That is the whole purpose. We do not sell your information, we do not rent
         it, and we do not pass it to anyone for their own marketing.</p></div>

    <div class="stack">{shead("04", "Who processes it for us")}
      <ul class="ticks">
        <li><b>Formspree</b> receives and stores submissions from our forms, and
            emails them to us. Their privacy policy is at
            <a href="https://formspree.io/legal/privacy-policy" rel="nofollow noopener"
               target="_blank">formspree.io/legal/privacy-policy</a>.</li>
        <li><b>Google Workspace</b> hosts the email account those messages arrive in.</li>
        <li><b>Vercel</b> hosts this website and keeps standard server logs.</li>
        <li><b>Google Ads</b> measures which adverts lead to enquiries. See below.</li>
      </ul></div>

    <div class="stack">{shead("05", "Text messages")}
      <p>The text message box on our forms is optional and is never ticked for you.
         If you tick it, you are agreeing to let us text you about your estimate.
         Message and data rates may apply. Reply <b>STOP</b> to any message and we
         will stop texting you. Consent to texts is not a condition of getting a
         quote or having work done.</p></div>

    <div class="stack">{shead("06", "Cookies and advertising")}
      <p>Most of this website uses no cookies and no tracking scripts at all. On the
         pages we advertise, and on the confirmation page shown after a form is sent,
         we use Google Ads conversion tracking. It tells us that an advert led to an
         enquiry. It does not tell us who you are, and we do not use it to build a
         profile of you.</p>
      <p>You can control or block these cookies in your browser settings, and you can
         review Google's own handling of this data at
         <a href="https://policies.google.com/technologies/partner-sites"
            rel="nofollow noopener" target="_blank">policies.google.com/technologies/partner-sites</a>.
         Blocking them does not stop you using this site or contacting us.</p></div>

    <div class="stack">{shead("07", "How long we keep it")}
      <p>We keep enquiries and job records for as long as we need them to serve you
         and to keep proper business records. If you would like your enquiry deleted,
         ask us and we will delete it.</p></div>

    <div class="stack">{shead("08", "Your choices")}
      <p>You can ask us what we hold about you, ask us to correct it, or ask us to
         delete it. You can withdraw text message consent at any time by replying
         STOP. To do any of these, call
         <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or email
         <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div>

    <div class="stack">{shead("09", "Children")}
      <p>This site is for our customers and is not directed at children, and we do
         not knowingly collect information from them.</p></div>

    <div class="stack">{shead("10", "Changes")}
      <p>If we change how we handle your information we will update this page and
         change the date at the top of it.</p></div>
  </div>
</section>
"""
    h += footer()
    pages.append(p)
    return write(p, h)


def build_thanks():
    """Where Formspree lands the visitor after a successful submit.

    This page is the entire form-conversion mechanism. `head()` gives it the
    Google tag AND the conversion event automatically because its slug is in
    TRACKED_PAGES — nothing about the tracking is written here, so this page
    cannot drift from the rule.

    It is deliberately plain and deliberately useful: it repeats the reply
    promise so the visitor knows what happens next, and offers the phone number
    for anyone who would rather not wait. A dead-end "thanks!" page wastes the
    one moment the visitor is most engaged.
    """
    _lb_reset()
    p = THANKS_PAGE
    h = head("Thank you | Auto Tops and Trim, Monroe NC",
             "Your estimate request has been sent. We reply to every request "
             "within one hour during shop hours.", p)
    h += header("contact.html")
    h += f"""<section class="hero">
  <div class="wrap">
    <div class="stack">{shead("", "Request sent")}
      <h1>Thanks &mdash; we have your request</h1>
      <p class="lead">{REPLY_PROMISE}. If you sent photos, they came through with it,
         and that is usually enough for us to give you a number without you bringing
         the vehicle in.</p>
      <div class="btnrow">
        <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn-ghost" href="before-after.html">See our work</a>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap stack">
    <div class="center stack">{shead("01", "What happens next", center=True)}
      <h2>We read it, then we call you</h2>
      <p class="lead">Every request is read by the shop, not a call centre. If we need
         another photo or a measurement to quote it properly, we will ask &mdash; we would
         rather ask than guess at a price.</p></div>
  </div>
</section>
"""
    h += footer()
    pages.append(p)
    return write(p, h)


# ============================================================== SITEMAP / ROBOTS
def build_meta():
    _lb_reset()
    # Clean URLs here too — a sitemap listing .html would hand Google a list of
    # URLs that all redirect, and the canonicals point elsewhere.
    # Paused trades stay out: a sitemap entry is a request to index, and those
    # three pages carry noindex. Asking Google to crawl a page that tells it not
    # to index is a contradiction, and Search Console reports it as one.
    urls = "".join(
        f"<url><loc>{SITE}{public_path(pg)}</loc>"
        f"<changefreq>monthly</changefreq>"
        f"<priority>{'1.0' if pg == 'index.html' else '0.8'}</priority></url>"
        # THANKS_PAGE is excluded for the same reason it is noindex: it exists
        # only as a post-submit redirect target, and a sitemap entry is a request
        # to index a page that says not to.
        for pg in pages if pg not in PAUSED_SERVICES and pg != THANKS_PAGE)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          f"{urls}</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    build_home()
    build_services_index()
    build_services()
    build_landings()
    build_gallery()
    build_process()
    build_before_after()
    build_about()
    build_careers()
    build_contact()
    build_privacy()
    build_thanks()
    build_blog()
    build_meta()
    print(f"pages written: {len(pages)}")
    for pg in pages:
        print("  ", pg)
