---
name: megaflow
description: >-
  Use for MegaFlow zero-shot large-displacement optical flow and dense point
  tracking (ECCV 2026, cvg/megaflow). Trigger on MegaFlow、光流、optical flow、
  large displacement、point tracking、点跟踪、运动估计、稠密跟踪、.flo。
---

# MegaFlow 光流 / 点跟踪

上游：[cvg/megaflow](https://github.com/cvg/megaflow) · 权重：[HuggingFace Kristen-Z/MegaFlow](https://huggingface.co/Kristen-Z/MegaFlow) · Apache-2.0

ViT 特征 + 轻量迭代精炼；**零样本**大位移光流，并扩展为长程点跟踪。经典 OpenCV Farneback/`calcOpticalFlow` → `opencv/video-analysis`；MOT 框跟踪 → `multi-object-tracking`。

## 环境

| 项 | 要求 |
| --- | --- |
| Python | ≥ 3.12 |
| PyTorch | ≥ 2.7，建议 CUDA |
| 安装 | `pip install git+https://github.com/cvg/megaflow.git` 或 clone 后 `pip install -e .` |
| 可选 | Hopper 上 FlashAttention-3（见上游 README） |

## 预训练权重（`from_pretrained` 自动下载）

| 名称 | 用途 |
| --- | --- |
| `megaflow-flow` | 光流默认 |
| `megaflow-chairs-things` | FlyingChairs/Things 训练光流 |
| `megaflow-track` | Kubric 微调点跟踪 |

## 输入约定

- `video`: `float32`，形状 `[1, T, 3, H, W]`，像素范围 **`[0, 255]`**（非 [0,1]）
- 长边建议对齐 demo 默认 **`fix_width=952`**，且可被 **patch_size=14** 整除
- 推理：`inference_mode` + CUDA 上 `autocast(bfloat16/float16)`；`num_reg_refine` 默认 **8**

## 光流 API

```python
import torch
from megaflow import MegaFlow  # 或 from megaflow.model import MegaFlow

device = "cuda" if torch.cuda.is_available() else "cpu"
model = MegaFlow.from_pretrained("megaflow-flow").eval().to(device)

# video: [1, T, 3, H, W] float32 in [0, 255]
with torch.inference_mode():
    with torch.autocast(device_type=device, dtype=torch.bfloat16, enabled=(device == "cuda")):
        out = model(video, num_reg_refine=8)
        flow = out["flow_preds"][-1]  # 相邻帧对 0→1, 1→2, ...
```

CLI：

```bash
python demo_flow.py --input assets/longboard.mp4 --output output/flow.mp4
python demo_flow.py --input path/to/images/ --output out_dir/ --save_flo --fix_width 952
```

关键参数：`--window_size`（滑窗，默认 4）、`--iters`（= `num_reg_refine`）、`--restore_size`、`--save_flo`。

## 点跟踪 API

```python
from megaflow.utils.basic import gridcloud2d

track = MegaFlow.from_pretrained("megaflow-track").eval().to(device)
with torch.inference_mode():
    with torch.autocast(device_type=device, dtype=torch.bfloat16, enabled=(device == "cuda")):
        flows_e = track.forward_track(video, num_reg_refine=8)["flow_final"]  # 0→t 偏移
        grid_xy = gridcloud2d(1, H, W, norm=False, device=device).float()
        grid_xy = grid_xy.permute(0, 2, 1).reshape(1, 1, 2, H, W)
        tracks = flows_e + grid_xy  # 绝对坐标轨迹
```

CLI：`python demo_track.py --input assets/apple.mp4 --grid_size 8`  
UI：`python demo_gradio.py` · [HF Space](https://huggingface.co/spaces/Kristen-Z/MegaFlow-demo) · [Colab](https://colab.research.google.com/github/cvg/megaflow/blob/main/demo_colab.ipynb)

## 训练 / 评测（需要时）

- 数据：FlyingChairs、FlyingThings3D、Sintel、KITTI、HD1K、TartanAir、Spring；跟踪另需 Kubric（AllTracker）+ TAP-Vid
- 布局：仓库根下 `datasets/` 符号链接（见上游 README）
- 课程：`train.sh`（多阶段 `restore_ckpt`）
- 评测：`python -m scripts.evaluate --cfg config/eval/zero-shot.json` / `tapvid.json`

## 机器人 / 具身衔接

| 场景 | 用法 |
| --- | --- |
| 人员跟随运动先验 | MegaFlow 稠密流 / 点轨迹 → 速度估计；控制层仍走 `robot-person-follow` + `cmd_vel` 互斥 |
| 导览避障运动场 | 光流幅值作动态障碍提示；导航权威仍是 Nav2（`embodied-tour-nav`） |
| 轻量实时 | 边缘设备优先 OpenCV / TensorRT 光流；MegaFlow 适合离线/工控机大位移 |

## 选型

| 需求 | 选 |
| --- | --- |
| 大位移零样本稠密光流 / 长程点轨迹 | **本 skill（MegaFlow）** |
| 经典稠密/稀疏光流、稳定化 | `opencv/video-analysis` |
| 检测框 ID 跟踪（SORT/ByteTrack） | `multi-object-tracking` |
| YOLO 检测 + 跟随 | `yolo` + `robot-person-follow` |

## 风险

- VRAM：高分辨率 × 长窗口易 OOM → 降 `fix_width` / `window_size`
- 输入归一化错误（误用 [0,1]）会严重降质
- CPU 可跑但慢；生产实时需压分辨率 + 限制 T
