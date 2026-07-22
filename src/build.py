#!/usr/bin/env python3
"""
Builds the single-file interactive experience: index.html

Two kinds of scene:
  - FLAT   : one image (src/art/<id>.jpg). Gentle ambient only.
  - LIVING : a background plate (src/art/<id>/plate.jpg) plus cut-out object
             sprites (src/art/<id>/<layer>.png) with positions in layers.json.
             Each object animates on its own layer (moon breathes, cloud drifts,
             butterfly flaps, flame flickers...).

To add / animate a scene later you only touch DATA, never the engine:
  * FLAT   -> drop <id>.jpg in src/art and add an entry to SCENES.
  * LIVING -> run the extractor to make src/art/<id>/, then add an entry to
              SCENES with its layer motions. Re-run this script.
"""
import json, base64, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ART = HERE / "art"

def datauri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

def jpg(name):  return datauri(ART / f"{name}.jpg", "image/jpeg")

# ----------------------------------------------------------------------------
# SCENES  (edit this list to extend the book)
#   kind: cover | atmos | spread | divider | night
#   eyebrow: small live caption ("" hides it)
#   living:  None (flat) OR a dict describing plate + animated layers
#     layer motions: moon | cloudDrift | cloudBreathe | butterfly | flame | sway | float
#     depth: parallax strength (0 = far/still, ~1.5 = near/reactive)
# ----------------------------------------------------------------------------
SCENES = [
 dict(id="cover", kind="cover", eyebrow="",
      alt="Cover. A honey-gold crescent moon with a gentle face and a sleeping cloud float over white lilies and an ornamental butterfly on a deep indigo night.",
      twinkle="sky",
      living=dict(dir="cover", layers=[
          dict(id="moon",  motion="moon",      depth=0.35, glow="#ffe7a0", glowSize=1.5),
          dict(id="cloud", motion="cloudBreathe", depth=0.55),
          dict(id="bfly",  motion="butterfly", depth=1.25, split=True),
      ])),
 dict(id="phasearc", kind="atmos", eyebrow="The moon has twenty-eight faces",
      alt="All twenty-eight phases of the moon arc across the night sky above a garden of lilies, with a sleeping cloud at the left.",
      living=None, twinkle="sky"),
 dict(id="elements", kind="spread", eyebrow="The living pieces",
      alt="A cast sheet of the book's living pieces: moon faces through their phases, ornamental butterflies, clouds that are happy, sleeping, and raining, and a border of flowers.",
      living=None),
 dict(id="foreword1", kind="spread", eyebrow="Before the First Night",
      alt="An open book rests in a moonlit garden, holding a crown, a lantern, a ship's wheel, a small blue book and a butterfly, while three moon faces drift above it.",
      living=None, twinkle="sky"),
 dict(id="foreword2", kind="spread", eyebrow="Before the First Night",
      alt="The mother in her long indigo robe holds her small daughter's hand and they walk together toward a closed book, a crescent moon above and a butterfly nearby.",
      living=None, twinkle="sky"),
 dict(id="firststories", kind="divider", eyebrow="The First Stories",
      alt="Section title: The First Stories, from before anyone counted nights. A small crescent moon with a face and a butterfly rest among lilies on cream.",
      living=None),
 dict(id="butterfly_moon", kind="spread", eyebrow="The First Stories",
      alt="The Butterfly and the Moon. A butterfly lifts from a white lily as a thread of light crosses to a crescent moon on the right of the spread.",
      living=None, twinkle="sky"),
 dict(id="storyhour", kind="spread", eyebrow="The First Stories",
      alt="The Story Hour. In the grey hour just before morning, the crescent moon leans low over a sleeping garden while a butterfly rests among giant lilies.",
      living=None, twinkle="sky"),
 dict(id="moonchanges", kind="spread", eyebrow="The First Stories",
      alt="Why the Moon Changes Shape. A row of moon faces shrinks from full to crescent across the sky, giving pieces of light away to the stars.",
      living=None, twinkle="sky"),
 dict(id="butterflycolors", kind="spread", eyebrow="The First Stories",
      alt="The Butterfly's Colors. A large ornamental butterfly glows above a sunrise-tinted garden, its wings coloured by the moon before the dew ever flew.",
      living=None),
 dict(id="moonsfavorite", kind="spread", eyebrow="The First Stories",
      alt="The Moon's Favorite. A great full moon with a serene face smiles near morning while small stars climb toward it down beams of light.",
      living=None, twinkle="sky"),
 dict(id="week1", kind="divider", eyebrow="Week One · Crescent · The Gentle Forms",
      alt="Week One divider. A honey-gold crescent moon with a face hangs in a deep blue sky above a lantern, a candle, a loaf of bread and a butterfly among the flowers.",
      twinkle="sky",
      living=dict(dir="week1", layers=[
          dict(id="moon",  motion="moon",  depth=0.35, glow="#ffe7a0", glowSize=1.6),
          dict(id="cloud", motion="cloudBreathe", depth=0.5),
      ], flames=[dict(x=64.4, y=80.5, r=2.7, color="#ffce68")])),
 dict(id="night1", kind="night", eyebrow="Night One · The Cloud Who Chose a Garden",
      alt="Night One, The Cloud Who Chose a Garden. A small sleeping cloud settles low over a child asleep in a moonlit garden while other clouds drift high above.",
      living=None, twinkle=None,
      rain=[dict(x=62.5, y=52, w=21, h=25, color="#cfe0ff")]),
]

