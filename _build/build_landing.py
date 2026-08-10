"""The paid-search LANDING PAGE type for autotopsandtrim.com.

This is `_draft-headliner.html` (approved at DRAFT v15) turned into a generator.
Every one of the eight ad groups in `c:\\Claude Code\\att_ads` gets its own page
built from this one renderer, so the other seven are content swaps rather than
rebuilds.

WHY IT IS A SEPARATE PAGE TYPE FROM service_page()
  A service page is a browsing page: three columns of bullets, a photo strip, a
  FAQ. A landing page has to carry one argument from top to bottom and finish
  with the form ON the page, because the visitor arrived from an ad for one
  specific thing and a second click is where paid traffic leaks away.

WHAT IT KEEPS FROM THE SITE
  head() / header() / footer(), so these are still real site pages. Six of the
  eight URLs are in the main nav, in sitemap.xml and linked from ~20 blog posts;
  a nav-less page at those URLs would dead-end organic and blog traffic. The
  draft had no chrome only because it was prototyping the body.

WHY THE CSS IS SCOPED UNDER .lp
  The draft names a dozen classes that already exist in assets/site.css — .hero,
  .band, .card, .pair, .review, .quote, .faq, .btn, .wrap. Scoping every selector
  under .lp does two jobs at once: it stops the landing styles reaching the
  header and footer, and it adds one class of specificity so the landing rules
  beat their site.css namesakes inside the page body. The block is emitted after
  the stylesheet link, so ties go to the landing page too.

  The draft's own .callbar rules are DROPPED — footer() already emits the site's
  sticky call bar, and two fixed bars would stack.

RULES CARRIED OVER FROM THE USER'S CORRECTIONS ON THE DRAFT. These apply to all
eight pages and are not negotiable per-page:
  1. NEVER surface a review count. "5.0 across nine" means every single review is
     five stars, so the honest, stronger line is that nobody has ever left a bad
     one. "9 reviews" and "two of them are headliners" were both cut.
  2. NEVER deny an accusation nobody made. "Nothing here is a stock photo" and
     "nothing bought, nothing written by us" were both cut. Three strikes.
  3. Replicate the site's components, do not invent them. The review marquee and
     the .pair deck are the site's own, lifted with their context.
  4. Mobile is not optional. The <900px pass at the bottom is load-bearing.
  5. Photo captions come from OPENING the photo, never from the filename.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_site import (  # noqa: E402
    PHONE_DISPLAY, PHONE_TEL, REPLY_PROMISE, FORM_ENDPOINT, FORM_ACCEPTS_FILES,
    SITE, THANKS_PAGE,
    img, head, header, footer, preload_image, write, split_callbar,
)

HERO_SIZES = "(min-width:900px) 46vw, 100vw"
CARD_SIZES = "(min-width:760px) 33vw, 100vw"
PAIR_SIZES = "(min-width:760px) 25vw, 50vw"
STRIP_SIZES = "(min-width:700px) 25vw, 50vw"


# ============================================================================
# CSS — the draft's own stylesheet, every selector scoped under .lp
# ============================================================================
LANDING_CSS = """<style>
/* ==========================================================================
   LANDING PAGE STYLES — scoped to .lp so they cannot touch the site header,
   the footer or the sticky call bar, all of which come from site.css.
   ========================================================================== */
