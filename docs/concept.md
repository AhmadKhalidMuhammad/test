# The Twenty-Eight Nights — Reading Experience Concept

## The idea in one line
Not a slideshow of scanned pages — **one continuous night you move through**, where the moon is
the narrator, every illustrated thing is alive on its own plane, and the words are real text set
in the book's voice.

## What the reader feels
A calm, bedtime descent through a single lunar month. The moon is always present and slowly
changes phase as you read. Each spread is a **living diorama** rather than a flat picture:

- **Background** sits behind (sky, room, garden), text and objects removed and painted in.
- **Objects** float on their own planes with gentle idle life drawn from the story — the sleeping
  cloud *breathes*, the lantern *flickers*, the tigress is *still*, the mother *pours light down*.
- **Text is live** — re-typeset from the manuscript in the book's typography, rising in a calm
  reading cadence, never baked into an image. It reflows on a phone, can be read aloud, and can be
  translated.

## The through-line: the moon, and the travelling light
The book's own logic is that the moon gives light away and gets it back. So the moon is the spine
of the experience, and **page turns morph** rather than cut: a single moon glides and changes
phase from one spread to the next; where the moon isn't the link, a mote of light travels (the
"passing down"). The whole book reads as one unbroken world.

## Pace and interaction (calm by default)
- **Two ways to read:** *Read to me* (auto-advance with the reading-cadence text and optional
  narration) and *I'll turn the pages* (self-paced by scroll / tap / arrow / keyboard).
- **The moon rail** shows where you are in the month and jumps to any night.
- **Rest, don't exit:** leaving keeps your place; you return to the same moon.
- Motion honours `prefers-reduced-motion` — everything settles to a quiet still.

## Two moments only the screen can do
- **Night 29 — The Looking:** the room dissolves into a real dusk sky and invites the reader
  *outside* to find the first new crescent.
- **Night 30 — The Night Made of Patience:** stays sealed and only unlocks in the months the true
  lunar calendar runs long — "only the sky may open this."

## Craft guardrails (from the book's own rules)
Hand-printed, matte, quiet negative space; the centre gutter protected; no titles on pills or
boxes; character continuity (the mother's moon-cream palette; the daughter distinct; the tigress
white and stripe-less); never an em dash in visible text; curly quotation marks.

## Why the rebuild
The old version baked text into images, cut objects with brittle colour thresholds, and shipped as
one monolithic file. The new architecture treats the book as **data**: every page is a manifest of
separated layers + live text, produced by a repeatable asset pipeline and rendered by a small,
modular engine. That is what makes "alive, page by page, cleanly" actually achievable and
maintainable.
