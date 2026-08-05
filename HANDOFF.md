# Auto Tops and Trim — Handoff

Read this first in a new chat. Everything needed to continue is in this repo.

**Last updated:** 2026-08-04

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
| `main` | still the OLD 14 MB single-page bundle. **Untouched. Still what autotopsandtrim.com serves.** |
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
- **Images:** 480/800/1400px WebP variants served via `srcset`.
  Mobile home page ≈ 430 KB across 11 images, versus 14 MB before.
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

## Open — in priority order

1. **BLOCKER — the contact form.** It posts to `https://formspree.io/f/mrpzzdgz`,
   an endpoint baked in by the original design tool that **neither the user nor I
   own or can verify.** The user reported a test lead reaching "my email" but has
   not confirmed which address. Until this is resolved, real customer names and
   phone numbers flow to an unverified destination. **Do not launch ads before fixing.**
   Fix: create a Formspree form on the user's own account pointed at
   contact@autotopsandtrim.com, swap `FORM_ENDPOINT` in `_build/build_site.py`.
2. **BLOCKER-ISH — the photo captions are not trustworthy.** A perceptual-hash
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
3. **Mobile pass.** Desktop is being signed off first, by the user's choice. Mobile
   currently needs alignment work throughout.
4. **Logo.** User is supplying an SVG or transparent PNG (~600px+). Goes where the
   `AUTO TOPS & TRIM` text sits in the header. Also kills the "AT&T" loading
   placeholder in the old bundle.
5. **Photos for the sunroof page.** The page ships with no photography because
   the catalogue has none of that repair. A few before/after shots of a sagging
   shade would finish it.
6. **Photos in Google Drive** — folder `1K6ndwfHhQg-N0GH1xWcbeceo9UjmETuA`
   ("Hopeton images resaves"), 100+ files (the listing pages).
   **The importer is written and waiting: `_build/import_photos.py`.** It dedupes
   by SHA-256, groups near-identical bursts by average-hash, fixes EXIF rotation,
   writes numbered review WebPs and a `contact-sheet.html` for the user to label.

   ⚠️ **Blocked on getting the files onto disk.** The Drive MCP returns file
   content as base64 through the conversation, so pulling 100 photos that way is
   not viable. Ask the user to download the folder (Drive → right-click → Download
   gives a zip), unzip it, then run:
   `python _build/import_photos.py --src "C:/path/to/unzipped"`

   📌 **The "HEIC" premise is probably wrong.** Drive reports `mimeType:
   image/jpeg` for every file in that folder, including the ones named `.HEIC` —
   Drive sniffs type from content, so these look like JPEG bytes carrying a stale
   extension (the folder is named "resaves"). If so, Chrome can display them and
   no HEIC conversion is needed. `import_photos.py` prints each file's **real**
   format, which settles it in one run. It also registers `pillow-heif` if
   installed, so genuine HEICs still work.

   Confirmed duplicates already visible in the listing: `957048668919016666.JPG`
   appears 3×, and `3577465635962975728.JPG`, `1016386281106343502.HEIC`,
   `4817363804744854242.HEIC`, `7048509423189683054.JPG` and
   `7757101485305033643.HEIC` each appear 2× at identical byte sizes.
7. **Merge `rebuild` → `main`** once approved. That is the go-live moment.
8. Google Business Profile is locked out (forgotten login) — recovery is the
   highest-leverage marketing task; it drives the local map pack.
9. Square recommended for card payments and invoices (NOT Shopify — wrong shape
   for in-person custom quoting).
10. Terms/privacy — user parked this. A short privacy note is the useful one,
   since the form collects names and numbers.

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
