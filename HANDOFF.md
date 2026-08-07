# Auto Tops and Trim — Handoff

Read this first in a new chat. Everything needed to continue is in this repo.

**Last updated:** 2026-08-06

> 🚀 **THE REBUILD IS LIVE.** www.autotopsandtrim.com serves the generated site.
> Workflow: push to `rebuild`, check the preview, then fast-forward `main`.
>
> **ROLLBACKS:** `6a1af08` (last production commit before the logo work) ·
> `45046b7` (the old single-page site).
> Revert production with `git push origin <sha>:main --force`.

## ⚠️ STATE AS OF 2026-08-07 — READ THIS FIRST

**`rebuild` and `main` are IDENTICAL and everything below is LIVE.** The
2026-08-06 block that used to sit here (claiming production lagged) was stale.

**The apex TLS blocker is FIXED.** `autotopsandtrim.com` now has one A record
(`216.198.79.1`), a valid Let's Encrypt cert issued 2026-08-05, and 308-redirects
to www. Old open item 1 is closed.

**Shipped 2026-08-07:** hours changed to Mon-Fri 9:00-7:00 (weekend unchanged);
the "we will not quote from a photo" policy REVERSED across 12 places on the
owner's correction - the shop does estimate from photos, with an in-person look
when the job needs it; hero slideshow reshuffled to two owner-supplied slides and
retimed to 2s a slide; a `_gotcha` honeypot added to the quote form; the four
unverified stock photos removed from the gallery.

### THE PHOTO BATCH — 283 sorted, mostly NOT on the site yet

The owner supplied **283 unique photographs** of real shop work (309 files, 26
exact duplicates dropped). **139 are genuine HEIC** and need `pillow-heif` —
unlike the earlier Drive batch, where the HEIC extensions were lying.

- Sorted into 14 category folders at
  `C:\Users\table\Downloads\hopeton-photos-sorted`, named
  `NNN__<set>__<BEFORE|AFTER>__<slug>.<ext>` so job sets sort together.
- Classification written from viewing every photo on contact sheets. **The
  folder each photo is in is reliable. The vehicle makes and model years in the
  filenames are NOT** — they were read off 430px thumbnails. Never caption from
  them; open the photo at full size first. Two of those thumbnail reads were
  already proved wrong when the vinyl-top photos were adopted.
- **17 photos have the retired 704-224-9124 number readable on the building.**
  Do not publish those. `#267` is a shipping label with an address on it.
- Only 7 of the 283 are adopted so far: 2 hero slides and 5 vinyl-top masters.

**What this batch settles:** there is **no aviation and no motorcycle work in
283 photos**, which confirms the four suspect images were never the shop's.
Marine is real — 3 boat photos plus boats on trailers in the shop exteriors.

### THE SERVICES RESTRUCTURE — AGREED, NOT YET BUILT

The owner's business card reads **convertible tops, vinyl tops, sunroofs,
vehicle interiors**, and the photo counts match it (62 convertible tops, 115
interior, 14 vinyl, 2 sunroof). The site's "four trades under one roof —
automotive, marine, aviation, motorcycle" framing is the outlier. Agreed plan:

1. **Build a Vinyl Tops page.** It is on his card, there are 14 photos including
   a complete before/after, and **the site has no such page at all.** The five
   masters are already adopted and unreferenced:
   `vinyl-top-before-roof-covering-rotted`, `vinyl-top-roof-stripped-trim-removed`,
   `vinyl-top-after-burgundy-fitted`, `vinyl-top-after-opera-window-detail`,
   `vinyl-top-before-peeling-at-rear`.
2. Reorder `SERVICES` in `build_site.py` to card order; rename
   "Auto Upholstery" to **Vehicle Interiors**. Keep existing URLs so nothing 404s.
3. Reorder `SCHEMA["makesOffer"]` and rewrite `SCHEMA["description"]` and the
   footer tagline, both of which still lead with the four-trades framing.
4. **Rewire the four stock photos out of the remaining places.** Off the gallery
   already; still used as service-page heroes, home `pcard` images, services-index
   images and the `photo` of six blog posts. Marine can use the real
   `boat-upholstery-projects-at-the-shop`; aviation and motorcycle need
   text-only treatments.
