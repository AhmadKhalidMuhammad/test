#!/usr/bin/env python3
# Assembles the single-file, self-contained experience:
#   design tokens (CSS)  +  SCENES data  +  ASSETS (base64 art)  +  engine (JS)
# Editing content later = edit the SCENES array / CSS tokens. The engine rarely changes.
import json, base64, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ART = HERE / "art"

def load_assets():
    """Every .jpg in ./art becomes an asset keyed by its filename (without extension).
    To add art later: drop <id>.jpg in ./art and reference <id> in a SCENES entry."""
    out = {}
    for f in sorted(ART.glob("*.jpg")):
        b = f.read_bytes()
        out[f.stem] = "data:image/jpeg;base64," + base64.b64encode(b).decode()
    return out

assets = load_assets()

# ------- SCENES: the ONLY thing you edit to extend the book -------
# kind: 'cover' | 'atmos' | 'spread' | 'divider' | 'night'
# eyebrow: small live label shown in the corner readout (optional, "" to hide)
# glow: {x,y,r} percent position of the moon for the breathing halo (or None)
SCENES = [
 dict(id="cover", kind="cover", eyebrow="",
      alt="Cover. A honey-gold crescent moon with a gentle face and a sleeping cloud float over white lilies and an ornamental butterfly on a deep indigo night.",
      glow=dict(x=17, y=22, r=30)),
 dict(id="phasearc", kind="atmos", eyebrow="The moon has twenty-eight faces",
      alt="All twenty-eight phases of the moon arc across the night sky above a garden of lilies, with a sleeping cloud at the left.",
      glow=None),
 dict(id="elements", kind="spread", eyebrow="The living pieces",
      alt="A cast sheet of the book's living pieces: moon faces through their phases, ornamental butterflies, clouds that are happy, sleeping, and raining, and a border of flowers.",
      glow=None),
 dict(id="foreword1", kind="spread", eyebrow="Before the First Night",
      alt="An open book rests in a moonlit garden, holding a crown, a lantern, a ship's wheel, a small blue book and a butterfly, while three moon faces drift above it.",
      glow=dict(x=63, y=16, r=16)),
 dict(id="foreword2", kind="spread", eyebrow="Before the First Night",
      alt="The mother in her long indigo robe holds her small daughter's hand and they walk together toward a closed book, a crescent moon above and a butterfly nearby.",
      glow=dict(x=14, y=20, r=15)),
 dict(id="firststories", kind="divider", eyebrow="The First Stories",
      alt="Section title: The First Stories, from before anyone counted nights. A small crescent moon with a face and a butterfly rest among lilies on cream.",
      glow=dict(x=8, y=60, r=14)),
 dict(id="butterfly_moon", kind="spread", eyebrow="The First Stories",
      alt="The Butterfly and the Moon. A butterfly lifts from a white lily as a thread of light crosses to a crescent moon on the right of the spread.",
      glow=dict(x=88, y=22, r=16)),
 dict(id="storyhour", kind="spread", eyebrow="The First Stories",
      alt="The Story Hour. In the grey hour just before morning, the crescent moon leans low over a sleeping garden while a butterfly rests among giant lilies.",
      glow=dict(x=78, y=22, r=16)),
 dict(id="moonchanges", kind="spread", eyebrow="The First Stories",
      alt="Why the Moon Changes Shape. A row of moon faces shrinks from full to crescent across the sky, giving pieces of light away to the stars.",
      glow=dict(x=64, y=22, r=14)),
 dict(id="butterflycolors", kind="spread", eyebrow="The First Stories",
      alt="The Butterfly's Colors. A large ornamental butterfly glows above a sunrise-tinted garden, its wings coloured by the moon before the dew ever flew.",
      glow=dict(x=13, y=20, r=13)),
 dict(id="moonsfavorite", kind="spread", eyebrow="The First Stories",
      alt="The Moon's Favorite. A great full moon with a serene face smiles near morning while small stars climb toward it down beams of light.",
      glow=dict(x=80, y=34, r=22)),
 dict(id="week1", kind="divider", eyebrow="Week One · Crescent · The Gentle Forms",
      alt="Week One divider. A honey-gold crescent moon with a face hangs in a deep blue sky above a lantern, a candle, a loaf of bread and a butterfly among the flowers.",
      glow=dict(x=16, y=30, r=18)),
 dict(id="night1", kind="night", eyebrow="Night One · The Cloud Who Chose a Garden",
      alt="Night One, The Cloud Who Chose a Garden. A small sleeping cloud settles low over a child asleep in a moonlit garden while other clouds drift high above.",
      glow=dict(x=52, y=16, r=14)),
]

