# Architecture

Clean separation of four concerns: **content** (text), **assets** (separated image layers),
**tools** (the pipeline that produces assets), and **app** (the engine that renders them). A build
step assembles everything into one distributable `dist/index.html` — so the source stays modular
and reviewable while the deliverable stays a single shareable / offline file.

## Directory layout

```
.
├── docs/                     concept.md, architecture.md
├── content/
│   ├── manuscript.md         the book's words — the single source of truth for text
│   └── book.json             ordered pages: which layers, positions, motions, transitions, text ids
├── assets/
│   └── pages/<id>/           one folder per page, fully decomposed:
│       ├── background.jpg      art with every object AND all text removed, holes inpainted
│       ├── obj-<name>.png      each object as a clean cut-out (transparent)
│       └── layers.json         per-object anchor box + which text blocks belong to the page
├── tools/                    the asset pipeline (Python + OpenCV) — never ships to the browser
│   ├── decompose.py            page -> background + object cut-outs + text-removed plate
│   ├── extract_text.py         locate baked text regions -> inpaint out -> record boxes
│   └── build.py                assemble modular src + inlined assets -> dist/index.html
├── src/                      the app (modular, no framework, no bundler needed)
│   ├── index.html              shell
│   ├── styles.css              tokens + components (light/dark, reduced-motion)
│   └── engine/
│       ├── main.js               boot: load book.json, build scenes, wire everything
│       ├── scene.js              a page: background + layers + live text
│       ├── layer.js              one object plane (position, depth, idle motion)
│       ├── motion.js             the motion vocabulary (breathe, drift, flicker, pour, still…)
│       ├── morph.js              shared-object morph across page turns (the moon, the light)
│       ├── text.js               live text rendering + reading-cadence reveal
│       ├── navigation.js         scroll / tap / keyboard / moon rail / pacing modes
│       └── ambient.js            stars, gold dust, global atmosphere
└── dist/index.html           built single-file distributable
```

## Data model

**A page** (`content/book.json` entry):
```jsonc
{
  "id": "cover",
  "kind": "cover|divider|night|interstitial",
  "background": "assets/pages/cover/background.jpg",
  "objects": [
    { "id": "moon",  "motion": "breathe", "depth": 0.35, "morph": "moon" },
    { "id": "cloud", "motion": "sleep",   "depth": 0.55 },
    { "id": "bfly",  "motion": "flit",    "depth": 1.25 }
  ],
  "text": ["cover.title", "cover.tagline"],   // ids into the manuscript
  "transition": { "morph": "moon" }            // what carries into the next page
}
```

**Text** lives in `content/manuscript.md` as addressable blocks (id + content + role), never in an
image. The engine positions and animates it over the background.

**Object geometry** (anchor box, pivots) lives in each page's `layers.json`, produced by the
pipeline — so positions are data, not code.

## The decomposition pipeline (`tools/`)
For every page: (1) detect and inpaint out the **text** → clean plate; (2) cut each **object** off
that plate (GrabCut with per-object trimaps + local repair), verified on a transparent
checkerboard; (3) inpaint the object holes → the final **background**; (4) write `layers.json`.
Output is committed under `assets/pages/<id>/`. The browser never runs OpenCV.

## The engine (`src/engine/`)
Small ES modules, one responsibility each, no framework. `morph.js` implements the
PowerPoint-Morph-style continuity: a shared object (the moon) is a single element positioned from
each page's rest layout and tweened + crossfaded across the turn. `motion.js` holds the reusable
idle motions so every page inherits the same restrained, matte feel.

## Build & distribute (`tools/build.py`)
Concatenates the engine modules in order, inlines `styles.css`, embeds each page's assets as data
URIs, and injects `book.json` + the manuscript, producing a self-contained `dist/index.html`
(works offline; publishes as a shareable link). No CDN, CSP-safe.

## Why this holds up
- Adding/animating a page = edit **data** (`book.json`, run the pipeline), never the engine.
- Text is correct, accessible, and translatable because it is never trapped in pixels.
- The single-file deliverable is preserved, but the source is clean and each concern is testable.
