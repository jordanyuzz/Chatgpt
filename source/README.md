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

这是二维分层（2.5D）照片合成，不是完整三维流体模拟。多边形保护船身、货柜、建筑和旗杆；海面有独立的向右下方传播的波纹；五条尾流区域有独立的行进泡沫亮度与纹理扰动；旗帜有从固定端向自由端增加的局部变形。相机固定，船身稳定，没有倒放、摆动、变焦或跨帧淡化。保留原有尾流骨架，未模拟泡沫粒子的真实生成与寿命；船身未增加起伏，天空与薄雾保持静止。不要将其宣传为完整三维航行模拟。

为了把全部船队保留在右侧，原图在水平方向缩至80%，左边使用原图干净海面并平滑拼接。所有物体保持时间上的稳定，画幅无黑边。船队最左缘约43%，左40%无船只。输出1920×1080由原图放大，不能恢复原图未包含的细节。

## 循环
300帧、30fps、10秒。所有动画都使用整数周期：波纹3/4/5周期，尾流6/8/10周期，旗面3/5周期。frame(300) 等于 frame(0)（源码将帧号对300取模，避免浮点周期端点舍入误差），文件不重复添加第300帧。无倒放、交叉淡化或首尾停顿。render.py 中的 ships、flags、wakes 可编辑区域与方向，N/FPS控制时长帧率，phase控制海面运动，disp控制旗面波幅。

## 交付
output/bluevoy-fleet-loop.mp4：H.264、yuv420p、faststart、无音轨。
output/bluevoy-fleet-loop.webm：VP9、无音轨。
output/poster.jpg：1920×1080封面。
output/index.html：预览和网站嵌入代码。
output/validation.json：当前文件的元数据和循环检查。

无需外部API，无收费服务。源码和用户原始素材一并保留，便于继续编辑。
