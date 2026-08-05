"""Page content for autotopsandtrim.com. Run this to emit the whole site."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_site import (  # noqa: E402
    IMAGES, SITE, PHONE_DISPLAY, PHONE_TEL, OUT,
    img, has, head, header, footer, cta, shead, quote_form, write, NAV, SERVICES, SCHEMA,
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
    ("Mr. Hopton restored my sunroof shade back to new condition. He even allowed me to watch "
     "the process. I recommend him 100% for all of your reupholstery needs. Thank you!",
     "Ozzie Pagan", "Local Guide &middot; 15 reviews", "8 months ago", "#2F6FB0"),
    ("Excellent work. We drove an hour to get our sunroof fixed and we were very happy with "
     "the service. Highly recommend!",
     "Lauren Corgan", "15 reviews", "11 months ago", "#8A5FA6"),
    # Charles Monk's review is truncated by Google's "More" link; only the complete
    # sentences visible on the profile are quoted here.
    ("Fantastic service. The job was done quickly, while I waited. The price was cheaper than "
     "what most people were charging here locally.",
     "Charles Monk", "Local Guide &middot; 8 reviews", "a month ago", "#B5732E"),
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


def review_card(q, who, sub, when, colour):
    initial = who.strip()[0].upper()
    return (f'<div class="review">'
            f'<div class="rev-top">'
            f'<span class="avatar" style="background:{colour}" aria-hidden="true">{initial}</span>'
            f'<span class="rev-id"><span class="rev-name">{who}</span>'
            f'<span class="rev-sub">{sub}</span></span></div>'
            f'<div class="rev-line">{stars()}<span class="rev-date">{when}</span></div>'
            f'<blockquote>{q}</blockquote></div>')


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
        "Free estimates — call (980) 385-8101.", p)
    h += header(p)

    # Hero slideshow. Deliberately NO per-slide captions: the inherited filenames
    # are unreliable (see HANDOFF open item 2), so the imagery rotates without
    # making any claim about what each individual photo shows.
    hero_slides = [
        "hero-best-finished-vehicle-wide-full-color",
        "g19-mercedes-gla-interior-work",
        "marine-boat-cushions-canvas",
        "custom-motorcycle-seat-upholstery-close-up",
    ]
    n_slides = len(hero_slides)
    slides = "".join(
        f'<figure style="animation-delay:{i * (20 / n_slides):.1f}s">'
        f'{img(b, "Upholstery work by Auto Tops and Trim in Monroe, NC", "(min-width:900px) 52vw, 100vw", eager=(i == 0))}'
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
        {img('marine-boat-cushions-canvas', 'Marine upholstery and boat cushions', HALF)}
        <span class="cat">Marine</span>
        <div class="pbody"><h3>Marine Upholstery</h3>
          <p>Boat canvas tops, cushions, helm trim and weather-resistant marine materials.</p>
          <span class="go">See the work</span></div>
      </a>
      <a class="pcard" href="motorcycle-seats.html">
        {img('motorcycle-custom-seat', 'Custom motorcycle seat upholstery', HALF)}
        <span class="cat">Motorcycle</span>
        <div class="pbody"><h3>Motorcycle Upholstery</h3>
          <p>Custom seats designed for comfort, durability and performance.</p>
          <span class="go">See the work</span></div>
      </a>
      <a class="pcard" href="aviation-upholstery.html">
        {img('aviation-cabin-seats', 'Aircraft cabin seat upholstery', HALF)}
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
      <p class="lead">A few pieces out of the Monroe shop &mdash; cars, trucks, boats and bikes.</p>
    </div>
    <div class="masonry">{masonry_tiles([
        ('g01-camaro-ss-new-convertible-top', 'Camaro SS — new convertible top', 'Automotive'),
        ('g16-cadillac-convertible-red-interior', 'Cadillac — red interior', 'Automotive'),
        ('g22-marine-cushions-and-helm-trim', 'Marine cushions and helm trim', 'Marine'),
        ('headliner-install', 'Headliner, fitted and finished', 'Automotive'),
        ('g06-ford-f1-cab-seat-carpet-and-trim', 'Ford F1 — seat, carpet and trim', 'Automotive'),
        ('custom-motorcycle-seat-upholstery-close-up', 'Stitched motorcycle seat', 'Motorcycle'),
        ('g09-truck-cab-black-seat-red-stitch', 'Truck cab — black seat, red stitch', 'Automotive'),
        ('aircraft-interior-seat-upholstery', 'Aircraft cabin seating', 'Aviation'),
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
        tiles = "".join(
            f'<figure class="tile">{img(ph, cap or h1, THIRD)}'
            + (f"<figcaption>{cap}</figcaption>" if cap else "")
            + "</figure>"
            for ph, cap in zip(photos, caps)
        )
        h += f"""<section class="band tint">
  <div class="wrap stack">
    <div class="stack">{shead("02","Recent work")}<h2>Jobs out of this shop</h2></div>
    <div class="grid g3">{tiles}</div>
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
        "convertible-top-after",
        [("Materials", ["Quality vinyl — holds up well in Carolina sun",
                        "Canvas cloth — correct on a classic, ages gracefully",
                        "Samples shown in the shop before you decide"]),
         ("Windows", ["Heated glass rear windows",
                      "Plastic curtain replacement",
                      "Often the reason the top failed first"]),
         ("The frame underneath", ["Collapsed pad replacement",
                                   "Bent bow straightening",
                                   "Checked before we quote, not after"])],
        ["g01-camaro-ss-new-convertible-top", "g05-burgundy-cloth-top-rear-window",
         "g17-cadillac-top-and-interior-finished", "convertible-top-replacement-and-finish",
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
         "Cadillac — top and interior finished", "Convertible top replacement and finish",
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
        ["g06-ford-f1-cab-seat-carpet-and-trim", "g07-bench-seat-red-piping-in-the-shop",
         "g09-truck-cab-black-seat-red-stitch", "headliner-install",
         "g11-carpet-fitted-and-trimmed", "g19-mercedes-gla-interior-work",
         "g12-shift-boot-and-carpet-detail", "g13-sound-deadening-before-carpet",
         "automotive-interior-restoration-detail"],
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
        ["Ford F1 — seat, carpet and trim", "Bench seat — red piping",
         "Truck cab — black seat, red stitch", "Headliner install",
         "Carpet fitted and trimmed", "Mercedes GLA — interior work",
         "Shift boot and carpet detail", "Sound deadening before carpet",
         "Interior restoration detail"])

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
        ["g22-marine-cushions-and-helm-trim", "marine-boat-cushions-canvas",
         "marine-canvas-cushions", "boat-upholstery-projects-at-the-shop",
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
        ["Marine cushions and helm trim", "Boat cushions and canvas", "Marine canvas and cushions",
         "Boat upholstery at the shop", "Marine materials and project parts"])

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
        ["aircraft-cabin-upholstery-craftsmanship", "aviation-cabin-seats",
         "aircraft-interior-seat-upholstery"],
        [("Do you do full cabin interiors?",
          "Yes — seating, side panels, carpet and trim, finished consistently across the cabin."),
         ("Can I bring just the seats?",
          "Absolutely, and it is often the easiest way to do it. Remove them and bring them to "
          "the shop in Monroe."),
         ("How is aviation work different from automotive?",
          "The standard of finish and the attention to weight and fit are higher, and the "
          "materials differ. It is the same craft, held to a tighter tolerance.")],
        ["Aircraft cabin craftsmanship", "Aviation cabin seats", "Aircraft interior seating"])

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
        ["motorcycle-custom-seat", "custom-bike-seat",
         "custom-motorcycle-seat-upholstery-close-up"],
        [("Do I need to bring the whole bike?",
          "No — take the seat off and bring it in. That is how most of these jobs start."),
         ("Can you make the seat taller or lower?",
          "Often yes. Reshaping the foam can change the height and the riding position. Tell us "
          "what is uncomfortable and we will talk through the options."),
         ("Can you do a custom stitch pattern?",
          "Yes. Diamond, pleated, contrast thread, two-tone — bring a picture of what you want "
          "and we will tell you what is achievable on your pan.")],
        ["Custom motorcycle seat", "Custom bike seat", "Stitched seat detail"])

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
        ("convertible-tops.html", "Convertible Tops", "convertible-top-after",
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
        ("marine-upholstery.html", "Marine Upholstery", "marine-canvas-cushions",
         "Boat seating, helm trim, cushions and canvas in materials built for sun, "
         "standing water and salt.",
         ["UV-stabilised marine vinyl", "Quick-dry foam", "Solution-dyed canvas"]),
        ("aviation-upholstery.html", "Aviation Upholstery", "aircraft-cabin-upholstery-craftsmanship",
         "Cockpit and cabin interiors, seating, panels and carpet. A trade almost nobody "
         "else in the region offers.",
         ["Cockpit and cabin seats", "Side panels and trim", "Cabin carpet"]),
        ("motorcycle-seats.html", "Motorcycle Seats", "custom-bike-seat",
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
GALLERY = [
    ("g01-camaro-ss-new-convertible-top", "Camaro SS — new convertible top", "Automotive"),
    ("g18-camaro-ss-profile", "Camaro SS — profile", "Automotive"),
    ("g16-cadillac-convertible-red-interior", "Cadillac convertible — red interior", "Automotive"),
    ("g17-cadillac-top-and-interior-finished", "Cadillac — top and interior finished", "Automotive"),
    ("g15-1969-cadillac-profile", "1969 Cadillac — profile", "Automotive"),
    ("g05-burgundy-cloth-top-rear-window", "Burgundy cloth top — rear window", "Automotive"),
    ("g06-ford-f1-cab-seat-carpet-and-trim", "Ford F1 cab — seat, carpet and trim", "Automotive"),
    ("g07-bench-seat-red-piping-in-the-shop", "Bench seat — red piping", "Automotive"),
    ("g08-cushion-and-armrest-trimmed", "Cushion and armrest — trimmed", "Automotive"),
    ("g09-truck-cab-black-seat-red-stitch", "Truck cab — black seat, red stitch", "Automotive"),
    ("g10-bel-air-new-carpet-going-in", "Bel Air — new carpet going in", "Automotive"),
    ("g11-carpet-fitted-and-trimmed", "Carpet fitted and trimmed", "Automotive"),
    ("g12-shift-boot-and-carpet-detail", "Shift boot and carpet detail", "Automotive"),
    ("g13-sound-deadening-before-carpet", "Sound deadening before carpet", "Automotive"),
    ("g19-mercedes-gla-interior-work", "Mercedes GLA — interior work", "Automotive"),
    ("headliner-install", "Headliner install", "Automotive"),
    ("classic-interior-finished", "Classic interior, finished", "Automotive"),
    ("automotive-interior-restoration-detail", "Interior restoration detail", "Automotive"),
    ("convertible-top-replacement-and-finish", "Convertible top replacement and finish", "Automotive"),
    ("automotive-ford-galaxie-top-after", "Ford Galaxie — top fitted", "Automotive"),
    ("seat-rebuild-after", "Seat rebuild — finished", "Automotive"),
    ("g22-marine-cushions-and-helm-trim", "Marine cushions and helm trim", "Marine"),
    ("marine-seating-and-interior-upholstery", "Marine seating and interior", "Marine"),
    ("marine-boat-cushions-canvas", "Boat cushions and canvas", "Marine"),
    ("marine-canvas-cushions", "Marine canvas and cushions", "Marine"),
    ("boat-upholstery-projects-at-the-shop", "Boat upholstery at the shop", "Marine"),
    ("upholstery-materials-and-marine-project-parts", "Materials and project parts", "Marine"),
    ("aircraft-interior-seat-upholstery", "Aircraft interior seating", "Aviation"),
    ("aircraft-cabin-upholstery-craftsmanship", "Aircraft cabin craftsmanship", "Aviation"),
    ("aviation-cabin-seats", "Aviation cabin seats", "Aviation"),
    ("motorcycle-custom-seat", "Custom motorcycle seat", "Motorcycle"),
    ("custom-bike-seat", "Custom bike seat", "Motorcycle"),
    ("custom-motorcycle-seat-upholstery-close-up", "Stitched seat detail", "Motorcycle"),
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
         "process-header-photo-wide"),
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
    <div class="hero-media">{img('process-header-photo-wide', 'Upholstery work in progress at the shop', HALF, eager=True)}</div>
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
    <div class="hero-media">{img('owner-shop-leadership-grayscale', 'Auto Tops and Trim shop leadership', HALF, eager=True)}</div>
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
      <figure class="tile">{img('services-strip-1', 'Upholstery materials and tools', QUARTER)}</figure>
      <figure class="tile">{img('services-strip-2', 'Door panel restoration in progress', QUARTER)}</figure>
      <figure class="tile">{img('services-strip-3', 'Seat frame rebuild', QUARTER)}</figure>
      <figure class="tile">{img('services-strip-4', 'Finished trim work', QUARTER)}</figure>
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
POSTS = [
    {
        "slug": "blog-convertible-top-cost-monroe-nc.html",
        "cat": "Convertible Tops", "date": "July 2026", "read": "4 min read",
        "photo": "g01-camaro-ss-new-convertible-top",
        "title": "How much does a convertible top replacement cost in Monroe, NC?",
        "excerpt": "What drives the price of a new top — material, window type, and the "
                   "condition of the frame underneath — plus what a fair quote looks like.",
        "body": [
            "A convertible top replacement is really three jobs in one: the fabric or vinyl top "
            "itself, the window, and whatever needs repairing on the frame and pads underneath. "
            "Most quotes people bring us from elsewhere only cover the first one.",
            "Material is the first fork in the road. A quality vinyl top costs less up front and "
            "holds up well in the Carolina sun. Canvas cloth costs more, looks correct on a "
            "classic, and ages more gracefully. We will show you both in person before you decide.",
            "The second factor is the rear window. A top with a heated glass window is a different "
            "job from one with a plastic curtain, and on older cars the window is often the reason "
            "the top failed in the first place.",
            "Third, the frame. If the pads are collapsed or the bows are bent, a new top will fit "
            "badly no matter how good the fabric is. We check that before quoting, which is why we "
            "ask you to bring the car in rather than quote from a photo.",
            "Bring your car by the shop in Monroe and we will walk it with you, show you material "
            "samples, and give you an itemized estimate at no cost.",
        ],
    },
    {
        "slug": "blog-marine-vinyl-vs-leather.html",
        "cat": "Marine", "date": "June 2026", "read": "3 min read",
        "photo": "marine-seating-and-interior-upholstery",
        "title": "Marine vinyl vs. automotive leather: what belongs on a boat",
        "excerpt": "Why the material that looks best in your car is the wrong choice on the water, "
                   "and what we specify for boat cushions and canvas instead.",
        "body": [
            "Leather is a wonderful material in a car interior. On a boat it is a maintenance "
            "problem: standing water, UV, and salt will dry it out and crack it in a season or two.",
            "For marine work we specify vinyl built for the water — UV-stabilized, "
            "mildew-resistant, and stitched with thread that will not rot. The foam matters just as "
            "much: quick-dry, reticulated foam lets water pass through instead of holding it "
            "against the cushion.",
            "Canvas tops follow the same logic. Solution-dyed acrylic holds color in full sun far "
            "longer than cheaper coated fabrics, and the difference shows up in year three, not "
            "year one.",
            "If your cushions are staying damp or your canvas has gone chalky, bring one piece by "
            "the shop and we will tell you honestly whether it needs recovering or replacing.",
        ],
    },
    {
        "slug": "blog-period-correct-or-upgraded-classic-interior.html",
        "cat": "Restoration", "date": "May 2026", "read": "5 min read",
        "photo": "classic-interior-finished",
        "title": "Period-correct or upgraded? Choosing an interior for a classic",
        "excerpt": "Restoring a classic interior means deciding how faithful to be. Here is how we "
                   "think about originality, comfort, and resale.",
        "body": [
            "Every classic interior project starts with one question: is this car going to shows, "
            "or is it going to be driven? The answer changes the material list.",
            "For a show car we chase originality — correct grain patterns, correct stitch "
            "spacing, correct carpet weave. Judges notice, and so do buyers.",
            "For a driver we keep the look and quietly improve the comfort: modern foam densities, "
            "better sound deadening under the carpet, and seat frames repaired properly instead of "
            "shimmed.",
            "You do not have to choose blind. We keep samples in the shop and can show you what "
            "period-correct and upgraded actually look like side by side.",
            "Bring the car to Monroe and we will build the spec with you before any cutting starts.",
        ],
    },
]


def build_blog():
    _lb_reset()
    p = "blog.html"
    h = head("Blog | Auto Tops and Trim, Monroe NC",
             "Advice on convertible tops, marine upholstery and classic interiors from a "
             "Monroe, NC upholstery shop trimming interiors since 1989.", p)
    h += header(p)
    cards = "".join(f"""<a class="card" href="{po['slug']}">
      {img(po['photo'], po['title'], THIRD, ratio='16/10')}
      <div class="card-body"><span class="meta">{po['cat']} &middot; {po['date']} &middot; {po['read']}</span>
      <h3>{po['title']}</h3><p>{po['excerpt']}</p>
      <span class="card-link">Read the article</span></div></a>""" for po in POSTS)
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

    for po in POSTS:
        schema = {
            "@context": "https://schema.org", "@type": "Article",
            "headline": po["title"], "description": po["excerpt"],
            "datePublished": "2026-07-01" if po["cat"] == "Convertible Tops" else "2026-06-01",
            "author": {"@type": "Organization", "name": "Auto Tops and Trim"},
            "publisher": {"@type": "Organization", "name": "Auto Tops and Trim"},
            "mainEntityOfPage": f"{SITE}/{po['slug']}",
        }
        ph = head(f"{po['title']} | Auto Tops and Trim", po["excerpt"], po["slug"], schema)
        ph += header("blog.html")
        body = "".join(f"<p>{t}</p>" for t in po["body"])
        ph += f"""<section class="band">
  <div class="wrap">
    <div class="article-head">
      <span class="meta">{po['cat']} &middot; {po['date']} &middot; {po['read']}</span>
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
    urls = "".join(
        f"<url><loc>{SITE}/{'' if pg == 'index.html' else pg}</loc>"
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
