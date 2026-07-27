#!/usr/bin/env python3
"""
Turns a flat spread (src/art/<id>.jpg) into a LIVING scene:
  src/art/<id>/plate.jpg   - background with the objects painted out (inpainted)
  src/art/<id>/<obj>.png   - each object cut out as a feathered transparent sprite
  src/art/<id>/layers.json - each object's pixel position on the plate

How the cut works, per object you list:
  - "warm"    : a warm/cream object (moon, cloud, lantern) sitting on blue sky
  - "notblue" : a colourful object (butterfly) sitting on blue sky
Holes are filled with a smooth sky-gradient fit (upper sky) or local inpainting
(near the horizon), so the object can move without revealing a ghost.

Run from the repo root:  python3 src/extract.py
Then run:                python3 src/build.py

To make a NEW scene living, add a block at the bottom with the object bounding
boxes (find them by eye on the spread), then re-run this and build.py.
"""
import cv2, numpy as np, json, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ROOT / "assets" / "sources"
PAGES = ROOT / "assets" / "pages"

def _save_sprite(im, mask, path):
    """Crop the masked region of `im` to a feathered BGRA sprite; return its bbox."""
    import numpy as np, cv2
    a = cv2.GaussianBlur((mask * 255).astype(np.uint8), (0, 0), 1.6)
    yy, xx = np.where(mask > 0)
    x0, x1, y0, y1 = xx.min(), xx.max() + 1, yy.min(), yy.max() + 1
    pad = 6; x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(im.shape[1], x1 + pad); y1 = min(im.shape[0], y1 + pad)
    bgra = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2BGRA); bgra[:, :, 3] = a[y0:y1, x0:x1]
    cv2.imwrite(str(path), bgra)
    return {"x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0)}

def _split_butterfly(im, mask, out, oid, axis_abs):
    """Split a butterfly mask into left wing, right wing, and a central body strip,
    each pivoting on the body axis, so the wings can flap in 3D without folding the body."""
    import numpy as np
    W = im.shape[1]
    ys, xs = np.where(mask > 0); x0, x1 = xs.min(), xs.max()
    bw = int((x1 - x0) * 0.085)                 # body strip half-width
    ov = int((x1 - x0) * 0.02)                  # wings overlap slightly under the body
    L = mask.copy(); L[:, axis_abs + ov:] = 0
    R = mask.copy(); R[:, :axis_abs - ov] = 0
    B = np.zeros_like(mask); B[:, axis_abs - bw:axis_abs + bw] = mask[:, axis_abs - bw:axis_abs + bw]
    parts = {}
    for pid, m in (("L", L), ("R", R), ("body", B)):
        bb = _save_sprite(im, m, out / f"{oid}_{pid}.png")
        bb["pivot"] = round((axis_abs - bb["x"]) / bb["w"] * 100, 2)  # axis as % of this part's width
        parts[pid] = bb
    whole = {"x": int(xs.min()), "y": int(ys.min()), "w": int(xs.max()-xs.min()+1), "h": int(ys.max()-ys.min()+1)}
    whole["parts"] = parts
    return whole

def extract(name, warm=(), notblue=(), butterflies=(), detext_boxes=(), telea_below=470):
    im = cv2.imread(str(SOURCES / f"{name}.jpg")); H, W = im.shape[:2]
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    Hh, S, V = hsv[:, :, 0].astype(int), hsv[:, :, 1].astype(int), hsv[:, :, 2].astype(int)

    def box(b): m = np.zeros((H, W), np.uint8); m[b[1]:b[3], b[0]:b[2]] = 1; return m
    def largest(m):
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
        return m if n <= 1 else (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    def fillh(m):
        ff = m.copy().astype(np.uint8); h, w = ff.shape; mm = np.zeros((h + 2, w + 2), np.uint8)
        inv = (1 - ff).astype(np.uint8); cv2.floodFill(inv, mm, (0, 0), 0)
        return ((ff > 0) | (inv > 0)).astype(np.uint8)

    def warm_grabcut(b, pad=22, iters=7):
        """Clean cut of a warm/cream object (moon, cloud) off blue sky, using GrabCut
        with strongly-blue pixels marked as definite background."""
        x0, y0, x1, y1 = max(0, b[0]-pad), max(0, b[1]-pad), min(W, b[2]+pad), min(H, b[3]+pad)
        roi = im[y0:y1, x0:x1]; hs = hsv[y0:y1, x0:x1]
        h, s, v = hs[:, :, 0].astype(int), hs[:, :, 1].astype(int), hs[:, :, 2].astype(int)
        warm = (((h < 86) | (h > 150)) | (s < 40)) & (v > 120)
        blue = (h >= 92) & (h <= 140) & (s > 45)
        gc = np.full(roi.shape[:2], cv2.GC_PR_BGD, np.uint8)
        gc[blue] = cv2.GC_BGD
        core = cv2.erode(largest(fillh((warm & ~blue).astype(np.uint8))), np.ones((5, 5), np.uint8))
        gc[warm & ~blue] = cv2.GC_PR_FGD
        gc[core > 0] = cv2.GC_FGD
        cv2.grabCut(roi, gc, None, np.zeros((1, 65)), np.zeros((1, 65)), iters, cv2.GC_INIT_WITH_MASK)
        ref = largest(fillh(((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8)))
        ref = largest(cv2.morphologyEx(ref, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)))
        full = np.zeros((H, W), np.uint8); full[y0:y1, x0:x1] = ref; return full
    objs = {}
    for oid, b, *rest in warm:
        objs[oid] = warm_grabcut(b)
    def notblue_mask(b, pad=34):
        # a colourful object (butterfly) on a textured, painted blue sky. GrabCut with a
        # trimap keyed to each pixel's CIELab distance from THIS image's local sky colour:
        #   - sure background : the padded border ring (guaranteed sky)
        #   - sure foreground : the butterfly's colourful core (far from sky, eroded)
        #   - probable fg     : everything moderately far from sky
        # GrabCut then models sky-vs-object colour and returns the whole butterfly as one
        # piece -- every wing edge and both antennae -- with the sky genuinely transparent.
        x0, y0, x1, y1 = max(0, b[0]-pad), max(0, b[1]-pad), min(W, b[2]+pad), min(H, b[3]+pad)
        roi = im[y0:y1, x0:x1]; rf = roi.astype(np.float32)
        bm = (rf[:, :, 0] > rf[:, :, 2] + 8) & (rf[:, :, 0] > 90)
        sky = (np.median(roi[bm].reshape(-1, 3), 0) if bm.sum() > 50
               else np.array([190, 150, 120])).astype(np.uint8)
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB).astype(np.float32)
        skl = cv2.cvtColor(np.uint8([[sky]]), cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)
        dist = np.sqrt(((lab - skl) ** 2).sum(2))
        gc = np.full(roi.shape[:2], cv2.GC_PR_BGD, np.uint8)
        gc[dist > 22] = cv2.GC_PR_FGD
        gc[:12, :] = gc[-12:, :] = gc[:, :12] = gc[:, -12:] = cv2.GC_BGD
        gc[cv2.erode(largest((dist > 34).astype(np.uint8)), np.ones((5, 5), np.uint8)) > 0] = cv2.GC_FGD
        cv2.grabCut(roi, gc, None, np.zeros((1, 65)), np.zeros((1, 65)), 8, cv2.GC_INIT_WITH_MASK)
        m = largest(((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8))
        m = largest(fillh(m))
        full = np.zeros((H, W), np.uint8); full[y0:y1, x0:x1] = m
        return full
    for oid, b, *rest in notblue:
        objs[oid] = notblue_mask(b)
    bflies = {}   # id -> (mask, axis_abs)
    for oid, b, axis_frac, *rest in butterflies:
        m = notblue_mask(b, rest[0] if rest else 9)
        bflies[oid] = (m, int(b[0] + axis_frac * (b[2] - b[0])))

    union = np.zeros((H, W), np.uint8)
    for m in objs.values(): union |= m
    for m, _ in bflies.values(): union |= m
    uni_d = cv2.dilate(union, np.ones((15, 15), np.uint8))

    # smooth 2D polynomial sky fit (no banding), used for holes in the upper sky
    sky = (((Hh >= 92) & (Hh <= 142) & (S > 28) & (V > 55)) |
           ((V > 150) & (S < 70) & (Hh >= 88) & (Hh <= 146))).astype(np.uint8)
    sky &= (1 - uni_d).astype(np.uint8); sky[700:, :] = 0
    ys, xs = np.where(sky > 0); xn, yn = xs / W, ys / H
    A = np.stack([np.ones_like(xn), xn, yn, xn * xn, xn * yn, yn * yn], 1)
    gx, gy = np.meshgrid(np.arange(W) / W, np.arange(H) / H)
    G = np.stack([np.ones_like(gx), gx, gy, gx * gx, gx * gy, gy * gy], -1)
    field = np.zeros((H, W, 3), np.float32)
    for ch in range(3):
        coef, _, _, _ = np.linalg.lstsq(A, im[ys, xs, ch].astype(np.float32), rcond=None)
        field[:, :, ch] = G @ coef
    field = np.clip(field + np.random.default_rng(7).normal(0, 3.0, (H, W, 1)), 0, 255)

    telea = cv2.inpaint(im, uni_d, 15, cv2.INPAINT_TELEA).astype(np.float32)
    band = np.zeros((H, W), np.float32); band[:telea_below, :] = 1
    usef = (uni_d.astype(np.float32) * band)[..., None]
    plate = (field * usef + telea * (1 - usef)).astype(np.uint8)

    # remove baked prose from the (object-free) plate, so one background has both gone.
    # Colour-aware: any pixel whose CIELab distance from the local paper exceeds `thr`
    # is text -- catches navy AND red/italic strokes fully (no faint ghosts left behind).
    if detext_boxes:
        tmask = np.zeros((H, W), np.uint8)
        for x0, y0, x1, y1, *thr in detext_boxes:
            t = thr[0] if thr else 16
            reg = plate[y0:y1, x0:x1]
            paper = np.median(reg.reshape(-1, 3), 0).astype(np.uint8)
            lab = cv2.cvtColor(reg, cv2.COLOR_BGR2LAB).astype(np.float32)
            plab = cv2.cvtColor(np.uint8([[paper]]), cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)
            tmask[y0:y1, x0:x1] = (np.sqrt(((lab - plab) ** 2).sum(2)) > t).astype(np.uint8)
        tmask = cv2.dilate(tmask, np.ones((3, 3), np.uint8), iterations=3)
        plate = cv2.inpaint(plate, tmask, 5, cv2.INPAINT_TELEA)
        print(f"    {name}: removed {int(tmask.sum())} px of baked text")

    out = PAGES / name; out.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out / "background.jpg"), plate, [cv2.IMWRITE_JPEG_QUALITY, 92])
    meta = {"w": W, "h": H, "layers": {}}
    for nm, m in objs.items():
        a = cv2.GaussianBlur((cv2.erode(m, np.ones((2, 2), np.uint8)) * 255).astype(np.uint8), (0, 0), 0.9)
        yy, xx = np.where(m > 0); x0, x1, y0, y1 = xx.min(), xx.max() + 1, yy.min(), yy.max() + 1
        pad = 6; x0 = max(0, x0 - pad); y0 = max(0, y0 - pad); x1 = min(W, x1 + pad); y1 = min(H, y1 + pad)
        bgra = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2BGRA); bgra[:, :, 3] = a[y0:y1, x0:x1]
        cv2.imwrite(str(out / f"obj-{nm}.png"), bgra)
        meta["layers"][nm] = {"x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0)}
    for oid, (m, axis_abs) in bflies.items():
        meta["layers"][oid] = _split_butterfly(im, m, out, oid, axis_abs)
    json.dump(meta, open(out / "layers.json", "w"), indent=1)
    print(f"  {name}: {list(meta['layers'])}")


def detext(name, boxes, radius=5):
    """Remove baked prose from a spread and write the clean text-free background.
    `boxes` are (x0,y0,x1,y1) rectangles around the text; within each, pixels markedly
    darker than the local paper are inpainted away. The words are re-typeset live from
    content/book.json over the result (see docs/architecture.md, Job B)."""
    im = cv2.imread(str(SOURCES / f"{name}.jpg")); H, W = im.shape[:2]
    V = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[:, :, 2].astype(int)
    mask = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in boxes:
        reg = V[y0:y1, x0:x1]
        mask[y0:y1, x0:x1] = (reg < np.median(reg) - 30).astype(np.uint8)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
    clean = cv2.inpaint(im, mask, radius, cv2.INPAINT_TELEA)
    out = PAGES / name; out.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out / "background.jpg"), clean, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"  detext {name}: removed {int(mask.sum())} px of baked text")


