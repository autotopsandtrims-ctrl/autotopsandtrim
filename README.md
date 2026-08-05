# Auto Tops and Trim

Website for Auto Tops and Trim — custom automotive, marine, aviation and
motorcycle upholstery in Monroe, North Carolina since 1989.

**Start here: [HANDOFF.md](HANDOFF.md)** — business facts, current state, open work.

## Structure

Static HTML, generated. Fifteen real pages, each with its own URL, meta and
structured data. No framework, no build step at deploy time, and **no JavaScript** —
the navigation, the photo lightbox and the page transitions are all CSS.

```
index.html, services.html, …   generated pages — DO NOT EDIT BY HAND
assets/                        responsive WebP variants (480/800/1400) + fonts
assets/originals/              recovered master photos — do not delete
_build/                        the generators
```

## Building

```bash
python _build/build_pages.py    # regenerate all pages
python _build/validate.py       # verify every link, image and srcset resolves
```

Page content lives in `_build/build_pages.py`; the shared shell (header, footer,
schema, form) in `_build/build_site.py`. Image paths come from
`_build/images.json` and are never hand-typed.

## Deployment

Vercel, deployed from this repo.

- `main` → production, **autotopsandtrim.com**
- `rebuild` → preview at
  `hopeton-website-git-rebuild-auto-top-and-trim.vercel.app`

Every push redeploys automatically.

> **Never edit files through GitHub's web editor.** It has silently committed an
> empty file and taken the live site down. Clone and push, or use the
> drag-and-drop "Upload files" flow.