CSS = """
:root{
  --ground:#0e1738; --ground-2:#0a1230; --matte:#0b1330;
  --ink:#f0e8d0; --ink-soft:#c3cbe6; --ink-faint:#8791b8;
  --gold:#e7c46b; --gold-deep:#c9a24e; --terra:#d0704e;
  --line:rgba(231,196,107,.22); --line-soft:rgba(240,232,208,.12);
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
  --sans:ui-sans-serif,"Helvetica Neue",Arial,sans-serif;
  --ease:cubic-bezier(.22,.61,.36,1);
}
:root[data-theme="day"]{
  --ground:#efe4c6; --ground-2:#e7d9b8; --matte:#e7d9b8;
  --ink:#1b2a55; --ink-soft:#3f4a76; --ink-faint:#71789c;
  --gold:#a9791f; --gold-deep:#8a6318; --terra:#bf5836;
  --line:rgba(27,42,85,.20); --line-soft:rgba(27,42,85,.10);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--matte); color:var(--ink); font-family:var(--sans);
  -webkit-font-smoothing:antialiased; overscroll-behavior:none}
:focus-visible{outline:2px solid var(--gold); outline-offset:3px; border-radius:3px}

/* scrolling deck holds the scenes; UI chrome sits above it */
#deck{position:fixed; inset:0; overflow-y:scroll; scroll-snap-type:y mandatory; scroll-behavior:smooth}
.scene{position:relative; height:100vh; height:100dvh; scroll-snap-align:start; scroll-snap-stop:always;
  display:grid; place-items:center; overflow:hidden}

.backdrop{position:absolute; inset:-6%; background-size:cover; background-position:center;
  filter:blur(30px) brightness(.42) saturate(1.1); transform:scale(1.12); z-index:0}
:root[data-theme="day"] .backdrop{filter:blur(30px) brightness(.9) saturate(1.05)}
.scrim{position:absolute; inset:0; z-index:1;
  background:radial-gradient(130% 120% at 50% 42%, transparent 52%, rgba(4,8,24,.62))}
:root[data-theme="day"] .scrim{background:radial-gradient(130% 120% at 50% 42%, transparent 60%, rgba(60,50,20,.18))}

.plate{position:relative; z-index:3; display:block;
  max-width:min(96vw,1480px); max-height:86dvh; width:auto; height:auto;
  border-radius:3px; box-shadow:0 26px 70px rgba(0,0,0,.5), 0 2px 0 rgba(255,255,255,.05) inset;
  opacity:0; transform:scale(1.045) translateY(14px); transition:opacity 1s var(--ease), transform 1.15s var(--ease);
  will-change:transform,opacity}
.scene.active .plate{opacity:1; transform:none}

/* breathing moon halo, positioned over the moon in the art */
.glow{position:absolute; z-index:2; pointer-events:none; border-radius:50%; mix-blend-mode:screen;
  background:radial-gradient(circle, rgba(255,244,210,.55), rgba(231,196,107,.20) 45%, transparent 70%);
  opacity:0; transition:opacity 1.4s var(--ease)}
.scene.active .glow{opacity:1; animation:breathe 8s ease-in-out infinite}
@keyframes breathe{0%,100%{transform:scale(1)}50%{transform:scale(1.09)}}

/* gold-dust canvas floats above everything, ignores clicks */
#dust{position:fixed; inset:0; z-index:40; pointer-events:none}

/* ---- chrome ---- */
.chrome{position:fixed; z-index:60; font-family:var(--sans)}
.topbar{top:0; left:0; right:0; display:flex; justify-content:space-between; align-items:center;
  padding:16px 20px; background:linear-gradient(rgba(6,10,26,.5), transparent); pointer-events:none}
:root[data-theme="day"] .topbar{background:linear-gradient(rgba(30,24,10,.14), transparent)}
.brand{font-family:var(--serif); font-size:15px; letter-spacing:.02em; color:var(--ink);
  opacity:.9; text-shadow:0 1px 10px rgba(0,0,0,.5)}
.brand .cres{display:inline-block; width:12px; height:12px; margin-right:8px; vertical-align:-1px;
  border-radius:50%; background:radial-gradient(circle at 130% 50%, transparent 46%, var(--gold) 47%)}
.tbtn{pointer-events:auto; cursor:pointer; border:1px solid var(--line);
  background:rgba(10,16,40,.5); color:var(--ink-soft); font-size:12px; letter-spacing:.04em;
  padding:7px 12px; border-radius:20px; backdrop-filter:blur(6px)}
:root[data-theme="day"] .tbtn{background:rgba(240,228,198,.55)}
.tbtn:hover{color:var(--ink); border-color:var(--gold)}

/* progress rail */
.rail{top:50%; right:18px; transform:translateY(-50%); display:flex; flex-direction:column; gap:10px;
  align-items:center; z-index:60}
.rail button{width:9px; height:9px; padding:0; border-radius:50%; cursor:pointer;
  border:1px solid var(--gold-deep); background:transparent; transition:all .4s var(--ease)}
.rail button:hover{background:var(--gold-deep)}
.rail button[aria-current="true"]{background:var(--gold); border-color:var(--gold);
  height:22px; border-radius:6px; box-shadow:0 0 12px color-mix(in srgb,var(--gold) 60%,transparent)}

/* corner readout (live text layer) */
.readout{left:22px; bottom:20px; max-width:60vw; z-index:60;
  font-family:var(--serif); color:var(--ink); text-shadow:0 1px 14px rgba(0,0,0,.6);
  opacity:0; transform:translateY(6px); transition:opacity .8s var(--ease), transform .8s var(--ease)}
.readout.show{opacity:1; transform:none}
.readout .eb{text-transform:uppercase; letter-spacing:.22em; font-size:11.5px; color:var(--gold)}

/* scroll cue on the first scene */
.cue{position:absolute; z-index:50; bottom:26px; left:50%; transform:translateX(-50%);
  display:flex; flex-direction:column; align-items:center; gap:4px; color:var(--ink);
  font-family:var(--serif); letter-spacing:.14em; text-transform:uppercase; font-size:12px;
  text-shadow:0 1px 12px rgba(0,0,0,.6); transition:opacity .8s var(--ease)}
.cue .chev{width:16px; height:16px; border-right:2px solid var(--gold); border-bottom:2px solid var(--gold);
  transform:rotate(45deg); animation:nudge 2.4s ease-in-out infinite}
@keyframes nudge{0%,100%{transform:rotate(45deg) translate(0,0); opacity:.5}50%{transform:rotate(45deg) translate(3px,3px); opacity:1}}

/* arrows */
.arrows{z-index:60}
.arrow{position:fixed; left:50%; transform:translateX(-50%); width:44px; height:44px; cursor:pointer;
  border:1px solid var(--line); border-radius:50%; background:rgba(10,16,40,.42); backdrop-filter:blur(6px);
  display:grid; place-items:center; transition:all .3s var(--ease)}
:root[data-theme="day"] .arrow{background:rgba(240,228,198,.5)}
.arrow:hover{border-color:var(--gold); background:rgba(10,16,40,.7)}
.arrow.up{top:14px} .arrow.down{bottom:14px}
.arrow i{width:11px; height:11px; border-right:2px solid var(--gold); border-bottom:2px solid var(--gold)}
.arrow.down i{transform:rotate(45deg); margin-top:-3px}
.arrow.up i{transform:rotate(-135deg); margin-bottom:-3px}
.arrow[hidden]{display:none}

/* intro veil */
#veil{position:fixed; inset:0; z-index:80; display:grid; place-items:center; text-align:center;
  background:radial-gradient(120% 100% at 50% 30%, #1a2a5e, #070d24 70%); transition:opacity 1.1s var(--ease)}
:root[data-theme="day"] #veil{background:radial-gradient(120% 100% at 50% 30%, #f4ead0, #e3d3ad 75%)}
#veil.gone{opacity:0; pointer-events:none}
#veil .in{max-width:640px; padding:0 28px}
#veil .eb{font-family:var(--serif); text-transform:uppercase; letter-spacing:.28em; font-size:12px; color:var(--gold)}
#veil h1{font-family:var(--serif); font-weight:700; color:var(--ink); text-wrap:balance;
  font-size:clamp(34px,7vw,64px); line-height:1.04; margin:.35em 0 .1em}
#veil p{color:var(--ink-soft); font-style:italic; font-family:var(--serif); font-size:clamp(15px,2.4vw,19px); margin:.2em 0 1.6em}
#veil .moon{width:78px; height:78px; margin:0 auto 20px; border-radius:50%;
  background:radial-gradient(circle at 38% 34%, #fff5d8, var(--gold) 55%, var(--gold-deep) 100%);
  box-shadow:0 0 50px 8px color-mix(in srgb,var(--gold) 45%,transparent); animation:breathe 7s ease-in-out infinite}
.begin{cursor:pointer; font-family:var(--serif); font-size:17px; letter-spacing:.02em; color:var(--ink);
  border:1px solid var(--gold); background:transparent; padding:12px 30px; border-radius:2px;
  transition:all .35s var(--ease)}
.begin:hover{background:var(--gold); color:#10142c}
#veil .hint{margin-top:20px; font-family:var(--sans); font-style:normal; font-size:12px; letter-spacing:.05em; color:var(--ink-faint)}

@media (prefers-reduced-motion: reduce){
  #deck{scroll-behavior:auto}
  .plate{transition:opacity .5s linear; transform:none !important}
  .scene.active .glow, #veil .moon, .cue .chev{animation:none}
  .glow{opacity:.7 !important}
}
/* portrait-phone reading nudge (CSS-only; this is a landscape book) */
#rotate{position:fixed; z-index:70; top:66px; left:50%; transform:translateX(-50%); display:none;
  align-items:center; gap:9px; padding:9px 15px; border-radius:22px; white-space:nowrap;
  background:rgba(10,16,40,.6); backdrop-filter:blur(8px); border:1px solid var(--line);
  color:var(--ink-soft); font-family:var(--sans); font-size:12.5px; letter-spacing:.02em}
:root[data-theme="day"] #rotate{background:rgba(240,228,198,.7)}
#rotate .icn{display:inline-block; width:15px; height:15px; border:2px solid var(--gold);
  border-radius:4px; position:relative; animation:tilt 3.2s ease-in-out infinite}
@keyframes tilt{0%,100%{transform:rotate(0)}50%{transform:rotate(-88deg)}}
@media (orientation:portrait) and (pointer:coarse){ #rotate{display:flex} }

@media (max-width:640px){
  .plate{max-width:96vw}
  .rail{right:10px} .readout{max-width:70vw; bottom:16px}
  .brand span.full{display:none}
}
"""

