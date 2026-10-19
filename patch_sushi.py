"""Usage: python patch_sushi.py index.html.txt
Writes index.fixed.html next to the original. Original is never modified.
Each patch must match exactly once; otherwise it is skipped and reported."""
import sys, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html.txt")
html = src.read_text(encoding="utf-8")

P = []
def patch(name, old, new):
    P.append((name, old, new))

# ============ Part 1: general bug fixes ============
patch("video modal close id",
 r'''<button class="h" id="vc">Close</button>''',
 r'''<button class="h" id="vclose">Close</button>''')
patch("video modal close handler",
 r'''$("#vc").onclick=()=>{$("#vm").classList.remove("show");$("#vo").pause()};''',
 r'''$("#vclose").onclick=()=>{$("#vm").classList.remove("show");$("#vo").pause()};
$("#vm").onclick=e=>{if(e.target.id==="vm"){$("#vm").classList.remove("show");$("#vo").pause()}};''')
patch("history cap",
 r'''function commit(){hist=hist.slice(0,hi+1);hist.push(snap());hi=hist.length-1;btns();saveSoon()}''',
 r'''function commit(){hist=hist.slice(0,hi+1);hist.push(snap());if(hist.length>60)hist.shift();hi=hist.length-1;btns();saveSoon()}''')
patch("shortcut scope",
 r'''const ed=/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)||document.activeElement.isContentEditable,m=e.ctrlKey||e.metaKey;''',
 r'''if(/\b(?:dm|vw|hw|gw)\b/.test(document.body.className))return;
 const ed=/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)||document.activeElement.isContentEditable,m=e.ctrlKey||e.metaKey;''')
patch("leave view during export",
 r'''if(!document.body.classList.contains("vw")){V.raf=0;vStop();return}''',
 r'''if(!document.body.classList.contains("vw")){V.raf=0;vStop();if(V.end)V.end();return}''')
patch("pause during export",
 r'''function vPlay(){if(V.playing){vStop();return}''',
 r'''function vPlay(){if(V.playing){if(!V.end)vStop();return}''')
patch("seek during export",
 r'''$("#vsk").oninput=e=>{V.drag=true;if(V.playing)vStop();vSeek(+e.target.value*vTotal())};''',
 r'''$("#vsk").oninput=e=>{if(V.end)return;V.drag=true;if(V.playing)vStop();vSeek(+e.target.value*vTotal())};''')
patch("keys during export",
 r'''if(!document.body.classList.contains("vw")||KP.open)return;''',
 r'''if(!document.body.classList.contains("vw")||KP.open||V.end)return;''')
patch("video export try/catch start",
 r'''$("#vexp").onclick=async()=>{if(!V.clips.length){toast("Add a video or photo first");return}''',
 r'''async function vExportRun(){if(!V.clips.length){toast("Add a video or photo first");return}''')
patch("video export try/catch end",
 r'''$("#vdl").textContent="Download "+(mp4?"MP4":"WebM");$("#vm").classList.add("show")};''',
 r'''$("#vdl").textContent="Download "+(mp4?"MP4":"WebM");$("#vm").classList.add("show")}
$("#vexp").onclick=async()=>{try{await vExportRun()}catch(e){V.end=null;vStop();const b=$("#vexp");b.disabled=false;b.textContent="Export video";toast("Export failed. Try Chrome, or a shorter or smaller video.")}};''')
patch("design export try/catch",
 r'''$("#ev").onclick=expVideo;''',
 r'''$("#ev").onclick=async()=>{try{await expVideo()}catch(e){RC=null;TIME=null;if(RAF)stopPlay(true);const b=$("#ev");b.disabled=false;b.textContent="Export video";draw();toast("Video export failed.")}};''')
patch("idle redraw throttle",
 r'''vDraw();vUI()}''',
 r'''if(V.playing||now-(V.idle||0)>120){V.idle=now;vDraw();vUI()}}''')
