#!/usr/bin/env python3
"""Usage: python patch_sushi.py index.html
Writes index.fixed.html next to the original. Original is never modified.
Each patch must match exactly once; otherwise it is skipped and reported."""
import sys, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
html = src.read_text(encoding="utf-8")

P = []
def patch(name, old, new):
    P.append((name, old, new))

# 1. Video modal Close button shared id="vc" with the canvas, so it never worked
patch("video modal close id",
 r'''<button class="h" id="vc">Close</button>''',
 r'''<button class="h" id="vclose">Close</button>''')
patch("video modal close handler",
 r'''$("#vc").onclick=()=>{$("#vm").classList.remove("show");$("#vo").pause()};''',
 r'''$("#vclose").onclick=()=>{$("#vm").classList.remove("show");$("#vo").pause()};
$("#vm").onclick=e=>{if(e.target.id==="vm"){$("#vm").classList.remove("show");$("#vo").pause()}};''')

# 2. Undo history grew without limit (each step stores every base64 image)
patch("history cap",
 r'''function commit(){hist=hist.slice(0,hi+1);hist.push(snap());hi=hist.length-1;btns();saveSoon()}''',
 r'''function commit(){hist=hist.slice(0,hi+1);hist.push(snap());if(hist.length>60)hist.shift();hi=hist.length-1;btns();saveSoon()}''')

# 3. Design shortcuts (Ctrl+Z / Ctrl+V / Delete) fired on other screens
patch("shortcut scope",
 r'''const ed=/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)||document.activeElement.isContentEditable,m=e.ctrlKey||e.metaKey;''',
 r'''if(/\b(?:dm|vw|hw|gw)\b/.test(document.body.className))return;
 const ed=/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)||document.activeElement.isContentEditable,m=e.ctrlKey||e.metaKey;''')

# 4. Video export could hang forever (leave view, pause, seek) and left button disabled
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

# 5. Design video export: same protection
patch("design export try/catch",
 r'''$("#ev").onclick=expVideo;''',
 r'''$("#ev").onclick=async()=>{try{await expVideo()}catch(e){RC=null;TIME=null;if(RAF)stopPlay(true);const b=$("#ev");b.disabled=false;b.textContent="Export video";draw();toast("Video export failed.")}};''')

# 6. Idle video editor redrew the canvas 60 times a second
patch("idle redraw throttle",
 r'''vDraw();vUI()}''',
 r'''if(V.playing||now-(V.idle||0)>120){V.idle=now;vDraw();vUI()}}''')

# 7. Big photos filled localStorage (quota error). Shrink to 1600px on add.
patch("photo shrink helper",
 r'''$("#file").onchange=e=>{const f=e.target.files[0];if(!f)return;''',
 r'''const shrinkSrc=(im,src,type)=>{const k=Math.min(1,1600/Math.max(im.width,im.height));if(k===1&&src.length<400000)return src;const c=document.createElement("canvas");c.width=Math.round(im.width*k);c.height=Math.round(im.height*k);c.getContext("2d").drawImage(im,0,0,c.width,c.height);return /png/.test(type)?c.toDataURL("image/png"):c.toDataURL("image/jpeg",.85)};
$("#file").onchange=e=>{const f=e.target.files[0];if(!f)return;''')
patch("photo shrink use",
 r'''im.onload=()=>{if(REPL){const o=S.els.find(x=>x.id===REPL);REPL=0;if(o){o.src=r.result;draw();commit();return}}add({t:"img",x:100,y:100,w:500,h:Math.round(500*im.height/im.width),src:r.result})};''',
 r'''im.onload=()=>{const src=shrinkSrc(im,r.result,f.type);if(REPL){const o=S.els.find(x=>x.id===REPL);REPL=0;if(o){o.src=src;draw();commit();return}}add({t:"img",x:100,y:100,w:500,h:Math.round(500*im.height/im.width),src})};''')

# 8. Blob URLs for downloads were never released
patch("revoke download urls",
 r'''a.click();a.remove();return true}''',
 r'''a.click();a.remove();setTimeout(()=>{URL.revokeObjectURL(u);BL.delete(u)},60000);return true}''')

# 9. First-run race: thumbnail callback could null the project you just opened
patch("first run race",
 r'''upThumb().then(()=>{persist();CP=null;dash()})''',
 r'''upThumb().then(()=>{persist();if(document.body.classList.contains("dm"))CP=null;dash()})''')

# 10. Canvas resize did not scale the current page (array used instead of spread)
patch("resize scaling bug",
 r'''[S.els,...(CP?CP.pages.filter((_,i)=>i!==PI).flatMap(pg=>pg.els):[])].forEach(o=>{o.x*=sx;o.y*=sy;o.w*=k;o.h*=k;if(o.t==="t"){o.size=Math.round(o.size*k);o.sw=(o.sw||0)*k}});''',
 r'''[...S.els,...(CP?CP.pages.filter((_,i)=>i!==PI).flatMap(pg=>pg.els):[])].forEach(o=>{if(o.t==="draw"){o.pts=o.pts.map(([x,y])=>[x*sx,y*sy]);o.w=w;o.h=h;o.bw2*=k;return}o.x*=sx;o.y*=sy;o.w*=k;o.h*=k;if(o.t==="t"){o.size=Math.round(o.size*k);o.sw=(o.sw||0)*k}});''')

# 11. Escape image sources (restored backups / synced data are untrusted)
patch("esc slide img", r'''<img src="${s.img}" alt="">''', r'''<img src="${esc(s.img)}" alt="">''')
patch("esc dash thumb", r'''<img src="${x.pages[0].th}" alt="">''', r'''<img src="${esc(x.pages[0].th)}" alt="">''')
patch("esc page thumb", r'''<img src="${pg.th}" alt="Page ${i+1}">''', r'''<img src="${esc(pg.th)}" alt="Page ${i+1}">''')
patch("esc canvas img", r'''<img src="${o.src}" alt="" style="filter:${imf(o)};${geo(o)}">''', r'''<img src="${esc(o.src)}" alt="" style="filter:${imf(o)};${geo(o)}">''')

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
