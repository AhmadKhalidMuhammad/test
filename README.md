# The Twenty-Eight Nights — Interactive Experience

An immersive, moon-guided web version of the picture book *The Twenty-Eight Nights*.
This is the **first sample slice**: from the cover through **Night One**.

## How to open it

**`index.html` is the whole experience in a single file.**

- **Offline / to keep or gift:** download `index.html`, then double-click it. It opens
  in any web browser (phone, tablet, or computer) and works with no internet, forever.
- **Shareable link:** the same file is published as a private web page you can share.
  (Ask, and it can be re-published any time it changes.)

It works best in a **dark, quiet room**. On a phone, turn it **sideways** to read.

### Ways to move through it
- **Scroll**, or **tap the arrows** at the top/bottom, or use the **arrow keys**.
- The **dots on the right** jump to any scene.
- **Night · Day** (top-right) switches the mood.

## What's in this sample
Cover → the moon's phases → the living pieces → *Before the First Night* (×2) →
*The First Stories* (the opening myths) → *Week One · Crescent* → **Night One · The Cloud Who Chose a Garden**.

## The objects come to life
This is not a slideshow of flat pictures. Hero objects are cut out of each spread and animated on
their own layer, and lighter touches (glows, flames, falling light, twinkles) are painted on top.

The **book intro and all four week introductions** are alive, each matched to what the story means:

- **Cover** — the moon breathes and glows, the cloud sleeps, the butterfly rests among the lilies.
- **Week One · Crescent** ("the gentle forms") — the crescent moon breathes; the lantern flickers.
- **Week Two · First Quarter** ("the powerful forms") — the growing half-moon shines a little stronger.
- **Week Three · Full Moon** ("the mirror") — the full moon glows at its brightest; the lantern flickers.
- **Week Four · Waning** ("the passing down") — the mother pours a stream of golden light down into
  her daughter's hands; the waning moon and lantern glow.
- **Night One** — the little cloud does not rain on the sleeper; it gives her **shade and warmth**,
  shown as a soft glow watching over her.

Every night-sky scene twinkles, with gold dust drifting throughout. The remaining nights can be
brought to life the same way, one at a time.

## For whoever builds the rest (the important part)
The experience is **data-driven**, so adding or animating scenes does **not** mean rewriting the engine.

```
index.html         ← the finished, self-contained experience (generated — do not hand-edit)
src/
  build.py         ← rebuilds index.html; holds the SCENES list, the look, and the motion engine
  extract.py       ← cuts objects out of a spread and paints in the background behind them
  art/
    <name>.jpg     ← a flat scene (one image)
    <name>/        ← a living scene: plate.jpg + one .png per object + layers.json
```

**To add a flat scene:** drop `<name>.jpg` in `src/art/`, add an entry to `SCENES`, run `python3 src/build.py`.

**To make a scene come alive:**
1. In `src/extract.py`, add the object bounding boxes for that spread (find them by eye).
2. Run `python3 src/extract.py` — it writes `src/art/<name>/` (background plate + object sprites).
3. In `src/build.py`, give that scene a `living=` block listing each object and its motion
   (`moon`, `cloudBreathe`, `cloudDrift`, `butterfly`, plus optional `flames`, `rain`, `twinkle`).
4. Run `python3 src/build.py`.

Motion, parallax, navigation, theming, accessibility, and phone handling are shared by every scene,
so new nights inherit all of it automatically.

## Design notes
- Palette and type follow the book: deep indigo night, honey-gold moon, warm cream, matte texture.
- Motion is deliberately gentle and matte — nothing bounces or flashes. It respects the system
  "reduce motion" setting (everything settles to a calm still).
- The story text currently lives inside each page image. A later enhancement can lift the text out
  as live, reflowable words (better on small phones, screen-reader friendly, translatable) — the
  engine is already built to accept that without a rewrite.
