# Vision setup

Read on demand before first build/run. Authoritative detail: component `README.md` §2 and `package.xml`.

## Dependencies

| Layer | Requirements |
| --- | --- |
| Build | CMake 3.10+, C++17; Python 3.12+ optional |
| C++ | OpenCV 4 (`core`, `imgproc`, `imgcodecs`, `highgui`, `dnn`), Eigen3, spacemit-ort / ONNX Runtime + SpaceMIT EP, yaml-cpp |
| Python (examples / wheel) | NumPy, OpenCV; for packaging: `pybind11`, `build`, `setuptools`, `wheel` |

Typical Debian/Ubuntu packages (confirm before `sudo apt`):

```bash
sudo apt-get update
sudo apt-get install -y python3-spacemit-ort opencv-spacemit libeigen3-dev spacemit-onnxruntime libyaml-cpp-dev
```

CMake path hints: `OpenCV_DIR` / `OpenCV_INSTALL_DIR`, `SPACEMIT_DIR`.

## Build options (high level)

| CMake option | Default | Meaning |
| --- | --- | --- |
| `BUILD_EXAMPLES` | ON | Example binaries |
| `BUILD_TESTS` | ON | Tests + `vision_infer_benchmark` |
| `BUILD_PYTHON_BINDINGS` | ON | pybind extension (skipped if no pybind11) |
| `BUILD_PYTHON_WHEEL` | ON | Pack `spacemit_vision` wheel during build |

Standalone:

```bash
cmake -S . -B build && cmake --build build -j
```

Inside SpacemiT Robot SDK: `source build/envsetup.sh`, then `mm` in `components/model_zoo/vision` (hand target/env details to `spacemit-robot-build`).

## Python wheel

```bash
python3 -m pip install -U pybind11 build setuptools wheel
cmake -S . -B build && cmake --build build -j    # wheel under src/python/dist/
python3 -m pip install --force-reinstall src/python/dist/*.whl
python3 -c "from spacemit_vision import VisionServiceNative; print('ok')"
```

Use the **same** `python3` for install and run. Bindings-only: `-DBUILD_PYTHON_WHEEL=OFF`. C++-only: `-DBUILD_PYTHON_BINDINGS=OFF`.

## Model cache

- Root: `~/.cache/models/vision/<type>/` (e.g. `yolov8/`, `siglip2/`, `buffalo_l/`).
- Per example/app: `examples/<name>/scripts/download_models.sh` or `applications/<app>/scripts/download_models.sh`.
- Bulk: component-root `scripts/download_all_models.sh` (confirm first; some models may need a per-example script).

Do not commit models into the source tree.

## Asset cache (images / videos)

- Root: `~/.cache/assets/` with `image/` and `video/`.
- Download: `scripts/download_assets.sh` (from SpacemiT archive; confirm before large downloads).
- Example yaml `test_image` / `test_video` paths usually point here.

## Headless / no-display boards

- Prefer `cv2.imwrite` / C++ `imwrite` over `imshow` / `highgui` windows.
- Pure SSH without `DISPLAY`: GUI failures are an environment limit, not a model bug.
- Camera demos still need a real device and user confirmation before opening the camera.

## Quick readiness checklist

1. System deps installed (`package.xml` / README §2.1).
2. Component built (standalone or SDK `mm`).
3. Wheel installed if using Python.
4. Required ONNX files under `~/.cache/models/vision/`.
5. Default assets under `~/.cache/assets/` if using stock test media.
6. Display strategy decided (GUI vs save-to-disk).
