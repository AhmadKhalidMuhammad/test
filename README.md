# The Twenty-Eight Nights — Interactive Book

An immersive, moon-guided reading of the picture book *The Twenty-Eight Nights*. Every page is
decomposed into separated layers (background, objects, live text) so the illustrations come alive
and morph from one page to the next.

New here? Read **[docs/concept.md](docs/concept.md)** (the reading experience) and
**[docs/architecture.md](docs/architecture.md)** (how it's built). The roadmap is
**[docs/roadmap.md](docs/roadmap.md)**.

## The deliverable
**`dist/index.html`** is the whole experience in one self-contained file: open it offline by
double-clicking, or publish it as a shareable link. It works on any phone, tablet, or computer,
best in a dark, quiet room (turn a phone sideways to read).

## Project layout
```
content/        the book as data
  book.json       ordered pages: layers, motions, transitions, text ids
  manuscript.md   the book's words (live text; never baked into an image)
assets/
  sources/        original full spreads (input to the pipeline)
  pages/<id>/     decomposed output: background.jpg + obj-*.png + layers.json
tools/          the pipeline (Python + OpenCV) and the build
  decompose.py    a spread -> background + object cut-outs (+ text later)
  build.py        assemble source + assets -> dist/index.html
src/            the app (modular, no framework)
  index.html      shell   ·   styles.css   ·   engine/ (motion, morph, ambient, nav…)
dist/index.html the built single-file distributable
docs/           concept, architecture, plan
```

## Working on it
```bash
python3 tools/decompose.py   # (re)cut objects for the living pages into assets/pages/
python3 tools/build.py       # assemble -> dist/index.html
```
Adding or animating a page is a **data** change: put its spread in `assets/sources/`, add object
boxes in `tools/decompose.py`, add a page entry to `content/book.json`, and rebuild. The engine,
motion, morph, navigation, and accessibility are shared, so every page inherits them.

## Status
Foundation + intro and the four week introductions are alive; the moon **morphs** from crescent to
first quarter across the Week One to Week Two turn. Remaining pages are decomposed and animated
through the pipeline, week by week, per `docs/roadmap.md`.
