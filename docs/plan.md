# The Twenty-Eight Nights — Plan to finish the living book

A roadmap in incremental **jobs**. Each job is self-contained, reviewable, and leaves the
experience shippable. Two disciplines run through all of them: **clean object cutting** and
**gentle, meaning-matched motion**, plus **morph-style page turns** where a shared object
carries from one spread to the next.

## Principles

- **Cut cleanly first.** Every animated object is separated from its background (GrabCut +
  local repair), the hole is painted in, and the piece is verified on a transparent
  checkerboard before it is animated. No cut, no animation.
- **Motion follows meaning.** Each object's gentle idle motion is drawn from what the story
  says it does (the sleeping cloud breathes; the lantern flickers; the mother pours light down).
  Nothing bounces or flashes; it is a bedtime book.
- **Morph the page turns.** Where two spreads share an object — above all the moon — a single
  element glides / grows / changes phase across the turn (the Week One → Week Two moon is the
  proof). Where they don't, a travelling mote of light bridges them.
- **Data-driven, no rewrites.** Adding a page = add its art + a scene entry + its object boxes.
  The engine (motion, parallax, morph, navigation, accessibility) is shared.
- **One self-contained `index.html`** stays the deliverable: a shareable link and an offline file.

## Job 0 — Foundation and proof  ✅ done
Engine, cutting/inpainting pipeline, per-object motion, breathing-glow + falling-light effects,
the intro and all four week introductions alive, and the **moon-morph PoC** (Week One ⇄ Week Two).

## Job 1 — Object & motion catalogue (the cast)
Use the **cast sheet** (the mother as queen, general, captain, lantern-keeper; the daughter; the
object icons) and the **element sheet** (moon phases, clouds happy/sleeping/raining, butterflies)
to build one clean sprite library with **multiple views/poses** of each recurring character and
prop. For each, define its gentle idle motion and its morph behaviour. Deliverable: the catalogue
+ a one-screen motion reference. *This is what makes every later night fast and consistent.*

## Jobs 2–5 — The four weeks, one week per job
For each week's seven nights: read the spread, cut its 1–3 hero objects, give each its
meaning-matched motion, and set the **morph transition** into and out of it (usually the moon's
phase progressing, or the "light travelling" in Week Four). Continuity checks against the cast.

- **Job 2 — Week One, Nights 1–7** (gentle forms): cloud, jasmine, rain-as-care, lantern-keeper…
- **Job 3 — Week Two, Nights 8–14** (powerful forms): the whispering queen, the still tigress…
- **Job 4 — Week Three, Nights 15–21** (the mirror): reflections, the paper crown, the full moon…
- **Job 5 — Week Four, Nights 22–28** (the passing down): light handed downward, the night of no moon…

## Job 6 — The Last Nights & the ending
Night 29 *The Looking* (turn the reader outward to find the new crescent), the **sealed page** and
Night 30 *The Night Made of Patience* unlocked by the **true lunar calendar**, the closing
("the circle begins again"), and the back matter.

## Job 7 — Whole-book polish
Morph every remaining page turn into a continuous moon/light journey; a full reduced-motion and
performance pass; optional narration and ambient night sound designed in from their reserved slots;
final QA on phones, tablets, and desktop.

## Per-night workflow (repeatable, ~ the same each time)
1. Read the exact spread text; pick the one hero action + supporting relationship.
2. Cut the hero object(s); inpaint; verify on checkerboard.
3. Assign gentle idle motion from the catalogue.
4. Set the morph in/out (shared object or light bridge).
5. Render, inspect at full size, correct once, commit.
