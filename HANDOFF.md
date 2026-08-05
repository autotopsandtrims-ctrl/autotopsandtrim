# Auto Tops and Trim — Handoff

Read this first in a new chat. Everything needed to continue is in this repo.

**Last updated:** 2026-08-05

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
python _build/build_pages.py     # regenerates all 15 pages
python _build/validate.py        # checks every link, image and srcset resolves
```

`_build/build_site.py` holds the shell (head, header, footer, CTA, form, schema).
`_build/build_pages.py` holds page content and the review data.
`_build/images.json` is the photo catalogue — **image paths are read from it, never typed by hand.**

Other tools, only needed if reworking photography:
- `_build/extract_assets.ps1` — pulls photos/fonts out of the old bundle
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

- **15 real pages, real URLs.** The old site was a single-page app where nav
  changed a JS variable and the URL never moved — which is why the back button
  was broken. That is fixed structurally.
- **Zero JavaScript.** Nav is a CSS checkbox; the lightbox is CSS `:target`
  (so the back button closes it); transitions are CSS. Everything works with
  scripts disabled.
- **Images:** 480/800/1400px WebP variants served via `srcset`.
  Mobile home page ≈ 430 KB across 11 images, versus 14 MB before.
- `assets/originals/` holds the 43 recovered master photos — **the uncle lost
  most of his originals; these came out of the old bundle. Do not delete.**

---

## Done

- 15 pages: home, services + 5 service pages, gallery, process, about, contact, blog + 3 articles
- Site outage fixed (an empty `index.html` had been committed)
- Phone corrected sitewide; hours corrected (site had said Mon–Fri 8–5, Sat 9–2 — both wrong)
- Street address added to contact, footer, map and schema
- All 7 written Google reviews, verbatim, with names and dates. Auto-sliding marquee on a dark band.
- Click-to-enlarge lightbox on gallery, home recent-work and the fanned stack
- Fanned photo stack on the gallery
- Photo-forward bento service cards; alternating service rows; step timeline on process
- Masonry so photos are never cropped
- Per-page meta, LocalBusiness + AggregateRating + Article schema, sitemap.xml, robots.txt

---

## Open — in priority order

1. **BLOCKER — the contact form.** It posts to `https://formspree.io/f/mrpzzdgz`,
   an endpoint baked in by the original design tool that **neither the user nor I
   own or can verify.** The user reported a test lead reaching "my email" but has
   not confirmed which address. Until this is resolved, real customer names and
   phone numbers flow to an unverified destination. **Do not launch ads before fixing.**
   Fix: create a Formspree form on the user's own account pointed at
   contact@autotopsandtrim.com, swap `FORM_ENDPOINT` in `_build/build_site.py`.
2. **Mobile pass.** Desktop is being signed off first, by the user's choice. Mobile
   currently needs alignment work throughout.
3. **Logo.** User is supplying an SVG or transparent PNG (~600px+). Goes where the
   `AUTO TOPS & TRIM` text sits in the header. Also kills the "AT&T" loading
   placeholder in the old bundle.
4. **Sunroof shade repair service page.** 2 of 9 Google reviews are specifically
   about this and one customer drove an hour for it. Not mentioned anywhere on
   the site. Real demand, no competition, no page to rank.
5. **~100 photos in Google Drive** — folder `1K6ndwfHhQg-N0GH1xWcbeceo9UjmETuA`
   ("Hopeton images resaves"). Mostly **HEIC, which Chrome cannot display**, with
   visible duplicates. Plan: download → dedupe by hash → convert to WebP →
   numbered contact sheet for the user to label.
6. **Merge `rebuild` → `main`** once approved. That is the go-live moment.
7. Google Business Profile is locked out (forgotten login) — recovery is the
   highest-leverage marketing task; it drives the local map pack.
8. Square recommended for card payments and invoices (NOT Shopify — wrong shape
   for in-person custom quoting).
9. Terms/privacy — user parked this. A short privacy note is the useful one,
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