5. Demote marine/motorcycle/aviation into one **"We also work on"** band with
   three text columns linking to their pages, which stay live. **Design them with
   no photo slot at all** — an empty slot looks broken, a text block does not.
   Explicitly NOT "photos coming soon".

   **DO NOT ask the owner to go and photograph anything.** He was asked on
   2026-08-07 and declined; the instruction is to work with what exists and
   ship the text-only treatment. Motorcycle and aviation get photos if and when
   he supplies them, not before. Build these sections so that dropping a photo
   in later is additive and needs no redesign.
6. A **Before & After** page/band was requested. Ten complete before/after job
   sets exist; the white sedan roof is the strongest.

### STILL BLOCKED

**The quote form still posts to `formspree.io/f/mrpzzdgz`.** The owner has now
paid for a Formspree Personal plan ($15/mo, file uploads) and Vercel Pro
($20/mo, which is what makes commercial hosting legitimate) — but the endpoint
he supplied was the old unowned one, read off the site rather than his
dashboard. **Get the endpoint from formspree.io → Forms.** Photo uploads are
built and ready behind `FORM_ACCEPTS_FILES` in `build_site.py`; do not switch
them on until the endpoint is his. Video is not viable at any tier: 25MB per
file, and phone video passes that in about 30 seconds.

**The header is mid-redesign and is the thing in flight.** Current state on
`rebuild`, all of it inside one delimited `TRIAL: white header` block at the end
of `assets/site.css` (delete the block to return to the dark header):

- header background is **white**, not the blue/charcoal gradient
- the diamond quilt is inverted — faint blue on white
- nav links, burger and active underline recoloured to charcoal / `#2F6FB0`
- the **circular cream badge logo** (`logo-badge-warm`) is the brand, at every
  width. The text wordmark is hidden everywhere (`.brand-name{display:none}`)
- desktop row: badge, nav beside it, phone button pushed right
- mobile row: badge, phone button, burger — **the sticky bottom call bar is
  hidden on mobile**, the number lives in the header instead
- `MONROE, NC · SINCE 1989` was removed from the header on the user's request

**Three unresolved problems with the current logo, in priority order:**

1. **It is a Ford Mustang with the running-horse emblem on the grille.** Using
   Ford's trademark in the shop's logo is real legal exposure, not a style
   question. Raised with the user; not yet acted on.
2. **It is a serif face.** The design system is locked to Archivo, never a
   serif. This is a direct conflict with the locked system.
3. **It is a cream disc, not linework**, so it sits as a pale circle rather than
   a mark — which is the reason the header went white in the first place.

Earlier candidates, already prepared and kept in `assets/originals/`:
`logo-light.png` (blue car, "AUTO TOPS" whitened, for dark surfaces) and
`logo-dark.png` (as supplied, for white). Both have their drop shadow stripped.

**⚠️ The apex domain is still broken — see open item 1.**

---

## The business (all verified, never guess these)

| | |
|---|---|
| Name | Auto Tops and Trim |
| Owner | Mr. Hopton (referenced by name in a Google review) |
| Address | **4209 W Hwy 74, Monroe, NC 28110** |
| Phone | **(980) 385-8101** (new number; the old 704-224-9124 is retired) |
| Email | contact@autotopsandtrim.com |
| Hours | Mon–Fri 9:00 AM–5:30 PM · Sat 11:00 AM–5:00 PM · Sun closed |
| Founded | 1989 |
| Google | 5.0 stars, 9 reviews · https://share.google/T8GTbx9cswkCKF3PI |
| Trades | Automotive · Marine · Aviation · Motorcycle |
| Serves | Monroe, Charlotte, Union County NC |

---

## Where things live

