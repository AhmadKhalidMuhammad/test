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
      if (L.motion==='butterfly' && L.parts){
        // three cut pieces: right wing, left wing (both flap in 3D), and a static body
        L.parts.forEach(pt=>{
          const cls = pt.id==='body' ? 'part body' : 'part wing '+pt.id;
          const p = el('div', cls,
            `left:${pt.x}%;top:${pt.y}%;width:${pt.w}%;height:${pt.h}%;`+
            (pt.id!=='body' ? `transform-origin:${pt.pivot}% 50%;` : ''));
          const im=el('img'); im.src=pt.src; im.alt=''; p.appendChild(im); anim.appendChild(p);
        });
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
  }
  // overlay effects (work on flat scenes too): flames, breathing glows, falling-light streams
  (s.flames||[]).forEach(f=>{
    stage.appendChild(el('div','flame',
      `left:${f.x}%;top:${f.y}%;width:${f.r*2}%;height:${f.r*3.2}%;background:radial-gradient(circle at 50% 60%, #fff3cf, ${f.color} 45%, transparent 72%)`));
  });
  (s.glows||[]).forEach(g=>{
    stage.appendChild(el('div','glowspot',
      `left:${g.x}%;top:${g.y}%;width:${g.r}%;aspect-ratio:1;background:radial-gradient(circle, ${g.color}, ${g.color}55 45%, transparent 70%)`));
  });
  if (s.twinkle){ const c=el('canvas','twk'); stage.appendChild(c); }
  if (s.streams && s.streams.length){ const rc=el('canvas','rainc'); rc._streams=s.streams; stage.appendChild(rc); }

  // live text (re-typeset from content, never baked into the art)
  if (s.content && s.textbox){
    const tb=s.textbox, c=s.content;
    const tl=el('div','textlayer',`left:${tb.x}%;top:${tb.y}%;width:${tb.w}%;height:${tb.h}%`);
    if (c.eyebrow) tl.appendChild(el('div','tl-eyebrow')).textContent=c.eyebrow;
    if (c.title){ const h=el('div','tl-title'); h.textContent=c.title; tl.appendChild(h); }
    const body=el('div','tl-body');
    (c.body||[]).forEach(par=>{ const p=el('p'); p.textContent=par; body.appendChild(p); });
    tl.appendChild(body);
    if (c.coda){ const cd=el('div','tl-coda'); cd.textContent=c.coda; tl.appendChild(cd); }
    stage.appendChild(tl);
  }

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

/* ---- the morphing moon (shared across the Week One -> Week Two page turn) ---- */
const morphEl=el('div'); morphEl.id='morphmoon'; const morphImgs={};
SCENES.forEach((s,i)=>{ if(s.moonMorph){ const im=el('img'); im.src=s.moonMorph.src; im.alt=''; morphEl.appendChild(im); morphImgs[i]=im; }});
document.body.appendChild(morphEl);
let prevMorph=false, morphCur=-1;
function restRect(A){ const vw=innerWidth, vh=innerHeight; const maxW=Math.min(0.96*vw,1480), maxH=0.86*vh;
  const w=Math.min(maxW, maxH*A); return {left:(vw-w)/2, top:(vh-w/A)/2, w, h:w/A}; }
function positionMorph(i, animate){
  const mm=SCENES[i].moonMorph, rr=restRect(SCENES[i].aspect);
  if(!animate) morphEl.classList.add('nofade');
  morphEl.style.left=(rr.left+mm.x/100*rr.w)+'px';
  morphEl.style.top=(rr.top+mm.y/100*rr.h)+'px';
  morphEl.style.width=(mm.w/100*rr.w)+'px';
  if(!animate){ morphEl.getBoundingClientRect(); morphEl.classList.remove('nofade'); }
  for(const k in morphImgs) morphImgs[k].classList.toggle('on', +k===i);
}

/* ---- twinkle canvases (per scene sky) ---- */
document.querySelectorAll('.twk').forEach(c=>{
  const st=c.parentElement;
  function size(){ c.width=Math.max(1,st.clientWidth); c.height=Math.max(1,st.clientHeight); }
  size(); new ResizeObserver(size).observe(st);
  const N=reduce?10:16;
  c._stars=Array.from({length:N},()=>({x:Math.random(),y:Math.random()*0.60,r:Math.random()*1.4+0.4,p:Math.random()*6.28,s:0.5+Math.random()}));
});
/* ---- stream canvases: falling motes of light in % regions of the stage
       (e.g. Week Four's mother pouring light down into her child's hands) ---- */
document.querySelectorAll('.rainc').forEach(c=>{
  const st=c.parentElement;
  function size(){ c.width=Math.max(1,st.clientWidth); c.height=Math.max(1,st.clientHeight); }
  size(); new ResizeObserver(size).observe(st);
  c._drops=[];
  c._streams.forEach(rg=>{ const n=reduce?0:Math.round(rg.w*4);
    for(let k=0;k<n;k++) c._drops.push({rg, x:Math.random(), y:Math.random(), r:0.8+Math.random()*1.6, sp:0.004+Math.random()*0.006, ph:Math.random()*6.28}); });
});

/* ---- active scene ---- */
let current=0;
function setActive(i){
  current=i;
  sceneEls.forEach((e,k)=>e.classList.toggle('active',k===i));
  dots.forEach((d,k)=>d.setAttribute('aria-current',k===i?'true':'false'));
  const s=SCENES[i];
  if(s.eyebrow && !s.content){ readout.innerHTML='<span class="eb">'+s.eyebrow+'</span>'; readout.classList.add('show'); }
  else readout.classList.remove('show');
  const cue=document.getElementById('cue'); if(cue) cue.style.opacity=i===0?'':'0';
  document.getElementById('up').hidden=i===0;
  document.getElementById('down').hidden=(i===0)||(i===sceneEls.length-1);
  if(s.moonMorph){ positionMorph(i, prevMorph); morphEl.style.opacity=1; prevMorph=true; morphCur=i; }
  else { morphEl.style.opacity=0; prevMorph=false; morphCur=-1; }
  setStageUnit(i);
}
// --u = 1% of the stage's rendered width, so live text scales with the art
function setStageUnit(i){
  const st=sceneEls[i].querySelector('.stage'); if(!st) return;
  const rr=restRect(SCENES[i].aspect||2.588);
  st.style.setProperty('--u', (rr.w/100)+'px');
}
addEventListener('resize',()=>{ if(morphCur>=0) positionMorph(morphCur,false); if(current>=0) setStageUnit(current); });
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
    if(rc&&rc._drops&&rc.width>1){ const rx=rc.getContext('2d'); rx.clearRect(0,0,rc.width,rc.height);
      for(const d of rc._drops){ const rg=d.rg; d.y+=d.sp; if(d.y>1){d.y=0;d.x=0.5+(Math.random()-0.5)*0.5;}
        // taper the column: wider at the top (the pouring hand), narrowing as it falls
        const spread=rg.w*(0.25+0.75*d.y), cxp=rg.x+rg.w*0.5;
        const X=(cxp+(d.x-0.5)*spread)/100*rc.width, Y=(rg.y+d.y*rg.h)/100*rc.height;
        const tw=0.35+0.65*Math.abs(Math.sin(t*0.004*d.sp*160+d.ph));  // sparkle
        rx.fillStyle=rg.color; rx.globalAlpha=reduce?0:0.85*tw*(1-0.15*d.y);
        rx.beginPath(); rx.arc(X,Y,d.r*devicePixelRatio*0.8,0,7); rx.fill(); }
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
