#!/usr/bin/env python3
"""
Assemble the distributable from clean source.

  content/book.json  +  assets/pages/<id>/*  +  src/(index.html, styles.css, engine/*.js)
        ->  dist/index.html   (self-contained: works offline, publishes as a shareable link)

The browser never sees the pipeline or the raw folders; everything is inlined here.
Run from the repo root:  python3 tools/build.py
"""
import json, base64, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "assets" / "pages"

def datauri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

def pct(v, whole):
    return round(v / whole * 100, 3)

def scene_descriptor(page):
    """Turn a book.json page + its assets into what the engine consumes."""
    pid = page["id"]; d = PAGES / pid
    s = dict(id=pid, kind=page["kind"], eyebrow=page.get("eyebrow", ""), alt=page["alt"],
             twinkle=page.get("twinkle"), flames=page.get("flames", []),
             glows=page.get("glows", []), streams=page.get("streams", []),
             content=page.get("content"), textbox=page.get("textbox"))
    layers_file = d / "layers.json"
    living = layers_file.exists()
    if living:
        meta = json.loads(layers_file.read_text()); iw, ih = meta["w"], meta["h"]
        s["living"] = True
        s["plate"] = datauri(d / "background.jpg", "image/jpeg")
        s["aspect"] = round(iw / ih, 5)
        L = []
        for obj in page.get("objects", []):
            p = meta["layers"][obj["id"]]
            item = dict(id=obj["id"], motion=obj.get("motion", "float"),
                        depth=obj.get("depth", 0.5), glow=obj.get("glow"),
                        glowSize=obj.get("glowSize", 1.4), amp=obj.get("amp", 2.0),
                        x=pct(p["x"], iw), y=pct(p["y"], ih), w=pct(p["w"], iw), h=pct(p["h"], ih),
                        src=datauri(d / f"obj-{obj['id']}.png", "image/png"))
            L.append(item)
        s["layers"] = L
        if page.get("moonMorph"):
            p = meta["layers"]["moon"]
            s["moonMorph"] = dict(src=datauri(d / "obj-moon.png", "image/png"),
                                  x=pct(p["x"], iw), y=pct(p["y"], ih),
                                  w=pct(p["w"], iw), h=pct(p["h"], ih))
    else:
        s["img"] = datauri(d / "background.jpg", "image/jpeg")
        with open(d / "background.jpg", "rb") as f:      # JPEG SOF0/2 gives H,W without Pillow
            data = f.read()
        i = 2
        while i < len(data):
            if data[i] != 0xFF: i += 1; continue
            m = data[i+1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3):
                hh = (data[i+5] << 8) | data[i+6]; ww = (data[i+7] << 8) | data[i+8]
                s["aspect"] = round(ww / hh, 5); break
            i += 2 + ((data[i+2] << 8) | data[i+3])
    return s

def main():
    book = json.loads((ROOT / "content" / "book.json").read_text())
    scenes = [scene_descriptor(p) for p in book["pages"]]

    styles = (ROOT / "src" / "styles.css").read_text()
    engine = "\n".join((ROOT / "src" / "engine" / m).read_text()
                       for m in book.get("engine", ["main.js"]))
    engine = engine.replace("__SCENES__", json.dumps(scenes))
    html = (ROOT / "src" / "index.html").read_text()
    html = html.replace("/*STYLES*/", styles).replace("/*ENGINE*/", engine)

    out = ROOT / "dist" / "index.html"; out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    living = ", ".join(s["id"] for s in scenes if s.get("living"))
    print(f"Built {out.relative_to(ROOT)} - {len(html)//1024} KB, {len(scenes)} pages (living: {living})")

if __name__ == "__main__":
    main()
