# Auto Tops and Trim — checkpoint

_Snapshot, not a log. Overwrite stale content._
**Updated: 2026-08-06**

> The authoritative document is **`HANDOFF.md` in this repo**. Read that first.
> This file is the two-line orientation.

---

## Where we are

The 16-page site is **live** on www.autotopsandtrim.com. `rebuild` is
**well ahead of `main`** — production does not have the logo work, the header
redesign, clean URLs or the 30-article queue. All of that is on `rebuild` and
verified on the preview URL only.

Preview: https://hopeton-website-git-rebuild-auto-top-and-trim.vercel.app

## Current focus

**The header is mid-redesign.** It is currently white (was dark blue/charcoal),
with a circular cream badge logo and no text wordmark. The whole change is one
delimited `TRIAL: white header` block at the end of `assets/site.css` — delete it
to go back to the dark header.

The logo has three unresolved problems, listed at the top of `HANDOFF.md`. The
first is not cosmetic: **it is a Ford Mustang with the running-horse emblem**,
which is a trademark exposure for the shop.

## Done recently

- Photo caption audit — 43 files are only 33 distinct images; 9 captions
  contradicted their photo. 5 of 16 pages showed the same photo twice. Now 0,
  guarded by `_build/dupcheck.py`.
- Clean URLs live in production (`/gallery`, not `/gallery.html`).
- 30 blog posts written, dated 3/day from 2026-08-06 to 2026-08-14.
- Keyword research saved to `SEO_KEYWORDS.md`.
- Charles Monk's review photos added; his review moved to position 2.
- Lightbox backdrop flash fixed; sticky header regression fixed.
- `make_responsive.py` no longer destroys alpha channels.

## Next steps

1. Settle the logo — trademark first, then SVG in two colourways.
2. Decide whether the white header stays or reverts.
3. Fast-forward `main` once the header is settled.
4. Keep releasing the blog queue (see blockers).

## Blocked on the user

- **Apex TLS.** Root cause found: a single `A @ Parked` row in GoDaddy.
  Paste-ready prompt at `APEX_TLS_FIX_PROMPT.md`.
- **`workflow` token scope** — without it the daily publish job cannot be
  committed, so the blog queue does not self-release.
- **Formspree ownership** of `mrpzzdgz` — log in with the shop email and check
  whether the form is in the account.
- **Google Business Profile recovery** — the single highest-value marketing task
  on the project. "near me" is where the demand is and only GBP wins it.
- **The 95 photo labels** in `_build/incoming/contact-sheet.html`. Deduplication
  left the catalogue thin, especially on landscape shots, which constrains the
  home page layout.
- **Marine / aviation / motorcycle photo provenance** — four images that read as
  commercial photography sit under a "cut, stitched and fitted in house" claim.

## Rules that bite

- Site is **generated**. Never hand-edit root `.html`. Run
  `python _build/build_pages.py` then `_build/validate.py` then `_build/dupcheck.py`.
- **Zero JavaScript** — a hard rule, because the old site used JS for nav and
  broke the back button.
- Design system is **locked**: Archivo, never a serif; the blues; no tan.
- **Never push to `main` without explicit approval.**
- Never caption a photo from its filename — read the verified-content map above
  `GALLERY` in `_build/build_pages.py`.
- The user has asked that **desktop not be touched** unless explicitly
  requested. State which breakpoints a change affects before making it.
