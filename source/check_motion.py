"""Check the loop and actual forward water transport before encoding validation."""
import json,numpy as np
from scipy.signal import correlate2d
from scipy.ndimage import gaussian_filter
import render
from pathlib import Path
f0=np.asarray(render.frame(0)).astype(float)
f1=np.asarray(render.frame(1)).astype(float)
f299=np.asarray(render.frame(299)).astype(float)
f300=np.asarray(render.frame(300)).astype(float)
a=render.ocean.frame(0,300).mean(2);b=render.ocean.frame(10,300).mean(2)
t=a[680:760,180:260];r=b[660:790,160:300]
t=t-gaussian_filter(t,7);r=r-gaussian_filter(r,7)
c=correlate2d(r,t,mode='valid');yy,xx=np.unravel_index(c.argmax(),c.shape)
dx,dy=int(xx)-20,int(yy)-20
assert dx>0 and dy>0,(dx,dy)
assert np.array_equal(f0,f300)
# Container stacks and hull positions stay fixed in a tracking camera.
a=render.ocean.frame(0,300);b=render.ocean.frame(10,300)
points=[(1000,400),(1200,500),(1050,710),(514,273),(595,223),(1545,565)]
assert all(np.max(abs(a[yy,xx]-b[yy,xx]))==0 for xx,yy in points)
directions=[]
for k in [0,60,120,180,240]:
 aa=render.ocean.frame(k,300).mean(2);bb=render.ocean.frame(k+10,300).mean(2)
 tt=aa[680:760,180:260];rr=bb[660:790,160:300]
 tt=tt-gaussian_filter(tt,7);rr=rr-gaussian_filter(rr,7)
 cc=correlate2d(rr,tt,mode='valid');qy,qx=np.unravel_index(cc.argmax(),cc.shape)
 motion={'start_frame':k,'dx':int(qx)-20,'dy':int(qy)-20}
 assert motion['dx']>0 and motion['dy']>0,motion
 directions.append(motion)
result={'version':2,'periodic_endpoint_max_pixel_difference':float(abs(f0-f300).max()),'last_to_first_mean_absolute_pixel_difference':float(abs(f299-f0).mean()),'first_to_second_mean_absolute_pixel_difference':float(abs(f1-f0).mean()),'water_motion_test':{'source_pixel_dx_over_10_frames':dx,'source_pixel_dy_over_10_frames':dy,'method':'high-pass patch correlation at foreground x180:260 y680:760','passed':True},'water_direction_samples':directions,'rigid_ship_sample_motion_test':'passed','ship_count':5,'left_text_safe_fraction':.4,'limitations':['2.5D photo-textured tracking shot, not full 3D simulation','original flag textures; distant text limited by original pixels','photographic tiled foam advection; not a fluid solver','no ship heave or mist animation']}
(render.ROOT/'output/validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