# ----------------------------------------------------------------------------
def build_assets():
    """Return scene descriptors with every image inlined as a data URI."""
    out = []
    for s in SCENES:
        d = dict(id=s["id"], kind=s["kind"], eyebrow=s["eyebrow"], alt=s["alt"],
                 twinkle=s.get("twinkle"), rain=s.get("rain", []))
        living = s.get("living")
        if living and not (ART / living["dir"] / "layers.json").exists():
            print(f"  ! {s['id']}: layers not extracted yet - falling back to flat")
            living = None
        if living:
            d["living"] = True
            ldir = ART / living["dir"]
            meta = json.load(open(ldir / "layers.json"))
            iw, ih = meta["w"], meta["h"]
            d["plate"] = datauri(ldir / "plate.jpg", "image/jpeg")
            d["aspect"] = round(iw / ih, 5)
            L = []
            for lay in living["layers"]:
                pos = meta["layers"][lay["id"]]
                L.append(dict(
                    id=lay["id"], motion=lay["motion"], depth=lay.get("depth", 0.5),
                    split=lay.get("split", False), glow=lay.get("glow"),
                    glowSize=lay.get("glowSize", 1.4), amp=lay.get("amp", 2.0),
                    src=datauri(ldir / f"{lay['id']}.png", "image/png"),
                    x=round(pos["x"]/iw*100, 3), y=round(pos["y"]/ih*100, 3),
                    w=round(pos["w"]/iw*100, 3), h=round(pos["h"]/ih*100, 3),
                ))
            d["layers"] = L
            d["flames"] = living.get("flames", [])
        else:
            d["img"] = jpg(s["id"])
        out.append(d)
    return out

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

#deck{position:fixed; inset:0; overflow-y:scroll; scroll-snap-type:y mandatory; scroll-behavior:smooth}
.scene{position:relative; height:100vh; height:100dvh; scroll-snap-align:start; scroll-snap-stop:always;
  display:grid; place-items:center; overflow:hidden}

.backdrop{position:absolute; inset:-6%; background-size:cover; background-position:center;
  filter:blur(30px) brightness(.42) saturate(1.1); transform:scale(1.12); z-index:0}
:root[data-theme="day"] .backdrop{filter:blur(30px) brightness(.9) saturate(1.05)}
.scrim{position:absolute; inset:0; z-index:1;
  background:radial-gradient(130% 120% at 50% 42%, transparent 52%, rgba(4,8,24,.62))}
