"""Photo-textured, unidirectional ocean advection and stern foam transport.
No sinusoidal water warping, reverse playback, or global temporal dissolves.
"""
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates, distance_transform_edt

def seamless(a):
 h,w=a.shape[:2]
 wx=(.5-.5*np.cos(np.arange(w)*2*np.pi/w))[None,:,None]
 a=a*wx+np.roll(a,w//2,axis=1)*(1-wx)
 wy=(.5-.5*np.cos(np.arange(h)*2*np.pi/h))[:,None,None]
 return (a*wy+np.roll(a,h//2,axis=0)*(1-wy)).astype(np.float32)

class Ocean:
 def __init__(self,a,x,y,sea,wakes):
  self.a=a;self.x=x;self.y=y;self.sea=sea.astype(np.float32)
  distance=distance_transform_edt(sea>.5)
  self.contact=(np.clip((a.min(axis=2)-95)/75,0,1)*np.exp(-distance/11)*self.sea)[:,:,None]
  self.depth=np.clip((y-143)/798,0,1)
  crop=a[430:878,0:448]
  low=gaussian_filter(crop,sigma=(14,14,0))
  self.tex=seamless(np.clip((crop+4)/(low+4),.65,1.55))
  # Row-specific colour from the clean left ocean, independent of vessel colours.
  row=gaussian_filter(a[:,20:420].mean(axis=1),sigma=(12,0))
  self.colour=row[:,None,:]
  d=self.depth+.3
  self.u=2*(x-850)/d
  self.v=2100/d
  self.mips=np.stack([gaussian_filter(self.tex,sigma=(.65*2**i,.65*2**i,0)) for i in range(5)])
  footprint=np.maximum(2/d,2100/(798*d*d))
  self.lod=np.clip(np.log2(footprint),0,4).astype(np.float32)
  # Foam's source is real white-water texture, made spatially periodic.
  fc=a[741:941,1200:1600].mean(axis=2)
  fc=(fc-np.percentile(fc,20))/(np.percentile(fc,95)-np.percentile(fc,20))
  self.foam=seamless(np.clip(fc,0,1)[:,:,None])[:,:,0]
  self.fields=[]
  for sx,sy,s in wakes:
   dx=x-sx;dy=y-sy
   along=dx*.60+dy*.80;cross=dx*.80-dy*.60
   width=38*s+np.maximum(along,0)*.20
   env=np.exp(-(cross/width)**2)*np.clip(along/14,0,1)*np.exp(-np.maximum(along,0)/(380*s+200))
   iy,ix=np.nonzero(env>.0001)
   self.fields.append((iy,ix,along[iy,ix],cross[iy,ix],env[iy,ix].astype(np.float32),s))
 def frame(self,k,n):
  t=(k%n)/n
  # Exact whole-tile translations per loop, with no reversals.
  # Projective depth makes foreground water pass faster than distant water.
  uv=[np.mod(self.v+448*t,448),np.mod(self.u-448*t,448)]
  tex=np.stack([map_coordinates(self.mips[:,:,:,c],[self.lod,*uv],order=1,mode='grid-wrap',prefilter=False) for c in range(3)],-1)
  water=self.colour*np.clip(1+(tex-1)*1.45,.45,1.8)
  for iy,ix,along,cross,env,s in self.fields:
   # 400px of true downstream foam transport per ten seconds.
   fy=np.mod(cross*2.8+100+s*57,200)
   fx=np.mod(along*2.8-1200*t+s*103,400)
   grain=map_coordinates(self.foam,[fy,fx],order=1,mode='grid-wrap',prefilter=False)
   # Dense fresh foam at stern, feathering and dispersing downstream.
   density=np.clip((grain-.25)*3.5,0,1)
   alpha=(env*np.clip(.12+.91*density,0,.98)*self.sea[iy,ix])[:,None]
   foamcolour=np.array([219,240,246],dtype=np.float32)+density[:,None]*20
   water[iy,ix]=water[iy,ix]*(1-alpha)+foamcolour*alpha
  water=water*(1-self.contact)+self.a*self.contact
  strength=(self.sea*np.clip((self.y-154)/75,0,1))[:,:,None]
  return self.a*(1-strength)+np.clip(water,0,255)*strength