| What | Where |
|---|---|
| Repo | `github.com/autotopsandtrims-ctrl/autotopsandtrim` |
| Working branch | **`rebuild`** — all new work |
| `main` | **PRODUCTION — now identical to `rebuild`.** Serves www.autotopsandtrim.com |
| Public preview | **https://hopeton-website-git-rebuild-auto-top-and-trim.vercel.app** |
| Vercel project | `hopeton-website`, scope `auto-top-and-trim` |
| GitHub token | `c:\Claude Code\.env.autotopsandtrim` (repo-scoped, Contents read/write) |
| git binary | `%LOCALAPPDATA%\GitHubDesktop\app-3.6.3\resources\app\git\cmd\git.exe` — **no git or gh on PATH** |
| Google Ads | account `6285559119`, linked ACTIVE to MCC `6918960041`. Not launched. |

---

## How to build

The site is **generated**, not hand-edited. Never edit the `.html` files at the
repo root — they are overwritten on every build.

```bash
python _build/build_pages.py     # regenerates all 16 pages
python _build/validate.py        # checks every link, image and srcset resolves
```

`_build/build_site.py` holds the shell (head, header, footer, CTA, form, schema).
`_build/build_pages.py` holds page content and the review data.
`_build/images.json` is the photo catalogue — **image paths are read from it, never typed by hand.**

Other tools, only needed if reworking photography:
- `_build/extract_assets.ps1` — pulls photos/fonts out of the old bundle
- `_build/import_photos.py` — triages a folder of raw photos into a labelled
  contact sheet (dedupe, burst grouping, EXIF rotation). Step 1 for new photography.
- `_build/make_responsive.py` — regenerates 480/800/1400px variants
- `_build/make_preview.py` — flattens the home page to one self-contained file

To deploy: commit and push to `rebuild`. Vercel redeploys the preview in ~30 s.

---

## Design system — LOCKED. Do not substitute.

The user rejected a redesign once already. The rebuild is about **structure, not restyling.**

- **Font: Archivo**, self-hosted from 3 woff2 subsets in `assets/fonts/`.
  Headings weight **800**, `line-height:1.07`, `letter-spacing:-0.028em`. **Never a serif.**
- **Palette:** `#2F6FB0` primary blue · `#5E9BD9` light blue · `#2A2E33` ink (charcoal, not navy)
  · `#E8EEF6` band tint · `#F1F5F9` second tint · `#D9E2ED` rules · `#23282E` dark bands
  · `#16344F` deep · `#1E5C99` buttons. **No tan/saddle accent — that was rejected.**
- **Signature devices, all load-bearing:**
  - Section header: `NN` + 26px dash + uppercase letterspaced label in blue
  - Numbered feature columns with large outlined numerals
  - 8×8 `#5E9BD9` square bullets (not ticks or discs)
  - Home band rhythm: white → tint → **dark** → white → tint2
- **Mobile is a hard requirement** — user's words: *"it literally has to be perfect in mobile. No compromise whatsoever."*

---

## Architecture notes

- **16 real pages, real URLs.** The old site was a single-page app where nav
  changed a JS variable and the URL never moved — which is why the back button
  was broken. That is fixed structurally.
- **Zero JavaScript.** Nav is a CSS checkbox; the lightbox is CSS `:target`
  (so the back button closes it); transitions are CSS. Everything works with
  scripts disabled.
- **The lightbox layer must stay outside `<main>`.** `<main>` runs the `pagein`
  transform animation, and a transform-animated ancestor becomes the containing
  block for `position:fixed` descendants — which made the overlay size itself to
  the height of `<main>` instead of the viewport, so photos opened far down the
  page. `footer(lightbox_markup())` emits it after `</main>`. Do not move it back.
- **Images:** 480/800/1400px WebP variants served via `srcset`, plus the master's
  native width when it exceeds the largest tier. Mobile home page ≈ 495 KB.
  Masters live in `assets/originals/` — `make_responsive.py` reads from there,
  **not** `assets/`, which now holds only generated variants.
- **Never put `overflow` on `<html>` or `<body>`.** When `<html>` is `visible`,
  `<body>`'s overflow propagates to the viewport, and at viewport level it breaks
  `position:fixed` on iOS — it stranded the sticky call bar mid-screen. Sideways
  drag is contained by clipping `main`, `.site-head` and `.site-foot` instead.
