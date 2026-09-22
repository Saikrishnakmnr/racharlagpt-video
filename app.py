import os
import re
import io
import math
import wave
import base64
import random
import shutil
import tempfile
import subprocess
from pathlib import Path

import streamlit as st
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps, ImageFont

APP_NAME = "RacharlaGPT AI Movie Studio"
ROOT = Path(__file__).parent
WORK = ROOT / "workspace"
WORK.mkdir(exist_ok=True)
FFMPEG = os.getenv("FFMPEG_BIN", "ffmpeg")

st.set_page_config(page_title=APP_NAME, page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------------------------------------------------------
# Premium visual system
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--bg:#05050d;--panel:rgba(18,19,42,.72);--panel2:rgba(255,255,255,.045);--line:rgba(255,255,255,.12);--gold:#ffd34d;--pink:#ff55c8;--cyan:#57e8ff;--purple:#a88bff;--green:#67f5ad;--text:#f8f8ff;--muted:#a9abc2}
html,body,[class*="css"]{font-family:Inter,system-ui,sans-serif}
.stApp{background:radial-gradient(circle at 8% 6%,rgba(255,211,77,.11),transparent 24%),radial-gradient(circle at 92% 8%,rgba(255,85,200,.11),transparent 25%),radial-gradient(circle at 50% 100%,rgba(87,232,255,.08),transparent 30%),linear-gradient(135deg,#05050d,#0b0b1d 45%,#070711);color:var(--text)}
.block-container{max-width:1260px;padding-top:1rem;padding-bottom:4rem}
header[data-testid="stHeader"]{background:transparent;height:0}
.hero{padding:34px 30px 30px;border:1px solid var(--line);border-radius:32px;background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(255,255,255,.025));box-shadow:0 24px 80px rgba(0,0,0,.36),inset 0 1px rgba(255,255,255,.08);position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;inset:-50%;background:conic-gradient(from 0deg,transparent,rgba(255,211,77,.08),transparent,rgba(255,85,200,.07),transparent);animation:spin 18s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.brand{position:relative;z-index:2;font-family:"Space Grotesk";font-size:1.05rem;font-weight:900;letter-spacing:.02em}.brand b{color:var(--gold)}
.hero h1{position:relative;z-index:2;font-family:"Space Grotesk";font-size:clamp(2.25rem,6vw,5.1rem);line-height:.96;letter-spacing:-.055em;margin:.55rem 0 1rem}.gradient{background:linear-gradient(90deg,#fff,var(--gold),#fff,var(--pink),var(--cyan));background-size:260% auto;-webkit-background-clip:text;background-clip:text;color:transparent;animation:flow 7s ease-in-out infinite}@keyframes flow{0%,100%{background-position:0%}50%{background-position:100%}}
.hero p{position:relative;z-index:2;color:var(--muted);max-width:900px;font-size:1.03rem;line-height:1.65}.pills{position:relative;z-index:2;display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}.pill{border:1px solid var(--line);background:rgba(255,255,255,.055);padding:7px 11px;border-radius:999px;font-size:.78rem;color:#ddd}
.card{border:1px solid var(--line);border-radius:24px;background:var(--panel);box-shadow:0 18px 55px rgba(0,0,0,.22),inset 0 1px rgba(255,255,255,.05);padding:20px}.section-title{font-family:"Space Grotesk";font-weight:900;font-size:1.3rem;margin-bottom:4px}.section-sub{color:var(--muted);font-size:.88rem;line-height:1.55;margin-bottom:16px}
div[data-testid="stTextArea"] textarea,div[data-testid="stTextInput"] input{background:rgba(4,5,14,.78)!important;border:1px solid rgba(255,255,255,.13)!important;color:#fff!important;border-radius:16px!important}
div[data-testid="stButton"]>button{border-radius:14px;border:1px solid rgba(255,255,255,.12);background:linear-gradient(135deg,rgba(255,255,255,.09),rgba(255,255,255,.035));color:#fff;font-weight:800;min-height:44px;transition:.18s ease}div[data-testid="stButton"]>button:hover{transform:translateY(-2px);border-color:rgba(255,211,77,.55);box-shadow:0 10px 30px rgba(255,211,77,.12)}
.create-btn button{background:linear-gradient(100deg,#ffd34d,#ff9d4d,#ff55c8)!important;color:#16120a!important;border:0!important;font-size:1.03rem!important;min-height:60px!important;box-shadow:0 0 35px rgba(255,179,69,.28)}
div[data-testid="stFileUploader"]{background:rgba(255,255,255,.025);border:1px dashed rgba(255,211,77,.32);border-radius:18px;padding:8px}
.scene{border:1px solid rgba(255,255,255,.10);border-radius:18px;padding:12px;background:rgba(255,255,255,.035);margin-bottom:10px}.scene-num{color:var(--gold);font-weight:900;font-size:.75rem}.scene-title{font-weight:900;margin:.2rem 0}.scene-meta{color:var(--muted);font-size:.78rem}
.status{padding:12px 14px;border-radius:14px;background:rgba(255,211,77,.06);border:1px solid rgba(255,211,77,.18);color:#ffe9a4}.ok{background:rgba(103,245,173,.06);border-color:rgba(103,245,173,.18);color:#cffff0}.warn{background:rgba(255,85,200,.06);border-color:rgba(255,85,200,.18);color:#ffd2f2}
.feature-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.feature-card{border:1px solid var(--line);border-radius:22px;padding:20px;background:linear-gradient(145deg,rgba(255,255,255,.065),rgba(255,255,255,.025));transition:.2s ease;min-height:160px}.feature-card:hover{transform:translateY(-6px) scale(1.01);border-color:rgba(255,211,77,.55);box-shadow:0 18px 40px rgba(0,0,0,.3),0 0 30px rgba(255,211,77,.08)}.feature-icon{font-size:2rem}.feature-card h3{margin:.6rem 0 .3rem;font-family:"Space Grotesk"}.feature-card p{color:var(--muted);font-size:.84rem;line-height:1.5;margin:0}.link-card{display:block;text-decoration:none;color:inherit}.link-card:hover{text-decoration:none;color:inherit}
.carousel{border:1px solid rgba(255,211,77,.24);border-radius:26px;padding:22px;background:linear-gradient(120deg,rgba(255,211,77,.07),rgba(255,85,200,.05),rgba(87,232,255,.05));box-shadow:0 20px 60px rgba(0,0,0,.2)}
.adbox{min-height:90px;border:1px dashed rgba(255,255,255,.10);border-radius:16px;display:flex;align-items:center;justify-content:center;color:#70738c;font-size:.72rem}.ad-label{font-size:.66rem;letter-spacing:.12em;text-transform:uppercase;color:#777b98;margin-bottom:7px;text-align:center}
.footer{color:#777b98;font-size:.76rem;text-align:center;padding:25px;line-height:1.7}.small{font-size:.78rem;color:var(--muted)}
@media(max-width:850px){.feature-grid{grid-template-columns:1fr}.hero{padding:25px 18px}.card{padding:16px}}
</style>
""", unsafe_allow_html=True)

# Short-lived flower/music/sparkle shower; reduced-motion friendly.
st.components.v1.html("""
<script>
(function(){
 const doc=window.parent.document;
 if(doc.getElementById('rgpt-shower')) return;
 const wrap=doc.createElement('div'); wrap.id='rgpt-shower'; Object.assign(wrap.style,{position:'fixed',inset:'0',pointerEvents:'none',zIndex:'999999',overflow:'hidden'}); doc.body.appendChild(wrap);
 const glyphs=['🌸','🎵','🎶','✨','💫','⭐','🎬','🎧'];
 function burst(){const n=5+Math.floor(Math.random()*6);for(let i=0;i<n;i++){const e=doc.createElement('span');e.textContent=glyphs[Math.floor(Math.random()*glyphs.length)];Object.assign(e.style,{position:'absolute',left:(4+Math.random()*92)+'vw',top:'-42px',fontSize:(18+Math.random()*22)+'px',filter:'drop-shadow(0 0 10px rgba(255,211,77,.9))',opacity:'0',transition:'transform 2.8s cubic-bezier(.15,.7,.25,1),opacity .35s'});wrap.appendChild(e);requestAnimationFrame(()=>{e.style.opacity='1';e.style.transform='translateY('+(65+Math.random()*45)+'vh) rotate('+(Math.random()*360-180)+'deg)';});setTimeout(()=>e.style.opacity='0',1900);setTimeout(()=>e.remove(),2900)}}
 setTimeout(burst,700); setInterval(burst,12000);
})();
</script>
""", height=0)

ASPECTS={"9:16 — Vertical":(9,16,1080,1920),"16:9 — Landscape":(16,9,1920,1080),"1:1 — Square":(1,1,1080,1080),"4:5 — Portrait":(4,5,1080,1350),"Custom":(16,9,1920,1080)}


def safe_font(size=42,bold=False):
    candidates=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    for p in candidates:
        if os.path.exists(p): return ImageFont.truetype(p,size)
    return ImageFont.load_default()


def fit_image(im,size,mode="Auto Fit",x=0,y=0,rotation=0):
    im=im.convert("RGB"); W,H=size
    if rotation: im=im.rotate(rotation,expand=True,resample=Image.Resampling.BICUBIC)
    if mode=="Stretch": return im.resize(size,Image.Resampling.LANCZOS)
    if mode=="Fill / Crop": return ImageOps.fit(im,size,method=Image.Resampling.LANCZOS,centering=(.5+x*.5,.5+y*.5))
    scale=min(W/im.width,H/im.height) if mode=="Auto Fit" else max(W/im.width,H/im.height)
    nw,nh=max(1,int(im.width*scale)),max(1,int(im.height*scale)); fg=im.resize((nw,nh),Image.Resampling.LANCZOS)
    bg=ImageOps.fit(im,(W,H),method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(28)); bg=ImageEnhance.Brightness(bg).enhance(.48)
    out=bg.copy(); ox=(W-nw)//2+int(x*W*.18); oy=(H-nh)//2+int(y*H*.18); out.paste(fg,(ox,oy)); return out


def text_wrap(draw,text,font,max_width):
    words=text.split(); lines=[]; cur=""
    for w in words:
        test=(cur+" "+w).strip()
        if draw.textbbox((0,0),test,font=font)[2]<=max_width: cur=test
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines


def make_local_cinematic(prompt,size,idx=1,style="Cinematic"):
    W,H=size; seed=sum(ord(c) for c in prompt)+idx*97; rng=random.Random(seed); base=Image.new("RGB",size,(8,9,20)); px=base.load(); c1=(rng.randint(35,90),rng.randint(15,55),rng.randint(50,120)); c2=(rng.randint(120,230),rng.randint(65,160),rng.randint(30,100))
    for yy in range(H):
        t=yy/max(1,H-1); col=tuple(int(c1[k]*(1-t)+c2[k]*t) for k in range(3))
        for xx in range(W): px[xx,yy]=col
    glow=Image.new("RGBA",size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
    for _ in range(7):
        x=rng.randint(0,W); y=rng.randint(0,H); r=rng.randint(max(2,min(W,H)//10),max(3,min(W,H)//3)); col=rng.choice([(255,211,77,80),(255,85,200,65),(87,232,255,60),(168,139,255,55)]); gd.ellipse((x-r,y-r,x+r,y+r),fill=col)
    base=Image.alpha_composite(base.convert("RGBA"),glow.filter(ImageFilter.GaussianBlur(max(12,min(W,H)//18)))); d=ImageDraw.Draw(base); horizon=int(H*.64); d.rectangle((0,horizon,W,H),fill=(3,4,10,180))
    for _ in range(4):
        x=rng.randint(0,W); w=rng.randint(max(2,W//10),max(3,W//3)); h=rng.randint(max(2,H//12),max(3,H//4)); d.polygon([(x,horizon),(x+w//2,horizon-h),(x+w,horizon)],fill=(5,6,14,220))
    f1=safe_font(max(22,int(min(W,H)*.035)),True); f2=safe_font(max(16,int(min(W,H)*.018)),False); lines=text_wrap(d,prompt.strip()[:110],f1,int(W*.82)); y=int(H*.12)
    for line in lines[:3]: d.text((W*.09,y),line,font=f1,fill=(255,255,255,245),stroke_width=2,stroke_fill=(0,0,0,100)); y+=int(f1.size*1.18)
    d.text((W*.09,H*.86),f"SCENE {idx:02d}  •  {style.upper()}",font=f2,fill=(255,211,77,235)); return base.convert("RGB")


def ffmpeg_ok():
    try: return subprocess.run([FFMPEG,"-version"],capture_output=True,text=True,timeout=8).returncode==0
    except Exception: return False


def make_music(path,seconds,bpm=96):
    sr=44100;n=max(1,int(sr*seconds));t=np.arange(n)/sr;beat=60/bpm;y=np.zeros(n,dtype=np.float32);notes=[261.63,329.63,392.0,523.25,392.0,329.63,293.66,440.0]
    for i,f in enumerate(notes):
        start=int(i*beat*sr/2);end=min(n,start+int(beat*sr*.9));tt=np.arange(max(0,end-start))/sr;env=np.exp(-3*tt/max(.01,beat));y[start:end]+=0.14*np.sin(2*np.pi*f*tt)*env+0.045*np.sin(2*np.pi*(f/2)*tt)*env
    for b in range(int(seconds/beat)+1):
        s=int(b*beat*sr);e=min(n,s+int(.12*sr))
        if e>s:
            tt=np.arange(e-s)/sr;y[s:e]+=0.12*np.sin(2*np.pi*70*tt)*np.exp(-28*tt)
    with wave.open(str(path),"wb") as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(y,-.9,.9)*32767).astype(np.int16).tobytes())


def write_srt(scenes,path):
    t=0;rows=[]
    for i,s in enumerate(scenes,1):
        dur=float(s["duration"]);a=t;b=t+dur
        def ts(x):
            h=int(x//3600);m=int((x%3600)//60);sec=int(x%60);ms=int((x-int(x))*1000);return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
        rows.append(f"{i}\n{ts(a)} --> {ts(b)}\n{(s.get('dialogue') or s.get('description') or '')[:180]}\n\n");t=b
    path.write_text("".join(rows),encoding="utf-8")


def render_movie(scene_files,durations,out_mp4,music_path=None,srt_path=None,output_size=(1080,1920)):
    if not ffmpeg_ok(): raise RuntimeError("FFmpeg was not found. Install FFmpeg and restart the app.")
    tmp=Path(tempfile.mkdtemp(prefix="rgpt_movie_",dir=WORK));clips=[]
    try:
        W,H=output_size
        for i,(img,dur) in enumerate(zip(scene_files,durations)):
            clip=tmp/f"clip_{i:03d}.mp4";frames=max(1,int(dur*30));vf=(f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,zoompan=z='min(zoom+0.0007,1.10)':d={frames}:s={W}x{H}:fps=30,format=yuv420p")
            q=subprocess.run([FFMPEG,"-y","-loop","1","-i",str(img),"-t",str(dur),"-vf",vf,"-r","30","-an",str(clip)],capture_output=True,text=True)
            if q.returncode!=0: raise RuntimeError(q.stderr[-1800:])
            clips.append(clip)
        concat=tmp/"concat.txt";concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips),encoding="utf-8");silent=tmp/"silent.mp4";q=subprocess.run([FFMPEG,"-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)],capture_output=True,text=True)
        if q.returncode!=0: raise RuntimeError(q.stderr[-1800:])
        current=silent;captioned=tmp/"captioned.mp4"
        if srt_path and srt_path.exists():
            sub=str(srt_path).replace("\\","/").replace(":","\\:").replace("'","\\'");q=subprocess.run([FFMPEG,"-y","-i",str(current),"-vf",f"subtitles='{sub}'","-c:v","libx264","-preset","veryfast","-crf","20","-an",str(captioned)],capture_output=True,text=True)
            if q.returncode==0: current=captioned
        if music_path:
            q=subprocess.run([FFMPEG,"-y","-i",str(current),"-stream_loop","-1","-i",str(music_path),"-filter_complex","[1:a]volume=0.42[a1]","-map","0:v:0","-map","[a1]","-shortest","-c:v","libx264","-preset","veryfast","-crf","20","-c:a","aac","-b:a","192k",str(out_mp4)],capture_output=True,text=True)
        else:
            q=subprocess.run([FFMPEG,"-y","-i",str(current),"-c:v","libx264","-preset","veryfast","-crf","20","-an",str(out_mp4)],capture_output=True,text=True)
        if q.returncode!=0: raise RuntimeError(q.stderr[-2200:])
    finally: shutil.rmtree(tmp,ignore_errors=True)


def plan_scenes(script,count=6):
    text=re.sub(r"\s+"," ",script.strip())
    if not text:return []
    parts=[p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+",text) if p.strip()]
    if len(parts)<=count:chunks=parts
    else:
        step=math.ceil(len(parts)/count);chunks=[" ".join(parts[i:i+step]) for i in range(0,len(parts),step)]
    styles=["Cinematic","Dreamy","Golden Hour","Neon Night","Epic","Intimate"];scenes=[]
    for i,c in enumerate(chunks[:count]):scenes.append({"id":i+1,"title":f"Scene {i+1}","description":c,"dialogue":c if len(c)<260 else c[:257]+"...","duration":max(3.0,min(9.0,3.2+len(c)/90)),"style":styles[i%len(styles)]})
    return scenes

# -----------------------------------------------------------------------------
# Gemini image engine — REST API, no secret in source code.
# -----------------------------------------------------------------------------
def gemini_key(): return os.getenv("GEMINI_API_KEY","").strip()
def gemini_model(): return os.getenv("GEMINI_IMAGE_MODEL","gemini-3.1-flash-image").strip()

def _gemini_part_from_bytes(data,mime): return {"inline_data":{"mime_type":mime,"data":base64.b64encode(data).decode("ascii")}}

def gemini_generate(prompt,out_path,reference_files=None):
    key=gemini_key()
    if not key:return False,"GEMINI_API_KEY is not configured."
    parts=[{"text":prompt}]
    for p in (reference_files or [])[:6]:
        raw=Path(p).read_bytes();mime="image/png" if str(p).lower().endswith(".png") else "image/jpeg";parts.append(_gemini_part_from_bytes(raw,mime))
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model()}:generateContent"
    payload={"contents":[{"role":"user","parts":parts}],"generationConfig":{"responseModalities":["IMAGE"]}}
    r=requests.post(url,params={"key":key},json=payload,timeout=240);r.raise_for_status();data=r.json()
    for cand in data.get("candidates",[]):
        for part in cand.get("content",{}).get("parts",[]):
            blob=part.get("inlineData") or part.get("inline_data")
            if blob and blob.get("data"):
                out_path.write_bytes(base64.b64decode(blob["data"]));return True,"Gemini image generated."
    return False,"Gemini returned no image data."

# -----------------------------------------------------------------------------
# Optional monetization injection. The exact legacy snippets are retained as
# configuration, but disabled unless the deployment explicitly enables them.
# This prevents accidental ad loading during development/testing.
# -----------------------------------------------------------------------------
MONETAG_SNIPPETS={
 "service_worker":"self.options = {\\n    \\\"domain\\\": \\\"5gvci.com\\\",\\n    \\\"zoneId\\\": 11852352\\n}\\nself.lary = \\\"\\\"\\nimportScripts('https://5gvci.com/act/files/service-worker.min.js?r=sw')",
 "banner":"<script>(function(s){s.dataset.zone='11852425',s.src='https://nap5k.com/tag.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>",
 "vignette":"<script>(function(s){s.dataset.zone='11852426',s.src='https://n6wxm.com/vignette.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>",
 "legacy_direct":"<script src=\"https://quge5.com/88/tag.min.js\" data-zone=\"284180\" async data-cfasync=\"false\"></script>",
}

def render_adsense_placeholder():
    if os.getenv("ADSENSE_ENABLED","0")!="1":
        st.markdown('<div class="adbox">Ad space reserved · enable ADSENSE_ENABLED=1 after your deployment/policy review</div>',unsafe_allow_html=True);return
    client=os.getenv("ADSENSE_PUBLISHER","pub-1188239058737040")
    st.markdown(f'''<div><div class="ad-label">Advertisement</div><div class="adbox"><ins class="adsbygoogle" style="display:block;width:100%;min-height:90px" data-ad-client="ca-{client}" data-ad-format="auto" data-full-width-responsive="true"></ins></div></div>''',unsafe_allow_html=True)
    st.components.v1.html(f'''<script>(window.adsbygoogle=window.adsbygoogle||[]).push({{}});</script>''',height=0)

def render_monetag_optional():
    if os.getenv("MONETAG_ENABLED","0")!="1": return
    # Load the non-service-worker tag in an isolated web component. Service-worker
    # registration must be deployed at the site's root by the hosting platform.
    html=MONETAG_SNIPPETS["banner"]+MONETAG_SNIPPETS["vignette"]
    st.components.v1.html(html,height=0)

# -----------------------------------------------------------------------------
# State
# -----------------------------------------------------------------------------
for k,v in {"scenes":[],"movie_bytes":None,"movie_name":"racharlagpt_cinematic_movie.mp4","gemini_result":None,"gemini_history":[]}.items():
    if k not in st.session_state: st.session_state[k]=v

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('''<div class="hero"><div class="brand">🎬 <b>RacharlaGPT</b> AI MOVIE STUDIO</div><h1>Turn ideas into <span class="gradient">cinematic stories.</span></h1><p>Create movies, AI images and posters from prompts, scripts and photos. Build scenes, characters, motion, music and captions, then render a real MP4 with Python + FFmpeg.</p><div class="pills"><span class="pill">🎭 Characters</span><span class="pill">🖼️ Gemini AI Images</span><span class="pill">🎞️ Storyboard</span><span class="pill">🎵 Music</span><span class="pill">📝 Captions</span><span class="pill">📱 9:16 / 16:9 / 1:1 / 4:5</span><span class="pill">⚡ Real FFmpeg MP4</span></div></div>''',unsafe_allow_html=True)
st.write("")

# -----------------------------------------------------------------------------
# Product carousel / feature discovery
# -----------------------------------------------------------------------------
if "carousel_idx" not in st.session_state: st.session_state.carousel_idx=0
carousel=[
 ("🎬","Idea → Movie","Give the Studio an idea or story and build an editable cinematic storyboard."),
 ("🖼️","Gemini AI Image Studio","Create images, transform photos, make posters and continue editing with prompts."),
 ("👤","Character Creator","Use reference photos for characters and reuse them across movie scenes."),
 ("🎵","Music + Motion","Combine photos, camera movement, background music and captions into an MP4."),
 ("💻","Free RacharlaGPT Tools","Programming, coding, debugging and ATS resume tools are available at RacharlaGPT.in."),
 ("🎮","Free RacharlaGPT Games","Dice, Spin, Memory, Ludo and Trivia are available at Spin.RacharlaGPT.in."),
]
i=st.session_state.carousel_idx%len(carousel);icon,title,desc=carousel[i]
st.markdown(f'''<div class="carousel"><div class="small">WHY RACHARLAGPT AI MOVIE STUDIO</div><div style="font-size:2.2rem;margin:.25rem 0">{icon}</div><h2 style="font-family:Space Grotesk;margin:.1rem 0">{title}</h2><p style="color:var(--muted);max-width:780px">{desc}</p></div>''',unsafe_allow_html=True)
ca,cb,cc=st.columns([1,2,1])
with ca:
    if st.button("← Previous",use_container_width=True): st.session_state.carousel_idx=(i-1)%len(carousel);st.rerun()
with cb: st.markdown(f"<div style='text-align:center;color:#8f93ad;padding:10px'>Feature {i+1} / {len(carousel)} · RacharlaGPT</div>",unsafe_allow_html=True)
with cc:
    if st.button("Next →",use_container_width=True): st.session_state.carousel_idx=(i+1)%len(carousel);st.rerun()

# -----------------------------------------------------------------------------
# Gemini AI Image Studio
# -----------------------------------------------------------------------------
st.write("")
st.markdown('<div class="card"><div class="section-title">🖼️ Gemini AI Image Studio</div><div class="section-sub">Text → image, photo → transformation, cinematic posters and iterative edits. Your Gemini API key stays in the deployment environment, never in GitHub.</div>',unsafe_allow_html=True)
imgtab,postertab,edittab=st.tabs(["✨ Create Image","🎬 Poster Maker","🔄 Continue Editing"])
with imgtab:
    a,b=st.columns([1.15,.85],gap="large")
    with a:
        gp=st.text_area("Gemini image prompt",height=150,placeholder="A cinematic movie hero walking through a neon city in the rain, dramatic rim light, premium poster photography, no text",key="gemini_prompt")
        gr=st.file_uploader("Optional reference photo(s)",type=["png","jpg","jpeg","webp"],accept_multiple_files=True,key="gemini_refs")
    with b:
        st.markdown("**Generation modes**")
        st.write("• Text → image\n\n• Photo + prompt → transformation\n\n• Reference images → visual direction")
        st.caption(f"Configured model: {gemini_model()}")
    if st.button("✨ Generate beautiful AI image",use_container_width=True,key="gemini_generate"):
        if not gp.strip(): st.warning("Enter a prompt first.")
        elif not gemini_key(): st.info("Add GEMINI_API_KEY to the deployment environment to enable Gemini. The local movie pipeline remains available without it.")
        else:
            with st.spinner("Gemini is creating the image…"):
                work=Path(tempfile.mkdtemp(prefix="rgpt_gemini_",dir=WORK));out=work/"gemini.png";refs=[]
                try:
                    for n,r in enumerate(gr or []):
                        p=work/f"ref_{n}.{'png' if r.type=='image/png' else 'jpg'}";p.write_bytes(r.read());refs.append(p)
                    ok,msg=gemini_generate(gp,out,refs)
                    if ok:
                        data=out.read_bytes();st.session_state.gemini_result=data;st.session_state.gemini_history.append((gp,data));st.success(msg);st.image(data,use_container_width=True);st.download_button("⬇️ Download AI image",data,"racharlagpt_ai_image.png","image/png",use_container_width=True)
                    else: st.error(msg)
                except Exception as e: st.error(f"Gemini request failed: {e}")
                finally: shutil.rmtree(work,ignore_errors=True)
with postertab:
    a,b=st.columns([1,.95],gap="large")
    with a:
        pp=st.text_input("Poster title",placeholder="THE LAST DOOR",key="poster_title");tag=st.text_input("Tagline",placeholder="Every ending opens another story.",key="poster_tag")
        ps=st.selectbox("Poster style",["Cinematic","Action","Romance","Fantasy","Thriller","Luxury","Comic","Anime-inspired"],key="poster_style")
        pf=st.selectbox("Poster format",list(ASPECTS.keys()),index=0,key="poster_format")
    with b:
        pr=st.file_uploader("Character / photo reference",type=["png","jpg","jpeg","webp"],key="poster_ref")
        st.caption("Gemini can generate the visual; title/tagline are included in the generation prompt. For critical typography, review the result before publishing.")
    if st.button("🎬 Generate movie poster",use_container_width=True,key="poster_generate"):
        if not gemini_key(): st.info("Add GEMINI_API_KEY to enable poster generation.")
        else:
            _,_,pw,ph=ASPECTS[pf];ratio=f"{pw}:{ph}";prompt=f"Create a premium {ps.lower()} movie poster. Title: {pp or 'Untitled Film'}. Tagline: {tag or 'A new cinematic story.'}. Aspect ratio {ratio}. Strong cinematic composition, professional lighting, expressive characters, polished poster design, high detail. Render the title and tagline clearly as part of the poster artwork."
            work=Path(tempfile.mkdtemp(prefix="rgpt_poster_",dir=WORK));out=work/"poster.png"
            try:
                refs=[]
                if pr:
                    rp=work/"ref.jpg";rp.write_bytes(pr.read());refs=[rp]
                with st.spinner("Creating poster…"):
                    ok,msg=gemini_generate(prompt,out,refs)
                if ok:
                    data=out.read_bytes();st.image(data,use_container_width=True);st.download_button("⬇️ Download poster",data,"racharlagpt_poster.png","image/png",use_container_width=True)
                else: st.error(msg)
            except Exception as e: st.error(f"Poster generation failed: {e}")
            finally: shutil.rmtree(work,ignore_errors=True)
with edittab:
    if st.session_state.gemini_result:
        st.image(st.session_state.gemini_result,use_container_width=True)
        ep=st.text_input("Tell Gemini what to change",placeholder="Make the jacket black and add dramatic rain.",key="edit_prompt")
        if st.button("🔄 Apply edit",use_container_width=True,key="gemini_edit"):
            work=Path(tempfile.mkdtemp(prefix="rgpt_edit_",dir=WORK));ref=work/"current.png";ref.write_bytes(st.session_state.gemini_result);out=work/"edited.png"
            try:
                with st.spinner("Applying edit…"):
                    ok,msg=gemini_generate(ep,out,[ref])
                if ok:
                    st.session_state.gemini_result=out.read_bytes();st.session_state.gemini_history.append((ep,st.session_state.gemini_result));st.image(st.session_state.gemini_result,use_container_width=True);st.download_button("⬇️ Download edited image",st.session_state.gemini_result,"racharlagpt_edited.png","image/png",use_container_width=True)
                else: st.error(msg)
            except Exception as e: st.error(f"Edit failed: {e}")
            finally: shutil.rmtree(work,ignore_errors=True)
    else: st.info("Generate an image first, then use Continue Editing for prompt-based changes.")
st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Movie Studio
# -----------------------------------------------------------------------------
left,right=st.columns([1.55,1],gap="large")
with left:
    st.markdown('<div class="card"><div class="section-title">🎞️ Script → Movie</div><div class="section-sub">Paste a story, screenplay or dialogue. Build an editable storyboard before rendering.</div>',unsafe_allow_html=True)
    script=st.text_area("Story / script",height=210,placeholder="A young photographer discovers a glowing doorway on a rainy night. Behind it is a forgotten cinema where every film predicts the future...",label_visibility="collapsed",key="movie_script")
    c1,c2,c3=st.columns(3)
    with c1: scene_count=st.slider("Scenes",3,10,6,key="scene_count")
    with c2: aspect=st.selectbox("Movie format",list(ASPECTS.keys()),index=0,key="movie_aspect")
    with c3: style=st.selectbox("Visual direction",["Dynamic styles","Cinematic","Anime-inspired","3D animation","Fantasy","Comic"],index=0,key="movie_style")
    if st.button("🧠 Understand story → Build storyboard",use_container_width=True):
        if not script.strip(): st.warning("Add a script or story first.")
        else: st.session_state.scenes=plan_scenes(script,scene_count);st.session_state.movie_bytes=None;st.success(f"Storyboard created with {len(st.session_state.scenes)} scenes.")
    st.markdown('</div>',unsafe_allow_html=True)
with right:
    st.markdown('<div class="card"><div class="section-title">🎭 Characters, photos & music</div><div class="section-sub">Upload reference photos for visual continuity or use generated/local scene visuals. Add your own music if desired.</div>',unsafe_allow_html=True)
    refs=st.file_uploader("Character/reference images",type=["png","jpg","jpeg","webp"],accept_multiple_files=True,key="movie_refs")
    music=st.file_uploader("🎵 Optional music",type=["mp3","wav","m4a","aac"],key="movie_music")
    st.caption("Reference photos are sent to Gemini only when you explicitly use Gemini generation and provide GEMINI_API_KEY.")
    st.markdown('</div>',unsafe_allow_html=True)

if st.session_state.scenes:
    st.write("");st.markdown('<div class="card"><div class="section-title">🎞️ Editable storyboard</div><div class="section-sub">Change the visual prompt, dialogue and duration. Regeneration happens per scene during the next render.</div>',unsafe_allow_html=True)
    for i,s in enumerate(st.session_state.scenes):
        a,b,c=st.columns([.14,1.65,.45])
        with a: st.markdown(f'<div class="scene-num">#{i+1:02d}</div>',unsafe_allow_html=True)
        with b:
            s["title"]=st.text_input("Scene title",s["title"],key=f"title_{i}",label_visibility="collapsed")
            s["description"]=st.text_area("Visual prompt",s["description"],height=75,key=f"desc_{i}",label_visibility="collapsed")
            s["dialogue"]=st.text_input("Dialogue / caption",s["dialogue"],key=f"dlg_{i}",label_visibility="collapsed")
        with c:
            s["duration"]=st.number_input("Seconds",3.0,15.0,float(s["duration"]),.5,key=f"dur_{i}")
            s["style"]=st.selectbox("Style",["Cinematic","Dreamy","Golden Hour","Neon Night","Epic","Intimate","Anime-inspired","Fantasy"],index=["Cinematic","Dreamy","Golden Hour","Neon Night","Epic","Intimate","Anime-inspired","Fantasy"].index(s.get("style","Cinematic")) if s.get("style") in ["Cinematic","Dreamy","Golden Hour","Neon Night","Epic","Intimate","Anime-inspired","Fantasy"] else 0,key=f"sty_{i}")
    st.markdown('</div>',unsafe_allow_html=True)

st.write("");st.markdown('<div class="card"><div class="section-title">🎬 Render a real MP4</div><div class="section-sub">Gemini is optional. Without a Gemini key, the deterministic local renderer still creates a real MP4 so the complete media pipeline can be tested.</div>',unsafe_allow_html=True)
r1,r2,r3=st.columns(3)
with r1: use_gemini=st.checkbox("Use Gemini for scene images",value=bool(gemini_key()),key="use_gemini")
with r2: auto_music=st.checkbox("Generate music if none uploaded",value=True,key="auto_music")
with r3: captions=st.checkbox("Burn captions",value=True,key="captions")
st.markdown('<div class="create-btn">',unsafe_allow_html=True);create=st.button("✨ CREATE CINEMATIC MOVIE",use_container_width=True,key="create_movie");st.markdown('</div>',unsafe_allow_html=True)

if create:
    if not st.session_state.scenes: st.error("Build the storyboard first.")
    elif use_gemini and not gemini_key(): st.info("Gemini is selected but GEMINI_API_KEY is missing. Either add the key or disable Gemini and use the local renderer.")
    else:
        progress=st.progress(0);status=st.empty();job=Path(tempfile.mkdtemp(prefix="rgpt_job_",dir=WORK));scene_files=[];durations=[float(s["duration"]) for s in st.session_state.scenes]
        try:
            ref_imgs=[]
            for j,r in enumerate(refs or []):
                p=job/f"ref_{j}.jpg";Image.open(r).convert("RGB").save(p,"JPEG",quality=94);ref_imgs.append(p)
            for i,s in enumerate(st.session_state.scenes):
                status.markdown(f'<div class="status">🎨 Scene {i+1}/{len(st.session_state.scenes)} · generating visual…</div>',unsafe_allow_html=True);out=job/f"scene_{i+1:02d}.png";generated=False
                if use_gemini:
                    prompt=f"Cinematic movie still, {s['style']} visual direction. {s['description']}. Strong composition, expressive characters, film lighting, depth, detailed environment, no watermark added by prompt, no text unless necessary for story."
                    try: generated,_=gemini_generate(prompt,out,ref_imgs)
                    except Exception: generated=False
                if not generated:
                    if ref_imgs: fit_image(Image.open(ref_imgs[i%len(ref_imgs)]),(ASPECTS[aspect][2],ASPECTS[aspect][3]),"Auto Fit").save(out)
                    else: make_local_cinematic(s["description"],(ASPECTS[aspect][2],ASPECTS[aspect][3]),i+1,s["style"]).save(out)
                scene_files.append(out);progress.progress(int((i+1)/len(st.session_state.scenes)*60))
            srt=job/"captions.srt";write_srt(st.session_state.scenes,srt) if captions else None;music_path=None
            if music: music_path=job/("uploaded_music"+Path(music.name).suffix.lower());music_path.write_bytes(music.getvalue())
            elif auto_music: music_path=job/"studio_music.wav";make_music(music_path,sum(durations))
            status.markdown('<div class="status">🎞️ FFmpeg is assembling the final MP4…</div>',unsafe_allow_html=True);out=job/"racharlagpt_cinematic_movie.mp4";render_movie(scene_files,durations,out,music_path,srt if captions else None,output_size=(ASPECTS[aspect][2],ASPECTS[aspect][3]));st.session_state.movie_bytes=out.read_bytes();st.session_state.movie_name="racharlagpt_cinematic_movie.mp4";progress.progress(100);status.markdown('<div class="status ok">✓ Movie rendered successfully.</div>',unsafe_allow_html=True)
        except Exception as e: st.exception(e)
        finally: shutil.rmtree(job,ignore_errors=True)

if st.session_state.movie_bytes:
    st.write("");st.markdown('<div class="card"><div class="section-title">🎥 Finished movie</div><div class="section-sub">Real MP4 output from the Python/FFmpeg pipeline.</div>',unsafe_allow_html=True);st.video(st.session_state.movie_bytes);st.download_button("⬇️ Download MP4",st.session_state.movie_bytes,file_name=st.session_state.movie_name,mime="video/mp4",use_container_width=True);st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Utility studio
# -----------------------------------------------------------------------------
st.write("");st.markdown('<div class="card"><div class="section-title">🧰 More free studio tools</div><div class="section-sub">Auto Fit, video → audio, video trimming and provider controls.</div>',unsafe_allow_html=True)
tabs=st.tabs(["🖼️ Auto Fit","🎵 Video → Audio","✂️ Video Trim","⚙️ Providers"])
with tabs[0]:
    up=st.file_uploader("Upload an image",type=["png","jpg","jpeg","webp"],key="fitup")
    if up:
        a,b=st.columns(2)
        with a:
            mode=st.selectbox("Fit mode",["Auto Fit","Fill / Crop","Stretch"],key="fitmode");ax=st.slider("Position X",-1.0,1.0,0.0,.05,key="ax");ay=st.slider("Position Y",-1.0,1.0,0.0,.05,key="ay");rot=st.slider("Rotation",-15,15,0,key="rot");fmt=st.selectbox("Output format",list(ASPECTS.keys()),key="fitfmt")
        with b:
            im=Image.open(up);_,_,W,H=ASPECTS[fmt];fitted=fit_image(im,(W,H),mode,ax,ay,rot);st.image(fitted,use_container_width=True);buf=io.BytesIO();fitted.save(buf,"PNG");st.download_button("⬇️ Download fitted PNG",buf.getvalue(),"fitted.png","image/png")
with tabs[1]:
    v=st.file_uploader("Video",type=["mp4","mov","mkv","webm"],key="audvid")
    if v and st.button("Extract MP3",key="extract"):
        p=WORK/"input_video";p.write_bytes(v.getvalue());out=WORK/"extracted.mp3";q=subprocess.run([FFMPEG,"-y","-i",str(p),"-vn","-codec:a","libmp3lame","-q:a","2",str(out)],capture_output=True,text=True)
        if q.returncode==0: st.download_button("⬇️ Download MP3",out.read_bytes(),"extracted.mp3","audio/mpeg")
        else: st.error(q.stderr[-1200:])
with tabs[2]:
    v=st.file_uploader("Video to trim",type=["mp4","mov","mkv","webm"],key="trimvid")
    if v:
        a,b=st.columns(2);start=a.number_input("Start seconds",0.0,9999.0,0.0,.1,key="ts");end=b.number_input("End seconds",0.1,9999.0,10.0,.1,key="te")
        if st.button("Trim video",key="trim"):
            p=WORK/"trim_in";p.write_bytes(v.getvalue());out=WORK/"trimmed.mp4";q=subprocess.run([FFMPEG,"-y","-ss",str(start),"-i",str(p),"-to",str(max(.1,end-start)),"-c","copy",str(out)],capture_output=True,text=True)
            if q.returncode==0: st.download_button("⬇️ Download trimmed MP4",out.read_bytes(),"trimmed.mp4","video/mp4")
            else: st.error(q.stderr[-1200:])
with tabs[3]:
    st.markdown("**Gemini**");st.code("GEMINI_API_KEY=your_google_ai_key\nGEMINI_IMAGE_MODEL=gemini-3.1-flash-image",language="bash");st.caption("Never commit GEMINI_API_KEY to GitHub.")
    st.markdown("**Legacy provider compatibility**");st.caption("The previous generic image-provider environment variables are not required for Gemini. The new image engine uses the Gemini REST API.")
st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Trust, product information, related free apps and compliance content
# -----------------------------------------------------------------------------
st.write("")
st.markdown('<div class="card"><div class="section-title">🌟 Explore the RacharlaGPT family</div><div class="section-sub">Useful product information and direct links, presented as normal navigation — not advertising.</div><div class="feature-grid">'
+'''<a class="link-card" href="https://racharlagpt.in/" target="_blank"><div class="feature-card"><div class="feature-icon">💻</div><h3>RacharlaGPT.in</h3><p>Free programming, coding, debugging, learning and ATS resume-building tools.</p></div></a>'''
+'''<a class="link-card" href="https://spin.racharlagpt.in/" target="_blank"><div class="feature-card"><div class="feature-icon">🎮</div><h3>Free RacharlaGPT Games</h3><p>Dice, Spin, Memory, Ludo and Trivia for free.</p></div></a>'''
+'''<div class="feature-card"><div class="feature-icon">🎬</div><h3>AI Movie Studio</h3><p>Movies, posters, characters, images, music, captions and video utilities in one creator workspace.</p></div>'''
+'''</div></div>''',unsafe_allow_html=True)

info_tabs=st.tabs(["📖 About & Features","🔒 Privacy","📜 Terms & AI disclosure","💰 Advertising"])
with info_tabs[0]:
    st.markdown("""### About RacharlaGPT AI Movie Studio
RacharlaGPT AI Movie Studio is a creator tool for turning ideas, scripts, photos and media into cinematic projects. The Studio combines deterministic Python/FFmpeg processing with optional AI image generation.

**Main features**
- Idea → Movie and Script → Movie
- Editable scene storyboard
- Gemini text-to-image and photo transformation
- AI poster maker
- Character/reference images
- Photo Auto Fit, Fill/Crop, Stretch, X/Y positioning and rotation
- Music upload or generated background music
- Captions / SRT burn-in
- Video → audio extraction
- Video trimming
- Real MP4 preview and download

AI output can vary by provider/model. Review generated media before publishing, especially names, faces, logos, text and copyrighted material.
""")
with info_tabs[1]:
    st.markdown("""### Privacy summary
- Uploaded files are processed by this Streamlit application only for the operation you request, except when you explicitly use a third-party AI provider such as Google Gemini.
- If Gemini is enabled, images/prompts sent to Gemini are subject to Google's applicable API terms and privacy documentation.
- Temporary render files are stored in the app workspace while a job runs and are deleted after the render attempt where the application can do so.
- Generated MP4/image bytes may remain in the current Streamlit session until the session is cleared or the app process is restarted.
- Do not upload material you do not have permission to process.
- Analytics/advertising services may use cookies or similar technologies when enabled in deployment.

Publish your complete legal Privacy Policy, cookie notice and contact information at the production domain before enabling advertising.
""")
with info_tabs[2]:
    st.markdown("""### Terms & AI disclosure
Users are responsible for the material they upload and for checking rights to images, music, scripts, trademarks and other content. AI-generated material may contain mistakes or unintended similarities. The Studio does not guarantee that generated content is suitable for every commercial or publishing use.

RacharlaGPT is not Google and Gemini is a third-party service. Provider names are shown for technical transparency, not endorsement.

For production, replace this summary with your reviewed Terms of Service, Copyright Policy, AI disclosure and contact/legal pages.
""")
with info_tabs[3]:
    st.markdown("""### Advertising & monetization
Ad placements must remain clearly separate from product navigation, create/download controls and interactive media. Do not ask users to click ads, do not disguise ads as feature cards, and do not place ads where they can cause accidental clicks.

The legacy AdSense publisher ID and Monetag zone references are retained in the project configuration. Monetization is **disabled by default** and requires explicit deployment environment flags.

For AdSense, use the current Google publisher policies and placement guidance before enabling `ADSENSE_ENABLED=1`. For Monetag, review the current provider rules before enabling `MONETAG_ENABLED=1`.
""")

# Optional ad slots are placed after substantial content, not beside primary controls.
st.write("")
render_adsense_placeholder()
render_monetag_optional()

# -----------------------------------------------------------------------------
# Configuration reference card
# -----------------------------------------------------------------------------
st.write("")
st.markdown('<div class="card"><div class="section-title">🔧 Monetization configuration vault</div><div class="section-sub">These values were collected from the old files as requested. The old projects are not used as the implementation source.</div>',unsafe_allow_html=True)
st.code("""GA4: G-RW7Q04LP7B
AdSense publisher: pub-1188239058737040

Monetag legacy references:
5gvci.com  zone 11852352  (service worker)
nap5k.com  zone 11852425  (tag)
n6wxm.com   zone 11852426  (vignette)
quge5.com  zone 284180    (legacy direct tag)

Runtime switches:
ADSENSE_ENABLED=0
MONETAG_ENABLED=0
""")
st.markdown("</div>",unsafe_allow_html=True)

st.markdown('<div class="footer">RacharlaGPT AI Movie Studio · New Python/Streamlit architecture · Old projects used only as configuration/reference vault · <a href="https://racharlagpt.in/" target="_blank">RacharlaGPT.in</a> · <a href="https://spin.racharlagpt.in/" target="_blank">Free Games</a></div>',unsafe_allow_html=True)
