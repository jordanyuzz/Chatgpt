# 蓝航船队循环视频交付 · 第二版

10 秒 · 1920×1080 · 30fps · 无音轨。MP4 使用 H.264，WebM 使用 VP9。

## 下载

- [MP4 视频](deliverables/bluevoy-fleet-loop.mp4)
- [WebM 视频](deliverables/bluevoy-fleet-loop.webm)
- [完整工程包 ZIP（含全部成品、素材与源码）](deliverables/bluevoy-fleet-source.zip)
- [封面 JPG](deliverables/poster.jpg)
- [动画预览 GIF](deliverables/preview.gif)
- [网站背景嵌入示例](deliverables/index.html)
- [验证结果](deliverables/validation.json)

打开文件页面后使用 Download raw file 下载；也可用仓库 Code → Download ZIP 下载整个仓库。

![封面](deliverables/poster.jpg)

## 实现和限制

第二版已重做海面与尾流：照片海纹在透视海面上持续向右下方输送，远近速度不同，并对远景纹理做过滤以减少闪烁。五条尾流的照片泡沫从各自船尾持续向后输送、扩散，保留船身接触水面处的白浪。没有水面正弦扭曲、往返运动、倒放或循环交叉淡化。船队朝左上方航行，等速跟随镜头保持船队的屏幕位置与队形，通过水面相对船体的持续运动表现航速。

仍属于二维分层照片动画，不是三维船舶或流体模拟。保留原旗帜纹理，远处 Logo 清晰度受原图限制。未加入船体起伏或薄雾动画。为了留出左侧40%文案空间，重新拼接海面并在水平方向压缩原图至80%。

两个视频均已完整解码验证：300帧、10秒、1920×1080、30fps、无音轨。运动检查在0/2/4/6/8秒分别追踪水面纹理，验证全部朝右下方移动。验证数值见 deliverables/validation.json。

## 编辑和运行

见 [source/README.md](source/README.md)。源码目录下执行 `python3 render.py`，输出到该目录内的 `output/`。原始输入文件位于 `source/assets/`。无需收费外部 API。