- **Radius belongs on the clipping container, not the image.** Anything with
  `overflow:hidden` and a hover `transform` on its child needs the radius on the
  parent, or the corners snap square on hover.
- `assets/originals/` holds the 43 recovered master photos — **the uncle lost
  most of his originals; these came out of the old bundle. Do not delete.**

---

## Done

- 16 pages: home, services + 6 service pages, gallery, process, about, contact, blog + 3 articles
- Site outage fixed (an empty `index.html` had been committed)
- Phone corrected sitewide; hours corrected (site had said Mon–Fri 8–5, Sat 9–2 — both wrong)
- Street address added to contact, footer, map and schema
- All 7 written Google reviews, verbatim, with names and dates. Auto-sliding marquee on a dark band.
- Click-to-enlarge lightbox on gallery and home recent-work
- Photo-forward bento service cards; alternating service rows
- Masonry so photos are never cropped
- Per-page meta, LocalBusiness + AggregateRating + Article schema, sitemap.xml, robots.txt

**2026-08-04**

- **Sunroof shade repair page** (`sunroof-shade-repair.html`) — was open item 4.
  In nav-adjacent SERVICES list, footer, services index, sitemap and schema.
  Copy is grounded in the two verbatim Google reviews about this exact repair;
  the page carries **no photos**, because the 43-photo catalogue has none of this
  work. Shoot some and it gets a "Recent work" strip for free.
- **Lightbox centring fixed** — see the architecture note above. Hover cursor is
  a normal pointer now, not `zoom-in`; the backdrop is `default`, not `zoom-out`.
- **Process page rebuilt** — flat hairline list replaced with a connected numbered
  timeline (`.flow`: blue rail, outlined nodes, photo in a third column on desktop),
  plus a band spelling out what the free estimate covers and a testimonials band.
- **Gallery simplified** at the user's request — fanned photo stack removed
  entirely (markup, `FAN_PHOTOS`, `fan_stack()` and the `.fan` CSS are all gone),
  and the "21 automotive · 6 marine · …" count line dropped.
- **About page bottom rebuilt** — it ended on a naked stats row with no heading,
  then the generic CTA. Now: stats with a header and lead → a four-card trades
  grid linking into the service pages → real testimonials → CTA. Sections run 01–06.
- **Motion pass** — scroll-driven reveals via `animation-timeline: view()`, so the
  zero-JavaScript guarantee holds. Gated behind `@supports` and
  `prefers-reduced-motion`, so unsupported browsers show the final state and
  nothing can get stuck invisible. Containers whose children animate are excluded.
- **FAQ + schema** — the 23 service-page questions had **no `FAQPage` markup**, so
  none could win a rich result. `head()` now takes `faqs=` and emits LocalBusiness
  + FAQPage in one `@graph`. Added 6 general questions to the contact page
  (29 questions in schema total). Note: the FAQs were never on the home page —
  git history confirms it — they have always lived on the service pages.
- Softened a "No appointment needed" line on the process page: nothing verified
  supported it, so it now reads "Walk in or call ahead".
- Two latent bugs fixed on the way past: the gallery CTA passed its heading and
  subcopy positionally into `cta()`'s `num`/`label` slots, so the heading rendered
  as the tiny numeral; and `make_responsive.py` referenced an undefined `OUT_JSON`
  and would have crashed with `NameError` the next time anyone ran it.

---

## The blog queue — 30 posts, self-releasing

`POSTS` in `_build/build_pages.py` now holds **30 articles**. Each carries a
`publish` ISO date and the build only emits a post once that date has arrived —
before then it produces no page, is absent from `blog.html` and absent from
`sitemap.xml`, and any stale file on disk is deleted.

- `python _build/build_pages.py` prints `blog: N live, M scheduled (next ...)`
- `BUILD_DATE=2026-08-14 python _build/build_pages.py` previews a future state
  without touching any publish date
- `publish` is the single source of truth for the displayed date **and** for
  schema.org `datePublished`. The displayed form is `"%B %Y"`, so readers only
  ever see "August 2026" — the day is invisible to them but drives the gate.

Three a day, 2026-08-06 through 2026-08-14. The 8/6 three have already released.