:root[data-theme="day"] .scrim{background:radial-gradient(130% 120% at 50% 42%, transparent 60%, rgba(60,50,20,.18))}

/* stage shrink-wraps the plate; object layers are positioned in % within it */
.stage{position:relative; z-index:3; line-height:0;
  filter:drop-shadow(0 26px 60px rgba(0,0,0,.5));
  opacity:0; transform:scale(1.04) translateY(14px);
  transition:opacity 1s var(--ease), transform 1.15s var(--ease); will-change:transform,opacity}
.scene.active .stage{opacity:1; transform:none}
.plate{display:block; max-width:min(96vw,1480px); max-height:86dvh; width:auto; height:auto; border-radius:3px}

.layer{position:absolute; will-change:transform}
.layer .anim{width:100%; height:100%; display:block; position:relative; transform-origin:center}
.layer img{position:absolute; inset:0; width:100%; height:100%; display:block}

/* halo behind the moon */
.halo{position:absolute; left:50%; top:47%; transform:translate(-50%,-50%);
  border-radius:50%; mix-blend-mode:screen; pointer-events:none; z-index:-1;
  animation:breathe 8s ease-in-out infinite}

/* ---- object motions ---- */
@keyframes breathe{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-50%) scale(1.12)}}
.m-moon{animation:moonMove 9s ease-in-out infinite}
@keyframes moonMove{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-1.5%) scale(1.008)}}
.m-cloudBreathe{animation:cloudBreathe 9s ease-in-out infinite}
@keyframes cloudBreathe{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(1.4%,-1.1%) scale(1.02)}}
.m-cloudDrift{animation:cloudDrift 26s ease-in-out infinite}
@keyframes cloudDrift{0%{transform:translate(0,0)}50%{transform:translate(3.4%,-0.6%)}100%{transform:translate(0,0)}}
.m-float{animation:floatY 7s ease-in-out infinite}
@keyframes floatY{0%,100%{transform:translateY(0)}50%{transform:translateY(-2.4%)}}
.m-sway{animation:sway 8s ease-in-out infinite; transform-origin:bottom center}
@keyframes sway{0%,100%{transform:rotate(-.7deg)}50%{transform:rotate(.7deg)}}

/* butterfly: body bob + two wings flapping */
.m-butterfly{animation:bflyBob 7s ease-in-out infinite}
@keyframes bflyBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-0.5%)}}
.wing{position:absolute; inset:0; background-repeat:no-repeat; background-size:100% 100%}
.wing.l{clip-path:inset(0 49.5% 0 0); transform-origin:right center; animation:flapL .62s ease-in-out infinite}
.wing.r{clip-path:inset(0 0 0 49.5%); transform-origin:left center; animation:flapR .62s ease-in-out infinite}
@keyframes flapL{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.9)}}
@keyframes flapR{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.9)}}

/* flame flicker */
.flame{position:absolute; border-radius:50%; mix-blend-mode:screen; pointer-events:none; z-index:4;
  transform:translate(-50%,-50%); animation:flick 1.7s ease-in-out infinite}
@keyframes flick{0%,100%{opacity:.55; transform:translate(-50%,-50%) scale(1)}
  45%{opacity:.9; transform:translate(-50%,-52%) scale(1.14)}
  70%{opacity:.7; transform:translate(-50%,-50%) scale(1.05)}}

.twk{position:absolute; inset:0; z-index:4; pointer-events:none}
.rainc{position:absolute; inset:0; z-index:5; pointer-events:none}

#dust{position:fixed; inset:0; z-index:40; pointer-events:none}

/* ---- chrome ---- */
.chrome{position:fixed; z-index:60; font-family:var(--sans)}
.topbar{top:0; left:0; right:0; display:flex; justify-content:space-between; align-items:center;
  padding:16px 20px; background:linear-gradient(rgba(6,10,26,.5), transparent); pointer-events:none}
