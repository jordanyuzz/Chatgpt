from pathlib import Path
import subprocess,json,numpy as np
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent;out=root/'output'
r=json.loads((out/'validation.json').read_text())
for ext in ['mp4','webm']:
 p=out/f'bluevoy-fleet-loop.{ext}'
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
 streams=info['streams'];v=next(s for s in streams if s['codec_type']=='video')
 assert len(streams)==1 and v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='30/1' and int(v['nb_read_frames'])==300,info
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
 r[ext]={'codec':v['codec_name'],'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'decoded_frames':int(v['nb_read_frames']),'duration':info['format'].get('duration'),'audio_streams':0,'full_decode':'passed','bytes':p.stat().st_size}
# Decoded MP4 seam compared with ordinary frame changes.
cmd=['ffmpeg','-v','error','-i',str(out/'bluevoy-fleet-loop.mp4'),'-vf','scale=480:270','-f','rawvideo','-pix_fmt','rgb24','-']
a=np.frombuffer(subprocess.check_output(cmd),dtype=np.uint8).reshape(300,270,480,3).astype(np.float32)
d=np.abs(a[1:]-a[:-1]).mean(axis=(1,2,3));seam=float(np.abs(a[-1]-a[0]).mean())
r['decoded_mp4_seam']={'mean_absolute_pixel_difference':seam,'ordinary_frame_difference_mean':float(d.mean()),'ordinary_frame_difference_max':float(d.max()),'seam_to_mean_ratio':float(seam/d.mean())}
sheet=Image.new('RGB',(960,810))
for j,k in enumerate([0,75,150,225,299,0]):
 im=Image.fromarray(a[k].astype(np.uint8));ImageDraw.Draw(im).text((12,12),f'Frame {k} / {k/30:.3f}s',fill='white');sheet.paste(im,((j%2)*480,(j//2)*270))
sheet.save(out/'contact-sheet.jpg',quality=92)
(out/'validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