**⚠️ Nothing publishes them automatically.** `.github/workflows/publish.yml` is
written and validated but **cannot be committed** — GitHub rejects the push
because the PAT lacks `workflow` scope. It is excluded via `.git/info/exclude`
so it stops blocking every push. Until the token gains that scope, each day's
posts go live only when someone runs the build and pushes.

Research behind the slate is in `SEO_KEYWORDS.md`. Headline findings: the site
ranks for **zero** keywords; city-modifier terms are tiny (`auto upholstery
charlotte nc` = 50/mo); the real demand is "near me" (`auto upholstery near me`
= 6,800/mo) which only the **locked-out Google Business Profile** can win.

## Open — in priority order

1. **BLOCKER — the apex domain has no valid certificate.**
   `https://autotopsandtrim.com` (no `www`) shows a browser security warning.
   The Let's Encrypt cert's SAN list contains **only** `www.autotopsandtrim.com`.

   Root cause found 2026-08-05: the apex has **three A records**, and only one is
   Vercel's —
   `3.33.130.190`, `15.197.148.33` (a registrar domain-forwarding service) and
   `216.198.79.1` (Vercel). Traffic round-robins between them.

   Fix, both halves required:
   - Vercel → project `hopeton-website` → Settings → Domains → add
     `autotopsandtrim.com`, configured to **redirect to www**. Read the A record
     value Vercel then displays — do not assume an IP, Vercel has changed it.
   - At the DNS host, **delete `3.33.130.190` and `15.197.148.33`** and leave a
     single apex A record matching what Vercel asked for. Do not touch `www`,
     MX or TXT.

   **ROOT CAUSE CONFIRMED 2026-08-05 from the user's GoDaddy panel.** DNS is at
   GoDaddy (`ns49`/`ns50.domaincontrol.com`). The panel shows exactly two apex A
   records:

       A   @   216.198.79.1    <- Vercel. KEEP.
       A   @   Parked          <- DELETE. This is the whole problem.

   The second literally reads "Parked" in the Data column. It is GoDaddy's
   domain-parking record and it expands to **both** rogue IPs, which is why an
   external lookup returns three addresses while the panel lists two.

   **Deleting that one row is the DNS half of the fix.** Also required: add
   `autotopsandtrim.com` in Vercel (project `hopeton-website`) set to redirect to
   www, and use whatever A record IP Vercel then displays.

   Do not touch: the `www` CNAME, the `MX` to `smtp.google.com` (the shop's
   Google email), NS, SOA, or `_domainconnect`. Two TXT records on `@` contain IP
   addresses — somebody's mistake, harmless, leave them.

   **A ready-to-paste browser-agent prompt is at `APEX_TLS_FIX_PROMPT.md`.**

2. **The contact form.** It posts to `https://formspree.io/f/mrpzzdgz`,
   an endpoint baked in by the original design tool that **neither the user nor I
   own or can verify.** The user reported a test lead reaching "my email" but has
   not confirmed which address. Until this is resolved, real customer names and
   phone numbers flow to an unverified destination. **Do not launch ads before fixing.**
   Fix: create a Formspree form on the user's own account pointed at
   contact@autotopsandtrim.com, swap `FORM_ENDPOINT` in `_build/build_site.py`.

   **Note (2026-08-05):** verified the OLD live site posted to this same endpoint,
   so going live did not create a new exposure — it inherited an existing one.
   The user believes the form is already connected to their inbox but has not
   confirmed which address. Still unresolved.