:root[data-theme="day"] .topbar{background:linear-gradient(rgba(30,24,10,.14), transparent)}
.brand{font-family:var(--serif); font-size:15px; letter-spacing:.02em; color:var(--ink); opacity:.9; text-shadow:0 1px 10px rgba(0,0,0,.5)}
.brand .cres{display:inline-block; width:12px; height:12px; margin-right:8px; vertical-align:-1px; border-radius:50%; background:radial-gradient(circle at 130% 50%, transparent 46%, var(--gold) 47%)}
.tbtn{pointer-events:auto; cursor:pointer; border:1px solid var(--line); background:rgba(10,16,40,.5); color:var(--ink-soft);
  font-size:12px; letter-spacing:.04em; padding:7px 12px; border-radius:20px; backdrop-filter:blur(6px)}
:root[data-theme="day"] .tbtn{background:rgba(240,228,198,.55)}
.tbtn:hover{color:var(--ink); border-color:var(--gold)}
.rail{top:50%; right:18px; transform:translateY(-50%); display:flex; flex-direction:column; gap:10px; align-items:center; z-index:60}
.rail button{width:9px; height:9px; padding:0; border-radius:50%; cursor:pointer; border:1px solid var(--gold-deep); background:transparent; transition:all .4s var(--ease)}
.rail button:hover{background:var(--gold-deep)}
.rail button[aria-current="true"]{background:var(--gold); border-color:var(--gold); height:22px; border-radius:6px; box-shadow:0 0 12px color-mix(in srgb,var(--gold) 60%,transparent)}
.readout{left:22px; bottom:20px; max-width:60vw; z-index:60; font-family:var(--serif); color:var(--ink); text-shadow:0 1px 14px rgba(0,0,0,.6);
  opacity:0; transform:translateY(6px); transition:opacity .8s var(--ease), transform .8s var(--ease)}
.readout.show{opacity:1; transform:none}
.readout .eb{text-transform:uppercase; letter-spacing:.22em; font-size:11.5px; color:var(--gold)}
.cue{position:absolute; z-index:50; bottom:26px; left:50%; transform:translateX(-50%); display:flex; flex-direction:column; align-items:center; gap:4px;
  color:var(--ink); font-family:var(--serif); letter-spacing:.14em; text-transform:uppercase; font-size:12px; text-shadow:0 1px 12px rgba(0,0,0,.6); transition:opacity .8s var(--ease)}
.cue .chev{width:16px; height:16px; border-right:2px solid var(--gold); border-bottom:2px solid var(--gold); transform:rotate(45deg); animation:nudge 2.4s ease-in-out infinite}
@keyframes nudge{0%,100%{transform:rotate(45deg) translate(0,0); opacity:.5}50%{transform:rotate(45deg) translate(3px,3px); opacity:1}}
.arrow{position:fixed; left:50%; transform:translateX(-50%); width:44px; height:44px; cursor:pointer; border:1px solid var(--line); border-radius:50%;
  background:rgba(10,16,40,.42); backdrop-filter:blur(6px); display:grid; place-items:center; transition:all .3s var(--ease); z-index:60}
:root[data-theme="day"] .arrow{background:rgba(240,228,198,.5)}
.arrow:hover{border-color:var(--gold); background:rgba(10,16,40,.7)}
.arrow.up{top:14px} .arrow.down{bottom:14px}
.arrow i{width:11px; height:11px; border-right:2px solid var(--gold); border-bottom:2px solid var(--gold)}
.arrow.down i{transform:rotate(45deg); margin-top:-3px}
.arrow.up i{transform:rotate(-135deg); margin-bottom:-3px}
.arrow[hidden]{display:none}
#rotate{position:fixed; z-index:70; top:66px; left:50%; transform:translateX(-50%); display:none; align-items:center; gap:9px; padding:9px 15px; border-radius:22px; white-space:nowrap;
  background:rgba(10,16,40,.6); backdrop-filter:blur(8px); border:1px solid var(--line); color:var(--ink-soft); font-family:var(--sans); font-size:12.5px; letter-spacing:.02em}