if __name__ == "__main__":
    print("Extracting living scenes...")
    # bounding boxes are (x0, y0, x1, y1) in the spread's own pixels
    extract("cover",
            warm=[("moon", (120, 30, 480, 440)), ("cloud", (1035, 70, 1410, 300))],
            notblue=[("bfly", (392, 432, 782, 778))],
            telea_below=470)
    extract("week1",
            warm=[("moon", (150, 40, 490, 505), 13)],
            telea_below=520)
    extract("week2",
            warm=[("moon", (258, 52, 478, 438))],
            telea_below=460)
    # week3 (full moon) and week4 (waning crescent) sit small, through a window frame:
    # they are lit with a breathing glow overlay in build.py rather than cut out.

    # ---- text layer (Job B): lift baked prose so it can be re-typeset live ----
    extract("night1", detext_boxes=[(135, 48, 300, 82), (132, 88, 475, 195),
                                    (133, 205, 535, 700), (553, 205, 895, 615)])
    # foreword: cut + animate the crescent moon AND lift its prose (text on the right)
    extract("foreword2", warm=[("moon", (120, 30, 270, 240))],
            detext_boxes=[(1055, 70, 1915, 122), (1055, 138, 1700, 438), (1030, 492, 1385, 695)],
            telea_below=260)
    print("Done. Now run: python3 tools/build.py")