3. ~~**BLOCKER-ISH — the photo captions are not trustworthy.**~~ **FIXED 2026-08-05,
   commit `411b109`, on `rebuild` and verified on the preview. Not yet on `main`.**

   All 43 masters were opened and described from the image. The dhash scan had
   **undercounted**: 17 files are only **7 distinct photographs**, and **nine**
   captions contradicted their photo, not two.

   Beyond the two already known: `convertible-top-after` is a truck cab interior
   and was the **hero of convertible-tops.html**; `marine-canvas-cushions` is a
   car rear bench seat filed under **Marine**; `custom-bike-seat` is a burgundy
   convertible top filed under **Motorcycle**; `g13-sound-deadening-before-carpet`
   is a finished **headliner**; `g05-burgundy-cloth-top-rear-window` is a Cadillac
   **front end**; `g07`/`g08` were effectively swapped; the About hero alt said
   "shop leadership" for a photo of the building with nobody in it.

   **5 of 16 pages showed the same photograph more than once** under different
   captions (the gallery repeated five separate photos, the home page four).
   That is now **0**, enforced by one canonical basename per image. Regression
   check: `scratchpad/dupcheck.py` groups the duplicates and fails any page that
   repeats one — rerun it after touching photography.

   Two deliberate consequences: home recent-work is **automotive only** (dedupe
   left 1 usable marine, 1 motorcycle, 2 aviation photos, all already in the
   bento above it) and its lead no longer promises boats and bikes;
   **motorcycle-seats.html lost its "Recent work" band entirely.** Both come back
   as soon as real photography lands.

   **The verified content of all 43 masters is now recorded in a comment above
   `GALLERY` in `_build/build_pages.py`.** Read it before touching any photo.
   Do not re-derive it, and never caption from a filename.

12. **Provenance of the marine, aviation and motorcycle photos is unconfirmed.**
    Every marine, aviation and motorcycle image on the site is one of just **four**
    photographs (a varnished-wood runabout cockpit, cream quilted aircraft seats,
    a private-jet cabin, a diamond-quilted seat on a mint café racer). All four
    read as commercial photography — even lighting, styled composition, shallow
    depth of field — and none carries any cue tying it to the Monroe shop. Every
    photo positively identifiable as the shop's own work is a phone photo taken at
    the shop or by the wooden fence. **gallery.html states "Every piece here was
    cut, stitched and fitted in house."** The user is checking provenance with his
    uncle; on his instruction the four were left in place for now. If they are not
    his, they must come out and that line has to change.

   <details><summary>Original finding, kept for reference</summary>

   A perceptual-hash
   scan (16×16 dhash) of the 43 site photos found **11 near-identical pairs** —
   the same photograph stored under two names and captioned differently. Verified
   by eye and by pixel RMS (~2 of 255, i.e. the same shot re-encoded):

   - `headliner-install` **is not a headliner install.** It is the same image as
     `g16-cadillac-convertible-red-interior` — a grey Cadillac convertible
     exterior. It was the sunroof page's hero until this was caught.
   - `g19-mercedes-gla-interior-work` **is not a Mercedes GLA.** It is a vintage
     red pickup interior with a rebuilt seat and carpet.
   - `hero-best-finished-vehicle-wide-full-color` == `g17-cadillac-top-and-interior-finished` (distance 0)
   - `g22-marine-cushions-and-helm-trim` == `marine-seating-and-interior-upholstery` (distance 0)
   - `aircraft-interior-seat-upholstery` == `aviation-cabin-seats`, and
     `custom-motorcycle-seat-upholstery-close-up` == `motorcycle-custom-seat` (distance 1)
   - also flagged: `convertible-top-after` == `g09-truck-cab-black-seat-red-stitch`,
     `process-header-photo-wide` == `seat-rebuild-after`

   These names came out of the old bundle and were never verified against the
   images. **The gallery therefore shows the same photo more than once under
   different captions, and at least two captions state something the photo does
   not show.** That is exactly what the project's never-invent rule exists to
   stop. Fix: view all 43, rewrite `GALLERY` captions from what is actually in
   frame, and drop the duplicates. Reproduce the scan with the dhash in
   `_build/import_photos.py`.

   </details>
4. **Mobile pass.** Desktop is being signed off first, by the user's choice. Mobile
   currently needs alignment work throughout.