:root[data-theme="day"] #rotate{background:rgba(240,228,198,.7)}
#rotate .icn{display:inline-block; width:15px; height:15px; border:2px solid var(--gold); border-radius:4px; animation:tilt 3.2s ease-in-out infinite}
@keyframes tilt{0%,100%{transform:rotate(0)}50%{transform:rotate(-88deg)}}
@media (orientation:portrait) and (pointer:coarse){ #rotate{display:flex} }

#veil{position:fixed; inset:0; z-index:80; display:grid; place-items:center; text-align:center;
  background:radial-gradient(120% 100% at 50% 30%, #1a2a5e, #070d24 70%); transition:opacity 1.1s var(--ease)}
:root[data-theme="day"] #veil{background:radial-gradient(120% 100% at 50% 30%, #f4ead0, #e3d3ad 75%)}
#veil.gone{opacity:0; pointer-events:none}
#veil .in{max-width:640px; padding:0 28px}
#veil .eb{font-family:var(--serif); text-transform:uppercase; letter-spacing:.28em; font-size:12px; color:var(--gold)}
#veil h1{font-family:var(--serif); font-weight:700; color:var(--ink); text-wrap:balance; font-size:clamp(34px,7vw,64px); line-height:1.04; margin:.35em 0 .1em}
#veil p{color:var(--ink-soft); font-style:italic; font-family:var(--serif); font-size:clamp(15px,2.4vw,19px); margin:.2em 0 1.6em}
#veil .moon{width:78px; height:78px; margin:0 auto 20px; border-radius:50%;
  background:radial-gradient(circle at 38% 34%, #fff5d8, var(--gold) 55%, var(--gold-deep) 100%);
  box-shadow:0 0 50px 8px color-mix(in srgb,var(--gold) 45%,transparent); animation:veilbreathe 7s ease-in-out infinite}
@keyframes veilbreathe{0%,100%{transform:scale(1); opacity:.96}50%{transform:scale(1.05); opacity:1}}
.begin{cursor:pointer; font-family:var(--serif); font-size:17px; letter-spacing:.02em; color:var(--ink); border:1px solid var(--gold); background:transparent; padding:12px 30px; border-radius:2px; transition:all .35s var(--ease)}
.begin:hover{background:var(--gold); color:#10142c}
#veil .hint{margin-top:20px; font-family:var(--sans); font-style:normal; font-size:12px; letter-spacing:.05em; color:var(--ink-faint)}

@media (prefers-reduced-motion: reduce){
  #deck{scroll-behavior:auto}
  .stage{transition:opacity .5s linear; transform:none !important}
  .m-moon,.m-cloudBreathe,.m-cloudDrift,.m-float,.m-sway,.m-butterfly,.wing,.halo,.flame,.cue .chev,#veil .moon,#rotate .icn{animation:none !important}
}
@media (max-width:640px){
  .plate{max-width:96vw}
  .rail{right:10px} .readout{max-width:70vw; bottom:16px}
  .brand span.full{display:none}
}
"""

JS = r"""
const SCENES = __SCENES__;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const deck = document.getElementById('deck');
const rail = document.getElementById('rail');
const readout = document.getElementById('readout');

function el(tag, cls, css){ const e=document.createElement(tag); if(cls)e.className=cls; if(css)e.style.cssText=css; return e; }

/* ---- build scenes ---- */
SCENES.forEach((s, i) => {
  const sec = el('section','scene'); sec.dataset.i=i; sec.setAttribute('aria-label', s.alt);
  const plateSrc = s.living ? s.plate : s.img;
  sec.append(el('div','backdrop','background-image:url('+plateSrc+')'), el('div','scrim'));

  const stage = el('div','stage');
  const plate = el('img','plate'); plate.src=plateSrc; plate.alt=s.alt;
  plate.loading = i<2?'eager':'lazy'; plate.decoding='async';
  stage.appendChild(plate);

  if (s.living){
    s.layers.forEach(L => {
      const layer = el('div','layer',
        `left:${L.x}%;top:${L.y}%;width:${L.w}%;height:${L.h}%;z-index:${L.motion==='butterfly'?6:4}`);
      layer.dataset.depth = L.depth;
      const anim = el('div','anim m-'+L.motion);
      if (L.motion==='butterfly' && L.split){
        const wl=el('div','wing l'), wr=el('div','wing r');
        wl.style.backgroundImage='url('+L.src+')'; wr.style.backgroundImage='url('+L.src+')';
        anim.append(wl,wr);
      } else {
        const im=el('img'); im.src=L.src; im.alt=''; anim.appendChild(im);
      }
      if (L.glow){
        const halo=el('div','halo',
          `width:${L.glowSize*100}%;height:${L.glowSize*100}%;background:radial-gradient(circle, ${L.glow}cc, ${L.glow}44 42%, transparent 68%)`);
        anim.appendChild(halo);
      }
      layer.appendChild(anim); stage.appendChild(layer);
    });
    (s.flames||[]).forEach(f=>{
      const fl=el('div','flame',
        `left:${f.x}%;top:${f.y}%;width:${f.r*2}%;height:${f.r*3.2}%;background:radial-gradient(circle at 50% 60%, #fff3cf, ${f.color} 45%, transparent 72%)`);
      stage.appendChild(fl);
    });
  }
  if (s.twinkle){ const c=el('canvas','twk'); stage.appendChild(c); }
  if (s.rain && s.rain.length){ const rc=el('canvas','rainc'); rc._rain=s.rain; stage.appendChild(rc); }

  sec.appendChild(stage);
  if (i===0){ const cue=el('div','cue'); cue.id='cue'; cue.innerHTML='Scroll<span class="chev"></span>'; sec.appendChild(cue); }
  deck.appendChild(sec);

  const dot=el('button'); dot.type='button'; dot.title=s.eyebrow||s.kind;
  dot.setAttribute('aria-label','Go to '+(s.eyebrow||('scene '+(i+1))));
  dot.addEventListener('click',()=>sceneEls[i].scrollIntoView());
  rail.appendChild(dot);
});
const sceneEls=[...deck.querySelectorAll('.scene')];
const dots=[...rail.querySelectorAll('button')];

/* ---- twinkle canvases (per scene sky) ---- */
document.querySelectorAll('.twk').forEach(c=>{
  const st=c.parentElement;
  function size(){ c.width=Math.max(1,st.clientWidth); c.height=Math.max(1,st.clientHeight); }
  size(); new ResizeObserver(size).observe(st);
  const N=reduce?10:16;
  c._stars=Array.from({length:N},()=>({x:Math.random(),y:Math.random()*0.60,r:Math.random()*1.4+0.4,p:Math.random()*6.28,s:0.5+Math.random()}));
});
/* ---- rain canvases (drops live in % regions of the stage) ---- */
document.querySelectorAll('.rainc').forEach(c=>{
  const st=c.parentElement;
  function size(){ c.width=Math.max(1,st.clientWidth); c.height=Math.max(1,st.clientHeight); }
  size(); new ResizeObserver(size).observe(st);
  c._drops=[];
  c._rain.forEach(rg=>{ const n=reduce?0:Math.round(rg.w*2.2);
    for(let k=0;k<n;k++) c._drops.push({rg, x:Math.random(), y:Math.random(), len:6+Math.random()*10, sp:0.006+Math.random()*0.008}); });
});

/* ---- active scene ---- */
let current=0;
function setActive(i){
  current=i;
  sceneEls.forEach((e,k)=>e.classList.toggle('active',k===i));
  dots.forEach((d,k)=>d.setAttribute('aria-current',k===i?'true':'false'));
  const s=SCENES[i];
  if(s.eyebrow){ readout.innerHTML='<span class="eb">'+s.eyebrow+'</span>'; readout.classList.add('show'); }
  else readout.classList.remove('show');
  const cue=document.getElementById('cue'); if(cue) cue.style.opacity=i===0?'':'0';
  document.getElementById('up').hidden=i===0;
  document.getElementById('down').hidden=(i===0)||(i===sceneEls.length-1);
}
const io=new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting&&e.intersectionRatio>=0.55) setActive(+e.target.dataset.i); }),{root:deck,threshold:[0.55]});
sceneEls.forEach(e=>io.observe(e)); setActive(0);

