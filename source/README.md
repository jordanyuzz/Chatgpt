# 蓝航船队首页循环视频

## 运行
需要 Python 3.12+、FFmpeg（libx264 和 libvpx-vp9）。

```sh
cd /path/to/fleet
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python3 render.py
python3 -m http.server 8000 --directory output
```

本地打开服务器的 output/index.html（服务器以 output 为根时访问 /），预览实际视频。index.html 也是可复制的网站背景嵌入示例，包含 autoplay/muted/loop/playsinline、MP4 回退和减少动态偏好响应。减少动态时仅显示 poster.jpg，并停止下载/播放视频。更换示例文案即可使用。保留完整画面时使用 16:9 容器；其他宽高比的 object-fit:cover 会裁切，可能减少文案空间。

## 资产与实现
assets/fleet.png 是用户上传的 1672×941 原图；assets/logo.jpg 是上传的品牌参考，保留在可编辑工程中。当前四艘护航船直接保留原图上已经存在的品牌旗帜纹理；没有重新绘制文字，也没有用生成式模型改字。中央旗帜同样保留原图的「企业出海」。远处两面旗帜的文字清晰度受原图分辨率限制。

这是二维分层（2.5D）照片合成，不是完整三维流体模拟。v2 已去掉正弦水面位移和泡沫亮度闪动。ocean.py 从用户照片的干净海面提取真实纹理，制作周期连续纹理，在透视水面上持续向右下方输送；近景流动更快，远景更慢，并使用多层纹理过滤抑制远景闪烁。五条尾流使用独立的船尾坐标、向后扩散的轮廓与持续向后输送的照片泡沫纹理。没有水面往返运动、倒放或全局跨帧淡化。船队在等速跟随镜头中保持固定队形与位置，通过水面和尾流相对船体的持续运动表现向左上方航行，避免船只在10秒末回跳。船身未增加起伏，天空与薄雾保持静止。
为了把全部船队保留在右侧，原图在水平方向缩至80%，左边使用原图干净海面并平滑拼接。所有物体保持时间上的稳定，画幅无黑边。船队最左缘约43%，左40%无船只。输出1920×1080由原图放大，不能恢复原图未包含的细节。

## 循环
300帧、30fps、10秒。海面世界坐标在每10秒整段前移一个完整448像素纹理周期，尾流纹理沿船尾方向前移三个完整400像素纹理周期；旗帜采用3/5个完整周期。frame(300) 等于 frame(0)（帧号对300取模）。没有首尾交叉淡化或重复添加第300帧。运动检查使用照片纹理的局部相关追踪，验证水面在屏幕上持续向右下方前进；船体内部像素检查确认其未参与海面变形。

```sh
OPENBLAS_NUM_THREADS=1 python3 check_motion.py
OPENBLAS_NUM_THREADS=1 python3 verify.py
```

render.py 定义 ships、flags、wakes 区域；ocean.py 控制海面透视、水流速度、泡沫输送和扩散。N/FPS 控制时长帧率；更改周期时必须同时检查单向运动速度与首尾连续性。
## 交付
output/bluevoy-fleet-loop.mp4：H.264、yuv420p、faststart、无音轨。
output/bluevoy-fleet-loop.webm：VP9、无音轨。
output/poster.jpg：1920×1080封面。
output/index.html：预览和网站嵌入代码。
output/validation.json：当前文件的元数据和循环检查。

无需外部API，无收费服务。源码和用户原始素材一并保留，便于继续编辑。
