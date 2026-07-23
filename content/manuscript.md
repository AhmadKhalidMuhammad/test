# The Twenty-Eight Nights — Manuscript

The single source of truth for the book's **words**. Text is never baked into an image; the engine
renders these blocks live over each page's background. Each block has an `id` (referenced from
`content/book.json`'s `text` array), a `role`, and its content.

Editorial rules: never an em dash in visible text; curly quotation marks and apostrophes; preserve
the author's meaning with only light punctuation and line-break edits for read-aloud clarity.

---

## Front matter

- **cover.title** (title) — The Twenty-Eight Nights
- **cover.tagline** (tagline) — A story for every night the moon has.

## Week openers

- **week1.eyebrow** (eyebrow) — Week One
- **week1.phase** (phase) — Crescent
- **week1.forms** (forms) — The Gentle Forms
- **week1.note** (note) — The small one's work this week is noticing.

- **week2.eyebrow** — Week Two
- **week2.phase** — First Quarter
- **week2.forms** — The Powerful Forms
- **week2.note** — The small one's work this week is admiring, and imitating.

- **week3.eyebrow** — Week Three
- **week3.phase** — Full Moon
- **week3.forms** — The Mirror
- **week3.note** — This week the light is at its fullest, and both faces can be seen.

- **week4.eyebrow** — Week Four
- **week4.phase** — Waning
- **week4.forms** — The Passing Down
- **week4.note** — This week the light travels. Watch where it goes.

## Nights (prose)

Populated as each night is decomposed. Example shape:

- **night1.title** (title) — The Cloud Who Chose a Garden
- **night1.body** (body) —
  The big clouds raced across the sky, as big clouds do.
  But one small, fluffy cloud stopped, right over one small garden, and stayed.
  And the small sleeper slept in the coolest shade in the whole city.
  She never knew why, and never got burned, not once, not ever.
- **night1.coda** (coda) — The softest ones choose one garden, and guard one nap, and call it enough.

> Remaining nights' prose is transcribed here as their pages enter the decomposition pipeline
> (see docs/architecture.md and PLAN.md).