/* ---- nav ---- */
function go(d){ const n=Math.min(sceneEls.length-1,Math.max(0,current+d)); sceneEls[n].scrollIntoView(); }
document.getElementById('down').addEventListener('click',()=>go(1));
document.getElementById('up').addEventListener('click',()=>go(-1));
addEventListener('keydown',e=>{
  if(['ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();go(1);}
  else if(['ArrowUp','PageUp'].includes(e.key)){e.preventDefault();go(-1);}
  else if(e.key==='Home'){e.preventDefault();sceneEls[0].scrollIntoView();}
  else if(e.key==='End'){e.preventDefault();sceneEls[sceneEls.length-1].scrollIntoView();}
});

/* ---- pointer parallax on object layers ---- */
let px=0,py=0,cx=0,cy=0,praf=0;
if(!reduce){
  addEventListener('pointermove',e=>{ px=e.clientX/innerWidth-0.5; py=e.clientY/innerHeight-0.5; if(!praf)praf=requestAnimationFrame(par); },{passive:true});
}
function par(){
  cx+=(px-cx)*0.06; cy+=(py-cy)*0.06;
  const sc=sceneEls[current]; if(sc){
    sc.querySelectorAll('.layer').forEach(l=>{
      const d=parseFloat(l.dataset.depth)||0;
      l.style.transform=`translate(${cx*-26*d}px,${cy*-18*d}px)`;
    });
  }
  if(Math.abs(px-cx)>0.001||Math.abs(py-cy)>0.001) praf=requestAnimationFrame(par); else praf=0;
}

/* ---- ambient render loop: gold dust + twinkles ---- */
(function(){
  const c=document.getElementById('dust'), ctx=c.getContext('2d'); let W,H,motes=[];
  const gold=()=>getComputedStyle(document.documentElement).getPropertyValue('--gold').trim()||'#e7c46b';
  function resize(){ W=c.width=innerWidth*devicePixelRatio; H=c.height=innerHeight*devicePixelRatio; c.style.width=innerWidth+'px'; c.style.height=innerHeight+'px';
    const n=reduce?0:Math.min(42,Math.floor(innerWidth/28));
    motes=Array.from({length:n},()=>({x:Math.random()*W,y:Math.random()*H,r:(Math.random()*1.5+0.5)*devicePixelRatio,s:(Math.random()*0.22+0.05)*devicePixelRatio,d:Math.random()*6.28,a:Math.random()*0.4+0.15}));
  }
  function frame(t){
    ctx.clearRect(0,0,W,H); ctx.fillStyle=gold();
    for(const m of motes){ m.y-=m.s; m.x+=Math.sin(t*0.0004+m.d)*0.2*devicePixelRatio; if(m.y<-4){m.y=H+4;m.x=Math.random()*W;}
      ctx.globalAlpha=m.a*(0.6+0.4*Math.sin(t*0.001+m.d)); ctx.beginPath(); ctx.arc(m.x,m.y,m.r,0,7); ctx.fill(); }
    const sc=sceneEls[current]; const tw=sc&&sc.querySelector('.twk');
    if(tw&&tw._stars&&tw.width>1){ const x2=tw.getContext('2d'); x2.clearRect(0,0,tw.width,tw.height); x2.fillStyle='#fff6d8';
      for(const st of tw._stars){ const a=0.25+0.6*(0.5+0.5*Math.sin(t*0.0016*st.s+st.p)); x2.globalAlpha=reduce?0.5:a;
        const X=st.x*tw.width, Y=st.y*tw.height, r=st.r; x2.beginPath(); x2.arc(X,Y,r,0,7); x2.fill();
        x2.globalAlpha*=0.5; x2.fillRect(X-r*3,Y-0.4,r*6,0.8); x2.fillRect(X-0.4,Y-r*3,0.8,r*6); }
      x2.globalAlpha=1; }
    const rc=sc&&sc.querySelector('.rainc');
    if(rc&&rc._drops&&rc.width>1){ const rx=rc.getContext('2d'); rx.clearRect(0,0,rc.width,rc.height); rx.lineWidth=1.1; rx.lineCap='round';
      for(const d of rc._drops){ const rg=d.rg; d.y+=d.sp; if(d.y>1){d.y=0;d.x=Math.random();}
        const X=(rg.x+d.x*rg.w)/100*rc.width, Y=(rg.y+d.y*rg.h)/100*rc.height;
        rx.strokeStyle=rg.color; rx.globalAlpha=reduce?0:0.5; rx.beginPath(); rx.moveTo(X,Y); rx.lineTo(X-1.5,Y+d.len); rx.stroke(); }
      rx.globalAlpha=1; }
    ctx.globalAlpha=1;
    if(!reduce) requestAnimationFrame(frame);
  }
  resize(); addEventListener('resize',resize);
  if(reduce){ frame(0); } else requestAnimationFrame(frame);
})();

/* ---- theme + intro ---- */
document.getElementById('theme').addEventListener('click',()=>{ const c=document.documentElement.getAttribute('data-theme'); document.documentElement.setAttribute('data-theme',c==='day'?'night':'day'); });
const veil=document.getElementById('veil');
document.getElementById('beginBtn').addEventListener('click',()=>{ veil.classList.add('gone'); setTimeout(()=>veil.style.display='none',1200); sceneEls[0].scrollIntoView(); });
"""

def main():
    scenes = build_assets()
    html = (
        '<title>The Twenty-Eight Nights</title>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="description" content="The Twenty-Eight Nights - an interactive bedtime story that follows the moon.">\n'
        f'<style>{CSS}</style>\n'
        '<div id="deck" aria-label="The Twenty-Eight Nights, scene by scene"></div>\n'
        '<canvas id="dust" aria-hidden="true"></canvas>\n'
        '<div class="chrome topbar"><div class="brand"><span class="cres"></span>'
        '<span class="full">The Twenty-Eight Nights</span></div>'
        '<button class="tbtn" id="theme" type="button" aria-label="Switch between night and day">Night · Day</button></div>\n'
        '<div class="chrome rail" id="rail" role="navigation" aria-label="Jump to a scene"></div>\n'
        '<div class="chrome readout" id="readout" aria-live="polite"></div>\n'
        '<div id="rotate" class="chrome"><span class="icn" aria-hidden="true"></span>Turn your device sideways to read</div>\n'
        '<div class="chrome arrows">'
        '<button class="arrow up" id="up" type="button" aria-label="Previous scene" hidden><i></i></button>'
        '<button class="arrow down" id="down" type="button" aria-label="Next scene"><i></i></button></div>\n'
        '<div id="veil"><div class="in"><div class="moon" aria-hidden="true"></div>'
        '<div class="eb">An interactive bedtime book</div><h1>The Twenty-Eight Nights</h1>'
        '<p>A story for every night the moon has.</p>'
        '<button class="begin" id="beginBtn" type="button">Begin</button>'
        '<div class="hint">Scroll, tap the arrows, or use your keyboard. Best in a dark, quiet room.</div></div></div>\n'
        f'<script>{JS.replace("__SCENES__", json.dumps(scenes))}</script>\n'
    )
    out = HERE.parent / "index.html"
    out.write_text(html)
    living = ", ".join(s["id"] for s in scenes if s.get("living"))
    print(f"Built {out} - {len(html)//1024} KB, {len(scenes)} scenes (living: {living})")

if __name__ == "__main__":
    main()
