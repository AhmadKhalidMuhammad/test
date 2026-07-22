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
ART = ROOT / "src" / "art"

def extract(name, warm=(), notblue=(), telea_below=470):
    im = cv2.imread(str(ART / f"{name}.jpg")); H, W = im.shape[:2]
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

    warmM = ((((Hh < 90) | (Hh > 150)) | (S < 45)) & (V > 108)).astype(np.uint8)
    objs = {}
    for oid, b, *rest in warm:
        c = rest[0] if rest else 11
        m = warmM & box(b); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((c, c), np.uint8))
        m = fillh(largest(m)); objs[oid] = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    for oid, b, *rest in notblue:
        c = rest[0] if rest else 9
        sky = ((Hh >= 95) & (Hh <= 140) & (S > 22) & (V > 90)).astype(np.uint8)
        m = ((1 - sky).astype(np.uint8)) & box(b); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((c, c), np.uint8))
        objs[oid] = fillh(largest(m))

    union = np.zeros((H, W), np.uint8)
    for m in objs.values(): union |= m
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

    out = ART / name; out.mkdir(exist_ok=True)
    cv2.imwrite(str(out / "plate.jpg"), plate, [cv2.IMWRITE_JPEG_QUALITY, 92])
    meta = {"w": W, "h": H, "layers": {}}
    for nm, m in objs.items():
        a = cv2.GaussianBlur((m * 255).astype(np.uint8), (0, 0), 1.6)
        yy, xx = np.where(m > 0); x0, x1, y0, y1 = xx.min(), xx.max() + 1, yy.min(), yy.max() + 1
        pad = 6; x0 = max(0, x0 - pad); y0 = max(0, y0 - pad); x1 = min(W, x1 + pad); y1 = min(H, y1 + pad)
        bgra = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2BGRA); bgra[:, :, 3] = a[y0:y1, x0:x1]
        cv2.imwrite(str(out / f"{nm}.png"), bgra)
        meta["layers"][nm] = {"x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0)}
    json.dump(meta, open(out / "layers.json", "w"), indent=1)
    print(f"  {name}: {list(meta['layers'])}")


if __name__ == "__main__":
    print("Extracting living scenes...")
    # bounding boxes are (x0, y0, x1, y1) in the spread's own pixels
    extract("cover",
            warm=[("moon", (120, 30, 480, 440)), ("cloud", (1035, 70, 1410, 300))],
            notblue=[("bfly", (390, 430, 805, 775))],
            telea_below=470)
    extract("week1",
            warm=[("moon", (150, 40, 490, 505), 13), ("cloud", (12, 545, 305, 712), 9)],
            telea_below=520)
    print("Done. Now run: python3 src/build.py")