def js_scene_list():
    return json.dumps([{k:s[k] for k in ("id","kind","eyebrow","alt","glow")} for s in SCENES])

JS = """
const SCENES = __SCENES__;
const ASSETS = __ASSETS__;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const deck = document.getElementById('deck');
const rail = document.getElementById('rail');
const readout = document.getElementById('readout');
let sceneEls = [];

/* ---- build scenes from data ---- */
SCENES.forEach((s, i) => {
  const sec = document.createElement('section');
  sec.className = 'scene'; sec.dataset.i = i;
  sec.setAttribute('aria-label', s.alt);
  const src = ASSETS[s.id];

  const bd = document.createElement('div');
  bd.className = 'backdrop'; bd.style.backgroundImage = `url(${src})`;
  const scrim = document.createElement('div'); scrim.className = 'scrim';

  const img = document.createElement('img');
  img.className = 'plate'; img.src = src; img.alt = s.alt;
  img.loading = i < 2 ? 'eager' : 'lazy'; img.decoding = 'async';

  sec.append(bd, scrim, img);

  if (s.glow){
    const g = document.createElement('div'); g.className = 'glow';
    // sized relative to the plate once it lays out; positioned in %
    g.style.cssText += `left:${s.glow.x}%; top:${s.glow.y}%; width:${s.glow.r}vmax; height:${s.glow.r}vmax; transform:translate(-50%,-50%)`;
    sec.appendChild(g);
  }
  if (i === 0){
    const cue = document.createElement('div'); cue.className = 'cue'; cue.id = 'cue';
    cue.innerHTML = 'Scroll<span class="chev"></span>';
    sec.appendChild(cue);
  }
  deck.appendChild(sec);

  const dot = document.createElement('button');
  dot.type = 'button'; dot.title = s.eyebrow || s.kind;
  dot.setAttribute('aria-label', 'Go to ' + (s.eyebrow || ('scene ' + (i+1))));
  dot.addEventListener('click', () => sceneEls[i].scrollIntoView());
  rail.appendChild(dot);
});
sceneEls = [...deck.querySelectorAll('.scene')];
const dots = [...rail.querySelectorAll('button')];

/* ---- active scene tracking ---- */
let current = 0;
function setActive(i){
  current = i;
  sceneEls.forEach((el, k) => el.classList.toggle('active', k === i));
  dots.forEach((d, k) => d.setAttribute('aria-current', k === i ? 'true' : 'false'));
  const s = SCENES[i];
  if (s.eyebrow){
    readout.innerHTML = `<span class="eb">${s.eyebrow}</span>`;
    readout.classList.add('show');
  } else { readout.classList.remove('show'); }
  const cue = document.getElementById('cue'); if (cue) cue.style.opacity = i === 0 ? '' : '0';
  document.getElementById('up').hidden = i === 0;
  // hide the down-arrow on the first scene so it doesn't collide with the scroll cue
  document.getElementById('down').hidden = (i === 0) || (i === sceneEls.length - 1);
}
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting && e.intersectionRatio >= 0.55){
    setActive(+e.target.dataset.i);
  }});
}, {root: deck, threshold: [0.55]});
sceneEls.forEach(el => io.observe(el));
setActive(0);

/* ---- navigation ---- */
function go(dir){
  const n = Math.min(sceneEls.length - 1, Math.max(0, current + dir));
  sceneEls[n].scrollIntoView();
}
document.getElementById('down').addEventListener('click', () => go(1));
document.getElementById('up').addEventListener('click', () => go(-1));
addEventListener('keydown', (e) => {
  if (['ArrowDown','PageDown',' '].includes(e.key)){ e.preventDefault(); go(1); }
  else if (['ArrowUp','PageUp'].includes(e.key)){ e.preventDefault(); go(-1); }
  else if (e.key === 'Home'){ e.preventDefault(); sceneEls[0].scrollIntoView(); }
  else if (e.key === 'End'){ e.preventDefault(); sceneEls[sceneEls.length-1].scrollIntoView(); }
});

/* ---- pointer parallax (depth on the active plate) ---- */
if (!reduce){
  let tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
  addEventListener('pointermove', (e) => {
    tx = (e.clientX / innerWidth - 0.5); ty = (e.clientY / innerHeight - 0.5);
    if (!raf) raf = requestAnimationFrame(tick);
  }, {passive:true});
  function tick(){
    cx += (tx - cx) * 0.06; cy += (ty - cy) * 0.06;
    const plate = sceneEls[current].querySelector('.plate');
    if (plate && sceneEls[current].classList.contains('active'))
      plate.style.transform = `translate(${cx*-16}px, ${cy*-12}px) scale(1.012)`;
    if (Math.abs(tx-cx) > 0.001 || Math.abs(ty-cy) > 0.001){ raf = requestAnimationFrame(tick); }
    else raf = 0;
  }
}

/* ---- gold-dust motes ---- */
(function(){
  const c = document.getElementById('dust'); const ctx = c.getContext('2d');
  let W, H, motes = [];
  const gold = () => getComputedStyle(document.documentElement).getPropertyValue('--gold').trim() || '#e7c46b';
  function resize(){
    W = c.width = innerWidth * devicePixelRatio; H = c.height = innerHeight * devicePixelRatio;
    c.style.width = innerWidth + 'px'; c.style.height = innerHeight + 'px';
    const n = reduce ? 0 : Math.min(46, Math.floor(innerWidth / 26));
    motes = Array.from({length:n}, () => ({
      x: Math.random()*W, y: Math.random()*H,
      r: (Math.random()*1.6 + 0.5) * devicePixelRatio,
      s: (Math.random()*0.22 + 0.05) * devicePixelRatio,
      d: Math.random()*Math.PI*2, a: Math.random()*0.4 + 0.15
    }));
  }
  function frame(t){
    ctx.clearRect(0,0,W,H); ctx.fillStyle = gold();
    for (const m of motes){
      m.y -= m.s; m.x += Math.sin(t*0.0004 + m.d) * 0.2 * devicePixelRatio;
      if (m.y < -4) { m.y = H + 4; m.x = Math.random()*W; }
      ctx.globalAlpha = m.a * (0.6 + 0.4*Math.sin(t*0.001 + m.d));
      ctx.beginPath(); ctx.arc(m.x, m.y, m.r, 0, 7); ctx.fill();
    }
    ctx.globalAlpha = 1;
    if (!reduce) requestAnimationFrame(frame);
  }
  resize(); addEventListener('resize', resize);
  if (!reduce) requestAnimationFrame(frame);
})();

/* ---- theme toggle ---- */
document.getElementById('theme').addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme');
  document.documentElement.setAttribute('data-theme', cur === 'day' ? 'night' : 'day');
});

/* ---- intro veil ---- */
const veil = document.getElementById('veil');
function begin(){ veil.classList.add('gone'); setTimeout(()=>veil.style.display='none', 1200);
  sceneEls[0].scrollIntoView(); }
document.getElementById('beginBtn').addEventListener('click', begin);
"""