.lp{
  --blue:#2F6FB0; --blue-lt:#5E9BD9; --btn:#1E5C99;
  --ink:#2A2E33; --ink-70:#5A626B; --ink-55:#7C858F;
  --tint:#E8EEF6; --tint2:#F1F5F9; --rule:#D9E2ED;
  --dark:#23282E; --deep:#16344F;
  --r-media:16px; --r-card:14px; --r-ctl:8px;
  /* ACCENT SWAP LIVES HERE. Set --accent to a hot colour (e.g. #E2622A orange)
     and the buttons, numerals and rules go warm without touching anything else.
     Currently blue, matching the rest of the site. */
  --accent:#2F6FB0;
  background:#fff;color:var(--ink);
  font-family:'Archivo',system-ui,-apple-system,'Segoe UI',sans-serif;
  font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
.lp h1,.lp h2,.lp h3,.lp h4{margin:0;font-weight:800;letter-spacing:-.028em;
  line-height:1.07;text-wrap:balance}
.lp p{margin:0}
.lp img{max-width:100%;display:block}
.lp a{color:var(--blue)}
.lp .wrap{max-width:1120px;margin:0 auto;padding:0 22px}
.lp .narrow{max-width:760px}

/* section header device — NN + dash + label */
.lp .shead{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.lp .shead .n{font-size:12px;font-weight:800;letter-spacing:.06em}
.lp .shead .dash{width:26px;height:2px;background:var(--blue-lt);flex:none}
.lp .shead .lab{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
  font-weight:700;color:var(--blue)}
.lp .on-dark .shead .n{color:#fff}
.lp .on-dark .shead .lab{color:var(--blue-lt)}

.lp .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;
  padding:15px 26px;font-weight:800;font-size:16.5px;text-decoration:none;
  border-radius:var(--r-ctl);letter-spacing:-.01em;border:2px solid transparent;
  transition:transform .12s ease,background .15s ease}
.lp .btn:hover{transform:translateY(-1px)}
.lp .btn-primary{background:var(--btn);color:#fff}
.lp .btn-primary:hover{background:#17497a}
/* btn-ghost DEFAULTS TO DARK TEXT, exactly as it does in site.css.
   This was `color:#fff` unscoped, which is correct in the hero and invisible
   everywhere else — the "See the full gallery" button under the photo strip sits
   on a WHITE band and was rendering white-on-white. It was in the DOM the whole
   time, which is why grepping the HTML kept saying it was present.
   site.css line ~197 does exactly this: dark by default, white only on a dark
   surface. Same lesson as the review marquee's edge mask — a component has to
   carry the surface it was designed for. */
.lp .btn-ghost{background:transparent;color:var(--ink);
  border-color:rgba(42,46,51,.25)}
.lp .btn-ghost:hover{background:rgba(42,46,51,.06)}
.lp .hero .btn-ghost,.lp .dark .btn-ghost,.lp .on-dark .btn-ghost,
.lp .cta .btn-ghost{color:#fff;border-color:rgba(255,255,255,.45)}
.lp .hero .btn-ghost:hover,.lp .dark .btn-ghost:hover,
.lp .on-dark .btn-ghost:hover,.lp .cta .btn-ghost:hover{background:rgba(255,255,255,.1)}
.lp .btn-dark{background:var(--ink);color:#fff}
.lp .btnrow{display:flex;flex-wrap:wrap;gap:12px}

/* ---------- 1. HERO ---------- */
.lp .hero{background:var(--dark);color:#fff;position:relative;overflow:hidden}
.lp .hero::before{content:"";position:absolute;inset:0;
  background:linear-gradient(115deg,#16344F 0%,#23282E 62%);opacity:.9}
/* the quilt — same device as the live site, faint */
.lp .hero::after{content:"";position:absolute;inset:0;opacity:.055;
  background-image:linear-gradient(45deg,#fff 25%,transparent 25%,transparent 75%,#fff 75%),
    linear-gradient(45deg,#fff 25%,transparent 25%,transparent 75%,#fff 75%);
  background-size:34px 34px;background-position:0 0,17px 17px}
.lp .hero .wrap{position:relative;z-index:2;display:grid;gap:34px;
  grid-template-columns:1fr;padding-top:56px;padding-bottom:56px}
.lp .hero h1{font-size:clamp(33px,6vw,56px);color:#fff;margin-bottom:16px}
.lp .hero .lead{font-size:clamp(16.5px,2.1vw,19px);color:#C9D6E4;max-width:52ch;
  margin-bottom:26px}
.lp .hero-media img{border-radius:var(--r-media);width:100%;height:100%;object-fit:cover;
  box-shadow:0 26px 60px rgba(0,0,0,.42)}
@media(min-width:900px){
  .lp .hero .wrap{grid-template-columns:1.08fr .92fr;align-items:center;
    padding-top:72px;padding-bottom:72px}
}

/* ---------- 2. TRUST STRIP ---------- */
.lp .trust{background:var(--deep);color:#fff}
.lp .trust .wrap{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;padding:0}
@media(min-width:820px){.lp .trust .wrap{grid-template-columns:repeat(4,1fr)}}
.lp .trust .t{padding:18px 20px;display:flex;flex-direction:column;gap:3px;
  box-shadow:1px 0 0 rgba(255,255,255,.11), 0 1px 0 rgba(255,255,255,.11)}
.lp .trust .big{font-size:19px;font-weight:800;letter-spacing:-.02em;
  display:flex;align-items:center;gap:.18em}
/* Inline SVG star, same approach as the footer social icons. Sized in em so it
   tracks the number. Moved up here when the duplicate stats band was cut. */
.lp .starmark{width:.72em;height:.72em;flex:none;fill:#F0B24A;transform:translateY(-.03em)}
.lp .trust .sm{font-size:12px;letter-spacing:.1em;text-transform:uppercase;
  font-weight:700;color:#93AFC9}

/* ---------- generic bands ---------- */
/* Site's band rhythm: shrinks properly on a phone instead of carrying desktop
   padding down. Was a flat 62px. */
.lp .band{padding:clamp(42px,7vw,72px) 0}
.lp .band.tint{background:var(--tint2)}
.lp .band.dark{background:var(--dark);color:#fff;position:relative;overflow:hidden}
/* Quilt dialled back for the dark BAND specifically. At the hero's .055 it sits
   on a flat dark ground with nothing else competing, so the checkerboard reads
   as a hard grid rather than texture. The hero keeps .055 because its gradient
   breaks it up. */
.lp .band.dark::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.022;
  background-image:linear-gradient(45deg,#fff 25%,transparent 25%,transparent 75%,#fff 75%),
    linear-gradient(45deg,#fff 25%,transparent 25%,transparent 75%,#fff 75%);
  background-size:34px 34px;background-position:0 0,17px 17px}
.lp .band.dark > .wrap{position:relative;z-index:2}
.lp .band.dark h2{color:#fff}
.lp .band h2{font-size:clamp(26px,3.9vw,38px);margin-bottom:14px}
.lp .band .sub{color:var(--ink-70);max-width:62ch;font-size:17px}
.lp .band.dark .sub{color:#B9C6D4}

/* ---------- 3. THE ARGUMENT ---------- */
.lp .arg{display:grid;gap:30px;grid-template-columns:1fr;align-items:start}
@media(min-width:900px){.lp .arg{grid-template-columns:1.05fr .95fr;gap:52px}}
.lp .pull{border-left:4px solid var(--blue);padding:6px 0 6px 22px;margin:26px 0}
.lp .pull b{display:block;font-size:clamp(20px,2.6vw,25px);font-weight:800;
  letter-spacing:-.028em;line-height:1.18;margin-bottom:8px}
.lp .pull span{color:var(--ink-70);font-size:16px}
.lp .myth{background:#fff;border:1px solid var(--rule);border-radius:var(--r-card);
  padding:22px 24px;box-shadow:0 1px 2px rgba(22,52,79,.05),0 10px 30px rgba(22,52,79,.06)}
.lp .myth h4{font-size:12px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-55);margin-bottom:14px}
.lp .myth ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:13px}
.lp .myth li{display:flex;gap:12px;align-items:flex-start;font-size:16px;
  color:var(--ink-70);line-height:1.5}
.lp .sq{width:8px;height:8px;background:var(--blue-lt);flex:none;margin-top:8px}
.lp .myth li b{color:var(--ink);font-weight:700}

/* ---------- 4. CARDS ---------- */
.lp .cards{display:grid;gap:16px;grid-template-columns:1fr;margin-top:30px}
@media(min-width:760px){.lp .cards{grid-template-columns:repeat(3,1fr)}}
.lp .card{background:#fff;border:1px solid var(--rule);border-radius:var(--r-card);
  display:flex;flex-direction:column;overflow:hidden}
/* These are phone photos, mostly PORTRAIT, and the subject is rarely dead centre.
   A 4/3 landscape crop threw away the whole frame and left sky and a door. Fixed
   height plus a per-card object-position (emitted inline by card_shot(), so the
   template stays reusable instead of hard-coding :nth-child rules) lands each
   one on its actual subject. */
.lp .card .shot{position:relative;line-height:0;background:var(--tint);
  height:250px;overflow:hidden}
.lp .card .shot img{width:100%;height:100%;object-fit:cover;object-position:center}
.lp .card .shot .step{position:absolute;left:14px;top:14px;z-index:2;
  width:38px;height:38px;border-radius:50%;background:var(--btn);color:#fff;
  display:flex;align-items:center;justify-content:center;
  font-size:15px;font-weight:800;letter-spacing:-.02em;
  box-shadow:0 4px 14px rgba(0,0,0,.35)}
.lp .card .body{padding:22px 22px 26px;display:flex;flex-direction:column;gap:13px;flex:1}
.lp .card .num{font-size:38px;font-weight:800;line-height:1;color:transparent;
  -webkit-text-stroke:1.5px var(--blue-lt)}

/* ---------- BEFORE / AFTER ---------- */
/* THE SITE'S PAIR DECK, lifted from assets/site.css (.pairs / .pair /
   .pair-shots / .pair-tag / .pair-arrow). This is the "The same job, twice"
   component off the home page. One comparison per card: the two shots butted
   together with a hairline between them, an arrow sitting on the join so the eye
   travels left to right, and the caption centred underneath. Square crops keep
   every card the same height, which is what fixes the alignment. */
.lp .pairs{display:grid;grid-template-columns:1fr;gap:clamp(12px,2vw,22px);
  padding-top:clamp(14px,2.5vw,26px)}
@media(min-width:760px){.lp .pairs{grid-template-columns:repeat(2,1fr)}}
.lp .pair{margin:0;display:flex;flex-direction:column;gap:7px;background:#fff;
  padding:8px 8px 10px;border-radius:14px;
  box-shadow:0 10px 26px rgba(22,52,79,.13);transition:transform .25s ease,box-shadow .25s ease}
.lp .pair:hover{transform:translateY(-4px);box-shadow:0 18px 36px rgba(22,52,79,.2)}
.lp .pair-shots{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:3px;
  border-radius:9px;overflow:hidden;background:var(--rule)}
.lp .pair-shot{position:relative;display:block;min-width:0}
.lp .pair-shot img{width:100%;aspect-ratio:1/1;object-fit:cover;border-radius:0;
  transition:transform .45s ease}
.lp .pair:hover .pair-shot:nth-child(2) img{transform:scale(1.06)}
.lp .pair-tag{position:absolute;top:7px;left:7px;z-index:2;padding:4px 8px;
  font-size:9.5px;font-weight:800;letter-spacing:.13em;text-transform:uppercase;
  color:#fff;background:rgba(20,25,31,.74);border-radius:5px}
.lp .pair-tag.after{background:var(--btn)}
.lp .pair-arrow{position:absolute;left:50%;top:50%;translate:-50% -50%;z-index:3;
  width:30px;height:30px;display:grid;place-items:center;border-radius:50%;
  background:#fff;color:var(--btn);font-size:15px;font-weight:800;
  box-shadow:0 3px 10px rgba(22,52,79,.28)}
.lp .pair figcaption{padding:1px 4px 0;text-align:center;font-size:13px;font-weight:700;
  letter-spacing:.02em;color:var(--ink-70)}
@media(max-width:759px){
  .lp .pair{padding:5px 5px 7px;border-radius:10px;gap:5px}
  .lp .pair-shots{gap:2px;border-radius:7px}
  .lp .pair-tag{font-size:8px;padding:3px 6px;letter-spacing:.08em;top:5px;left:5px}
  .lp .pair-arrow{width:24px;height:24px;font-size:12px}
  .lp .pair figcaption{font-size:11.5px}
}

/* ---------- STRIP ---------- */
.lp .strip{display:grid;gap:12px;grid-template-columns:repeat(2,1fr);margin-top:26px}
@media(min-width:700px){.lp .strip{grid-template-columns:repeat(4,1fr)}}
.lp .strip figure{margin:0;border-radius:var(--r-card);overflow:hidden;
  border:1px solid var(--rule);background:var(--tint);line-height:0}
.lp .strip img{width:100%;aspect-ratio:1/1;object-fit:cover;transition:transform .3s ease}
.lp .strip figure:hover img{transform:scale(1.04)}
.lp .card h3{font-size:19px}
.lp .card ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.lp .card li{display:flex;gap:11px;align-items:flex-start;font-size:15.5px;
  color:var(--ink-70);line-height:1.5}

/* ---------- 6. WORK ---------- */
.lp figure{margin:0;background:#fff;border:1px solid var(--rule);
  border-radius:var(--r-media);overflow:hidden}
.lp figcaption{padding:13px 16px;font-size:13.5px;font-weight:600;color:var(--ink-70);
  letter-spacing:-.005em}

/* ---------- 7. REVIEW ---------- */
/* LIFTED VERBATIM from assets/site.css (.revmarquee / .revtrack / .review).
   Do not re-invent this: the site already has a working review marquee and it
   should look identical here.
   NO EDGE MASK. The site can afford one because its review marquee sits on a
   DARK band -- dark cards fading into a dark ground is invisible. Here the band
   is light tint, so the same mask dissolved the cards into near-white and left a
   hard bright edge. Cards now simply run off the viewport, which is what a
   marquee should look like. (If this band is ever made dark, the site's
   7%/93% gradient can come back and will behave.)
   The keyframes are named lp-revscroll, not revscroll: @keyframes are global to
   the document and the site has its own marquee animation. */
.lp .revmarquee{overflow:hidden;position:relative;margin-top:26px;
  will-change:transform;contain:paint}
.lp .revtrack{display:flex;align-items:stretch;gap:clamp(26px,3vw,54px);width:max-content;
  padding-block:4px;padding-inline:clamp(13px,2vw,27px);
  animation:lp-revscroll 46s linear infinite}
.lp .revmarquee:hover .revtrack,.lp .revmarquee:focus-within .revtrack{animation-play-state:paused}
.lp .revtrack .review{width:min(80vw,390px);flex:none}
@keyframes lp-revscroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media(prefers-reduced-motion:reduce){
  .lp .revmarquee{overflow-x:auto;mask-image:none;-webkit-mask-image:none}
  .lp .revtrack{animation:none}
}
/* the site's card: avatar and name on top, then stars, then the quote */
.lp .review{display:flex;flex-direction:column;gap:14px;max-width:44ch;text-align:left;
  background:#2F343A;border:1px solid rgba(255,255,255,.11);
  border-radius:var(--r-card);padding:22px 22px 24px}
.lp .rev-top{display:flex;align-items:center;gap:12px}
.lp .rev-id{display:flex;flex-direction:column;gap:3px;min-width:0}
.lp .rev-name{font-weight:700;font-size:15px;color:#fff;letter-spacing:-.01em}
.lp .rev-sub{font-size:12.5px;color:#93A5B4}
.lp .rev-line{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.lp .review .stars{color:#F0B24A;letter-spacing:3px;font-size:15px}
.lp .review blockquote{margin:0;font-size:16.5px;font-weight:500;
  letter-spacing:-.008em;line-height:1.5;color:#E7EDF3}
.lp .review .tagline{font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
  font-weight:800;color:var(--blue-lt)}
.lp .review .av{width:42px;height:42px;border-radius:50%;color:#fff;flex:none;
  display:flex;align-items:center;justify-content:center;font-weight:800;font-size:15px}

/* ---------- 8. FAQ ---------- */
.lp .faq{display:flex;flex-direction:column;gap:0;margin-top:26px}
.lp details{border-bottom:1px solid var(--rule)}
.lp summary{cursor:pointer;list-style:none;padding:19px 40px 19px 0;position:relative;
  font-weight:700;font-size:17px;letter-spacing:-.015em}
.lp summary::-webkit-details-marker{display:none}
.lp summary::after{content:"+";position:absolute;right:6px;top:16px;font-size:24px;
  font-weight:400;color:var(--blue)}
.lp details[open] summary::after{content:"\\2013"}
.lp .ans{padding:0 0 20px;color:var(--ink-70);font-size:16px;max-width:70ch}

/* ---------- 9. FORM ---------- */
.lp .formwrap{display:grid;gap:34px;grid-template-columns:1fr;align-items:start}
/* Desktop is PINNED so pulling the map out of .formside changed nothing here:
   formside top-left, form down the right, map under formside exactly as before.
   On mobile these rules do not apply and the three children stack in DOM order —
   formside, form, map — which is the order the page actually wants. */
@media(min-width:940px){
  .lp .formwrap{grid-template-columns:.85fr 1.15fr;gap:52px;row-gap:22px}
  .lp .formwrap > .formside{grid-column:1;grid-row:1}
  .lp .formwrap > .quote{grid-column:2;grid-row:1/span 3}
  .lp .formwrap > .orcall{grid-column:1;grid-row:2}
  .lp .formwrap > .mapblock{grid-column:1;grid-row:3}
}
/* Mobile stacks these in DOM order: intro, form, "or skip the form", map. */
.lp .formwrap > .orcall{margin-top:0}
.lp .formside .big{font-size:clamp(26px,3.6vw,36px);font-weight:800;letter-spacing:-.03em;
  line-height:1.1;color:#fff;margin-bottom:14px}
.lp .formside p{color:#B9CBDC;font-size:16.5px;margin-bottom:22px;max-width:44ch}
.lp .formside .why{list-style:none;margin:0 0 26px;padding:0;display:flex;
  flex-direction:column;gap:11px}
.lp .formside .why li{display:flex;gap:11px;align-items:flex-start;font-size:15.5px;color:#C9D6E4}
.lp .formside .why .sq{background:var(--blue-lt)}
.lp .orcall{border-top:1px solid rgba(255,255,255,.16);padding-top:20px}
.lp .orcall .lbl{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;
  font-weight:700;color:#7F97AE;margin-bottom:12px}
/* DRAFT v16: the call line and the text-a-photo line, as two tappable rows.
   Texting a photo is a few seconds; the form is eight fields plus a file picker.
   On a page whose whole ask is "send us a photo", that gap is real. */
.lp .contactline{display:flex;align-items:center;gap:13px;text-decoration:none;
  padding:11px 13px;border-radius:var(--r-ctl);margin-bottom:8px;
  border:1px solid rgba(255,255,255,.16);transition:background .15s ease}
.lp .contactline:hover{background:rgba(255,255,255,.07)}
.lp .contactline .ci{width:36px;height:36px;border-radius:50%;flex:none;
  background:rgba(255,255,255,.11);display:flex;align-items:center;
  justify-content:center;font-size:17px;color:#fff}
.lp .contactline b{display:block;color:#fff;font-size:17px;font-weight:800;
  letter-spacing:-.02em;line-height:1.25}
.lp .contactline em{display:block;font-style:normal;font-size:12.5px;color:#9DB3C8}
/* Same embed as the contact page. An iframe needs no JavaScript of ours, and
   loading=lazy keeps it off the critical path. */
.lp .mapwrap{margin-top:22px;border-radius:var(--r-media);overflow:hidden;
  border:1px solid rgba(255,255,255,.18);line-height:0;
  box-shadow:0 14px 34px rgba(0,0,0,.28)}
.lp .mapwrap iframe{width:100%;height:210px;border:0;display:block;
  filter:grayscale(.25) contrast(1.04)}
.lp .maplbl{margin-top:11px;font-size:13.5px;color:#B9CBDC;line-height:1.5}
.lp .maplbl a{color:#fff;font-weight:700;text-decoration:none}
.lp .maplbl a:hover{color:var(--blue-lt)}

.lp .quote{background:#fff;border-radius:var(--r-card);padding:26px 24px 28px;
  display:flex;flex-direction:column;gap:15px;
  box-shadow:0 24px 60px rgba(0,0,0,.30)}
.lp .quote label{display:flex;flex-direction:column;gap:6px;font-size:13px;
  font-weight:700;letter-spacing:.02em;color:var(--ink)}
.lp .quote input[type=text],.lp .quote input[type=tel],.lp .quote input[type=email],
.lp .quote textarea{
  font:inherit;font-size:16px;font-weight:400;padding:12px 13px;
  border:1.5px solid var(--rule);border-radius:var(--r-ctl);background:#fff;
  color:var(--ink);width:100%}
.lp .quote input:focus,.lp .quote textarea:focus{outline:none;border-color:var(--blue);
  box-shadow:0 0 0 3px rgba(47,111,176,.16)}
.lp .quote textarea{resize:vertical;min-height:96px}
/* Split EARLY. These used to hold at one column until 560px, which meant a
   430px phone (iPhone 16 Pro Max) stacked all eight fields into one column and
   the form ran to roughly three full screens of scrolling — the single biggest
   mobile complaint on this page.
   The old note warned that three columns at 360px gives ~100px each. True, so
   .f3 waits for 400px (~118px a column, fine for Year / Make / Model, which take
   4-10 characters) while .f2 splits at 380px (~170px a column). Below that a
   phone really is too narrow and they stack, which is correct. */
.lp .f2,.lp .f3{display:grid;gap:13px;grid-template-columns:1fr}
@media(min-width:380px){.lp .f2{grid-template-columns:1fr 1fr}}
@media(min-width:400px){.lp .f3{grid-template-columns:repeat(3,1fr)}}
.lp .filefield input[type=file]{font:inherit;font-size:14px;font-weight:400;
  padding:11px;border:1.5px dashed var(--rule);border-radius:var(--r-ctl);
  background:var(--tint2);width:100%;cursor:pointer}
.lp .filefield input[type=file]:hover{border-color:var(--blue-lt);background:var(--tint)}
.lp .opt{font-weight:500;color:var(--ink-55);letter-spacing:0}
.lp .fieldnote{font-size:12.5px;font-weight:400;color:var(--ink-55);letter-spacing:0}
.lp .consent{flex-direction:row;align-items:flex-start;gap:10px;font-weight:400;
  font-size:13.5px;color:var(--ink-70);line-height:1.45}
.lp .consent input{margin-top:3px;width:17px;height:17px;flex:none;accent-color:var(--blue)}
.lp .quote .send{margin-top:4px;width:100%;font:inherit;font-size:17px;font-weight:800;
  padding:16px;border:0;border-radius:var(--r-ctl);background:var(--btn);color:#fff;
  cursor:pointer;letter-spacing:-.01em}
.lp .quote .send:hover{background:#17497a}
.lp .quote .promise{font-size:12.5px;color:var(--ink-55);text-align:center;font-weight:600}
/* honeypot — off-screen rather than display:none, some bots skip hidden fields */
.lp .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}

/* ---------- 10. CTA BAND ---------- */
.lp .cta{background:var(--deep);color:#fff;text-align:center}
.lp .cta h2{font-size:clamp(28px,4.4vw,42px);color:#fff;margin-bottom:14px}
.lp .cta p{color:#B9CBDC;max-width:56ch;margin:0 auto 26px}
.lp .cta .btnrow{justify-content:center}
.lp .cta .micro{margin-top:20px;font-size:11.5px;letter-spacing:.14em;
  text-transform:uppercase;font-weight:700;color:#7F97AE}

/* NO STICKY-BAR RULES HERE. The split call/text bar is the SITE's component now
   — `.callbar.split` in assets/site.css, emitted by footer() on every page.
   This block used to carry a second implementation of it and that was a bug
   waiting to happen: same component, two class names, two sets of mobile tuning,
   and only the landing pages getting the second one. If the bar needs changing,
   change it in site.css and every page moves together. */

/* ==========================================================================
   MOBILE PASS  (< 900px)
   The site's own rule: "it literally has to be perfect in mobile, no compromise."
   Everything here is a step-down, nothing changes structure, and none of it
   applies at 900px and up, so desktop is untouched.
   Note: NEVER put overflow on <html> or <body> — body overflow propagates to the
   viewport and breaks position:fixed on iOS, which is what stranded the sticky
   call bar last time. Sideways drag is contained by clipping sections instead.
   ========================================================================== */
@media (max-width:899px){
  .lp{font-size:16px}

  /* hero: tighter, and the two CTAs sit side by side rather than stacking into
     two full-width slabs */
  .lp .hero .wrap{padding-top:38px;padding-bottom:38px;gap:26px}
  .lp .hero h1{margin-bottom:12px}
  .lp .hero .lead{margin-bottom:20px;font-size:16px}
  .lp .btnrow{gap:10px}
  .lp .btn{padding:13px 18px;font-size:15.5px;flex:1 1 auto;min-width:0}

  /* HERO PHOTO. It had no aspect ratio on a phone, so it rendered at the
     source's own proportions and ate most of the first screen — the h1 was
     pushed below the fold and the shot read as "cut off" because all a visitor
     saw was foreground. 3:2 crops it to a landscape band, and the 42% vertical
     origin keeps the CAR in frame instead of centring on the driveway. */
  /* 4:3, which is the source photos' own ratio — so nothing is cropped and the
     whole vehicle stays in frame. 3:2 was trimming the top and bottom to save
     35px of height, and losing part of the car to save 35px is a bad trade on a
     page selling the look of the finished job. */
  .lp .hero-media img{aspect-ratio:4/3;height:auto;object-position:center 45%}

  /* Both hero CTAs on ONE row. `flex-wrap:wrap` plus `flex:1 1 auto` let them
     wrap into two full-width slabs the moment the text was wider than the row,
     which at 430px it always is. Pinning nowrap + `flex:1 1 0` makes them share
     the width equally, and the font scales down rather than wrapping. */
  .lp .hero .btnrow{flex-wrap:nowrap}
  .lp .hero .btnrow .btn{flex:1 1 0;white-space:nowrap;padding:13px 8px;
    font-size:clamp(12px,3.15vw,15.5px)}

  /* TRUST STRIP: four across, not a 2x2 block. Type scales with the viewport so
     nothing is clipped — the labels wrap onto a second line on a narrow phone,
     which is fine; cropping would not be. */
  /* Centred, and sized so the HEADLINE figure never wraps — "Within 1 hour"
     breaking onto two lines was what made the row look ragged, because the four
     cells then had different heights and nothing lined up. The small label is
     allowed to wrap onto a second line; that reads as a caption and stays tidy
     because everything is centred. */
  .lp .trust .wrap{grid-template-columns:repeat(4,1fr)}
  .lp .trust .t{padding:14px 6px;gap:3px;align-items:center;text-align:center}
  .lp .trust .big{font-size:clamp(11px,2.95vw,15px);line-height:1.15;
    letter-spacing:-.015em;white-space:nowrap;justify-content:center}
  .lp .trust .sm{font-size:clamp(7.5px,1.95vw,10px);letter-spacing:.03em;
    line-height:1.3;color:#9DB8D0;text-wrap:balance}

  /* (The old rule-and-margin hack that separated .pairs from the service cards
     is gone — before/after is its own <section> now, so the band's own padding
     and the tint/white alternation do the separating properly.) */

  .lp .band h2{margin-bottom:11px}
  .lp .band .sub{font-size:15.5px}

  /* SECTION SPACING. 42px top and bottom was making consecutive bands feel
     crammed on a phone even though the desktop rhythm was fine. Nudged up so
     each section reads as a separate idea — the content inside gets TIGHTER
     below, which is the right trade: less air inside, more air between. */
  .lp .band{padding:clamp(52px,9vw,72px) 0}

  /* "WHY THEY FAIL", compacted. Same words, less swiping — the section is the
     page's price defence and people bounce off a wall of prose on a phone.
     Line-height and the gaps do the work; nothing is cut. */
  .lp .arg{gap:15px}
  .lp .arg p{font-size:15.5px;line-height:1.5;margin-bottom:11px}
  .lp .pull{margin:13px 0;padding:3px 0 3px 13px;border-left-width:3px}
  .lp .pull b{font-size:18px;line-height:1.25}
  .lp .pull span{font-size:14.5px;line-height:1.45}
  .lp .myth{padding:14px 15px}
  .lp .myth h4{font-size:11px;margin-bottom:9px}
  .lp .myth ul{gap:9px}
  .lp .myth li{font-size:14.5px;line-height:1.45;gap:9px}

  /* step cards: shorter photo, tighter body */
  .lp .card .shot{height:200px}
  .lp .card .body{padding:18px 18px 20px;gap:11px}
  .lp .card li{font-size:14.5px}

  /* photo strip: 6 tiles, not 8. Two dangling tiles on a phone read as an
     unfinished grid, and the site caps its recent-work strip the same way. */
  .lp .strip{gap:9px}
  .lp .strip figure:nth-child(n+7){display:none}

  /* FORM. Compacted hard — this was the worst offender on the page, running to
     roughly three screens of scrolling. The pairing of fields (.f2/.f3 above)
     does most of the work; these tighten what is left. Input font stays 16px
     because anything smaller makes iOS zoom the page on focus. */
  .lp .quote{padding:18px 16px 20px;gap:10px}
  .lp .quote label{font-size:12px;gap:4px}
  .lp .quote input[type=text],.lp .quote input[type=tel],.lp .quote input[type=email],
  .lp .quote textarea{padding:9px 11px;font-size:16px}   /* 16px stops iOS zooming */
  .lp .quote textarea{min-height:74px}
  .lp .f2,.lp .f3{gap:9px}
  .lp .quote .send{padding:14px;font-size:16px;margin-top:2px}
  .lp .quote .consent{font-size:12.5px;gap:9px}
  .lp .quote .fieldnote{font-size:11.5px}
  .lp .quote .promise{font-size:12.5px;margin-top:8px}
  .lp .formside .big{margin-bottom:11px}
  .lp .formside p{margin-bottom:18px;font-size:15.5px}
  .lp .formside .why{margin-bottom:20px;gap:9px}

  /* Map now sits at the very bottom of the section, after the form. */
  .lp .mapblock{margin-top:4px}
  .lp .mapwrap{margin-top:0}
  .lp .mapwrap iframe{height:170px}

  /* FAQ */
  .lp summary{font-size:15.5px;padding:16px 34px 16px 0}
  .lp summary::after{top:13px;font-size:22px}
  .lp .ans{font-size:15px}

  .lp .cta .micro{margin-top:16px}
}

/* very narrow phones */
@media (max-width:400px){
  .lp .hero h1{font-size:29px}
  .lp .card .shot{height:180px}
  .lp .quote{padding:17px 15px 19px}
  .lp .trust .t{padding:14px 15px}
  .lp .trust .big{font-size:17.5px}
}
</style>
"""


# ============================================================================
# Shared content — identical on every landing page
# ============================================================================
STAR_SVG = ('<svg class="starmark" viewBox="0 0 24 24" aria-hidden="true" '
            'focusable="false"><path d="M12 2l2.9 6.26 6.86.74-5.12 4.6 1.44 6.72L12 '
            '17.1l-6.08 3.22 1.44-6.72L2.24 9l6.86-.74L12 2z"/></svg>')

# The four trust cells. "Within 1 hour" is REPLY_PROMISE's headline number and is
# scoped to shop hours in the small print underneath, exactly as the promise is.
TRUST = [
    (f"5.0{STAR_SVG}", "On Google"),
    ("Since 1989", "37 years in Monroe"),
    ("Free", "Estimates"),
    ("Within 1 hour", "We reply, shop hours"),
]

ADDRESS = "4209 W Hwy 74, Monroe, NC 28110"
MAP_Q = "4209+W+Hwy+74,+Monroe,+NC+28110"
HOURS_LINE = ("Mon&ndash;Fri 9:00&ndash;7:00 &middot; Sat 11:00&ndash;5:00 "
              "&middot; Sun closed")


def initials(name):
    """RD, CM, OP … from the reviewer's name, as the draft's avatars do."""
    parts = [p for p in name.split() if p]
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def review_cards(reviews, taglines, hidden=False):
    """One pass of the marquee.

    `taglines` maps reviewer name -> the small blue label above the quote. It is
    per-page and it must stay TRUE to what the reviewer actually wrote: Robert
    Danneman's review names a headliner and console leather, so those are the
    only two jobs his card may be labelled with. Anyone the page has no honest
    label for falls back to "Google review".
    """
    out = []
    aria = ' aria-hidden="true"' if hidden else ""
    for r in reviews:
        quote, name, sub, _when, colour = r[0], r[1], r[2], r[3], r[4]
        tag = taglines.get(name, "Google review")
        out.append(
            f'<div class="review"{aria}>'
            f'<div class="rev-top">'
            f'<span class="av" style="background:{colour}">{initials(name)}</span>'
            f'<span class="rev-id"><span class="rev-name">{name}</span>'
            f'<span class="rev-sub">{sub}</span></span></div>'
            f'<div class="rev-line"><span class="stars">'
            + "&#9733;" * 5 +
            f'</span><span class="tagline">{tag}</span></div>'
            f'<blockquote>&ldquo;{quote}&rdquo;</blockquote></div>')
    return "".join(out)


def shead(num, label):
    return (f'<div class="shead"><span class="n">{num:02d}</span>'
            f'<span class="dash"></span><span class="lab">{label}</span></div>')


def bullets(items):
    return "".join(f'<li><span class="sq"></span>{i}</li>' for i in items)


def card_shot(step, photo, alt, focus):
    """One numbered step card photo. `focus` is the object-position y, e.g. '68%'."""
    return (f'<div class="shot"><span class="step">{step}</span>'
            + img(photo, alt, CARD_SIZES, ratio=False,
                  style_extra=f"object-position:center {focus}")
            + "</div>")


def landing_form(subject, placeholder, filenote):
    """The site's form, on the page rather than a click away.

    Same endpoint, same field names, same honeypot, same TCPA consent as
    quote_form(). Only `_subject` differs, so a lead from this page is
    identifiable in the inbox. Zero JavaScript. The reply promise is
    REPLY_PROMISE — never retyped here, or the page and the contact form drift.
    """
    enctype = ' enctype="multipart/form-data"' if FORM_ACCEPTS_FILES else ""
    photos = f"""
        <label class="filefield">Photos <span class="opt">optional</span>
          <input type="file" name="Photos" accept="image/*" multiple>
          <span class="fieldnote">{filenote}</span>
        </label>""" if FORM_ACCEPTS_FILES else ""
    return f"""<form class="quote" action="{FORM_ENDPOINT}" method="post"{enctype}>
        <input type="hidden" name="_subject" value="{subject}">
        <!-- Formspree redirects here on success; that page fires the Google Ads
             conversion. See TRACKED_PAGES in build_site.py. -->
        <input type="hidden" name="_next" value="{SITE}/{THANKS_PAGE[:-5]}">
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
        <label>What do you need? <textarea name="Project description" rows="4" required
          placeholder="{placeholder}"></textarea></label>{photos}
        <label class="consent">
          <input type="checkbox" name="SMS consent" value="Yes, agreed to receive text messages">
          <span>Text me about my estimate. Message and data rates may apply &mdash; reply
            STOP to opt out.</span>
        </label>
        <button class="send" type="submit">Get my free estimate</button>
        <p class="promise">{REPLY_PROMISE}</p>
      </form>"""


# ============================================================================
# THE PAGE TYPE
# ============================================================================
def landing_page(cfg, reviews, pages=None):
    """Render one paid-search landing page from a content dict.

    Section numbers are COUNTED, not hard-coded, so a page that carries the
    optional `extra` band still numbers straight through instead of skipping.
    """
    slug = cfg["slug"]
    h = head(cfg["title"], cfg["desc"], slug, faqs=cfg["faq"]["items"],
             preload=preload_image(cfg["hero"][0], HERO_SIZES),
             extra_head=LANDING_CSS)
    h += header(cfg.get("nav_active", "services.html"))
    h += '<div class="lp">\n'

    n = 1
    # ---- 1. HERO ----------------------------------------------------------
    hero_photo, hero_alt = cfg["hero"]
    h += f"""<section class="hero on-dark">
  <div class="wrap">
    <div>
      {shead(n, cfg["eyebrow"])}
      <h1>{cfg["h1"]}</h1>
      <p class="lead">{cfg["lead"]}</p>
      <div class="btnrow">
        <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn-ghost" href="#estimate">Send photos for a quote</a>
      </div>
    </div>
    <div class="hero-media">{img(hero_photo, hero_alt, HERO_SIZES, ratio=False,
                                 eager=True, priority=True)}</div>
  </div>
</section>

<section class="trust">
  <div class="wrap">
""" + "".join(f'    <div class="t"><span class="big">{big}</span>'
              f'<span class="sm">{sm}</span></div>\n' for big, sm in TRUST) + """  </div>
</section>
"""

    # ---- 2. THE ARGUMENT --------------------------------------------------
    n += 1
    a = cfg["argument"]
    myth_lis = "".join(
        f'<li><span class="sq"></span><span><b>{b}</b> {rest}</span></li>'
        for b, rest in a["myths"])
    h += f"""
<section class="band">
  <div class="wrap">
    {shead(n, a["label"])}
    <div class="arg">
      <div>
        <h2>{a["h2"]}</h2>
        <p class="sub">{a["sub"]}</p>
        <div class="pull">
          <b>{a["pull"][0]}</b>
          <span>{a["pull"][1]}</span>
        </div>
      </div>
      <div class="myth">
        <h4>{a["myth_title"]}</h4>
        <ul>{myth_lis}</ul>
      </div>
    </div>
  </div>
</section>
"""

    # ---- 3. WHAT WE DO + the before/after deck ----------------------------
    n += 1
    s = cfg["steps"]
    cards = ""
    for i, (photo, alt, focus, title, items) in enumerate(s["cards"], 1):
        cards += (f'      <div class="card">\n        {card_shot(i, photo, alt, focus)}\n'
                  f'        <div class="body"><h3>{title}</h3>'
                  f'<ul>{bullets(items)}</ul></div>\n      </div>\n')
    h += f"""
<section class="band tint">
  <div class="wrap">
    {shead(n, s["label"])}
    <h2>{s["h2"]}</h2>
    <p class="sub">{s["sub"]}</p>
    <div class="cards">
{cards}    </div>
  </div>
</section>
"""

    # ---- 3b. BEFORE AND AFTER --------------------------------------------
    # Its OWN numbered section, matching the home page's `before-after` band,
    # instead of being tacked onto the end of the "what we do" band. It was
    # sharing that section, so on a phone it ran straight on from the service
    # cards and read as more of the same block rather than a different idea.
    #
    # The heading deliberately does NOT claim these are the same vehicle. The
    # 2026-08-05 caption audit established that several pairs in the library are
    # two different cars, and each figcaption already says so where that is true.
    # A section headline promising "the same car, before and after" would make
    # every one of those captions a contradiction.
    if cfg.get("pairs"):
        n += 1
        cards_html = ""
        for before, b_alt, after, a_alt, cap in cfg["pairs"]:
            cards_html += (
                f'      <figure class="pair"><span class="pair-shots">'
                f'<span class="pair-shot"><span class="pair-tag">Before</span>'
                f'{img(before, b_alt, PAIR_SIZES, ratio=False)}</span>'
                f'<span class="pair-shot"><span class="pair-tag after">After</span>'
                f'{img(after, a_alt, PAIR_SIZES, ratio=False)}</span>'
                f'<span class="pair-arrow" aria-hidden="true">&rarr;</span></span>'
                f'<figcaption>{cap}</figcaption></figure>\n')
        ba = cfg.get("ba", {})
        h += f"""
<section class="band ba-band" id="before-after">
  <div class="wrap">
    {shead(n, ba.get("label", "Before and after"))}
    <h2>{ba.get("h2", "The work, either side of the job")}</h2>
    <p class="sub">{ba.get("sub", "Every photograph was taken at the shop in Monroe.")}</p>
    <div class="pairs">
{cards_html}    </div>
  </div>
</section>
"""

    # ---- 4. OUT OF THIS SHOP ---------------------------------------------
    n += 1
    w = cfg["work"]
    tiles = "".join(
        f'      <figure>{img(p, alt, STRIP_SIZES, ratio=False)}</figure>\n'
        for p, alt in w["photos"])
    # `tint`, not plain. Before/after sits on white directly above this, so two
    # white bands ran together and read as one long section with a stray heading
    # in the middle. The page alternates tint/white the whole way down; this was
    # the one place the alternation broke after before/after became its own band.
    h += f"""
<section class="band tint">
  <div class="wrap">
    {shead(n, w["label"])}
    <h2>{w["h2"]}</h2>
    <p class="sub">{w["sub"]}</p>
    <div class="strip">
{tiles}    </div>
    <div class="btnrow" style="margin-top:28px;justify-content:center">
      <!-- btn-ghost, not btn-dark. This matches the home page's own recent-work
           CTA exactly ("See the full gallery"), which is a transparent button
           with a hairline border. A black slab pulled more attention than a
           secondary link deserves, and competed with the blue Call button. -->
      <a class="btn btn-ghost" href="gallery.html">See the full gallery</a>
    </div>
  </div>
</section>
"""

    # ---- 5. REVIEWS -------------------------------------------------------
    # NEVER COUNT THE REVIEWS. A 5.0 average across nine means every one of them
    # is five stars — a single four-star would drag it to 4.9. So nobody has ever
    # left this shop a bad review, and that says something about quality rather
    # than volume. See the module docstring, rule 1.
    n += 1
    tags = cfg["review_taglines"]
    # DARK BAND, not tint. Changed 2026-08-09.
    #
    # The review cards are #2F343A. On a light tint band their edges cut hard
    # against near-white as they scroll off, which reads as a bright fringe at
    # both sides — the exact thing the user kept flagging. Removing the site's
    # edge mask helped but could not fix it, because the mask was never the
    # cause: the CONTEXT was. The site's own review marquee sits on a dark band,
    # which is why it looks right there and wrong here.
    #
    # Same lesson as the mask and the pair deck: copy the component AND the
    # surface it was designed for, not just its CSS.
    h += f"""
<section class="band dark on-dark">
  <div class="wrap">
    {shead(n, "From customers")}
    <h2>Nobody has ever left this shop a bad review</h2>
    <p class="sub">5.0 on Google. Every word below is copied straight off the profile.</p>
  </div>

  <!-- OUTSIDE .wrap on purpose: the marquee runs full-bleed, edge to edge,
       exactly as it does on the live site. Inside the gutter it read as a boxed
       strip. The second pass is a duplicate purely so the CSS loop is seamless. -->
  <div class="revmarquee">
    <div class="revtrack">{review_cards(reviews, tags)}{review_cards(reviews, tags, hidden=True)}</div>
  </div>
</section>
"""

    # ---- 6. FAQ -----------------------------------------------------------
    n += 1
    f = cfg["faq"]
    # FAQ starts fully CLOSED. The first item used to be forced open, which on a
    # phone pushed the rest of the list down and made the section read as longer
    # than it is. Closed, every question is visible at once — which is the point
    # of an accordion.
    items = "".join(
        f'<details><summary>{q}</summary>'
        f'<div class="ans">{a}</div></details>'
        for q, a in f["items"])
    h += f"""
<section class="band">
  <div class="wrap narrow">
    {shead(n, f["label"])}
    <h2>{f["h2"]}</h2>
    <div class="faq">{items}</div>
  </div>
</section>
"""

    # ---- 7. optional extra band (internal links) --------------------------
    if cfg.get("extra"):
        n += 1
        e = cfg["extra"]
        links = "".join(f'<a class="btn btn-dark" href="{href}">{label}</a>'
                        for href, label in e["links"])
        h += f"""
<section class="band tint">
  <div class="wrap narrow">
    {shead(n, e["label"])}
    <h2>{e["h2"]}</h2>
    <p class="sub">{e["sub"]}</p>
    <div class="btnrow" style="margin-top:22px">{links}</div>
  </div>
</section>
"""

    # ---- 8. FORM — on the page, not a click away --------------------------
    n += 1
    fm = cfg["form"]
    why = "".join(f'<li><span class="sq"></span>{x}</li>' for x in fm["why"])
    h += f"""
<section class="band cta" id="estimate" style="text-align:left">
  <div class="wrap">
    {shead(n, "Free estimate")}
    <div class="formwrap">
      <div class="formside">
        <div class="big">{fm["big"]}</div>
        <p>{fm["p"]}</p>
        <ul class="why">{why}</ul>
        <!-- DRAFT v16. sms: carries NO body param on purpose — iOS wants &body=,
             Android wants ?body=, and getting it wrong breaks the link on one of
             them. A bare sms: link opens a blank message to the shop on both. -->
      </div>

      {landing_form(fm["subject"], fm["placeholder"], fm["filenote"])}

      <!-- "Or skip the form" MOVED OUT of .formside 2026-08-10, same reasoning as
           the map. On a phone the column collapses, so offering the shortcut
           BEFORE the form meant the page talked you out of the form before you
           had seen it. After the form it reads as the fallback it actually is:
           "still here? just call or text a photo." Desktop is pinned below. -->
      <div class="orcall">
        <div class="lbl">Or skip the form</div>
        <a class="contactline" href="tel:{PHONE_TEL}">
          <span class="ci">&#9742;</span>
          <span><b>{PHONE_DISPLAY}</b><em>Call the shop</em></span></a>
        <a class="contactline" href="sms:{PHONE_TEL}">
          <span class="ci">&#9993;</span>
          <span><b>Text a photo</b><em>Same number &middot; send a picture of the job</em></span></a>
      </div>

      <!-- Same Google Maps embed as the contact page.
           MOVED OUT of .formside 2026-08-10. It used to sit inside the left
           column, which on a phone (one column) put a 210px map BETWEEN the
           "text a photo" links and the form — so the map interrupted the exact
           path the page is trying to push people down. As its own grid child it
           falls naturally last on mobile, and desktop is pinned back to column 1
           row 2 below so the two-column layout is unchanged. -->
      <div class="mapblock">
        <div class="mapwrap">
          <iframe title="Map to Auto Tops and Trim, {ADDRESS}" loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            src="https://www.google.com/maps?q={MAP_Q}&amp;output=embed"></iframe>
        </div>
        <p class="maplbl"><a href="https://www.google.com/maps/search/?api=1&amp;query={MAP_Q}">{ADDRESS}</a><br>{HOURS_LINE}</p>
      </div>
    </div>
  </div>
</section>
"""

    h += "</div>\n"
    # The split call / text-a-photo bar, which ONLY the paid landing pages get.
    # The markup and the reasoning both live in split_callbar() in build_site.py,
    # and the styling is `.callbar.split` in site.css — this passes the site's
    # component through rather than defining a second one, which is what it used
    # to do (same bar, different class names, different mobile tuning, and only
    # these two pages getting the fork).
    h += footer(callbar=split_callbar())
    if pages is not None:
        pages.append(slug)
    return write(slug, h)