patch("photo shrink helper",
 r'''$("#file").onchange=e=>{const f=e.target.files[0];if(!f)return;''',
 r'''const shrinkSrc=(im,src,type)=>{const k=Math.min(1,1600/Math.max(im.width,im.height));if(k===1&&src.length<400000)return src;const c=document.createElement("canvas");c.width=Math.round(im.width*k);c.height=Math.round(im.height*k);c.getContext("2d").drawImage(im,0,0,c.width,c.height);return /png/.test(type)?c.toDataURL("image/png"):c.toDataURL("image/jpeg",.85)};
$("#file").onchange=e=>{const f=e.target.files[0];if(!f)return;''')
patch("photo shrink use",
 r'''im.onload=()=>{if(REPL){const o=S.els.find(x=>x.id===REPL);REPL=0;if(o){o.src=r.result;draw();commit();return}}add({t:"img",x:100,y:100,w:500,h:Math.round(500*im.height/im.width),src:r.result})};''',
 r'''im.onload=()=>{const src=shrinkSrc(im,r.result,f.type);if(REPL){const o=S.els.find(x=>x.id===REPL);REPL=0;if(o){o.src=src;draw();commit();return}}add({t:"img",x:100,y:100,w:500,h:Math.round(500*im.height/im.width),src})};''')
patch("revoke download urls",
 r'''a.click();a.remove();return true}''',
 r'''a.click();a.remove();setTimeout(()=>{URL.revokeObjectURL(u);BL.delete(u)},60000);return true}''')
patch("first run race",
 r'''upThumb().then(()=>{persist();CP=null;dash()})''',
 r'''upThumb().then(()=>{persist();if(document.body.classList.contains("dm"))CP=null;dash()})''')
patch("resize scaling bug",
 r'''[S.els,...(CP?CP.pages.filter((_,i)=>i!==PI).flatMap(pg=>pg.els):[])].forEach(o=>{o.x*=sx;o.y*=sy;o.w*=k;o.h*=k;if(o.t==="t"){o.size=Math.round(o.size*k);o.sw=(o.sw||0)*k}});''',
 r'''[...S.els,...(CP?CP.pages.filter((_,i)=>i!==PI).flatMap(pg=>pg.els):[])].forEach(o=>{if(o.t==="draw"){o.pts=o.pts.map(([x,y])=>[x*sx,y*sy]);o.w=w;o.h=h;o.bw2*=k;return}o.x*=sx;o.y*=sy;o.w*=k;o.h*=k;if(o.t==="t"){o.size=Math.round(o.size*k);o.sw=(o.sw||0)*k}});''')
patch("esc slide img",   r'''<img src="${s.img}" alt="">''',  r'''<img src="${esc(s.img)}" alt="">''')
patch("esc dash thumb",  r'''<img src="${x.pages[0].th}" alt="">''', r'''<img src="${esc(x.pages[0].th)}" alt="">''')
patch("esc page thumb",  r'''<img src="${pg.th}" alt="Page ${i+1}">''', r'''<img src="${esc(pg.th)}" alt="Page ${i+1}">''')
patch("esc canvas img",  r'''<img src="${o.src}" alt="" style="filter:${imf(o)};${geo(o)}">''',
                          r'''<img src="${esc(o.src)}" alt="" style="filter:${imf(o)};${geo(o)}">''')

# ============ Part 2: ghost mannequin upgrades ============
patch("ghost: median background",
 r'''function gBgEst(){const d=GM.src.data,w=GM.w,h=GM.h,p=Math.max(4,Math.round(Math.min(w,h)*.02));let r=0,g=0,b=0,n=0;const add=(x,y)=>{const i=(y*w+x)*4;r+=d[i];g+=d[i+1];b+=d[i+2];n++};for(let y=0;y<p;y++)for(let x=0;x<w;x++){add(x,y);add(x,h-1-y)}for(let x=0;x<p;x++)for(let y=p;y<h-p;y++){add(x,y);add(w-1-x,y)}return[r/n,g/n,b/n]}''',
 r'''function gBgEst(){const d=GM.src.data,w=GM.w,h=GM.h,p=Math.max(4,Math.round(Math.min(w,h)*.02)),R=[],G=[],B=[];const add=(x,y)=>{const i=(y*w+x)*4;R.push(d[i]);G.push(d[i+1]);B.push(d[i+2])};for(let y=0;y<p;y++)for(let x=0;x<w;x++){add(x,y);add(x,h-1-y)}for(let x=0;x<p;x++)for(let y=p;y<h-p;y++){add(x,y);add(w-1-x,y)}
 const med=a=>{a.sort((x,y)=>x-y);return a[a.length>>1]};return[med(R),med(G),med(B)]}''')