5. **Logo — IN FLIGHT, see the state block at the top of this file.** Four
   candidates have been through the header. The current one is a circular cream
   badge with a Ford Mustang and serif type; all three problems with it are
   listed at the top. It still needs to become a real SVG in two colourways
   rather than an upscaled raster.

   **Hard-won lessons, do not repeat these:**
   - `make_responsive.py` used to do `im.convert("RGB")` on everything, which
     silently destroyed alpha and composited logos onto black. **Fixed** — it now
     keeps RGBA when the source has it. Photos still flatten to RGB.
   - The global `img{background:#EDF1F5}` loading placeholder shows straight
     through a transparent logo as a pale box. `.brand img` and `.foot-brand img`
     set `background:none` to stop it.
   - Recolouring a drop shadow along with the artwork turns a grey shadow into a
     white glow. Strip shadows (faint + neutral pixels) before recolouring.
   - Deriving alpha from a JPG's luminance gives mushy edges. Only remap colour
     on sources that already have a correct alpha channel.
6. **Photos for the sunroof page.** The page ships with no photography because
   the catalogue has none of that repair. A few before/after shots of a sagging
   shade would finish it.
7. ~~**Photos in Google Drive**~~ — **DOWNLOADED 2026-08-04.** 105 files pulled,
   10 byte-identical duplicates dropped, **95 unique photos** kept, 1 near-identical
   group. Contact sheet at `_build/incoming/contact-sheet.html` (gitignored),
   awaiting the user's labels.

   ✅ **The HEIC premise was wrong, confirmed.** Every one of the 95 is a real
   **JPEG** — files named `.HEIC` start with the JPEG magic number `FF D8 FF`.
   Chrome displays them fine and no HEIC conversion is needed. `pillow-heif` is
   not required.

   How the download worked, for next time: the folder's normal page is JS-rendered
   and yields nothing to a scraper, but
   `https://drive.google.com/embeddedfolderview?id=<FOLDER>#list` returns static
   HTML with every file id, and `https://drive.google.com/uc?export=download&id=<ID>`
   fetches the bytes. Script kept at `scratchpad/fetch_drive.py`. This avoids the
   Drive MCP, which returns base64 through the conversation and cannot do 100 files.

   NEXT: user labels the numbers → adopt the keepers into `assets/` under real
   names → `make_responsive.py` → add to `GALLERY`. **Label from the image, never
   from the old filename** (see open item 2).

8. ~~**Merge `rebuild` → `main`** once approved. That is the go-live moment.
9. Google Business Profile is locked out (forgotten login) — recovery is the
   highest-leverage marketing task; it drives the local map pack.
10. Square recommended for card payments and invoices (NOT Shopify — wrong shape
   for in-person custom quoting).
11. Terms/privacy — user parked this. A short privacy note is the useful one,
   since the form collects names and numbers.
13. **Photo uploads on the quote form.** Built and switched off behind
    `FORM_ACCEPTS_FILES` in `_build/build_site.py`. A file input needs no
    JavaScript, so it does not touch the zero-JS rule. Gated on two things:
    the endpoint being an account the shop owns, and that account being on a
    **paid** Formspree plan — the free tier is 50 submissions/month with no
    attachments, and the cheapest tier that accepts files is $15/mo.
14. **Charles Monk's full review text.** His Google review is truncated at
    "...took the time to redo some of it when he didn't like the way it
    turned…". The visible part is stronger than anything currently quoted.
    Expand "More" on the profile and transcribe it verbatim.
