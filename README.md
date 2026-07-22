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

## For whoever builds the rest (the important part)
The experience is **data-driven**, so adding the remaining nights does **not** mean rewriting anything.

```
index.html         ← the finished, self-contained experience (generated — do not hand-edit)
src/
  build.py         ← rebuilds index.html; holds the SCENES list + the look & motion
  art/             ← one .jpg per scene (the page images)
```

**To add a scene:**
1. Put its image in `src/art/` as `<name>.jpg`.
2. Add one entry to the `SCENES` list in `src/build.py`.
3. Run `python3 src/build.py`. That regenerates `index.html`.

The animation engine, styling, navigation, accessibility, and phone handling are shared by
every scene, so new nights inherit all of it automatically.

## Design notes
- Palette and type follow the book: deep indigo night, honey-gold moon, warm cream, matte texture.
- Motion is deliberately gentle — a breathing moon halo, drifting gold dust, soft parallax, and
  a slow settle as each scene arrives. It respects "reduce motion" system settings.
- The story text currently lives inside each page image. A later enhancement can lift the text out
  as live, reflowable words (better on small phones, screen-reader friendly, translatable) — the
  engine is already built to accept that without a rewrite.