patch("ghost: stroke undo snapshot",
 r'''if(tool==="neck"){GM.nx=x;GM.ny=y;gDraw();return}''',
 r'''if(tool==="neck"){GM.nx=x;GM.ny=y;gDraw();return}
 GM.prevOv=GM.ov.slice();''')
patch("ghost: undo & reset buttons (HTML)",
 r'''<label class="vl">Brush size<input type="range" id="gbr" min="6" max="160" value="40"></label>''',
 r'''<label class="vl">Brush size<input type="range" id="gbr" min="6" max="160" value="40"></label><div class="vrow"><button class="vb" id="gundo">↶ Undo brush</button><button class="vb" id="greset">Reset edits</button></div>''')
patch("ghost: undo & reset handlers",
 r'''gv("gpick").onclick=()=>{if(!GM.src){toast("Upload a photo first");return}GM.pick=true;GM.view="orig";gTabs();gv("gmsg").textContent="Click the background in the photo."};''',
 r'''gv("gpick").onclick=()=>{if(!GM.src){toast("Upload a photo first");return}GM.pick=true;GM.view="orig";gTabs();gv("gmsg").textContent="Click the background in the photo."};
gv("gundo").onclick=()=>{if(!GM.src||!GM.prevOv)return;GM.ov=GM.prevOv;GM.prevOv=null;gRun()};
gv("greset").onclick=()=>{if(!GM.src)return;GM.ov=new Uint8Array(GM.w*GM.h);GM.nx=null;GM.ny=null;GM.prevOv=null;GM.view="edit";gTabs();gRun()};''')
patch("ghost: cylinder shading",
 r'''else{const tt=(v+1)/2,m=.72-.36*tt;ir=ar*m;ig=ag*m;ib=ab*m}''',
 r'''else{const tt=(v+1)/2,cyl=Math.max(.6,1-.4*u*u),m=(.72-.36*tt)*cyl;ir=ar*m;ig=ag*m;ib=ab*m}''')
patch("ghost: softer inner-neck fade",
 r'''if(q<1.2){const f=Math.min(1,Math.max(0,(1-Math.sqrt(q))/.1));if(f>0){''',
 r'''if(q<1.4){const f=Math.min(1,Math.max(0,(1-Math.sqrt(q))/.15));if(f>0){''')
patch("ghost: auto neck from mask top",
 r'''const nk=gv("gneck").checked,cx=GM.nx??(x0+bw/2),cy=GM.ny??(y0+bh*.07),''',
 r'''const nk=gv("gneck").checked;let topCx=(x0+x1)/2;if(!GM.nx){let topY=-1,topL=0,topR=0;for(let yy=y0;yy<=y1&&topY<0;yy++){for(let xx=x0;xx<=x1;xx++)if(M[yy*w+xx]>.5){if(topY<0){topY=yy;topL=xx;topR=xx}else if(xx>topR)topR=xx}}if(topY>=0)topCx=(topL+topR)/2}
 const cx=GM.nx??topCx,cy=GM.ny??(y0+bh*.07),''')
patch("ghost: clamp edge softness",
 r'''const sr=Math.round(+gv("gsoft").value*w/1000*1.5);''',
 r'''const sr=Math.max(0,Math.min(Math.round(+gv("gsoft").value*w/1000*1.5),Math.round(Math.min(w,h)/15)));''')

# ============ Apply ============
ok = fail = 0
for name, old, new in P:
    n = html.count(old)
    if n == 1:
        html = html.replace(old, new)
        ok += 1
        print("OK    ", name)
    else:
        fail += 1
        print("SKIP  ", name, f"(found {n} matches, expected 1)")

out = src.with_name("index.fixed.html")
out.write_text(html, encoding="utf-8")
print(f"\n{ok} applied, {fail} skipped -> {out}")