15. **Reviewer photo permission.** His two headliner before/after photos are now
    live in his review card (review #2, deliberately). They are his, not the
    shop's. Worth asking before using them more widely.
16. **Swipe in the lightbox** needs JavaScript. The zero-JS rule exists because
    the OLD site used JS for navigation and broke the back button — a gesture
    layer on top of the existing `:target` links would not reintroduce that.
    Proposed to the user as progressive enhancement; not yet decided.

---

## Rules learned the hard way

- **Never invent reviews, specs or business facts.** All review text is verbatim
  from the Google profile. Charles Monk's is truncated by Google's "More" link —
  only his complete visible sentences are quoted. Two reviews have no text and
  are counted but not quoted.
- **Never edit this repo through GitHub's web editor.** It silently committed an
  empty file and took the live site down. Clone and push, or use drag-and-drop upload.
- **Never push to `main`** without explicit approval — that is production.
- Verify live state before claiming anything works. Check the deployed URL,
  not just local output.

**2026-08-06 — content, clean URLs, logo trials**

- **Clean URLs.** `vercel.json` sets `cleanUrls`; every internal link, canonical,
  `og:url`, sitemap entry and Article `mainEntityOfPage` emits the extensionless
  form. Old `.html` URLs 308-redirect, so nothing indexed breaks. Links are
  rewritten once in `write()` rather than at hundreds of call sites, which also
  keeps `header()`'s `href == active` comparison working.
- **30 blog posts written and queued** — see the queue section above.
- **The three original posts were rewritten** with verified material comparison
  tables (Haartz Stayfast/Twillfast/pinpoint vinyl; Sunbrella/Top Gun/Stamoid/
  Seamark) and **re-dated honestly to 2026-08-04**, the day they actually
  entered the repo. They had claimed May/June/July.
- **Reviewer photos.** Charles Monk's headliner before/after now render inside
  his review card, and his review was moved to **position 2** on purpose.
- **Lightbox flash fixed.** `.lb:target` ran `animation:lbin` fading the whole
  backdrop from transparent, so stepping between photos flashed the page
  through. The backdrop is now static; only the photo eases.
- **Sticky header restored.** The quilted-header block set `position:relative`
  on `.site-head` after the `position:sticky` declaration — same specificity,
  later in the cascade — and silently un-stuck the header. There is a comment at
  the spot now saying not to put it back.
- **Recent-work masonry.** The caption fix had swapped in five portrait photos
  and one landscape, so the CSS columns went badly unbalanced and left a large
  gap. The tile order is now tall/wide/tall on both sides — **the order is
  load-bearing, check ratios in `_build/images.json` before swapping any tile.**
- A uniform-grid version of that strip was tried and reverted; the user prefers
  the masonry.

**2026-08-05 — GO LIVE + mobile + polish**

- **MERGED `rebuild` → `main` and pushed.** Clean fast-forward, 39 commits, 211
  files, zero conflicts. www.autotopsandtrim.com now serves the new site
  (36 KB HTML vs the old 13.7 MB bundle). All 7 key URLs verified 200.
- **Mobile pass, five rounds**, all inside `@media (max-width:899px)` — nothing in
  it applies at 900px and up, so desktop was never touched:
  - sideways drag fixed (see architecture note), sticky call bar fixed
  - buttons side by side; a lone button no longer stretches full width
  - recent work capped at 6 tiles; About photos and blog cards became swipe rows
  - footer rebuilt as tap-to-open dropdowns (hidden-checkbox, still zero JS)
  - scroll-reveals disabled below 900px — they were the "choppy" feel
  - body copy stepped down repeatedly; section intros centred
- **Rounded corners** as three tokens: `--r-media` 16px, `--r-card` 14px,
  `--r-ctl` 8px, matching the reference site's Tailwind radii.
- **Header + dark surfaces got the shop's own craft in CSS** — a blue-to-charcoal
  gradient, a faint diamond-quilt tufting texture, and a stitched seam as the
  header's divider. Quilting also on the hero, dark bands and footer at ~half
  opacity. All palette colours, no images. Review cards were made opaque
  (`#2F343A`) so the quilting stops at the card edge.
- **Hero slideshow** — 4 photos, 5s crossfade, timer bars, zero JS, holds slide 1
  under reduced-motion. No per-slide captions, deliberately: the filenames are
  untrustworthy (open item 3).
- **TCPA SMS consent** on the quote form — not required, not pre-checked,
  carrying every required disclosure.
- **Contrast fix:** the 01–04 feature numerals were `--rule` on a tint band =
  **1.12:1**, effectively invisible. Now `--blue`: 4.47:1 on tint, 5.22:1 on white.
- **Performance:** font preload sitewide, srcset-aware LCP image preload on home,
  `fetchpriority="high"` on the hero, `content-visibility:auto` on bands.
- **All 105 Drive photos pulled** — 95 unique, every one a real JPEG. Contact
  sheet at `_build/incoming/contact-sheet.html`, awaiting the user's labels.
- **Logo direction agreed** — combine the stitch-outline (their ref #1) with the
  quilted seats (ref #2); a prompt was supplied 2026-08-05. Still open.