html = f"""<title>The Twenty-Eight Nights</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="The Twenty-Eight Nights — an interactive bedtime story that follows the moon.">
<style>{CSS}</style>

<div id="deck" aria-label="The Twenty-Eight Nights, scene by scene"></div>
<canvas id="dust" aria-hidden="true"></canvas>

<div class="chrome topbar">
  <div class="brand"><span class="cres"></span><span class="full">The Twenty-Eight Nights</span></div>
  <button class="tbtn" id="theme" type="button" aria-label="Switch between night and day">Night · Day</button>
</div>
<div class="chrome rail" id="rail" role="navigation" aria-label="Jump to a scene"></div>
<div class="chrome readout" id="readout" aria-live="polite"></div>
<div id="rotate" class="chrome"><span class="icn" aria-hidden="true"></span>Turn your device sideways to read</div>
<div class="chrome arrows">
  <button class="arrow up" id="up" type="button" aria-label="Previous scene" hidden><i></i></button>
  <button class="arrow down" id="down" type="button" aria-label="Next scene"><i></i></button>
</div>

<div id="veil">
  <div class="in">
    <div class="moon" aria-hidden="true"></div>
    <div class="eb">An interactive bedtime book</div>
    <h1>The Twenty-Eight Nights</h1>
    <p>A story for every night the moon has.</p>
    <button class="begin" id="beginBtn" type="button">Begin</button>
    <div class="hint">Scroll, tap the arrows, or use your keyboard. Best in a dark, quiet room.</div>
  </div>
</div>

<script>{JS.replace('__SCENES__', js_scene_list()).replace('__ASSETS__', json.dumps(assets))}</script>
"""

out = HERE.parent / "index.html"
out.write_text(html)
print("Built", out, "-", len(html)//1024, "KB,", len(assets), "scenes of art")
