# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is
An interactive, animated web reading of the picture book *The Twenty-Eight Nights*. Each page is
broken into separated layers (background, cut-out objects, and — by design — live text) that
animate and **morph** between pages. Read `docs/concept.md` and `docs/architecture.md` first.

## Commands
```bash
python3 tools/decompose.py   # cut objects off the source spreads -> assets/pages/<id>/
python3 tools/build.py       # assemble content + assets + src -> dist/index.html
```
- No package manager, no bundler, no test runner. The pipeline needs `opencv-python-headless`,
  `numpy`, `pymupdf`, `Pillow` (pip). The app has zero runtime dependencies.
- **Preview / verify:** open `dist/index.html`, or drive it headless with the preinstalled
  Chromium at `/opt/pw-browsers/chromium-*/chrome-linux/chrome` via Playwright (`--no-sandbox`).
  There is no automated test suite; changes are verified visually by screenshotting scenes.
- The deliverable is the single self-contained `dist/index.html` (works offline, publishes as an
  Artifact). Never hand-edit `dist/`; it is generated.

## Architecture (the data flow is the whole point)
`content/` (data) → `tools/decompose.py` (Python/OpenCV pipeline) → `assets/pages/<id>/` (cut
layers) → `tools/build.py` (inline everything) → `dist/index.html` (runtime). The browser never
runs Python or fetches anything.

- **`content/book.json`** is the ordered list of pages. Each page names its `background`, its
  `objects` (with a `motion` and `depth`), overlay effects (`flames`/`glows`/`streams`/`twinkle`),
  optional `moonMorph`, and `text` ids into the manuscript. **Editing a page = editing this file**,
  not the engine.
- **`content/book.json`** also carries each page's live `content` (eyebrow/title/body/coda) and
  its `textbox`; `content/manuscript.md` is the human-readable prose reference. Text is rendered
  live over backgrounds, never baked in. Object cutting AND text-removal are both implemented
  (`tools/decompose.py`: `extract` cuts objects, `detext` inpaints baked prose — Night One is the
  live-text reference).
- **`tools/decompose.py`** cuts each object off blue sky (warm objects via GrabCut with a
  blue-as-background trimap; colourful objects like the butterfly via a clean silhouette + a local
  antenna-reconnect box), inpaints the hole into `background.jpg` (a smooth 2D polynomial sky fit
  above the horizon, local inpaint below), and writes `assets/pages/<id>/layers.json` (per-object
  pixel boxes). Object bounding boxes are hand-specified in the `__main__` block. Always verify a
  cut on a transparent checkerboard before animating it.
- **`tools/build.py`** turns each page + its assets into a scene descriptor (positions become
  percentages, images become data URIs), injects the array into the engine by replacing the
  `__SCENES__` token, inlines `styles.css`, and writes `dist/index.html`.
- **`src/engine/main.js`** is the runtime. It builds each `.scene` from its descriptor
  (blurred backdrop + centered `.stage` holding the background `.plate` and absolutely-%-positioned
  object `.layer`s), tracks the active scene with an IntersectionObserver, and runs one ambient
  canvas loop for gold dust + per-scene twinkles/streams.

## Two mechanisms worth knowing before editing the engine
- **Motion** is CSS, not JS: object motion is a class `m-<motion>` (`moon`, `cloudBreathe`,
  `cloudDrift`, `butterfly`, etc.) defined in `src/styles.css`. Overlay effects (`flame`,
  `glowspot`, gold-dust/twinkle/stream canvases) are also there. Add a motion = add a keyframe +
  class; all motion is gated by `prefers-reduced-motion`.
- **Morph** (PowerPoint-style page turns): pages flagged `moonMorph` share ONE `#morphmoon` overlay
  element. On scene change it is positioned from each page's *rest layout* (`restRect(aspect)`,
  scroll-independent) and its position/size CSS-transition while the two moon sprites crossfade —
  so the moon glides and changes phase across the turn. Those pages' backgrounds have the moon
  painted out so there is no double.

## Conventions
- Keep the hand-printed, matte, calm aesthetic; nothing bounces or flashes; protect negative space.
- Visible text: no em dashes; curly quotation marks/apostrophes; preserve the author's meaning.
- Character continuity: the mother's moon-cream palette; the daughter kept distinct; Night Eleven's
  tigress stays white and stripe-less.
- Git: work on the designated feature branch; the built `dist/index.html` is committed so the
  Artifact can be republished from it.
