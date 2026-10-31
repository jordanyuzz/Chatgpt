"""Editable 2.5D fleet loop. Coordinates refer to the supplied 1672x941 image."""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from scipy.ndimage import map_coordinates
from pathlib import Path
import subprocess, json
ROOT=Path(__file__).resolve().parent
W,H=1672,941; FPS=30; N=300
src=Image.open(ROOT/'assets/fleet.png').convert('RGB').resize((W,H))
a=np.asarray(src).astype(np.float32)
y,x=np.mgrid[:H,:W].astype(np.float32)
# Rigid silhouettes: hulls, containers, superstructure, masts and flagpoles.
ships=[[(674,255),(704,242),(711,201),(723,198),(731,241),(815,244),(962,284),(970,309),(1080,339),(1122,354),(1128,327),(1172,326),(1170,306),(1180,301),(1184,333),(1226,322),(1243,267),(1265,266),(1274,325),(1300,325),(1315,418),(1357,425),(1365,450),(1455,474),(1463,568),(1500,579),(1484,635),(1455,668),(1411,687),(1352,665),(1230,620),(1097,551),(976,482),(857,407),(744,337),(696,295)],[(477,268),(490,253),(504,250),(507,228),(513,225),(519,251),(537,260),(549,283),(537,294),(504,286)],[(566,218),(580,208),(586,184),(596,182),(600,211),(615,221),(625,235),(608,241),(581,233)],[(948,680),(963,663),(984,661),(998,645),(1018,645),(1028,609),(1039,607),(1046,657),(1065,675),(1079,699),(1087,728),(1128,745),(1120,766),(1086,771),(1024,749),(981,719)],[(1473,548),(1492,534),(1510,531),(1522,503),(1536,498),(1545,537),(1569,555),(1580,579),(1614,591),(1606,611),(1577,617),(1520,595),(1486,570)]]
flags=[[(1353,303),(1532,369),(1538,441),(1346,379)],[(519,215),(571,232),(568,259),(519,241)],[(602,176),(660,188),(656,215),(599,201)],[(1069,614),(1194,674),(1180,719),(1061,666)],[(1555,480),(1647,516),(1645,558),(1552,524)]]
rigid=Image.new('L',(W,H));d=ImageDraw.Draw(rigid)
for p in ships+flags:d.polygon(p,fill=255)
rigid=rigid.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(1))
sea=(1-np.asarray(rigid)/255)*np.clip((y-143)/35,0,1)
# Wake fields originate at the stern and always extend towards lower right.
wakes=[(1417,676,1.0),(1096,754,.62),(1594,603,.5),(531,287,.35),(609,235,.25)]
wake=np.zeros((H,W),np.float32)
for sx,sy,s in wakes:
 dx=x-sx;dy=y-sy;along=(dx*.60+dy*.80);cross=dx*.80-dy*.60
 wake+=np.exp(-(cross/(12*s+np.maximum(along,0)*.19))**2)*np.clip(along/24,0,1)*np.exp(-np.maximum(along,0)/420)*s
wake=np.clip(wake,0,1)*sea
# Recompose the fleet into the right 60% using a horizontal scene scale.
S=.8; ox=334
# Flag patches use source typography and logo, preserving exact branding.
flagdata=[]
for poly in flags:
 xx=[p[0] for p in poly]; yy=[p[1] for p in poly]; l=max(0,min(xx)-4);r=min(W,max(xx)+5);t=max(0,min(yy)-5);b=min(H,max(yy)+6)
 mask=Image.new('L',(r-l,b-t));ImageDraw.Draw(mask).polygon([(u-l,v-t) for u,v in poly],fill=255)
 flagdata.append((l,t,r,b,np.asarray(mask.filter(ImageFilter.GaussianBlur(.65)))/255))

def frame(k):
 theta=2*np.pi*(k % N)/N
 depth=np.clip((y-145)/(H-145),0,1)
 # Integer temporal harmonics make sea, foam and cloth exactly periodic.
 phase=(x*.032+y*.045-theta*5)
 dx=depth*(2.6*np.sin(phase)+1.1*np.sin(x*.061+y*.025-theta*3))
 dy=depth*(1.8*np.sin(phase)+.8*np.cos(x*.025+y*.057-theta*4))
 dx+=wake*4*np.sin((x+y)*.055-theta*8)
 dy+=wake*5*np.sin((x+y)*.055-theta*8)
 coords=[np.clip(y-dy,0,H-1),np.clip(x-dx,0,W-1)]
 moving=np.stack([map_coordinates(a[:,:,c],coords,order=1,mode='nearest',prefilter=False) for c in range(3)],axis=-1)
 out=a+(moving-a)*sea[:,:,None]
 foam=(np.sin((x*.60+y*.80)*.17-theta*10)+np.sin(x*.11-y*.09-theta*6))*.5
 out+=wake[:,:,None]*foam[:,:,None]*9
 # Local cloth distortion increases towards the free trailing edge; pole is fixed.
 for j,(l,t,r,b,mask) in enumerate(flagdata):
  fy,fx=np.mgrid[t:b,l:r].astype(np.float32);u=(fx-l)/max(1,r-l-1)
  disp=u*u*(1.5*np.sin(u*8-theta*3+j)+.45*np.sin(u*14-theta*5))
  patch=np.stack([map_coordinates(a[:,:,c],[np.clip(fy-disp,0,H-1),fx],order=1,prefilter=False) for c in range(3)],-1)
  alpha=mask[:,:,None]
  out[t:b,l:r]=out[t:b,l:r]*(1-alpha)+patch*alpha
 im=Image.fromarray(np.uint8(np.clip(out,0,255)))
 scaled=im.resize((round(W*S),H),Image.Resampling.LANCZOS)
 canvas=im.copy();canvas.paste(scaled,(ox,0))
 clear=im.crop((0,0,470,H)).resize((760,H),Image.Resampling.LANCZOS)
 ar=np.asarray(canvas).astype(np.float32)
 # Feather clean ocean into the right-hand scene before the nearest escort.
 feather=np.clip((np.arange(760)-390)/290,0,1);feather=feather*feather*(3-2*feather)
 ar[:,:760]=np.asarray(clear)*(1-feather[None,:,None])+ar[:,:760]*feather[None,:,None]
 # Quiet, deep blue text-safe left region with a smooth transparent grade.
 grade=np.clip((760-x)/760,0,1)*.22
 ar*=1-grade[:,:,None]
 return Image.fromarray(np.uint8(np.clip(ar,0,255))).resize((1920,1080),Image.Resampling.LANCZOS)

def main():
 out=ROOT/'output';out.mkdir(exist_ok=True)
 cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'bluevoy-fleet-loop.mp4')]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for k in range(N):
  f=frame(k)
  if k==0:f.save(out/'poster.jpg',quality=95)
  if k in [0,75,150,225,299]:f.save(out/f'check-{k:03}.jpg',quality=90)
  p.stdin.write(f.tobytes())
  if k%30==0:print(f'{k}/{N}',flush=True)
 p.stdin.close()
 if p.wait():raise RuntimeError('H.264 encoding failed')
 subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(out/'bluevoy-fleet-loop.mp4'),'-an','-c:v','libvpx-vp9','-b:v','0','-crf','32','-row-mt','1','-threads','4',str(out/'bluevoy-fleet-loop.webm')],check=True)
 print('done',flush=True)
if __name__=='__main__':main()
