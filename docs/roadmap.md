# Roadmap — Jobs To Be Done

Incremental jobs, each a shippable slice that moves the book from "a slideshow of scanned spreads"
to "the best interactive reading of this book." Every job is framed as the reader's job to be done,
then what we build to serve it. Replaces the old flat plan.

Legend: ✅ done · ▶ next · ○ queued

---

### Job A ✅ — "I want the art to feel whole, not chopped up."
**Robust object cutting, proven.** Objects are separated with GrabCut driven by each pixel's colour
distance from the image's *local* sky, on a padded box, and every cut is verified on a transparent
checkerboard (a sky pixel must read transparent, the object opaque). Locked in `tools/decompose.py`.
*Reference: the cover — moon, cloud, and the full butterfly (both antennae, every wing edge).*

### Job B ▶ — "I want to read the words, comfortably, on any screen."
**The text layer.** Add a pipeline stage that detects the baked prose on each spread, inpaints it
out to a clean background, and records where it sat; the words come from `content/manuscript.md`
and are re-typeset **live** over the art with a reading-cadence reveal. This is the single biggest
upgrade — it unblocks every story page, fixes small-phone readability, and makes the book
accessible and translatable. *Deliverable: Night One fully live-typeset as the reference.*

### Job C ○ — "I want to feel inside each scene, not looking at a card."
**The living-diorama pass.** Depth parallax on pointer/scroll per object plane, a barely-there
camera settle on entry, and orchestrated text-with-art timing. Applied to the cover + Week One as
the reference feel, then inherited by all pages. *This is the concrete answer to "not a slideshow."*

### Job D ○ — "Read me Week One." (Nights 1–7, the gentle forms)
Cut each night's hero objects, remove/relayer its text, assign meaning-matched motion, and set the
**moon-phase morph** into and out of each turn. Establishes the repeatable per-night workflow.

### Job E ○ — "Read me Week Two." (Nights 8–14, the powerful forms)
Includes the white, stripe-less tigress (continuity guardrail) and her signature stillness.

### Job F ○ — "Read me Week Three." (Nights 15–21, the mirror)
Reflections and the full moon at its brightest; the paper-crown night.

### Job G ○ — "Read me Week Four." (Nights 22–28, the passing down)
The light travels downward; ends on the night of no moon.

### Job H ○ — "Take me to the end, and outside."
Night 29 *The Looking* turns the reader outward to find the new crescent; the **sealed page** and
Night 30 unlock on the true lunar calendar; the closing loop and back matter.

### Job I ○ — "Make the whole thing sing."
Morph every remaining page turn into one continuous moon/light journey; wire the reserved narration
and ambient-sound slots; a full reduced-motion, performance, and cross-device QA pass.

---

## The per-night workflow (Jobs D–G, repeatable)
1. Read the exact spread in `content/manuscript.md`; pick one hero action + one supporting relationship.
2. `tools/decompose.py`: cut the hero object(s); **verify on the checkerboard** before animating.
3. Remove/relayer the text (Job B stage); add the prose block to the manuscript.
4. Assign gentle idle motion; set the morph in/out (shared moon, or a light bridge).
5. `tools/build.py`; inspect the built page at full size; correct once; commit.

## Definition of done for a page
Objects verified transparent-clean · text live and readable on a phone · one clear hero motion ·
a morph or light bridge on at least one side of the turn · reduced-motion still is intact.
