import ast, pathlib, tempfile
from pathlib import Path
src=Path(__file__).with_name('app.py').read_text()
tree=ast.parse(src)
want={'safe_font','text_wrap','fit_image','make_local_cinematic','ffmpeg_ok','make_music','write_srt','render_movie','plan_scenes','_gemini_part_from_bytes','gemini_generate'}
ns={'os':__import__('os'),'re':__import__('re'),'io':__import__('io'),'math':__import__('math'),'wave':__import__('wave'),'base64':__import__('base64'),'random':__import__('random'),'shutil':__import__('shutil'),'tempfile':__import__('tempfile'),'subprocess':__import__('subprocess'),'Path':Path}
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance,ImageOps,ImageFont
ns.update({'np':np,'Image':Image,'ImageDraw':ImageDraw,'ImageFilter':ImageFilter,'ImageEnhance':ImageEnhance,'ImageOps':ImageOps,'ImageFont':ImageFont})
ns['WORK']=Path(tempfile.mkdtemp(prefix='rgpt_smoke_')); ns['FFMPEG']='ffmpeg'
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in want:
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(Path(__file__).with_name('app.py')),'exec'),ns)
assert ns['ffmpeg_ok'](), 'ffmpeg unavailable'
scenes=ns['plan_scenes']('A hero enters a glowing cinema. The screen predicts tomorrow. He must choose whether to change the future.',3)
assert len(scenes)==3
imgs=[]
for i,s in enumerate(scenes,1):
    p=ns['WORK']/f'scene{i}.jpg'; ns['make_local_cinematic'](s['description'],(640,360),i,s['style']).save(p); imgs.append(p)
music=ns['WORK']/ 'music.wav'; ns['make_music'](music,4)
srt=ns['WORK']/ 'captions.srt'; ns['write_srt'](scenes,srt)
out=ns['WORK']/ 'movie.mp4'; ns['render_movie'](imgs,[1.2,1.2,1.2],out,music,srt,(640,360))
assert out.exists() and out.stat().st_size>1000
print('SMOKE_OK', out, out.stat().st_size)
