# Research Dossier

> A working artifact, not one of the three curriculum documents. This is the
> source-checked ground truth gathered *before* writing them.

Every version number, API signature, rate limit and price below was checked against a
live source by a research agent. Anything the first agent could not verify was handed to
a second agent whose only job was to re-check it and downgrade or correct it. Claims are
labelled:

| Label | Meaning |
|---|---|
| **VERIFIED** | An agent fetched a page that states this. |
| *likely* | Inferred from strong indirect evidence. Trust, but re-check before depending on it. |
| `UNVERIFIED` | Could not be confirmed. **Treat as a research task for you, not as fact.** |

**Why this file exists:** these are exactly the facts that rot. A curriculum written from
memory would have been pinned to stale versions - and several findings below already
contradict what a mid-2026 model would assume by default.

## Collection status

| Sweep | Reported | Planned |
|---|---|---|
| Main sweep (reference repos + stack versions) | 10 | 13 |
| Emulator sweep (capture, input, hardware budget) | 0 | 6 |

Sections marked *pending* had not reported yet.

## Contents

**For Document 1 - Clash Royale AI Bot**

- [Reference Project: CRBot-public](#reference-project-crbot-public) *(pending)*
- [Android Emulator Options](#android-emulator-options) *(pending)*
- [Emulator Capture and Input Path](#emulator-capture-and-input-path) *(pending)*
- [Hardware Budget and Frame Budget](#hardware-budget-and-frame-budget) *(pending)*
- [Computer Vision Stack](#computer-vision-stack)
- [Reinforcement Learning Stack](#reinforcement-learning-stack)

**For Document 2 - Zerodha Trading Platform**

- [Zerodha Kite Connect and pykiteconnect](#zerodha-kite-connect-and-pykiteconnect)
- [Python Async Backend Stack](#python-async-backend-stack)
- [React and TypeScript Frontend Stack](#react-and-typescript-frontend-stack)

**For Document 3 - ML Algorithmic Trading Engine**

- [Quant and ML Trading Research Stack](#quant-and-ml-trading-research-stack)

---

# For Document 1 - Clash Royale AI Bot

## Reference Project: CRBot-public

*Pending.* Agent had not reported when this file was written. Re-render to fill it in.

---

## Android Emulator Options

*Pending.* Agent had not reported when this file was written. Re-render to fill it in.

---

## Emulator Capture and Input Path

*Pending.* Agent had not reported when this file was written. Re-render to fill it in.

---

## Hardware Budget and Frame Budget

*Pending.* Agent had not reported when this file was written. Re-render to fill it in.

---

## Computer Vision Stack

<sub>2 report(s) &middot; 39 verified, 12 likely &middot; 33 pitfalls &middot; 22 outdated patterns &middot; 86 sources</sub>

### Facts

- **VERIFIED** OpenCV 5.0 shipped in June 2026 and `pip install opencv-python` now resolves to 5.0.0.93 by default, not 4.x.
  - PyPI history: opencv-python 5.0.0.93 released 2026-07-02; the 4.x line is still maintained in parallel (4.14.0.94 on 2026-07-28, 4.13.0.92 on 2026-02-05). Because 5.0.0.93 sorts higher, an unpinned install gets OpenCV 5. For a curriculum, pin explicitly: `opencv-python==4.14.0.94` if you want every StackOverflow answer from 2018-2025 to apply verbatim, or `==5.0.0.93` to be current. Do not leave it unpinned — the learner and the author will silently be on different majors.
- **VERIFIED** The OpenCV 4→5 Python surface is nearly unchanged; the real breakage is in cv2.dnn and VideoCapture.get().
  - Official migration wiki: 'all functions remain accessible as cv2.<funcname>() regardless of which C++ module they now live in. No import changes are needed.' So cv2.matchTemplate, cv2.imread, cv2.cvtColor are identical. Breaking: readNetFromCaffe() and readNetFromDarknet() are REMOVED (convert to ONNX and use readNetFromONNX), and VideoCapture.get() now returns -1 for unsupported properties instead of 0 (test with `< 0`, not `== -1`). readNet() tries the new DNN engine first and falls back to classic; force with `engine=cv2.dnn.ENGINE_CLASSIC`. New engine covers >80% of ONNX ops vs ~22% in 4.x, but is CPU-only at launch.
- **VERIFIED** There are four mutually exclusive opencv-python packages and installing two of them breaks cv2 silently.
  - opencv-python, opencv-contrib-python, opencv-python-headless, opencv-contrib-contrib-headless. Repo says: 'you should SELECT ONLY ONE OF THEM... There is no plugin architecture: all the packages use the same namespace (cv2).' For this project the base `opencv-python` is correct — you need cv2.imshow for debugging, and contrib only adds aruco/xfeatures2d/tracking/ximgproc which you will not use. Note: in OpenCV 5 the G-API and classic `ml` modules moved OUT of core into contrib.
- **VERIFIED** dxcam is measurably ~3x faster than mss on Windows: 239.19 FPS vs 75.87 FPS in the maintainer's own benchmark.
  - DXcam README benchmark (240fps target, newly-rendered frames only): DXcam 239.19 FPS (σ 1.25), D3DShot 118.36 (σ 0.32), python-mss 75.87 (σ 0.54). At fixed targets DXcam holds 61.71 FPS (σ 0.26) at 60fps target and 30.08 (σ 0.02) at 30fps. dxcam 0.3.0 released 2026-03-12, MIT, requires Python >=3.10 — it is alive again after years of being stale at 0.0.5.
- **VERIFIED** windows-capture 2.0.1 is the only one of the three that captures a specific window by name AND keeps working when that window is occluded.
  - windows-capture 2.0.1 released 2026-08-08, MIT, Python >=3.9, deps numpy + opencv-python. Python API: `WindowsCapture(cursor_capture=None, draw_border=None, monitor_index=None, window_name=None)` — event/callback based, delivers numpy frames. Backed by Windows.Graphics.Capture (WGC) with an optional DXGI Desktop Duplication path. OBS's own docs state WGC 'captures occluded or moved windows accurately' whereas 'BitBlt sometimes fails with occluded windows.' This is the correct choice for an emulator window you want to leave in the background.
- **VERIFIED** The WGC yellow capture border can only be turned off on Windows 11, and requires an explicit consent prompt.
  - GraphicsCaptureSession.IsBorderRequired was introduced in Windows 10 build 10.0.20348.0 (i.e. Win11-era only). To use it the app must call GraphicsCaptureAccess.RequestAccessAsync with GraphicsCaptureAccessKind.Borderless and declare the `graphicsCaptureWithoutBorder` capability. Also: if any other app on the machine sets IsBorderRequired=true for the same window, the border comes back. On Windows 11 Home this is fine; just expect a yellow rectangle by default and don't let it contaminate your crops near the window edge.
- **VERIFIED** Desktop Duplication (dxcam) only hands you a frame when the screen content actually changed — an idle screen looks like a hung capture loop.
  - Documented behavior of the underlying API: 'The Windows Desktop Duplication API will only return new texture data if the contents of the screen has changed.' dxcam's `.grab()` returns None in that case. Your capture loop must handle None by reusing the previous frame, or your FPS counter and your state machine will both lie to you. This is a feature (free change-detection) but it is the #1 confusing first-hour bug.
- **VERIFIED** scrcpy v4.1 claims 35–70 ms end-to-end latency and is the right tool only if you use a physical phone rather than an emulator.
  - scrcpy README v4.1 (released ~2026-07-12): stated latency '35~70ms'. Relevant flags for a capture pipeline: `--max-fps=60`, `--max-size=1920` ('may greatly improve performance'), `--no-audio`, `--video-codec=h265`, `-b16M`. It requires ADB and no root. Recent versions also added VP8/VP9 encoders and `--flex-display`.
- **VERIFIED** Ultralytics 8.4.121 is AGPL-3.0 and Ultralytics interprets that to cover private, internal, non-distributed use — including weights you fine-tuned yourself.
  - Latest ultralytics on PyPI: 8.4.121, released 2026-08-17. Their own license page states you must either 'Open-source your entire project under AGPL-3.0' or buy Enterprise, and that this 'applies regardless of whether you train from scratch, use it internally, or deploy privately.' Compliance means 'publicly releasing the complete corresponding source code for the entire derivative work, including the larger application, modifications, scripts, configuration files, and, where applicable, model weights.' Enterprise triggers they list explicitly include 'Custom models – fine-tuned versions in commercial settings' and 'Undisclosed R&D – projects not fully open-sourced.' For a personal learning project on a public GitHub repo under AGPL-3.0: fine. For a private repo, a closed portfolio piece, a Discord bot others use, or anything you later monetize: not fine.
- **VERIFIED** YOLO26n is 40.9 mAP50-95 at 640px and 38.9 ± 0.7 ms/image on CPU via ONNX Runtime — a 43% CPU speedup over YOLO11n's 56.1 ms.
  - Ultralytics YOLO26 docs table: YOLO26n 640px / 40.9 mAP / 38.9±0.7 ms CPU ONNX / 2.4M params / 5.4 GFLOPs. YOLO26s 48.6 mAP / 87.2±0.9 ms / 9.5M / 20.7B. YOLO26m 53.1 / 220.0 ms. Benchmark CPU is an Intel Xeon @ 2.00 GHz. YOLO26 (released Jan 2026) is natively end-to-end: NMS-free by default and DFL-free regression, which is exactly why the CPU number improved. Budget expectation for a Ryzen 3 7320U (4C/8T Zen 2, 2.4/4.1 GHz): same ballpark or somewhat worse than the Xeon figure — call it ~40–70 ms/frame for the nano model in plain ONNX, i.e. 15–25 FPS, before any OpenVINO work.
- **VERIFIED** OpenVINO FP32 export is the single biggest CPU win available: YOLO26n goes 29.28 ms → 4.09 ms/image, ~7x.
  - Ultralytics OpenVINO integration benchmarks on Intel Core Ultra X7 358H: YOLO26n PyTorch-CPU 29.28 ms → OpenVINO FP32 4.09 ms (7.2x); YOLO26s 59.32 → 5.08 ms (11.7x); YOLO26m 143.21 → 7.10 ms (20x). Export is one line: `model.export(format="openvino")`. INT8 PTQ: `model.export(format="openvino", quantize=8, data="coco8.yaml")` — requires calibration data. Ultralytics' own conservative doc text says 'up to 3x CPU speedup'; the measured table exceeds that on Intel silicon.
- **VERIFIED** Those OpenVINO numbers will NOT transfer cleanly to a Ryzen 3 7320U — AMD CPUs are not validated by Intel and the 7320U lacks AVX-512 and VNNI.
  - OpenVINO 2026.3.0 (Apache-2.0, Python 3.10–3.14). Intel's support article 'Unable to Run OpenVINO Inference on AMD Ryzen CPU' states AMD platforms are not validated; running there is 'not recommended' though users report it working. Ryzen 3 7320U is Mendocino: 4 Zen 2 cores / 8 threads, 4 MB L3, base 2.4 GHz boost 4.1 GHz, AVX2 yes, AVX-512 no, therefore no AVX-512-VNNI. Consequence for INT8: ONNX Runtime docs warn that x86-64 without VNNI 'may experience saturation issues' and prescribe `reduce_range=True` (quantize weights to 7 bits) — and warn 'it is not rare to get worse performance on old devices.' Expect INT8 on this laptop to buy memory/model size, not necessarily latency. Measure, don't assume.
- **VERIFIED** ONNX Runtime 1.28.0 now requires Python >= 3.11.
  - PyPI metadata for onnxruntime 1.28.0: `requires_python: ">=3.11"`, MIT license. This is a real trap because torch 2.13.0 requires >=3.10 and supervision requires >=3.10 — so a 3.10 venv installs torch and supervision fine and then fails on onnxruntime with a confusing resolver error. Standardize the curriculum on Python 3.12.
- **VERIFIED** torchvision's own detectors are BSD-licensed and free of the AGPL problem, but they are markedly weaker: ssdlite320_mobilenet_v3_large is 21.3 box mAP vs YOLO26n's 40.9.
  - torchvision 0.28.0 detection zoo (COCO box mAP): ssdlite320_mobilenet_v3_large 21.3 (3.4M params), fasterrcnn_mobilenet_v3_large_320_fpn 22.8 (19.4M), fasterrcnn_mobilenet_v3_large_fpn 32.8 (19.4M), fcos_resnet50_fpn 39.2 (32.3M), retinanet_resnet50_fpn_v2 41.5 (38.2M). Docs flag the detection module as 'Beta stage' with no backward-compat guarantee. Caveat that matters: COCO mAP is a proxy for 80 messy natural classes — on a fixed-camera, fixed-palette game screen with 10-30 sprite classes, even ssdlite320 fine-tuned can be adequate. The gap on YOUR data is much smaller than the COCO gap suggests.
- **VERIFIED** supervision's built-in sv.ByteTrack is DEPRECATED and gets deleted in 0.31.0 — tracking has moved to a separate Apache-2.0 `trackers` package with a different method name.
  - supervision 0.30.0 released 2026-08-04. Docs: 'ByteTrack is deprecated since supervision-0.28.0 and will be removed in supervision-0.31.0.' Migration: `pip install trackers`, use `ByteTrackTracker`, and the update call renames from `update_with_detections(detections)` to `update(...)`. The old constructor args were track_activation_threshold=0.25, lost_track_buffer=30, minimum_matching_threshold=0.8, frame_rate=30, minimum_consecutive_frames=1. Any tutorial written before ~mid-2025 uses the dead API.
- **VERIFIED** The `trackers` package (2.6.0, 2026-08-06, Apache-2.0) gives you SORT, ByteTrack, OC-SORT, BoT-SORT, C-BIoU and McByte as clean-room reimplementations decoupled from any detector.
  - trackers 2.6.0, Python >=3.10, deps numpy>=2.0.2, supervision>=0.26.1, scipy, opencv-python. Being detector-agnostic is the point: you can pair it with a torchvision or D-FINE detector and never touch AGPL code. Contrast with Ultralytics, which ships its own trackers (botsort.yaml default, plus bytetrack.yaml, ocsort.yaml, deepocsort.yaml, fasttrack.yaml, tracktrack.yaml) behind `model.track(source, persist=True, tracker="bytetrack.yaml")` — convenient, but AGPL.
- **VERIFIED** On MOT17, upgrading SORT → ByteTrack buys almost nothing (60.4 → 60.5 HOTA); BoT-SORT's gain comes from camera-motion compensation you do not have.
  - Roboflow trackers benchmark, MOT17 with tuned parameters, HOTA/IDF1/MOTA: SORT 60.4/72.5/75.8; ByteTrack 60.5/72.7/76.1; OC-SORT 62.0/76.5/77.3; BoT-SORT 63.8/78.7/79.4; C-BIoU 63.0/79.1/77.4. Their own guidance: SORT 'when speed is the primary constraint', ByteTrack is the 'default recommendation', BoT-SORT 'when camera ego-motion is strong'. A game screen has a FIXED camera — so BoT-SORT's GMC (sparseOptFlow by default) is pure wasted CPU. Start at SORT, and only move to ByteTrack because it recovers low-confidence detections (which is your real problem: half-occluded sprites).
- **VERIFIED** cv2.matchTemplate offers 6 metrics; TM_CCOEFF_NORMED plus np.where thresholding is the multi-instance recipe, and it is scale- and rotation-sensitive by construction.
  - Methods: TM_SQDIFF, TM_SQDIFF_NORMED (minimum = best match), TM_CCORR, TM_CCORR_NORMED, TM_CCOEFF, TM_CCOEFF_NORMED (maximum = best). Single best match via cv2.minMaxLoc(); multiple instances by thresholding the response map (e.g. 0.8) and np.where(). The docs describe pure spatial sliding comparison with no transformation handling — so a resized emulator window, a UI scale change, or a sprite rendered at a different zoom silently drops your match score below threshold. Mitigation for the curriculum: normalize the capture to a canonical resolution once (locate the window, warp/resize to a fixed 1280x720 canvas), then all templates and all fixed-position crops become valid again. That single normalization step is what makes classical CV viable at all here.
- **VERIFIED** CVAT is MIT-licensed, exports both YOLO txt and COCO JSON among 20+ formats, and supports model-assisted pre-labeling — but its self-host is a multi-container Docker Compose stack.
  - CVAT Community is MIT. Docs: 'move data in and out using 20+ industry-standard formats' explicitly including 'YOLO (TXT)' and 'COCO (JSON)'; AI-powered annotation lets you 'Connect your own ML models for detection, segmentation, and tracking'. Prerequisites are Docker Engine + Docker Compose + Git; on Windows that means Docker Desktop over WSL2. No official minimum RAM is published, but the stack is server + db + redis + opa + ui + (optional serverless/nuclio for auto-annotation) — on 8 GB total, with WSL2 itself taking a cut, this is the heaviest of the three options and the serverless auto-annotation tier is realistically out of reach.
- **VERIFIED** Label Studio 1.23.0 states a minimum of 8 GB RAM with 16 GB recommended — i.e. this laptop is exactly at the documented floor.
  - Label Studio 1.23.0, Apache-2.0, requires_python >=3.10,<4. Install requirements page: minimum 8 GB RAM, 16 GB recommended, 50 GB disk for production; PostgreSQL 13+ or SQLite 3.35+. It runs as a single pip install with SQLite, which is dramatically lighter than CVAT's compose stack. Pre-labeling: HumanSignal ships an official YOLO ML backend (Simple mode = pretrained COCO classes, Trainable mode = few-shot on your submitted labels); you set `model_path="yolo26n.pt"` on the RectangleLabels tag and register http://localhost:9090 as the ML backend. Recommendation for 8 GB: Label Studio with SQLite, not CVAT.
- **VERIFIED** mss 10.2.0 (released 2026-04-23) is MIT, pure-Python-ctypes, and its Windows backend is 100% GDI — the module is literally src/mss/windows/gdi.py.
  - PyPI confirms 10.2.0 / 2026-04-23 / MIT / 'ultra fast cross-platform multiple screenshots module in pure python using ctypes'. The GitHub contents API shows src/mss/windows/ contains exactly two files: __init__.py and gdi.py. gdi.py calls GetWindowDC, CreateCompatibleDC, CreateDIBSection, SelectObject, BitBlt, GdiFlush, EnumDisplayMonitors, GetMonitorInfoW, EnumDisplayDevicesW, SetProcessDpiAwareness. There is no DXGI / Desktop Duplication code anywhere in the package. Blog posts claiming 'modern mss leverages DXGI' are wrong.
- **VERIFIED** CORRECTION to the source claim: mss 10.x no longer calls GetDIBits, and the famous 'ScreenShotError: gdi32.GetDIBits() failed' string no longer exists in the codebase.
  - Current gdi.py uses CreateDIBSection (which hands you a directly-addressable buffer) instead of the older BitBlt+GetDIBits pair, and the error strings were genericised to 'Windows graphics function returned failure: {func.__name__}' / 'Windows graphics function failed: {func.__name__}: {winerror.strerror}'. The GetDIBits failure reports (issues #59, #83, #135, #198, #209, #212, #267) are all against mss <=9.x. Practical effect for a curriculum: if you google that error you will land on advice for a code path that no longer exists; the underlying GDI fragility (thread-safety, long capture loops) is still real.
- **VERIFIED** mss cannot capture a window that is covered by another window; the feature request has been open for six years.
  - GitHub API on BoboTiG/python-mss issue #180: title 'Allow for capturing obscured windows', state OPEN, created_at 2020-08-13T15:55:36Z, closed_at null, filed by BanditTech referencing GetDCEx. mss grabs a screen-coordinate bbox off the desktop DC, so anything visually on top of the emulator lands in your frame. Fine for a Lesson-1 capture loop; not the endgame.
- **VERIFIED** torch 2.13.0 was released 2026-07-08 and requires Python >=3.10.
  - PyPI project page for torch: latest 2.13.0, 2026-07-08, Requires-Python >=3.10.
- **VERIFIED** torchvision 0.28.0 (2026-07-08, BSD) is the correct pin for torch 2.13.0 — but the PyPI page's own compatibility prose is misleading.
  - PyPI: torchvision 0.28.0, released 2026-07-08, BSD, Requires-Python >=3.10 with an explicit !=3.14.1 exclusion; wheels for cp310-cp314 on Windows x86-64. The pytorch/vision README compatibility matrix maps torch 2.13 -> torchvision 0.28 (>=3.10, <=3.14), and the official previous-versions page corroborates the off-by-one pattern with 'pip install torch==2.12.1 torchvision==0.27.1'. Reading the PyPI blurb alone can leave you pinning 2.12.
- **VERIFIED** The CPU-only install form is `--index-url https://download.pytorch.org/whl/cpu`, and this is what PyTorch's own docs print.
  - pytorch.org/get-started/previous-versions shows CPU-only Windows commands verbatim in the form `pip install torch==2.12.1 torchvision==0.27.1 --index-url https://download.pytorch.org/whl/cpu`. The `--index-url` vs `--extra-index-url` distinction is the load-bearing part for an 8 GB laptop: --extra-index-url leaves PyPI in the resolver's search set, so pip can still pick the multi-GB CUDA build. Note the wheel index (download.pytorch.org/whl/cpu/torch/) is a very large flat HTML listing — do not try to eyeball it to confirm a wheel exists; use pip's own resolution.
- **VERIFIED** torch.compile's Inductor CPU backend works on Windows from PyTorch 2.5, requires a C++ compiler, and MSVC must be installed even if you intend to use clang-cl or icx-cl.
  - Official tutorial 'How to use torch.compile on Windows CPU/XPU' (docs.pytorch.org/tutorials/unstable/inductor_windows.html — note it moved from /prototype/ to /unstable/): 'C++ compiler is required for TorchInductor optimization'; PyTorch 2.5+ for CPU, 2.7+ for XPU; supported compilers MSVC (cl, default), LLVM (clang-cl, `set CXX=clang-cl`), Intel (icx-cl, `set CXX=icx-cl`); the alternative compilers still depend on MSVC runtime libraries, so Visual Studio Build Tools is a hard prerequisite either way. Curriculum read: multi-GB toolchain plus per-shape compile pauses for a payoff OpenVINO/ONNX Runtime deliver more cheaply. Skip it for inference.
- **VERIFIED** Ultralytics 8.4.121 (2026-08-17) is AGPL-3.0-or-later (dual-licensed with a paid Enterprise license), and RT-DETR ships inside that package — so `from ultralytics import RTDETR` is AGPL code regardless of the architecture's origin.
  - PyPI ultralytics: latest 8.4.121, 2026-08-17, 'GNU Affero General Public License v3 or later (AGPLv3+)', with an Ultralytics Enterprise License offered explicitly to bypass 'the open-source requirements of AGPL-3.0'. RT-DETR is listed among supported models in the package's own classifiers/tags. The license follows the implementation you import, not the architecture.
- **VERIFIED** Upstream lyuwenyu/RT-DETR is Apache-2.0 and was accepted to CVPR 2024 — confirming the license split with Ultralytics' reimplementation.
  - github.com/lyuwenyu/RT-DETR: Apache-2.0 badge, README states 'Our work has been accepted to CVPR 2024!'. Teaching point stands: 'is this model permissive?' is the wrong question; 'which codebase am I importing?' is the right one.
- **VERIFIED** rfdetr 1.9.3 (released 2026-08-17, Python >=3.10) is Apache-2.0 for the base package, while rfdetr_plus and the RF-DETR-XL / 2XL models are PML 1.0.
  - PyPI rfdetr 1.9.3: 'Plus components, including the rfdetr_plus extension and RF-DETR-XL / RF-DETR-2XL detection models, are licensed under PML 1.0'; core Apache-2.0. Accepted to ICLR 2026, arXiv 2511.09554. Export paths: ONNX, TensorRT, TFLite, CoreML; integrates with supervision.
- **VERIFIED** CORRECTION: the RF-DETR parameter counts are Nano 30.5M / Small 32.1M / Medium 33.7M / Large 33.9M / XL 126.4M / 2XL 126.9M — the source claim gave 126.9M for XL, which is the 2XL figure.
  - Full ladder from the rfdetr PyPI page. The important curriculum fact survives: even 'Nano' is 30.5M params, ~13x YOLO26n's 2.4M, and the family barely scales down. Benchmarks on the page are NVIDIA T4 latency (Medium: 54.7 AP50:95 / 73.6 AP50 at 4.4 ms on T4) — nothing CPU. On a 4-core Zen 2 laptop treat RF-DETR as a 'train it, run it offline to auto-label' tool, not a real-time option. The '2XL = 60.1 AP, first real-time model past 60 AP' sub-claim was not stated on the page I fetched; treat that specific number as unconfirmed.
- **VERIFIED** For the size contrast: YOLO26n is 2.4M params / 40.9 mAP at 640px, and YOLO26 is AGPL-3.0-or-Enterprise like the rest of Ultralytics.
  - docs.ultralytics.com/models/yolo26/ — five scales n/s/m/l/x, nano at 2.4M params and 40.9 mAP on COCO detection at 640; 'YOLO26 code, models, and documentation' offered under AGPL-3.0 and Enterprise. This is the apples-to-apples number that makes the RF-DETR weight class visible.
- **VERIFIED** D-FINE is genuinely first-class in HuggingFace transformers (DFineConfig / DFineModel / DFineForObjectDetection), and both code and published weights are Apache-2.0.
  - transformers model doc `d_fine` documents DFineForObjectDetection with AutoImageProcessor; canonical checkpoints are `ustc-community/dfine_x_coco`, `ustc-community/dfine-xlarge-coco`, `ustc-community/dfine-small-coco`. The small-coco model card lists license apache-2.0 and ~10.4M params; dfine_x_coco likewise apache-2.0. Upstream github.com/Peterande/D-FINE is Apache-2.0. Caveat found while checking: one code sample in the docs still references a non-canonical `PekingU/DFine_r50vd` id — use the ustc-community ids. Best 'permissive DETR you can pip install and fine-tune' in 2026, and at ~10.4M params the small model is far more laptop-viable than RF-DETR-Nano.
- **VERIFIED** Tesseract 5.5.3 was published 2026-07-24.
  - GitHub API /repos/tesseract-ocr/tesseract/releases/latest returns tag_name 5.5.3, published_at 2026-07-24T18:33:22Z. (Rendering the HTML releases page can mis-read the year as 2024 — the API is the source to trust.)
- **VERIFIED** PaddleOCR 3.7.0 (2026-06-11, Apache-2.0) ships PP-OCRv6 in tiny 1.5M / small 7.7M / medium 34.5M parameter tiers, with a claimed 5.2x CPU speedup via OpenVINO.
  - PyPI paddleocr 3.7.0: PP-OCRv6 single unified model covering Chinese, English, Japanese and 46 Latin-script languages; medium tier +4.6% detection / +5.1% recognition over PP-OCRv5_server; '5.2x CPU speedup (OpenVINO), 6.1x on Apple M4 (tiny), 0.13s on A100 GPU'. CORRECTION: the source claim's '~9.6 MB mobile rec model, ~0.78 s/image on a Xeon 8350C with OpenVINO' is PP-OCRv5-era marketing and does not appear on the current page — do not quote it.
- **VERIFIED** EasyOCR's last release is 1.7.2 on 2024-09-24 — nearly two years stale as of 2026-08.
  - PyPI easyocr: latest 1.7.2, 2024-09-24. Its execution is entirely PyTorch-based and the install notes tell Windows users to install torch+torchvision first, i.e. it drags a full DL stack in for what is a 10-class problem in this curriculum. Effectively unmaintained; do not build a lesson on it.
- **VERIFIED** CORRECTION: Roboflow's free Public Plan gives 15 credits/month and 2 users — not '~$60/month in credits'.
  - roboflow.com/pricing, Public tier: '15 credits / month', '2 users', 10 projects, 250,000 image workspace dataset cap, 3x image augmentations, no credit card; 'Data and models are open source on Roboflow Universe'. Extra prepaid credits start at $4 with 8-20% bulk discounts. The '$60/month in credits' and '$6/credit' figures circulating in secondary reporting do not match the live pricing page — drop them.
- **VERIFIED** The rest of the Roboflow Public Plan wording checks out verbatim in the official docs.
  - docs.roboflow.com/platform/billing-and-plans/plans: 'All of your datasets and models listed publicly on Universe', 'Credits that refresh every month', 'Support from our Community Forum', and 'Each user can only create one workspace with a Public Plan.' Tradeoff to surface to a learner: lowest-friction annotate + auto-label + YOLO/COCO export path at zero cost, but you are open-sourcing your dataset — and for screenshots of a commercial game that is also a ToS question.
- **VERIFIED** 'Cut, Paste and Learn: Surprisingly Easy Synthesis for Instance Detection' is arXiv 1708.01642, published at ICCV 2017, and reports >21% relative improvement when synthetic data is combined with real images.
  - arXiv 1708.01642 (Dwibedi, Misra, Hebert); ICCV 2017 open-access proceedings copy at openaccess.thecvf.com/content_ICCV_2017/papers/Dwibedi_Cut_Paste_and_ICCV_2017_paper.pdf. The paper's own framing is that patch-level realism suffices, and that boundary artifacts must be defeated by synthesizing the same scene with multiple blending modes. CORRECTION to the source claim's framing: the '~15% recovery' figure was not locatable; the paper's own headline number is >21% relative improvement from synthetic + real.
- *likely* mss uses GDI BitBlt/GetDIBits, not DXGI — and it cannot capture a window that is covered by another window.
  - mss 10.2.0 (2026-04-23), MIT, 'pure python using ctypes'. Its Windows path calls gdi32 (the tracked bug 'ScreenShotError: gdi32.GetDIBits() failed' confirms the GDI path). Issue #180 'Allow for capturing obscured windows' has been OPEN since 2020 with no maintainer fix. Blog posts claiming 'modern mss leverages DXGI' are wrong. mss grabs a screen-coordinate bbox, so whatever is visually on top of the emulator ends up in your frame. Good enough for a Lesson-1 capture loop; not the endgame.
- *likely* For an Android emulator on the same laptop, screen-capturing the emulator window beats ADB by roughly an order of magnitude, and ADB screencap is unusable for real-time.
  - Measured comparison from an Android automation MCP server: `adb exec-out screencap -p` costs 500–1500 ms/frame (PNG encode on device + decode on host); scrcpy single-frame ~100–300 ms; polling a running scrcpy H.264 stream <50 ms/frame. Since an emulator already renders into a Win32 window on your desktop, windows-capture/dxcam against that window skips the whole device-transport problem — no ADB, no H.264 decode, no scrcpy dependency. Use ADB only for input injection (`adb shell input tap`) and for ground-truth queries, never for the frame loop.
- *likely* Ultralytics' RTDETR class is AGPL-3.0 even though upstream RT-DETR is Apache-2.0 — the license follows the implementation, not the architecture.
  - lyuwenyu/RT-DETR (the original Baidu release, CVPR 2024) ships under Apache-2.0. But `from ultralytics import RTDETR` pulls the Ultralytics repo, which is AGPL-3.0 in its entirety. Teaching point for the curriculum: 'is this model permissive?' is the wrong question; 'which codebase am I importing?' is the right one.
- *likely* PyTorch 2.13.0 (2026-07-08) requires Python >=3.10; the CPU-only Windows wheel comes from a separate index URL.
  - Version and requires_python verified on PyPI (torch 2.13.0, 2026-07-08; 2.12.1 2026-06-17; 2.11.0 2026-03-23). Install form: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`. Use `--index-url`, not `--extra-index-url` — with extra-index pip can still resolve the ~2.5 GB CUDA wheel from PyPI, which on an 8 GB/limited-disk laptop is a genuinely painful mistake. torchvision 0.28.0 pairs with torch 2.13.0 and is BSD-licensed.
- *likely* torch.compile's Inductor CPU backend does work on Windows since PyTorch 2.5, but it requires a C++ compiler installed on the machine.
  - PyTorch ships an official tutorial 'How to use torch.compile on Windows CPU/XPU'. Supported compilers: MSVC (cl), clang-cl, and Intel icx-cl; PyTorch >= 2.5 required. Practical read for this curriculum: it means installing Visual Studio Build Tools (multi-GB) and eating a per-shape compile pause, for a payoff that OpenVINO/ONNX Runtime already deliver more cheaply. Skip torch.compile for inference; it is not the CPU lever you want.
- *likely* RF-DETR (rfdetr 1.9.3) is Apache-2.0 for the core models and is the strongest permissive recommendation — but its 'Plus'/XL tier is under a restrictive PML-1.0 license and its benchmarks are all NVIDIA T4/TensorRT.
  - rfdetr on PyPI: 1.9.3, Python >=3.10, deps torch>=2.2.0 + torchvision + supervision>=0.29.0; ONNX export via the `[onnx]` extra. Apache-2.0 for the base package; `rfdetr_plus` (RF-DETR-XL/2XL) is PML-1.0. Family spans Nano (30.5M params, 384x384 input) to 2XL (126.9M, 880x880). Paper accepted to ICLR 2026; first real-time model past 60 AP on COCO (2XL = 60.1). Note the Nano is 30.5M params — an order of magnitude heavier than YOLO26n's 2.4M. On a 4-core Zen 2 laptop this is not a real-time option; it's a 'train it, run it offline to auto-label' option.
- *likely* D-FINE is Apache-2.0 for both code and weights and is available directly in HuggingFace transformers.
  - D-FINE (USTC) reframes box regression as Fine-grained Distribution Refinement. Apache-2.0 code + weights; HF checkpoints under `ustc-community/dfine-*` (e.g. dfine-small-coco). Being in `transformers` means the training loop is standard and there is no bespoke repo to fight. This is the best 'permissive DETR you can actually pip install and fine-tune' option in 2026.
- *likely* General OCR is heavyweight for a HUD digit and the fixed-font template/tiny-CNN route is the correct answer; a Tesseract user reported ~30% accuracy on a fixed segment font even after training and whitelisting.
  - Current versions if you insist: Tesseract 5.5.3 (2026-07-24); PaddleOCR 3.7.0 (2026-06-11, Apache-2.0, PP-OCRv6, mobile rec model ~9.6 MB, ~0.78 s/image end-to-end pipeline on a Xeon 8350C with OpenVINO); EasyOCR 1.7.2 — last released 2024-09-24, effectively unmaintained and it drags in full torch+torchvision for what is a 10-class problem. Reported field experience on fixed segment/LCD fonts: template matching against a digit dictionary is 'often more reliable', while a Tesseract user got 'around 30% success at best' after font training with a character whitelist. Mechanically: general OCR spends its budget on text DETECTION and on a 6000+ character vocabulary. You already know where the digits are (fixed crop) and that there are exactly 10 of them. A 10-class 20x28 template bank or a ~50k-parameter CNN runs in microseconds and hits ~100% on a fixed font. Do the template bank FIRST, and only train the tiny CNN when anti-aliasing over a moving background breaks it — that is the moment the learner earns the CNN.
- *likely* Roboflow's free tier is the 'Public Plan' — one workspace per user, and every dataset and model is published publicly on Roboflow Universe.
  - Roboflow docs: Public Plan gives 'All of your datasets and models listed publicly on Universe', monthly refreshing credits (~$60/month in credits per secondary reporting), community-forum support, and 'Each user can only create one workspace with a Public Plan'. Exact credit rates are deliberately kept on the pricing page rather than the docs. The tradeoff to surface to a learner: it is the lowest-friction annotation + auto-label + YOLO/COCO export path and costs nothing, but you are open-sourcing your dataset. For screenshots of a commercial game, that may also be a ToS question worth thinking about.
- *likely* Cut-and-paste sprite compositing is a legitimate, published technique for generating labeled detection data for free — but random placement underperforms plain augmentation.
  - The canonical reference is 'Cut, Paste and Learn: Surprisingly Easy Synthesis for Instance Detection'. Key finding repeated across follow-up work: context matters — 'random Cut-Paste performs worse than using traditional data augmentation techniques, but contextual augmentation yields significant improvement', i.e. paste sprites only where they can legally appear (on the arena, on valid lanes, at valid scales). Sim2real studies report ~15% recovery from combining synthetic generation with basic procedures on real target-domain images. Your domain is unusually favorable: you have the EXACT sprite assets and the EXACT renderer, so there is no photometric domain gap in the classic sense — but see pitfalls for the four gaps that remain.
- *likely* The 'random placement is worse than plain augmentation, context matters' result traces to Dvornik et al.'s context-modeling work, not to Cut-Paste-and-Learn itself.
  - Multiple follow-up papers (e.g. Scene-Aware Location Modeling for Data Augmentation in Automotive Object Detection, arXiv 2504.17076; Context-Matched Collage Generation, arXiv 2211.08479) attribute to Dvornik et al. the experiment where segmented objects pasted at completely random positions not only failed to improve VOC'12 detection but degraded it, motivating a learned context model. I confirmed this attribution via multiple secondary sources but did not fetch Dvornik et al. directly, so: attribute the finding, don't quote a number. Actionable form for the curriculum: paste sprites only where they can legally appear (on the arena, on valid lanes, at valid scales).
- *likely* The ADB-vs-scrcpy frame timings (500-1500 ms for `adb exec-out screencap`, 100-300 ms scrcpy single frame, <50 ms scrcpy stream polling) come from one project's self-reported measurements, not an independent benchmark.
  - Traced to the jduartedj/android-mcp-server documentation (docs/SCRCPY_STREAMING.md, mirrored on deepwiki and glama.ai), which states ADB screencap 500-1500 ms/frame from on-device PNG encode plus host decode, scrcpy single-frame 100-300 ms via H.264 hardware encode, and <50 ms/frame polling a pre-buffered persistent stream. Corroborating direction of travel: Genymobile/scrcpy issue #3345 and the adbnativeblitz project both exist specifically because screencap is too slow for periodic capture. The order-of-magnitude conclusion is safe; the exact numbers are one vendor's. For an emulator on the same laptop the whole comparison is moot — the emulator already renders into a Win32 window, so desktop capture skips device transport entirely. Use ADB only for input injection and ground-truth queries.

### Pitfalls you will actually hit

- TRAIN/TEST LEAKAGE FROM CONSECUTIVE FRAMES — the big one, mechanically: you record a 3-minute match at 30 FPS, get 5400 frames, label 500 of them, and call `train_test_split(shuffle=True)`. Frame 1204 lands in train and frame 1205 lands in val. Those two images differ by ~33 ms: the same background, the same tower positions, the same units, moved by 2-3 pixels. Your val set is therefore a near-duplicate copy of your train set. The network memorizes the specific pixel layout of THAT match and val mAP climbs to 0.95 by frame two of training. Then you play a different match with a different arena skin and it detects nothing. The published framing: 'temporally adjacent frames may be assigned to different splits, placing near-duplicate samples in both training and validation sets, introducing spatiotemporal leakage where the model can achieve high validation performance by implicitly memorizing background structure rather than learning robust object-centric representations' (arXiv 2511.13944; see also IEEE 10485397). THE FIX IS NOT A BETTER SPLIT RATIO — it is that the unit of splitting must be the MATCH (or the recording session), never the frame. Hold out entire matches. Secondary defenses: sample frames at >=1 s intervals rather than every frame, and cluster frames by embedding similarity before splitting. If your val mAP is above ~0.9 on your first ever training run, you have this bug, not a good model.
- CLASS IMBALANCE — in a game screen the tower is in literally every frame and a rare unit appears in maybe 2% of them. Gradient descent 'performs well on majority classes, but poorly on minority classes.' Your mAP looks great because the common classes dominate the average, while the class you actually need for a decision is at 0.2 recall. Count instances per class BEFORE training and print the table; if the rarest class has fewer than ~100 instances, no amount of epochs will save it — you need targeted collection or synthetic compositing for that class specifically.
- TINY OBJECTS — an elixir drop or a small unit might be 12x12 px in a 1280x720 frame. After a detector's stride-32 downsample that is smaller than one output cell. Symptoms: the class trains to near-zero recall while everything else works fine, and the loss looks healthy. Fixes in order of effort: (a) don't detect it at all, use a fixed-position crop + template match; (b) run the detector on a cropped region of interest at native resolution instead of downscaling the whole frame; (c) raise imgsz to 960/1280, which costs you 2-4x the CPU time you don't have. Note that Ultralytics specifically cites STAL in YOLO26 as improving 'small-object label coverage' — that is an acknowledgment that this is the standard failure.
- MOTION BLUR AND FRAME TEARING — screen capture is not synchronized to the emulator's render loop. dxcam/Desktop Duplication hands you the composited desktop whenever it changes, so you can capture mid-frame and get a torn image, or capture during a fast projectile and get a smeared sprite that matches no template. Symptom: intermittent single-frame detection dropouts with no pattern. Mitigations: cap the emulator to a fixed FPS, capture at or below that rate, and make your state machine tolerant of one-frame gaps (this is precisely what a tracker buys you).
- OVERLAPPING SPRITES AND NMS — units stack on top of each other during a push. A classical NMS pass with IoU 0.45 will delete the second of two heavily overlapping same-class boxes, so a 3-unit clump reports as 1 unit. Template matching has the mirror-image failure: np.where thresholding returns 40 near-identical hits for one sprite and you need your own clustering/NMS on top. YOLO26's NMS-free end-to-end head sidesteps the tuning problem but not the underlying ambiguity. Test this deliberately with a screenshot of a stacked group; do not discover it in a live run.
- SILENT AGPL EXPOSURE — the failure mode is not a lawsuit, it is discovering at the end that your finished portfolio project cannot go in a private repo or on a resume-linked closed demo without either open-sourcing everything (including your fine-tuned .pt) or paying Ultralytics. Decide the license posture in week one, not week twelve.
- INSTALLING THE CUDA TORCH WHEEL BY ACCIDENT — `pip install torch` with no index-url, or with `--extra-index-url` instead of `--index-url`, pulls a ~2.5 GB CUDA build onto a machine with no NVIDIA GPU. On 8 GB RAM with a small SSD this is a real problem, and torch will still import and run on CPU, so nothing errors — you just silently lose disk and get no benefit. Verify with `torch.__version__` ending in `+cpu`.
- PYTHON VERSION RESOLVER DEADLOCK — onnxruntime 1.28.0 now needs >=3.11 while plenty of tutorials assume 3.10. Pick Python 3.12 and never think about it again.
- INT8 QUANTIZATION MAKING THINGS SLOWER — Zen 2 (Ryzen 3 7320U) has AVX2 but no AVX-512 and no VNNI. ONNX Runtime's own docs warn 'quantization has overhead (from quantizing and dequantizing), so it is not rare to get worse performance on old devices', and prescribe reduce_range (7-bit weights) on non-VNNI x86-64 to avoid saturation. Benchmark FP32 vs INT8 on YOUR machine before believing any speedup claim; the expected win here is model size, not latency.
- COPYING OPENVINO BENCHMARKS ONTO AN AMD CPU — the 7x/11x/20x numbers are from an Intel Core Ultra X7 358H. Intel does not validate OpenVINO on AMD Ryzen and explicitly says running there is not recommended. It generally works, but assume a fraction of the published gain and measure. If OpenVINO misbehaves, ONNX Runtime's default CPU EP is the vendor-neutral fallback.
- CAPTURING THE WRONG PIXELS — mss grabs a screen-coordinate box, so a notification toast, the Windows taskbar, or a second window on top ends up inside your 'game frame' and your fixed-position crops shift the moment the emulator window moves or the user changes DPI scaling. Always locate the emulator window handle, normalize to a canonical resolution, and assert on a known invariant pixel (a HUD corner) every N frames.
- COLOR SPACE AND CHANNEL ORDER — capture libraries hand back BGRA or RGB depending on the library, OpenCV expects BGR, PyTorch expects RGB CHW float. A silent R/B swap produces a model that trains fine and then fails at inference, or template matches that are subtly worse than they should be. Print the array shape, dtype and a known-color pixel once, at the boundary of every library.
- TEMPLATE MATCHING DYING ON A WINDOW RESIZE — matchTemplate has zero scale invariance. Everything works, the learner resizes the emulator window, and 100% of matches drop to zero with no error. This is not a reason to abandon classical CV; it is the reason the normalization step exists.
- TRAINING ON THIS LAPTOP — 4 Zen 2 cores and 8 GB RAM is enough to fine-tune YOLO26n on a few hundred 640px images overnight, but only with batch small (4-8), workers=0 or 2 (Windows spawns dataloader workers as full processes, and 8 workers will OOM an 8 GB machine), cache=False, and the browser closed. Budget hours, not minutes. Google Colab's free tier is the sane place to do the actual training runs; keep the laptop for capture, labeling, and inference.
- GENERAL OCR ON A 14-PIXEL-TALL DIGIT — Tesseract's line-based engine expects text with margins and consistent baselines. Feed it a 2-character elixir counter drawn in a stylized font over a translucent gradient and you get empty strings, '1' read as 'l', '0' as 'O', and nondeterminism between frames. If you must use it, at minimum upscale 3-4x, binarize, add padding, and set --psm 7/8 or 10 with a digit whitelist — but the honest answer is that you should not be using it for this.
- SYNTHETIC DATA THAT ONLY TEACHES THE COMPOSITOR — four concrete gaps when you paste known sprite assets onto captured backgrounds: (1) alpha-edge artifacts — your PNG cutout has a hard or halo'd edge that the real renderer never produces, and the network learns 'find the halo' rather than 'find the unit'; (2) missing render effects — real frames have drop shadows, team-color tints, health-bar overlays, particle effects and selection glows that your bare sprite lacks; (3) implausible placement — pasting uniformly at random teaches wrong scale/position priors, which is exactly why the literature finds random cut-paste underperforms plain augmentation; (4) missing compression/scaling artifacts — real frames went through the emulator's scaler and your capture path. Fixes: composite with a feathered alpha, re-apply the same downscale the real pipeline uses, restrict paste locations and scales to a mask of legal arena positions, and always mix in real labeled frames — synthetic-only is a demo, synthetic-plus-real is a dataset.
- mAP HIDING THE ONE CLASS THAT MATTERS — mAP averages per-class AP and then averages over IoU thresholds, so it is 'difficult to interpret to gauge the practical usability of a detector in terms of how likely it is to miss objects'. For a game agent, a missed enemy unit is a lost match; a slightly loose bounding box costs nothing. The metric you should print every epoch is PER-CLASS RECALL AT YOUR OPERATING CONFIDENCE THRESHOLD, plus false-positives-per-frame. A model at 0.55 mAP with 0.98 recall on every class beats a model at 0.70 mAP that drops the rare unit 40% of the time. Also: your IoU requirement is application-defined — if you only need a click target, IoU 0.3 is fine and grading yourself at 0.5:0.95 is self-flagellation.
- FORGETTING THAT TRACKING IS ALSO A FILTER — the pitch for a tracker is usually ID persistence, but on a fixed-camera game screen the bigger win is that it lets you lower your detection confidence threshold safely. A tracklet confirmed over 3 consecutive frames (minimum_consecutive_frames) turns flickery 0.3-confidence detections into stable objects, and a Kalman prediction carries an occluded unit through 30 lost frames (lost_track_buffer). It also gives you velocity for free, which per-frame detection cannot. The cost is that a single ID switch corrupts downstream state, so log ID switches as a first-class metric.
- Googling 'mss gdi32.GetDIBits() failed' lands you on advice for mss <=9.x — that code path was replaced by CreateDIBSection in 10.x and the error string is now the generic 'Windows graphics function returned failure: <func>'. Match the fix to your installed version before you copy a workaround.
- mss will happily hand you a frame containing whatever notification toast, tooltip, or overlay is sitting on top of the emulator, with no error and no warning. Your capture loop looks healthy and your detector silently degrades. Issue #180 has been open since Aug 2020; there is no maintainer fix coming.
- Using `--extra-index-url` instead of `--index-url` for the CPU wheels leaves PyPI in pip's resolver set, so it can still pull the multi-GB CUDA torch build. On an 8 GB / limited-disk laptop you will find out only after the download completes.
- torchvision's own PyPI blurb can read as though 0.28.0 pairs with torch 2.12. The pytorch/vision README matrix says torch 2.13 -> torchvision 0.28, and previous-versions corroborates with 2.12.1 -> 0.27.1. Trust the matrix, not the blurb.
- Choosing clang-cl or icx-cl to avoid installing Visual Studio does not work: PyTorch's Windows Inductor tutorial states the alternative compilers still depend on MSVC runtime libraries, so MSVC is a prerequisite either way. There is no 'lightweight' path to torch.compile on Windows.
- 'RT-DETR is Apache-2.0' is true of lyuwenyu/RT-DETR and false of `from ultralytics import RTDETR` — the latter is AGPL-3.0-or-later. Any AGPL import taints the deployment, not just the training script.
- RF-DETR's model names mislead about size: 'Nano' is 30.5M params, ~13x YOLO26n. Every published latency number on the page is NVIDIA T4 / TensorRT. Sizing a laptop CPU budget from those numbers will be off by a large factor.
- The rfdetr package is Apache-2.0 but `pip install rfdetr[plus]` (or reaching for XL/2XL) silently moves you onto PML 1.0. The license boundary is inside one PyPI distribution, not between two repos.
- The transformers D-FINE docs contain a stale checkpoint id (`PekingU/DFine_r50vd`) in one code sample. Use the `ustc-community/dfine-*` ids; the others will 404 or resolve to something you did not intend.
- Reading the Tesseract releases page as HTML can yield a 2024 date for 5.5.3; the GitHub API says 2026-07-24. When a release date looks two years stale, check the API before you conclude a project is dead.
- EasyOCR is a trap of a different kind: it still installs and still works, so nothing tells you it has had no release since 2024-09-24 — you just inherit a frozen torch dependency chain for a 10-class digit problem.
- Roboflow's free tier is 15 credits/month, not the ~$60/month figure repeated in reviews and secondary reporting. Budget a lesson plan around 15 credits and you will not be surprised mid-project.
- Roboflow Public Plan means every dataset and model is published on Universe, and one workspace per user — you cannot keep a private scratch workspace alongside it. For game screenshots that is a ToS question as well as a privacy one.
- Naive random sprite placement is not a neutral baseline for synthetic detection data — Dvornik et al. found it actively degraded VOC'12 detection relative to plain augmentation. If your synthetic set underperforms, suspect placement priors before you suspect volume.
- Cut-and-paste compositing introduces boundary artifacts the detector will happily learn as the class signal. The original paper's fix is to synthesize the same scene with several different blending modes so the network cannot latch onto subpixel edge discrepancies.

### Outdated - distrust any tutorial that says these

- 'pip install opencv-python gives you OpenCV 4.x' — as of 2026-07-02 the default resolution is 5.0.0.93. Pin explicitly.
- 'Load YOLO into cv2.dnn with readNetFromDarknet(cfg, weights)' — readNetFromDarknet and readNetFromCaffe were REMOVED in OpenCV 5. Convert to ONNX and use readNetFromONNX(). Every 2019-2023 'YOLO with OpenCV DNN' tutorial is now dead code.
- 'VideoCapture.get() returns 0 for unsupported properties' — OpenCV 5 returns -1. Check `< 0`, not `== 0` and not `== -1`.
- 'Use sv.ByteTrack() and tracker.update_with_detections(detections)' — deprecated since supervision 0.28.0 and REMOVED in 0.31.0. Use `pip install trackers`, ByteTrackTracker, and `.update()`.
- 'YOLOv5 / YOLOv8 / YOLO11 is the current Ultralytics model' — YOLO26 shipped January 2026 and is the default recommendation for CPU work (38.9 ms vs YOLO11n's 56.1 ms on CPU ONNX). YOLO11 is still supported and is the conservative choice if you need a well-documented, stable ecosystem.
- 'You must tune NMS IoU/conf for YOLO' — YOLO26 is natively end-to-end and NMS-free by default; NMS is no longer in the default inference path, and DFL is gone from the regression head. Advice about exporting with `nms=True` or tuning agnostic_nms no longer applies the same way.
- 'D3DShot is the fast Windows capture library' — it is superseded; dxcam (same Desktop Duplication approach) benchmarks 239 FPS vs D3DShot's 118, and windows-capture is the better choice when you need a specific, possibly-occluded window.
- 'mss uses DXGI on Windows so it's fast' — this claim circulates in blog posts and is wrong. mss goes through GDI (BitBlt/GetDIBits) and benchmarks at ~76 FPS against dxcam's 239, and it cannot capture an obscured window (open issue since 2020).
- 'EasyOCR is a solid default OCR' — last release 1.7.2 in September 2024; effectively unmaintained, and it drags in the full torch+torchvision stack. If you need general OCR in 2026, PaddleOCR 3.7.0 (PP-OCRv6, Apache-2.0, ~9.6 MB mobile English rec model) or Tesseract 5.5.3 are the live options.
- 'RT-DETR is Apache-2.0, so `from ultralytics import RTDETR` is safe for closed-source use' — false. The upstream lyuwenyu/RT-DETR is Apache-2.0, but Ultralytics' RTDETR class lives in the AGPL-3.0 repo. The license follows the code you import, not the architecture you name.
- 'AGPL only matters if you distribute or run a network service' — that is the general FSF reading, but Ultralytics' own license page asserts it applies 'regardless of whether you train from scratch, use it internally, or deploy privately', and that fine-tuned weights count as part of the derivative work. Plan around their stated interpretation, not the one you'd prefer.
- 'torch.compile doesn't work on Windows' — the Inductor CPU backend has worked on Windows since PyTorch 2.5, with MSVC/clang-cl/icx-cl. It's just rarely worth the toolchain install for inference when OpenVINO/ONNX Runtime already exist.
- 'Use --extra-index-url for CPU PyTorch' — use --index-url. With --extra-index-url pip can still pick the multi-GB CUDA wheel off PyPI.
- 'Roboflow's free tier is just a limited trial' — it's the Public Plan with real monthly credits and full annotation/training/export, but the price is that every dataset and model is published on Roboflow Universe, and you get exactly one workspace.
- 'Modern mss uses DXGI / Desktop Duplication' — false. As of mss 10.2.0 the entire Windows backend is one file, src/mss/windows/gdi.py, and contains no DXGI code at all. If you want DXGI you need dxcam or windows-capture.
- 'mss fails with gdi32.GetDIBits() failed' as a current-version description — mss 10.x uses CreateDIBSection and does not call GetDIBits; the error strings were genericised.
- The torch.compile-on-Windows tutorial moved from docs.pytorch.org/tutorials/prototype/inductor_windows.html to .../unstable/inductor_windows.html — the /prototype/ URL is dead.
- PaddleOCR guidance quoting a '~9.6 MB mobile recognition model' and '~0.78 s/image on a Xeon 8350C' is PP-OCRv5-era. PaddleOCR 3.7.0 ships PP-OCRv6 with tiny/small/medium at 1.5M / 7.7M / 34.5M params and quotes a 5.2x OpenVINO CPU speedup instead.
- Roboflow free-tier writeups quoting '~$60/month in credits' and '$6 per flex credit' are stale or wrong; the live pricing page says 15 credits/month for Public and extra prepaid credits starting at $4.
- Treating RF-DETR XL/2XL as 'part of the Apache-2.0 RF-DETR release' — they were moved under the rfdetr_plus extension with a PML 1.0 license.
- EasyOCR as a live recommendation — no release since 2024-09-24.
- Recommending `adb exec-out screencap` for any real-time loop; it is a universal-fallback capture path (500-1500 ms/frame), and for a desktop emulator it is the wrong layer entirely.

<details>
<summary>Sources (86)</summary>

- https://api.github.com/repos/BoboTiG/python-mss/contents/src/mss/windows
- https://api.github.com/repos/BoboTiG/python-mss/issues/180
- https://api.github.com/repos/tesseract-ocr/tesseract/releases/latest
- https://arxiv.org/abs/1708.01642
- https://arxiv.org/abs/2311.11039
- https://arxiv.org/abs/2511.09554
- https://arxiv.org/html/2403.07113v1
- https://arxiv.org/html/2511.13944v1
- https://arxiv.org/pdf/2211.08479
- https://arxiv.org/pdf/2504.17076
- https://deepwiki.com/jduartedj/android-mcp-server/5.2-high-speed-frame-streaming-with-scrcpy
- https://deepwiki.com/obsproject/obs-studio/4.2.3-game-capture-and-window-capture
- https://docs.cvat.ai/docs/administration/community/basics/installation/
- https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
- https://docs.pytorch.org/tutorials/unstable/inductor_windows.html
- https://docs.pytorch.org/vision/stable/models.html#object-detection-instance-segmentation-and-person-keypoint-detection
- https://docs.roboflow.com/platform/billing-and-plans/plans
- https://docs.ultralytics.com/compare/yolo26-vs-yolo11
- https://docs.ultralytics.com/guides/yolo-performance-metrics
- https://docs.ultralytics.com/integrations/openvino/
- https://docs.ultralytics.com/models/yolo26/
- https://docs.ultralytics.com/modes/benchmark/
- https://docs.ultralytics.com/modes/track/
- https://github.com/BoboTiG/python-mss/issues/180
- https://github.com/Genymobile/scrcpy/blob/master/README.md
- https://github.com/Genymobile/scrcpy/issues/3345
- https://github.com/Peterande/D-FINE
- https://github.com/cvat-ai/cvat
- https://github.com/lyuwenyu/RT-DETR
- https://github.com/lyuwenyu/RT-DETR/blob/main/LICENSE
- https://github.com/opencv/opencv-python
- https://github.com/opencv/opencv/wiki/OpenCV-4-to-5-migration
- https://github.com/orgs/ultralytics/discussions/8113
- https://github.com/pytorch/vision
- https://github.com/ra1nty/DXcam
- https://github.com/roboflow/rf-detr
- https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.3
- https://groups.google.com/g/tesseract-ocr/c/587rJCQllbs
- https://huggingface.co/docs/transformers/en/model_doc/d_fine
- https://huggingface.co/ustc-community/dfine-small-coco
- https://huggingface.co/ustc-community/dfine_x_coco
- https://ieeexplore.ieee.org/document/10485397/
- https://labelstud.io/blog/use-yolo26-with-label-studio-for-fast-bounding-box-pre-annotations/
- https://labelstud.io/guide/install_requirements
- https://labelstud.io/tutorials/yolo
- https://learn.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturesession.isborderrequired
- https://medium.com/@mansoormemon/digit-recognition-for-7-segment-displays-using-template-matching-a-simple-approach-6a52951beddf
- https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html
- https://openaccess.thecvf.com/content_ICCV_2017/papers/Dwibedi_Cut_Paste_and_ICCV_2017_paper.pdf
- https://paddlepaddle.github.io/PaddleOCR/main/en/version3.x/algorithm/PP-OCRv5/PP-OCRv5.html
- https://pypi.org/project/easyocr/
- https://pypi.org/project/mss/
- https://pypi.org/project/opencv-python/#history
- https://pypi.org/project/paddleocr/
- https://pypi.org/project/rfdetr/
- https://pypi.org/project/supervision/#history
- https://pypi.org/project/torch/
- https://pypi.org/project/torch/#history
- https://pypi.org/project/torchvision/
- https://pypi.org/project/ultralytics/
- https://pypi.org/project/ultralytics/#history
- https://pypi.org/project/windows-capture/
- https://pypi.org/pypi/dxcam/json
- https://pypi.org/pypi/easyocr/json
- https://pypi.org/pypi/label-studio/json
- https://pypi.org/pypi/mss/json
- https://pypi.org/pypi/onnxruntime/json
- https://pypi.org/pypi/openvino/json
- https://pypi.org/pypi/paddleocr/json
- https://pypi.org/pypi/rfdetr/json
- https://pypi.org/pypi/torch/json
- https://pypi.org/pypi/torchvision/json
- https://pypi.org/pypi/trackers/json
- https://pypi.org/pypi/ultralytics/json
- https://pypi.org/pypi/windows-capture/json
- https://pytorch.org/get-started/locally/
- https://pytorch.org/get-started/previous-versions/
- https://raw.githubusercontent.com/BoboTiG/python-mss/main/src/mss/windows/gdi.py
- https://roboflow.com/model/d-fine
- https://roboflow.com/pricing
- https://supervision.roboflow.com/develop/trackers/
- https://trackers.roboflow.com/latest/trackers/comparison/
- https://www.cpu-monkey.com/en/cpu-amd_ryzen_3_7320u
- https://www.intel.com/content/www/us/en/support/articles/000093369/software/development-software.html
- https://www.researchgate.net/publication/322060104_Cut_Paste_and_Learn_Surprisingly_Easy_Synthesis_for_Instance_Detection
- https://www.ultralytics.com/license

</details>

---

## Reinforcement Learning Stack

<sub>2 report(s) &middot; 47 verified, 5 likely &middot; 27 pitfalls &middot; 19 outdated patterns &middot; 52 sources</sub>

### Facts

- **VERIFIED** Gymnasium 1.3.0 is current (released 2026-04-22), requires Python >=3.10. openai/gym was archived read-only on 2026-04-08.
  - PyPI upload_time for gymnasium 1.3.0 = 2026-04-22T13:47:12; prior 1.2.3 = 2025-12-18, 1.2.2 = 2025-11-04. The openai/gym README states the team 'moved all future development to Gymnasium, a drop in replacement for Gym (import gymnasium as gym), and Gym will not be receiving any future updates.' Install `gymnasium`, never `gym`.
- **VERIFIED** The exact Gymnasium Env API: reset(*, seed=None, options=None) -> (obs, info) and step(action) -> (obs, reward, terminated, truncated, info).
  - From gymnasium.farama.org/api/env: `reset(*, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[ObsType, dict[str, Any]]` — seed and options are KEYWORD-ONLY (the bare `*`). `step(action: ActType) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]`. Attributes: action_space, observation_space, metadata, render_mode, spec, unwrapped, np_random, np_random_seed.
- **VERIFIED** terminated vs truncated is not cosmetic — it changes the bootstrapping target. target = reward + (1 - terminated) * gamma * next_value.
  - The Gymnasium migration guide gives exactly this formula. With the old single `done`, hitting a time limit was treated as a real terminal state, so the agent learned that the world ends at the horizon. For a match-based game: losing/winning = terminated; hitting your own step cap = truncated. Getting this backwards silently biases the value function and is nearly impossible to debug from reward curves.
- **VERIFIED** Old-gym 4-tuple code fails in four distinct ways, and shimmy is the escape hatch.
  - Per the migration guide: (1) `obs, reward, done, info = env.step(a)` raises ValueError (too many values to unpack, expected 4); (2) `obs = env.reset()` silently binds the tuple `(obs, info)` to obs — no exception, just garbage observations; (3) `info.get('TimeLimit.truncated')` no longer exists; (4) `env.render(mode='human')` is invalid — render_mode goes to `gym.make(..., render_mode='human')`. Shimmy 2.0.1 (2026-04-10) provides `gymnasium.make('GymV21Environment-v0', env_id=...)`. Helpers `convert_to_terminated_truncated_step_api()` / `convert_to_done_step_api()` exist.
- **VERIFIED** Stable-Baselines3 2.9.0 (2026-06-15) requires gymnasium>=0.29.1,<2.0, torch>=2.8,<3.0, numpy<3.0, Python >=3.10. torch is at 2.13.0.
  - PyPI JSON: SB3 2.9.0 uploaded 2026-06-15T17:00:29; 2.8.0 = 2026-04-01. 2.9.0 relaxed the gymnasium ceiling from <1.3.0 to <2.0 and raised the torch floor from 2.3 to 2.8 for security. torch latest = 2.13.0 (2026-07-08). CPU-only install: `pip install torch --index-url https://download.pytorch.org/whl/cpu` — do this FIRST or pip pulls ~2.5 GB of CUDA wheels onto an 8 GB laptop.
- **VERIFIED** SB3's DQN supports ONLY Discrete action spaces — not MultiDiscrete, not MultiBinary, not Box.
  - Confirmed in both the SB3 algorithms table and modules/dqn.html. This is the single most consequential fact for a card-choice x placement-grid action space: the moment you factorize the action into MultiDiscrete([n_cards, grid_x, grid_y]), DQN is off the table. PPO, A2C, TRPO, MaskablePPO and RecurrentPPO all support MultiDiscrete.
- **VERIFIED** SB3's DQN is deliberately vanilla: no Double DQN, no Dueling, no Prioritized Experience Replay. But n-step returns WERE added in SB3 2.7.0.
  - modules/dqn.html states verbatim: 'This implementation provides only vanilla Deep Q-Learning and has no extensions such as Double-DQN, Dueling-DQN and Prioritized Experience Replay.' However the changelog shows Release 2.7.0 (2025-07-25) 'n-step returns for all off-policy algorithms' via an `n_steps` parameter and a new `NStepReplayBuffer` ('without additional memory requirement'). The DQN signature now includes `n_steps: int = 1`. Caveat from 2.9.1a1: `n_steps` only applies when `replay_buffer_class` is None; with a custom buffer you must pass `replay_buffer_kwargs={'n_steps': ..., 'gamma': ...}`.
- **VERIFIED** SB3 DQN defaults (verified against dqn.py source, not just docs): learning_rate=1e-4, buffer_size=1_000_000, learning_starts=100, batch_size=32, tau=1.0, gamma=0.99, train_freq=4, gradient_steps=1, n_steps=1, target_update_interval=10000, exploration_fraction=0.1, exploration_initial_eps=1.0, exploration_final_eps=0.05, max_grad_norm=10.
  - tau=1.0 means a HARD target copy every target_update_interval steps (not Polyak). target_update_interval=10000 is in environment steps, and with train_freq=4 that is only one target refresh per 2500 gradient updates — far too slow for a 100k-step budget. RL-Zoo tuned values show how much this moves: CartPole uses target_update_interval=10, MountainCar 600, LunarLander 250, Atari 1000.
- **VERIFIED** exploration_fraction is a FRACTION OF total_timesteps passed to learn(), not an absolute step count.
  - dqn.py docstring: 'fraction of entire training period over which the exploration rate is reduced.' With the default 0.1, epsilon anneals 1.0 -> 0.05 over the first 10% of the budget then stays flat. Consequence: calling `learn(50_000)` twice is NOT the same as `learn(100_000)` — the schedule restarts. This is a top-3 silent bug for learners doing incremental training runs.
- **VERIFIED** SB3's ReplayBuffer PREALLOCATES the full buffer as np.zeros at construction and warns via psutil if it exceeds available RAM.
  - buffers.py: `self.observations = np.zeros((buffer_size, n_envs, *obs_shape), dtype=observation_space.dtype)` plus a separate `next_observations` array unless optimize_memory_usage=True; then compares total nbytes against `psutil.virtual_memory().available`. Two hard traps in the same file: `optimize_memory_usage=True` AND `handle_timeout_termination=True` together raise ValueError (issue #934), and DictReplayBuffer asserts `not optimize_memory_usage` — Dict observations cannot use the memory-efficient path at all.
- **VERIFIED** Replay-buffer RAM arithmetic on an 8 GB laptop: a 1M-step buffer over a Box(128,) float32 observation costs ~1.02 GB; over an 84x84x4 uint8 image it costs ~56.4 GB.
  - Computed from the SB3 allocation formula (obs + next_obs, both preallocated). Box(64,) f32 -> 0.51 GB; Box(128,) f32 -> 1.02 GB; Box(512,) f32 -> 4.10 GB (already fatal on 8 GB alongside Windows + Python + torch). Image 84x84x4 uint8 = 28,224 B/obs -> 1M buffer = 56.4 GB, 100k buffer = 5.6 GB. Practical rule: keep the observation a small hand-engineered float vector, and set buffer_size to 50k-200k, not the 1M default.
- **VERIFIED** SB3's VecEnv step() returns a 4-TUPLE (obs, rewards, dones, infos) — deliberately NOT the Gymnasium 5-tuple.
  - From guide/vec_envs: `dones = terminated or truncated` per env, and the true terminal observation is stashed at `infos[env_idx]['terminal_observation']` because the returned obs is already the first frame of the NEXT episode. So a learner must write a 5-tuple `gym.Env` and then read a 4-tuple from the VecEnv wrapping it. This inconsistency looks exactly like the deprecated old-gym API and reliably confuses people into 'fixing' their env back to the old signature.
- **VERIFIED** SubprocVecEnv on Windows uses the 'spawn' start method and requires an `if __name__ == "__main__":` guard.
  - Explicit warning in guide/vec_envs. Without the guard, each subprocess re-imports and re-executes the training script, forking recursively. Related: MaskablePPO's docs note SubprocVecEnv requires `action_masks` implemented directly on the env — the ActionMasker wrapper does not survive the process boundary.
- **VERIFIED** sb3-contrib 2.9.0 (same day as SB3, 2026-06-15) provides MaskablePPO, RecurrentPPO, QR-DQN, TQC, TRPO, ARS, CrossQ. MaskablePPO supports Discrete, MultiDiscrete AND MultiBinary.
  - PyPI pins `stable_baselines3>=2.9.0,<3.0` — versions are locked in lockstep, so never mix e.g. SB3 2.9 with contrib 2.8. Masking contract: the env implements `action_masks()` returning a boolean array (True = legal), or you wrap with `ActionMasker(env, mask_fn)`. Limitation: you MUST use the maskable variants of EvalCallback and evaluate_policy — the standard ones silently evaluate without masks and report garbage. Recurrent policies are not supported by MaskablePPO.
- **VERIFIED** THE CORE ARITHMETIC — steps/day against a live real-time game, single client, 24/7, zero downtime: 10 steps/s = 864,000/day; 20 steps/s = 1,728,000/day; 30 steps/s = 2,592,000/day.
  - Direct computation (rate * 86,400 s). This is the ceiling, and it is unimprovable: a real-time game cannot be run faster than real time, and you have one client. Contrast with Atari, where a CPU emulator runs thousands of steps/sec and you can run 8-16 copies in parallel.
- **VERIFIED** THE CORE ARITHMETIC — wall-clock time to reach standard RL training budgets against the live game.
  - Computed from the rates above. || 1M steps (= SB3's DEFAULT buffer_size alone): 1.2 days @10/s, 13.9 h @20/s, 9.3 h @30/s. || 10M steps (SB3 RL-Zoo's TUNED DQN budget for Atari, verified from hyperparams/dqn.yml n_timesteps=1e7): 11.6 days @10/s, 5.8 days @20/s, 3.9 days @30/s. || 50M steps (the classic unconstrained Atari budget, 200M frames at frameskip 4): 57.9 days @10/s, 28.9 days @20/s, 19.3 days @30/s. || 200M steps: 231 days @10/s, 77 days @30/s. Conclusion for the curriculum: matching the budget that DQN needs for PONG takes between 4 days and 2 months of uninterrupted 24/7 play, for a game far harder than Pong, on a laptop that must also be usable.
- **VERIFIED** THE CORE ARITHMETIC — episode/reward-signal view: at 10 steps/s a 3-minute match is 1,800 steps, so 10M steps = 5,556 matches = 278 hours of continuous matches, yielding only 5,556 win/loss reward signals.
  - Computed. At 30 steps/s: 5,400 steps/match, 1,852 matches, 93 h. The reward-signal count is the number that should end the argument — 5,556 labeled outcomes is a SMALL SUPERVISED DATASET, and you spent 278 hours of real time collecting it. The same 278 hours of recorded human play gives you ~10 million labeled (state, action) pairs for BC, because BC gets a training label on every single frame instead of one per match.
- **VERIFIED** The only live-game-tractable budget is Atari-100k scale: 100,000 steps = 2.78 h @10/s. But Atari-100k methods are not DQN.
  - Computed; the 100k benchmark is defined as ~2 hours of human-equivalent play and is 500x smaller than the standard 50M-step budget. The methods that work at that budget (EfficientZero, DrQ, SPR, Data-Efficient Rainbow) are model-based or heavy-augmentation methods far more complex than DQN, they target Atari's dense per-frame scores rather than one terminal bit, and they still do not reach expert human play. Do not promise a learner that 3 hours of live play will train anything.
- **VERIFIED** Precedent check: AlphaStar did imitation learning from human replays FIRST, and the supervised-only agent already beat the built-in Elite AI in 95% of games.
  - DeepMind's AlphaStar blog: trained initially on anonymised human games from Blizzard; that purely supervised agent 'defeated the built-in Elite level AI - around gold level for a human player - in 95% of games.' Only then did league training run 14 days on 16 TPUs per agent, with each agent experiencing 'up to 200 years of real-time StarCraft play.' The strongest possible argument for BC-first: the state of the art in RTS RL started with behavioral cloning, and BC alone got to gold-level human play.
- **VERIFIED** Precedent check on RL scale: OpenAI Five played 180 years of game per day, on 256 GPUs and 128,000 CPU cores, for 10 months (770±50 PFlops/s·days).
  - From OpenAI's own writeup. Useful as the honest upper bound on 'what it actually costs to RL a real-time strategy game from scratch.' Put next to 864,000 steps/day on one laptop, this is the scale gap the curriculum has to name out loud.
- **VERIFIED** Potential-based reward shaping (Ng, Harada & Russell 1999) is the only shaping form with a policy-invariance guarantee: F(s,s') = gamma*Phi(s') - Phi(s).
  - 'Policy Invariance Under Reward Transformations: Theory and Application to Reward Shaping', ICML 1999, pp. 278-287. The result: adding a shaping term expressible as the difference of a potential function over states leaves the set of optimal policies unchanged — and this form is NECESSARY, not merely sufficient. Practical translation: shape with a potential over STATE (e.g. Phi = w * tower_hp_differential), never with a bonus on ACTIONS or events. Any shaping term that is not a potential difference can and will change what the optimal policy is.
- **VERIFIED** Canonical reward-hacking case: OpenAI's CoastRunners agent scored ~20% higher than a human player while never finishing the race.
  - 'Faulty Reward Functions in the Wild' (Amodei & Clark, OpenAI, Dec 2016). The agent found an isolated lagoon, drove in circles knocking over the same three targets timed to their respawn, repeatedly caught fire and crashed into other boats, and never completed a lap. Direct analogues for a card/RTS game to warn about: rewarding damage-dealt -> the agent farms chip damage and never pushes; rewarding elixir-spent -> it dumps cards at spawn; rewarding units-placed -> it spams the cheapest card; rewarding match-duration-survived -> it learns to stall to timeout; rewarding tower-HP-delta without a potential formulation -> it learns to oscillate a value that goes up and down.
- **VERIFIED** The `imitation` library is EFFECTIVELY UNMAINTAINED and pinned to versions incompatible with the current stack.
  - This is the biggest practical landmine in the topic. Latest release v1.0.1 (2025-01-07); last commit to master 2025-01-07, and the commit before that was 2024-01-17 — 19 months of no development. setup.py pins `gymnasium[classic-control]~=0.29` and `stable-baselines3~=2.2.1`. Current stack is Gymnasium 1.3.0 and SB3 2.9.0. `pip install imitation` into a working SB3 2.9 environment will DOWNGRADE gymnasium to 0.29.x and SB3 to 2.2.1, breaking everything else. It implements BC, DAgger, GAIL, AIRL, DRLHP, Density-based reward modeling, MCE-IRL and SQIL. Recommendation for this curriculum: do NOT pip install it into the main env — either use a separate throwaway venv, or (better) write BC yourself.
- **VERIFIED** The theoretical reason BC alone degrades: compounding distribution shift. DAgger (Ross, Gordon & Bagnell 2011) fixes it by querying the expert on the LEARNER's own state distribution.
  - arXiv:1011.0686. The paper's framing: 'sequential prediction problems such as imitation learning, where future observations depend on previous predictions (actions), violate the common i.i.d. assumptions made in statistical learning.' Once the BC policy makes one mistake it lands in states absent from the human data, where its predictions are unconstrained, and errors cascade (the classic result is error growing as T^2*epsilon for naive BC vs T*epsilon for DAgger). Practical caveat for THIS project: DAgger requires an interactive expert who can label the agent's own visited states — i.e. the human must sit and annotate live gameplay. That is often not worth it; the cheaper fix is simply recording more human data covering the failure states.
- **VERIFIED** CleanRL: the GitHub repo is active (last commit 2026-04-20) but the PyPI package is ABANDONED and will wreck an environment.
  - PyPI cleanrl 1.2.0 dates from 2023-05-22 and pins `gym==0.23.1`, `stable-baselines3==1.2.0`, and `python >=3.7.1,<3.11` — it will not even install on Python 3.12+ and pulls the dead gym. Correct usage matches CleanRL's own stated philosophy: 'CleanRL is not a modular library and therefore it is not meant to be imported' — you COPY a single file (their PPO-Atari is ~340 lines) and read/edit it. 13+ algorithms incl. PPO, DQN, C51, SAC, TD3, PQN, Rainbow, QDagger. Ideal as the 'read the whole algorithm in one sitting' companion to SB3's black box.
- **VERIFIED** PettingZoo 1.27.0 (2026-08-13, four days ago) requires gymnasium>=1.0.0 and Python >=3.10,<3.15. ParallelEnv step returns FIVE dicts keyed by agent.
  - `reset(seed=None, options=None) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict]]`; `step(actions: dict[AgentID, ActionType]) -> (observations, rewards, terminations, truncations, infos)`, all dicts keyed by agent ID. The AEC API is the turn-based sequential alternative; wrappers convert between them. Curriculum note: self-play and league training are strictly downstream of having a FAST SIMULATOR — the arithmetic above already shows single-agent RL against the live game is impractical, and self-play multiplies the required steps by the population size. This is a 'read about it, do not build it' topic until a headless simulator exists.
- **VERIFIED** Reproducibility: Henderson et al. 2018 (arXiv:1709.06560) showed deep RL results swing wildly on random seed alone; Agarwal et al. 2021 (arXiv:2108.13264) says report IQM with stratified bootstrap CIs, not mean/median.
  - Henderson ('Deep Reinforcement Learning that Matters', AAAI 2018) documents that single-run reports are unreliable and that hyperparameter and seed sensitivity make fair comparison hard. Agarwal ('Deep RL at the Edge of the Statistical Precipice', NeurIPS 2021) provides the fix and the `rliable` library: interquartile mean (IQM) as the aggregate, stratified bootstrap confidence intervals, and performance profiles — explicitly designed for the 'few run' regime a hobbyist is stuck in. SB3's own rl_tips page independently says to run multiple seeds and evaluate over 5-20 episodes. For this project: report win rate vs a FIXED baseline opponent, over >=3-5 seeds, with a CI — a single run's win rate is not evidence.
- **VERIFIED** evaluate_policy needs the env wrapped in Monitor or the numbers are wrong, and it warns by default.
  - evaluation.py: `evaluate_policy(model, env, n_eval_episodes=10, deterministic=True, ...)` with a `warn=True` parameter that 'warns user about lack of a Monitor wrapper'. The docstring notes that without Monitor, reward and episode length are counted from raw `env.step` calls, so any reward-scaling or early-reset wrapper contaminates the evaluation. Rule: `Monitor(env)` goes on FIRST, before any other wrapper, so it sees the true reward.
- **VERIFIED** Experiment tracking: TensorBoard 2.21.0 and MLflow 3.15.1 both run fully offline; W&B 0.28.2 needs an explicit offline mode.
  - TensorBoard 2.21.0 (2026-06-29) is the zero-friction choice — SB3 takes `tensorboard_log='./logs/'` directly and it is a local static file reader. MLflow 3.15.1 (2026-08-03) logs to a local `./mlruns` directory by default with NO server, config, or network access; `mlflow server --port 5000` serves the UI at 127.0.0.1, and a SQLite backend is available. W&B 0.28.2 (2026-08-12) defaults to streaming to the cloud; offline use requires `wandb.init(mode='offline')` or `WANDB_MODE=offline`, with `wandb sync` to upload later. Recommendation for an 8 GB offline-friendly laptop: TensorBoard first, MLflow when you need to compare runs as a table.
- **VERIFIED** Gymnasium 1.3.0 added a `RepeatAction` wrapper for frame-skipping / coarser control loops — directly relevant to a real-time game.
  - From the Gymnasium releases page for v1.3.0, alongside the pygame -> pygame-ce swap (which unlocks Python 3.14). Repeating each action over k frames is the standard lever for cutting the effective step rate: at 30 steps/s with k=3 you get 10 agent decisions/sec, shortening episodes in agent-steps by 3x and making the credit-assignment horizon per match 600 steps instead of 1800 — without changing wall-clock cost. Gymnasium 1.2.1 also added DiscretizeObservation/DiscretizeAction wrappers and fixed AsyncVectorEnv.step hangs.
- **VERIFIED** SB3's DQN supports Discrete action spaces ONLY — MultiDiscrete, MultiBinary and Box are all marked unsupported — and there is no action-masking API on DQN anywhere in SB3 or sb3-contrib.
  - The DQN docs space-support table (SB3 2.9.1a1 master) shows Discrete supported, Box/MultiDiscrete/MultiBinary unsupported for actions (observations may be Discrete/Box/MultiDiscrete/MultiBinary/Dict). sb3-contrib 2.9.0's algorithm list is ARS, QR-DQN, MaskablePPO, RecurrentPPO, TQC, TRPO, CrossQ — there is no masked DQN. So the original claim's 'DQN can do neither' is correct as stated.
- **VERIFIED** CORRECTION to claim 1: MaskablePPO does support MultiDiscrete, but its MultiDiscrete masking is FACTORED per-head, not joint — so MultiDiscrete([n_cards, grid_x, grid_y]) cannot express 'this cell is legal only for that card'.
  - sb3_contrib/common/maskable/distributions.py: masks_tensor = masks_tensor.view(-1, sum(self.action_dims)) then split_masks = th.split(masks_tensor, list(self.action_dims), dim=1), one independent mask per categorical sub-distribution. Mask shape is (batch_size, sum(nvec)) — i.e. n_cards+grid_x+grid_y booleans, NOT n_cards*grid_x*grid_y. Consequence for a card x placement design: the 'collapse the head count from a product to a sum' benefit costs you joint legality, which matters because spells/troops/buildings have different legal regions. If card-conditional placement legality matters, use a flat Discrete(n_cards * cells) with a full joint mask — MaskablePPO supports that and it is the only way to encode the constraint.
- **VERIFIED** MaskablePPO action-space support: Discrete yes, MultiDiscrete yes, MultiBinary yes, Box no, Dict no. Masks come either from an action_masks() method on the env or from the ActionMasker wrapper (True = valid).
  - sb3-contrib master ppo_mask docs, space-support table plus the masking section.
- **VERIFIED** MaskablePPO has three non-obvious usage requirements that silently produce wrong numbers if ignored.
  - Verbatim from the docs: 'You must use evaluate_policy from sb3_contrib.common.maskable.evaluation instead of the SB3 one'; 'You must use MaskableEvalCallback from sb3_contrib.common.maskable.callbacks instead of the base EvalCallback to properly evaluate a model with action masks'; 'In order to use SubprocVecEnv with MaskablePPO, you must implement the action_masks inside the environment (ActionMasker cannot be used).' Masking is optional at inference; predict() takes an action_masks kwarg.
- **VERIFIED** The rl_tips sample-efficiency quote in claim 2 is accurate, verbatim.
  - SB3 rl_tips: 'Model-free RL algorithms (i.e. all the algorithms implemented in SB3) are usually sample inefficient. They require a lot of samples (sometimes millions of interactions) to learn anything useful.'
- **VERIFIED** NUANCE against claim 2: the same rl_tips page recommends, for single-process discrete actions, 'DQN with extensions (double DQN, prioritized replay, ...)' — which SB3 does not ship — and for sparse reward it recommends HER or ARS, not PPO.
  - rl_tips verbatim: single-process discrete -> 'DQN with extensions (double DQN, prioritized replay, ...) are the recommended algorithms'; multiprocessed discrete -> 'You should give a try to PPO or A2C'; 'In sparse reward settings, we recommend using dedicated methods like HER (see below) or population-based algorithms like ARS.' HER needs a goal-conditioned Dict observation, which a win/loss card game does not naturally have. The BC-first verdict is defensible but is a judgment call, not something SB3 endorses.
- **VERIFIED** SB3's DQN warning states plainly: 'This implementation provides only vanilla Deep Q-Learning and has no extensions such as Double-DQN, Dueling-DQN and Prioritized Experience Replay.'
  - Verbatim from SB3 master DQN docs, confirming claim 5's 'not in SB3 at all' for PER. Prioritized replay remains an open request (DLR-RM/stable-baselines3 issue #1242). The one DQN extension you can actually pip install is QR-DQN in sb3-contrib 2.9.0.
- **VERIFIED** n-step returns landed in SB3 2.7.0 (2025-07-25) via the n_steps parameter and NStepReplayBuffer — but with two restrictions claim 5 omits.
  - DQN docs verbatim: 'When n_step > 1, uses n-step return (with the NStepReplayBuffer) when updating the Q-value network. Note: it is only used when replay_buffer_class is None, and is not supported for Dict observation spaces yet.' So n_steps is a silent no-op if you pass a custom replay_buffer_class, and unavailable with a Dict observation (a natural encoding for hand + arena + elixir). Default n_steps=1. Claim 5's 'SB3 2.7.0+' is correct.
- **VERIFIED** SB3 DQN defaults confirmed: buffer_size=1000000, learning_starts=100, target_update_interval=10000, exploration_fraction=0.1, exploration_initial_eps=1.0, exploration_final_eps=0.05, train_freq=4, n_steps=1.
  - SB3 master DQN docs. Note learning_starts=100, not the old 50000 — claim 5's worry about 'fitting to 100 samples' is exactly right, that IS the current default.
- **VERIFIED** CORRECTION to claim 5's RL Zoo range: tuned target_update_interval in rl-baselines3-zoo is 10-600 for classic control and 1000 for Atari, not '10-1000 for short runs'.
  - hyperparams/dqn.yml (master): CartPole-v1 target_update_interval=10 (buffer 100000, learning_starts 1000, train_freq 256, gradient_steps 128, exploration_fraction 0.16, final_eps 0.04, lr 2.3e-3, 5e4 steps); MountainCar-v0 =600 (buffer 10000, learning_starts 1000, train_freq 16, gradient_steps 8, exp_fraction 0.2, final_eps 0.07, lr 4e-3, 1.2e5 steps); LunarLander-v3 and Acrobot-v1 =250 (buffer 50000, learning_starts 0, train_freq 4, gradient_steps -1, exp_fraction 0.12, final_eps 0.1, lr 6.3e-4, 1e5 steps); atari =1000 (buffer 100000, learning_starts 100000, train_freq 4, gradient_steps 1, exp_fraction 0.1, final_eps 0.01, 1e7 steps). Headline: every tuned config shrinks buffer_size far below the 1e6 default, and Atari's learning_starts=100000 alone exceeds the learner's entire realistic live-step budget.
- **VERIFIED** SB3's ReplayBuffer stores next_observations as a SEPARATE full-size array by default, roughly doubling observation memory, and warns via psutil when it will not fit.
  - stable_baselines3/common/buffers.py: total_memory_usage = observations.nbytes + actions.nbytes + rewards.nbytes + dones.nbytes, plus next_observations.nbytes when optimize_memory_usage is False; if it exceeds available memory it warns 'This system does not have apparently enough memory to store the complete replay buffer X.XXGB > Y.YYGB'. optimize_memory_usage=True drops the next_observations copy. This makes claim 5's 'size the buffer to your RAM' point concrete and measurable on an 8 GB machine.
- **VERIFIED** CORRECTION to claim 3: the imitation BC constructor default is policy=None, not policy=FeedForward32Policy. BC builds a FeedForward32Policy internally when policy is None.
  - Actual signature: BC(observation_space, action_space, rng, policy=None, demonstrations=None, batch_size=32, minibatch_size=None, optimizer_cls=torch.optim.Adam, optimizer_kwargs=None, ent_weight=0.001, l2_weight=0.0, device='auto', custom_logger=None). train(n_epochs=None, n_batches=None, on_epoch_end=None, on_batch_end=None, log_interval=500, log_rollouts_venv=None, log_rollouts_n_episodes=5, progress_bar=True, reset_tensorboard=False). In bc.py, when policy is None it constructs FeedForward32Policy with CombinedExtractor for Dict observations else FlattenExtractor.
- **VERIFIED** The 'BC is just cross-entropy' claim is literally true in imitation's own source: loss = negative log-prob + entropy term + L2 term.
  - BehaviorCloningLossCalculator in src/imitation/algorithms/bc.py: neglogp = -log_prob; ent_loss = -self.ent_weight * entropy; l2_loss = self.l2_weight * l2_norm; loss = neglogp + ent_loss + l2_loss. Docs describe BC as 'supervised learning on observation-action pairs from expert demonstrations' and warn the 'policy often generalizes poorly and does not recover well from errors' (covariate shift / compounding error). Hand-writing it in ~50 lines of PyTorch is fair; the only non-obvious extras to replicate are the entropy bonus (default 0.001) and the L2 term (default 0.0).
- **VERIFIED** The imitation dependency conflict is real and now severe: imitation 1.0.1 (last release 2025-01-07, ~19 months stale) pins stable-baselines3~=2.2.1 and gymnasium[classic-control]~=0.29.
  - PyPI imitation 1.0.1 requires_dist; GitHub releases confirm nothing newer than v1.0.1. Current stable-baselines3 is 2.9.0 (requires_python >=3.10; gymnasium>=0.29.1,<2.0; numpy>=1.20,<3.0; torch>=2.8,<3.0) and gymnasium is 1.3.0 (2026-04-22). sb3-contrib 2.9.0 requires stable_baselines3>=2.9.0,<3.0. So installing imitation alongside sb3-contrib is unsatisfiable — imitation drags SB3 back to 2.2.x and gymnasium to 0.29, which sb3-contrib 2.9.0 rejects. Writing BC by hand is the right call for a checkable reason, not a vibe.
- **VERIFIED** SBX version and dependency claims in claim 4 are exactly right: sbx-rl 0.28.0, uploaded 2026-07-24, requires_python >=3.10.
  - PyPI requires_dist verbatim: stable_baselines3<3.0,>=2.9.0; jax<0.12.0,>=0.4.24; flax; optax; tqdm; rich; tfp-nightly>=0.26.0.dev20250831. The nightly TensorFlow-Probability pin is confirmed and is a genuine install-fragility signal on Windows. The 'skip it on CPU-only 8 GB' verdict is judgment rather than fetched fact, but the dependency evidence supports it.
- **VERIFIED** Version floor gating this whole curriculum on the target laptop: SB3 2.9.0, sb3-contrib 2.9.0 and sbx-rl 0.28.0 all require Python >=3.10, and SB3 2.9.0 requires torch>=2.8,<3.0.
  - All from PyPI requires_python / requires_dist. A learner on Python 3.9 cannot install current SB3 at all. On a CPU-only box install torch from the CPU wheel index (pip install torch --index-url https://download.pytorch.org/whl/cpu) or pip pulls the multi-GB CUDA wheel by default — disk and RAM both matter at 8 GB.
- **VERIFIED** SB3's latest documented build is 2.9.1a1 (docs master, dated 2026-07-18); latest released PyPI stable is 2.9.0.
  - SB3 changelog master header vs PyPI JSON. Pin 2.9.0 in the curriculum's requirements file — 2.9.1a1 is an unreleased alpha and should not be pip-installed by a learner.
- *likely* Action masking is the highest-leverage single change for a card-choice x placement-grid action space, and it is why MaskablePPO beats DQN here on engineering grounds.
  - In a game like this the vast majority of the raw action space is illegal at any instant: only ~4 cards are in hand, elixir gates which are affordable, and large regions of the placement grid are out-of-bounds for the current side. A flat Discrete(n_cards * grid_cells) forces DQN to learn legality from reward, wasting most of an already-impossible sample budget. MultiDiscrete([n_cards, grid_x, grid_y]) collapses the head count from a product to a sum, and masking removes illegal choices from the softmax before sampling. DQN can do neither: it is Discrete-only in SB3, and masking Q-values is not supported.
- *likely* Honest algorithm verdict: neither DQN nor PPO is the right first step against a live real-time game. Behavioral cloning from recorded human play is.
  - The chain of verified constraints: (a) the env step is real-time and cannot be sped up or parallelized past one game client; (b) reward is one sparse bit (win/loss) per ~1800 steps; (c) SB3's own rl_tips page says model-free RL 'require[s] a lot of samples (sometimes millions of interactions)'; (d) the arithmetic below shows millions of live steps is weeks-to-months of wall clock. BC has none of these problems: it is supervised classification on (observation, action) pairs, it trains offline from a fixed file, it needs no environment at all during training, it fits in RAM, and it converges in minutes on CPU. If you must do RL later, use MaskablePPO with a BC-pretrained policy, never DQN.
- *likely* Writing BC yourself is ~50 lines and is the correct call here, because BC for discrete actions is literally just cross-entropy classification.
  - The `imitation` BC class takes (observation_space, action_space, demonstrations, rng, policy=FeedForward32Policy, batch_size, minibatch_size, ent_weight, l2_weight) and `train(n_epochs=...)`. Every one of those pieces is standard PyTorch: a dataset of (obs, action) pairs, an MLP, nn.CrossEntropyLoss, Adam. Given the library's dependency conflict above, hand-writing it is both safer and far more educational — and it gives the learner an honest first ML win (a train/val accuracy number) on a CPU in minutes.
- *likely* SBX (sbx-rl 0.28.0, 2026-07-24) is the JAX-backed SB3 drop-in and is NOT useful on this hardware.
  - PyPI deps: `stable_baselines3>=2.9.0,<3.0`, `jax>=0.4.24,<0.12.0`, flax, optax, plus `tfp-nightly` (a nightly pin — itself a fragility signal). SBX's payoff is JIT-compiled GPU/TPU throughput; on a CPU-only Ryzen 3 with 8 GB it adds a large dependency tree and JIT compile latency for little gain, and JAX's Windows story is weaker than PyTorch's. Skip it in this curriculum.
- *likely* Which DQN tricks actually matter vs cargo cult, for THIS setting.
  - MATTERS: (1) buffer_size sized to your RAM and budget — the 1M default is wrong on 8 GB and wrong for a 100k-step run (you never overwrite, so it is just an ever-growing on-policy dataset); (2) target_update_interval scaled to the budget — 10000 default vs RL-Zoo's 10-1000 for short runs; (3) exploration_fraction, because it is budget-relative; (4) learning_starts, so you do not fit to 100 samples. PROBABLY MATTERS: n-step returns (n=3), now built into SB3 2.7.0+, and the cheapest real win under sparse delayed reward since it propagates the terminal signal n times faster. CARGO CULT AT THIS SCALE: prioritized replay (large complexity and bias-correction burden for a modest gain, and not in SB3 at all); Dueling (an architecture tweak whose gain is dwarfed by your sample-budget problem); Double DQN (real but small; overestimation is not your binding constraint when you have 5,556 reward signals). The honest ranking: none of these tricks move the needle compared to (a) using recorded human data instead of live steps, (b) masking illegal actions, (c) shrinking the observation.

### Pitfalls you will actually hit

- `pip install imitation` will silently DOWNGRADE your working environment — it pins gymnasium~=0.29 and stable-baselines3~=2.2.1, so pip rips out Gymnasium 1.3.0 and SB3 2.9.0. Symptom: your previously-working training script starts throwing 'too many values to unpack' or AttributeError on wrappers that existed yesterday. Use a separate venv, or write BC by hand.
- `pip install cleanrl` fails outright on Python 3.12+ ('requires-python >=3.7.1,<3.11') or, on an older interpreter, installs the dead `gym==0.23.1` alongside your gymnasium. CleanRL is meant to be copy-pasted file-by-file from GitHub, not installed.
- `obs = env.reset()` from an old tutorial raises NO error — it binds the whole `(obs, info)` tuple to `obs`. Symptom: check_env passes, training runs, reward never improves, and the network is being fed a Python tuple that numpy silently object-arrays. You must write `obs, info = env.reset()`.
- You write a correct 5-tuple `step()`, then wrap in DummyVecEnv, then unpack 5 values from `vec_env.step()` and get ValueError. Symptom: 'not enough values to unpack (expected 5, got 4)'. SB3's VecEnv deliberately returns `(obs, rewards, dones, infos)` with the real terminal observation hidden in `infos[i]['terminal_observation']`. Do not 'fix' your env back to the old API.
- `pip install stable-baselines3` before installing CPU-only torch pulls the default CUDA-enabled torch wheel — multiple GB of CUDA libraries you cannot use, on a laptop with 8 GB RAM and limited disk. Install torch from https://download.pytorch.org/whl/cpu FIRST, then SB3.
- DQN(buffer_size=1_000_000) with an image or large-vector observation triggers an SB3 psutil warning at CONSTRUCTION time and then MemoryError, because the buffer is preallocated as np.zeros for both obs and next_obs. Symptom: the process dies before a single training step. An 84x84x4 uint8 buffer at 1M is 56.4 GB.
- Setting `optimize_memory_usage=True` to fix the above raises `ValueError: ReplayBuffer does not support optimize_memory_usage = True and handle_timeout_termination = True simultaneously.` And if your observation is a Dict space, DictReplayBuffer asserts optimize_memory_usage is False — the option does not exist for you at all.
- Calling `model.learn(50_000)` twice instead of `model.learn(100_000)` once restarts the epsilon schedule both times, so the agent re-explores from eps=1.0. Symptom: reward curve sawtooths back to random at every resume, and it looks like catastrophic forgetting.
- Leaving target_update_interval at its 10000 default while training for 100k steps means the target network refreshes only ~10 times all run, and with train_freq=4 that is one refresh per 2500 gradient steps. Symptom: Q-loss looks fine, the policy learns nothing.
- You factorize the action space to MultiDiscrete([n_cards, x, y]) to tame the combinatorics, then get an AssertionError from DQN. SB3's DQN is Discrete-only. You must switch to PPO or MaskablePPO at that moment.
- MaskablePPO trains fine, then you evaluate with the ordinary `evaluate_policy` / `EvalCallback` and the win rate collapses. Those helpers do not pass action masks — you must use the maskable variants. Same class of bug with SubprocVecEnv, where the ActionMasker wrapper does not cross the process boundary and `action_masks` must live on the env itself.
- SubprocVecEnv on Windows spawns rather than forks; without an `if __name__ == "__main__":` guard the training script re-imports and re-executes itself in every child. Symptom: an exponential fork bomb, or a cryptic RuntimeError about the current process finishing bootstrapping.
- Evaluating without `Monitor` as the innermost wrapper reports rewards measured AFTER your reward-shaping and scaling wrappers, so you are grading the agent on the shaped reward rather than the real win/loss. Symptom: eval reward climbs beautifully while the actual win rate is flat.
- Shaping with an action bonus or an event bonus rather than a potential difference changes the optimal policy. Symptom: the agent optimizes the shaped quantity perfectly and plays worse — spamming the cheapest card, stalling to timeout, or farming chip damage without ever pushing, exactly as the CoastRunners boat circled the lagoon for a 20% higher score without finishing the race.
- Reporting a single seed's win rate as a result. Henderson et al. showed seed alone moves deep-RL numbers substantially; with only a few hundred evaluation matches your confidence interval is wide enough to swallow the entire claimed improvement.
- Planning to 'just train it against the live game overnight.' One night at 20 steps/s is ~600k steps — less than the SB3 default replay buffer, and roughly 1/17th of the tuned budget RL-Zoo uses for Atari DQN. Nothing will have happened.
- Believing a stale claim that SB3's DQN has no n-step returns. It gained an `n_steps` parameter and NStepReplayBuffer in 2.7.0 (2025-07-25) — but the parameter is IGNORED if you also pass a custom `replay_buffer_class`; you must then set `replay_buffer_kwargs={'n_steps': ..., 'gamma': ...}` instead.
- You size a MultiDiscrete([n_cards, grid_x, grid_y]) mask as n_cards*grid_x*grid_y booleans and MaskablePPO raises a shape error — it wants sum(nvec) = n_cards+grid_x+grid_y, because each head is masked independently. The worse case is when it does NOT error: you have then expressed 'these cards are legal' and 'these cells are legal' as independent facts, and the agent will happily place a spell in your own tower zone because that cell was legal for some other card.
- You set n_steps=3 on DQN while also passing a custom replay_buffer_class, and nothing changes — the docs say n_steps 'is only used when replay_buffer_class is None'. Same silent no-op if your observation is a Dict space, where n-step is unsupported.
- You evaluate a MaskablePPO model with the ordinary sb3 evaluate_policy and score far below what training suggested — the standard evaluator passes no masks, so the policy samples illegal actions. Identical trap with EvalCallback instead of MaskableEvalCallback.
- You wrap the env in ActionMasker and later switch to SubprocVecEnv for speed; masks stop reaching the model. The docs require action_masks to be implemented inside the env itself when using SubprocVecEnv.
- You leave DQN's default buffer_size=1000000 on an 8 GB laptop and get 'This system does not have apparently enough memory to store the complete replay buffer X GB > Y GB', or an outright MemoryError. SB3 allocates next_observations as a second full-size array unless optimize_memory_usage=True, so budget roughly 2x your observation bytes.
- You pip install imitation to get BC and pip either refuses to resolve or quietly downgrades stable-baselines3 to 2.2.1 and gymnasium to 0.29 — after which sb3-contrib 2.9.0 (MaskablePPO) no longer imports. The two cannot coexist at current versions.
- You follow a tutorial on Python 3.9 and pip install stable-baselines3 gives you an ancient version or fails outright — SB3 2.9.0, sb3-contrib 2.9.0 and sbx-rl 0.28.0 all declare requires_python >=3.10.
- You pip install torch on a CPU-only Ryzen and pip downloads the CUDA build, consuming gigabytes of disk for nothing. Use the /whl/cpu index explicitly.
- You reach for prioritized replay / Double DQN / Dueling after reading SB3's own rl_tips recommendation of 'DQN with extensions' — none of them exist in SB3, and the DQN page says so in a warning box. The only shipped extension is QR-DQN in sb3-contrib.
- You copy DQN hyperparameters from the Atari block of rl-baselines3-zoo: learning_starts=100000 means the agent collects 100k random steps before a single gradient update, which on a real-time game client is your entire budget spent on noise.

### Outdated - distrust any tutorial that says these

- The old-gym 4-tuple step API `obs, reward, done, info = env.step(action)` and bare `obs = env.reset()`. REPLACEMENT: `obs, reward, terminated, truncated, info = env.step(action)` and `obs, info = env.reset(seed=...)`. Any tutorial showing the 4-tuple predates gym 0.26 (2022) and is at least four years stale. The `done` flag conflated task failure with time-limit expiry, which corrupts value bootstrapping.
- `import gym` / `pip install gym`. REPLACEMENT: `import gymnasium as gym` / `pip install gymnasium`. openai/gym was ARCHIVED read-only on 2026-04-08 and its own README directs users to Gymnasium as a drop-in replacement. Anything still importing `gym` is unmaintained.
- `env.seed(42)` as a separate call, and `env.render(mode='human')`. REPLACEMENT: `env.reset(seed=42)` and `gym.make(env_id, render_mode='human')`. Also `info['TimeLimit.truncated']` is gone — that information is now the `truncated` return value.
- 'Just use DQN' as the default advice for any discrete-action game. This is wrong here for four independently sufficient reasons: SB3's DQN is Discrete-only so it cannot take a factorized MultiDiscrete action space; it cannot use action masking, which is the single biggest win in a mostly-illegal action space; it is vanilla (no Double/Dueling/PER) so it is not even the DQN the advice imagines; and it is off-policy sample-hungry precisely where samples cost real-time seconds. REPLACEMENT: behavioral cloning from recorded human play first; MaskablePPO with a BC-pretrained policy only once a fast simulator exists.
- 'Reinforcement learning is the way to make a game agent.' REPLACEMENT for a project with recorded human gameplay: supervised behavioral cloning. AlphaStar's own pipeline did imitation learning from human replays first, and that supervised-only agent already beat the built-in Elite AI in 95% of games — gold-level human play with zero RL. BC gives a training label on every frame; RL gives one bit per 1,800 frames.
- Ray RLlib as a beginner's entry point. It is a distributed-execution framework (Ray actors, cluster config, its own env and config abstractions) whose entire value proposition is scaling across many machines — the exact thing a single 8 GB CPU laptop cannot use. Its API has also churned hard across recent releases, so tutorials rot fast. REPLACEMENT: SB3 for a working baseline, CleanRL single files for reading how the algorithm actually works.
- 'Add a small reward for every good thing the agent does.' REPLACEMENT: potential-based shaping only, F(s,s') = gamma*Phi(s') - Phi(s) over STATES (Ng, Harada & Russell 1999). That form is provably policy-invariant, and the paper proved the potential-difference form is NECESSARY, not just sufficient — any other shaping term can change which policy is optimal.
- Reporting mean or median return over a handful of runs as if it were a result. REPLACEMENT: interquartile mean (IQM) with stratified bootstrap confidence intervals and performance profiles, per Agarwal et al. 2021 and the `rliable` library, which was designed specifically for the few-run regime.
- `pip install imitation` as the standard way to get BC/DAgger. As of today it is 19 months without meaningful development and pins gymnasium~=0.29 + SB3~=2.2.1, which is mutually exclusive with the current Gymnasium 1.3.0 / SB3 2.9.0 stack. REPLACEMENT: write BC yourself (it is cross-entropy on (obs, action) pairs), or isolate `imitation` in a throwaway venv.
- `pip install cleanrl`. The PyPI package froze at 1.2.0 in May 2023 pinning gym==0.23.1 and Python <3.11, even though the GitHub repo is actively maintained (last commit 2026-04-20). REPLACEMENT: clone the repo or copy the single algorithm file you want — CleanRL states outright that it 'is not a modular library and therefore it is not meant to be imported.'
- Guidance that SB3's off-policy algorithms only support 1-step TD targets. n-step returns landed in SB3 2.7.0 (2025-07-25) via the `n_steps` parameter and NStepReplayBuffer, for all off-policy algorithms, in SB3, sb3-contrib and SBX alike.
- Copying SB3's documented DEFAULT hyperparameters as if they were tuned values. They are Atari-scale placeholders: buffer_size=1e6 and target_update_interval=10000 assume a 10M-step budget. REPLACEMENT: start from the RL-Zoo tuned entries for a comparably-sized problem (LunarLander DQN: buffer_size=50000, learning_starts=0, target_update_interval=250, train_freq=4, gradient_steps=-1, exploration_fraction=0.12, exploration_final_eps=0.1, n_timesteps=1e5).
- 'DQN's learning_starts default is 50000' — it is 100 in current SB3. The failure mode flipped: you now start fitting on almost no data rather than never starting at all.
- 'SB3 has no n-step returns, write your own buffer' — false since SB3 2.7.0 (2025-07-25), which added the n_steps parameter and NStepReplayBuffer (with the replay_buffer_class=None and no-Dict-observation restrictions).
- 'imitation is the standard way to get BC on top of SB3' — imitation's last release is v1.0.1 (2025-01-07) and it pins stable-baselines3~=2.2.1 / gymnasium~=0.29, seven minor versions and a major version behind current (SB3 2.9.0, gymnasium 1.3.0). Any tutorial installing both imitation and current sb3-contrib is now broken.
- 'import gym' and Gym 0.21-era env APIs — gymnasium 1.3.0 (2026-04-22) is the maintained line and SB3 requires gymnasium>=0.29.1,<2.0. Gymnasium 1.0 introduced breaking changes older SB3 (<2.4.0) cannot handle, so mixed-vintage pins fail in confusing ways.
- 'MaskablePPO is Discrete-only' — it supports Discrete, MultiDiscrete and MultiBinary (Box and Dict actions unsupported). But see the pitfall: MultiDiscrete masking is per-head, not joint.
- The original claim that RL Zoo uses target_update_interval of 10-1000 'for short runs' — the tuned classic-control values are 10 (CartPole), 250 (LunarLander/Acrobot) and 600 (MountainCar); 1000 is the Atari value on a 1e7-step budget.
- The original claim that imitation's BC defaults to policy=FeedForward32Policy — the constructor default is policy=None; FeedForward32Policy is what BC constructs internally in that case.

<details>
<summary>Sources (52)</summary>

- https://api.github.com/repos/HumanCompatibleAI/imitation/commits
- https://api.github.com/repos/HumanCompatibleAI/imitation/releases
- https://arxiv.org/abs/1011.0686
- https://arxiv.org/abs/1709.06560
- https://arxiv.org/abs/2108.13264
- https://deepmind.google/discover/blog/alphastar-mastering-the-real-time-strategy-game-starcraft-ii/
- https://docs.cleanrl.dev/
- https://docs.wandb.ai/guides/track/launch/
- https://github.com/DLR-RM/rl-baselines3-zoo/blob/master/hyperparams/dqn.yml
- https://github.com/DLR-RM/stable-baselines3/issues/1242
- https://github.com/Farama-Foundation/Gymnasium/releases
- https://github.com/HumanCompatibleAI/imitation
- https://github.com/Stable-Baselines-Team/stable-baselines3-contrib
- https://github.com/openai/gym
- https://gymnasium.farama.org/api/env/
- https://gymnasium.farama.org/api/spaces/fundamental/
- https://gymnasium.farama.org/api/vector/
- https://gymnasium.farama.org/introduction/migration_guide/
- https://imitation.readthedocs.io/en/latest/algorithms/bc.html
- https://mlflow.org/docs/latest/ml/tracking/
- https://openai.com/index/faulty-reward-functions/
- https://openai.com/index/openai-five/
- https://pettingzoo.farama.org/api/parallel/
- https://pypi.org/pypi/Shimmy/json
- https://pypi.org/pypi/cleanrl/json
- https://pypi.org/pypi/gymnasium/json
- https://pypi.org/pypi/imitation/json
- https://pypi.org/pypi/mlflow/json
- https://pypi.org/pypi/pettingzoo/json
- https://pypi.org/pypi/sb3-contrib/json
- https://pypi.org/pypi/sbx-rl/json
- https://pypi.org/pypi/stable-baselines3/json
- https://pypi.org/pypi/tensorboard/json
- https://pypi.org/pypi/torch/json
- https://pypi.org/pypi/wandb/json
- https://raw.githubusercontent.com/DLR-RM/rl-baselines3-zoo/master/hyperparams/dqn.yml
- https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/docs/misc/changelog.md
- https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/stable_baselines3/common/buffers.py
- https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/stable_baselines3/common/evaluation.py
- https://raw.githubusercontent.com/DLR-RM/stable-baselines3/master/stable_baselines3/dqn/dqn.py
- https://raw.githubusercontent.com/HumanCompatibleAI/imitation/master/src/imitation/algorithms/bc.py
- https://raw.githubusercontent.com/Stable-Baselines-Team/stable-baselines3-contrib/master/sb3_contrib/common/maskable/distributions.py
- https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html
- https://stable-baselines3.readthedocs.io/en/master/guide/algos.html
- https://stable-baselines3.readthedocs.io/en/master/guide/custom_env.html
- https://stable-baselines3.readthedocs.io/en/master/guide/rl_tips.html
- https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html
- https://stable-baselines3.readthedocs.io/en/master/misc/changelog.html
- https://stable-baselines3.readthedocs.io/en/master/modules/dqn.html
- https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html
- https://www.cs.utexas.edu/~shivaram/readings/b2hd-NgHR1999.html
- https://www.emergentmind.com/topics/atari-100k-benchmark

</details>

---

# For Document 2 - Zerodha Trading Platform

## Zerodha Kite Connect and pykiteconnect

<sub>1 report(s) &middot; 30 verified &middot; 16 pitfalls &middot; 8 outdated patterns &middot; 29 sources</sub>

### Facts

- **VERIFIED** pykiteconnect is 5.2.1 on PyPI, uploaded 2026-07-23T09:22:52Z; __version__.py on master also says 5.2.1.
  - GitHub releases: v5.1.0 (2026-03-27) added market_protection to place_order/modify_order; v5.2.0 (2026-04-23) added place_autoslice_order(); v5.2.1 (2026-07-23) added algo_id to order params. The only hard breaking change in the 5.x line is v5.0.0 (2023-10-16) dropping Python 2.7. Nothing in 5.1/5.2 breaks 5.0 call sites — they are additive optional kwargs.
- **VERIFIED** The package declares NO python_requires; its classifiers still say Python 3.5/3.6/3.7, but CI (.github/workflows/test.yml) tests matrix [3.8, 3.9, "3.10", "3.11", "3.12"] on ubuntu-22.04 and windows-latest.
  - Python 3.13 is NOT in the tested matrix. Metadata is stale — do not read the classifiers as a support statement.
- **VERIFIED** Empirically on this exact target (Windows 11, CPython 3.13.2): `pip install kiteconnect` succeeds from wheels only — no C compiler needed — resolving kiteconnect 5.2.1, autobahn 19.11.2, Twisted 26.4.0, txaio 26.6.1, pyOpenSSL 26.4.0, cryptography 50.0.0, service_identity 26.1.0, pywin32 312. `from kiteconnect import KiteConnect, KiteTicker` imports cleanly and `autobahn.twisted.websocket` imports fine.
  - I built a venv and ran this. The README's 'needs Visual C++ 14.0 / libffi-dev' instructions are obsolete for Python 3 on Windows — everything ships wheels now.
- **VERIFIED** setup.py hard-pins `autobahn[twisted]==19.11.2` (exact ==, released 2020-01-09, classifiers stop at Python 3.7). Dependabot PR #224 to bump it to 20.12.3 is still open and unmerged.
  - autobahn 19.11.2 puts no upper bound on Twisted, so pip pulls modern Twisted (26.4.0) alongside a 2019 autobahn. It works today, but this is the most brittle dependency in the stack and the reason the whole WebSocket layer is Twisted-based.
- **VERIFIED** KiteConnect (connect.py) is 100% synchronous: zero occurrences of async/await/asyncio/aiohttp in the file. All HTTP goes through a `requests.Session` (`self.reqsession.request(...)`), default timeout 7 seconds, optional `pool` dict mapped onto a requests HTTPAdapter.
  - Signature: KiteConnect(api_key, access_token=None, root=None, debug=False, timeout=None, proxies=None, pool=None, disable_ssl=False). In FastAPI every KiteConnect call MUST go through `await asyncio.to_thread(...)` / `run_in_executor` or a sync `def` endpoint, or it blocks the event loop for the full network round trip.
- **VERIFIED** THE key architectural fact: `kiteconnect/__init__.py` does `from kiteconnect.ticker import KiteTicker`, and ticker.py line 18 does `from twisted.internet import reactor` at module scope. So merely running `from kiteconnect import KiteConnect` installs the default Twisted reactor into the process at import time.
  - Verified empirically: after `import kiteconnect`, `'twisted.internet.reactor' in sys.modules` is True and the reactor is a SelectReactor on Windows. You cannot avoid this by importing only KiteConnect.
- **VERIFIED** Because of that, importing kiteconnect BEFORE `twisted.internet.asyncioreactor.install()` raises `ReactorAlreadyInstalledError: reactor already installed`.
  - Reproduced. If you ever want the asyncio reactor, `asyncioreactor.install()` must be the first thing that touches Twisted, before any `import kiteconnect` anywhere in the import graph — including transitively via your own modules. That is extremely fragile in a FastAPI app.
- **VERIFIED** Twisted's AsyncioSelectorReactor requires a SelectorEventLoop. On Windows/CPython 3.13 the default `asyncio.new_event_loop()` is ProactorEventLoop, and `asyncioreactor.install()` fails with `TypeError: ProactorEventLoop is not supported, got: <ProactorEventLoop ...>`.
  - Reproduced on the target laptop. You must call `asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())` first, which then costs you asyncio subprocess support on Windows. Uvicorn does not do this for you.
- **VERIFIED** Even with asyncioreactor correctly installed first, `reactor.run(installSignalHandlers=False)` from inside a running asyncio loop raises `RuntimeError: Cannot run the event loop while another loop is running` — and `KiteTicker.connect()` calls exactly that whenever `not reactor.running`.
  - Reproduced. ticker.py connect(): `if not reactor.running: if threaded: Thread(target=reactor.run, kwargs={'installSignalHandlers': False}, daemon=True).start() else: reactor.run()`. So `ticker.connect()` can never be called from inside a FastAPI startup coroutine or endpoint on the same loop.
- **VERIFIED** The 'just call reactor.startRunning() and let asyncio drive it' workaround does not work on Twisted 26.4.0: reactor.running flips to True but Twisted timed calls never fire, and `AsyncioSelectorReactor` has no `_scheduleSimulate` attribute to kick the pump.
  - Reproduced: startRunning(installSignalHandlers=False) then reactor.callLater(0.2, ...) inside asyncio.run() — the callback had not fired after 2s. Conclusion: the asyncioreactor cohabitation path is a dead end for this library. Do not build the curriculum on it.
- **VERIFIED** The Twisted reactor is single-shot per process: calling reactor.run() a second time raises `ReactorNotRestartable`. `KiteTicker.stop()` is literally `reactor.stop()`.
  - Reproduced, and it is the root cause of pykiteconnect issue #185 (open since 2023-09-22) against the shipped examples/threaded_ticker.py. Practical consequence: once you call ticker.stop(), that process can never open another KiteTicker. Use ticker.close()/stop_retry() instead, or accept that the ticker process must be restarted.
- **VERIFIED** The only working pattern is a daemon thread plus a thread-safe handoff, or a separate process. `ticker.connect(threaded=True)` runs `reactor.run` in a `threading.Thread(daemon=True)`; `reactor.callFromThread(fn)` bridges into the reactor thread, and `loop.call_soon_threadsafe` / `asyncio.run_coroutine_threadsafe(coro, loop)` bridge back into the FastAPI loop.
  - I ran the threaded-reactor + callFromThread pattern successfully. Python docs (asyncio-dev): 'Almost all asyncio objects are not thread safe'; 'To schedule a callback from another OS thread, the loop.call_soon_threadsafe() method should be used'; 'To schedule a coroutine object from a different OS thread, the run_coroutine_threadsafe() function should be used.' on_ticks fires on the reactor thread — never touch an asyncio.Queue directly from it. Note asyncio.to_thread/run_in_executor solve the REST-client blocking problem, not the ticker problem: the ticker owns a permanent loop, not a one-shot call.
- **VERIFIED** Login flow: GET https://kite.zerodha.com/connect/login?api_key=xxx&v=3 → browser login → request_token on your registered redirect URL → POST /session/token with api_key, request_token, checksum where checksum = SHA-256(api_key + request_token + api_secret) hexdigest.
  - kite.login_url() returns '{login_uri}?api_key={key}&v=3'. generate_session(request_token, api_secret) computes the sha256 itself and auto-calls set_access_token() on success. All later calls send header `Authorization: token api_key:access_token`.
- **VERIFIED** access_token expiry, verbatim from the docs: "Unless this is invalidated using the API, or invalidated by a master-logout from the Kite Web trading terminal, it'll expire at `6 AM` on the next day (regulatory requirement)".
  - So the token is good for the rest of the calendar day plus overnight until 06:00 IST. Persist it (DB/keyring) keyed by date, and treat 6 AM IST as the hard rotation boundary in any scheduler.
- **VERIFIED** There is no non-interactive login path for individual developers. `renew_access_token(refresh_token, api_secret)` exists (POST /session/refresh_token, checksum = SHA-256(api_key + refresh_token + api_secret)), but the docs state refresh_token is "A token for getting long standing read permissions. This is only available to certain approved platforms".
  - For everyone else the browser+TOTP flow must be re-done daily. The library gives you `kite.set_session_expiry_hook(fn)` — it fires on any HTTP 403 with error_type TokenException, which is the correct place to mark the session dead and page the operator. `invalidate_access_token()` and `invalidate_refresh_token()` also exist. Scripted TOTP login exists in the wild but means storing password + TOTP seed on the server; treat it as out-of-scope/at-own-risk.
- **VERIFIED** Rate limits, verbatim from the exceptions page table: Quote 1req/second, Historical candle 3req/second, Order placement 10req/second, All other endpoints 10req/second.
  - Plus the note: "There are limitations at 400 orders per minute and 10 orders per second", "a single user/API key will not be able to place more than 5000 orders per day. This restriction is across all segments and varieties", and "a maximum of 25 modifications are allowed per order. Post that user has to cancel the order and place it again." Rate-limit breach = HTTP 429. The quote 1/s limit is the one that bites — design around the WebSocket, not polling.
- **VERIFIED** place_order exact signature (5.2.1): place_order(variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None, validity=None, validity_ttl=None, disclosed_quantity=None, trigger_price=None, iceberg_legs=None, iceberg_quantity=None, auction_number=None, algo_id=None, tag=None, market_protection=None). modify_order(variety, order_id, parent_order_id=None, quantity=None, price=None, order_type=None, trigger_price=None, validity=None, disclosed_quantity=None, market_protection=None). cancel_order(variety, order_id, parent_order_id=None).
  - The first 7 params are positional-required. place_autoslice_order() takes the identical signature and hits the autoslice endpoint. `algo_id` is in the library as of 5.2.1 but is NOT documented on kite.trade/docs/connect/v3/orders/ yet.
- **VERIFIED** Allowed enum values (docs 'Glossary of constants'): variety = regular | amo | co | iceberg | auction; order_type = MARKET | LIMIT | SL | SL-M; product = CNC | NRML | MIS | MTF; validity = DAY | IOC | TTL; transaction_type = BUY | SELL; exchange = NSE, BSE, NFO, CDS, BCD, MCX. market_protection = >0..100 (custom %) or -1 (auto).
  - The library exposes PRODUCT_MIS/CNC/NRML/CO but has NO PRODUCT_MTF constant — pass the literal string "MTF". VARIETY_BO/bracket orders are gone. iceberg_legs must be 2–50, iceberg_quantity = quantity/iceberg_legs, validity_ttl is in minutes.
- **VERIFIED** `tag` is documented verbatim as "An optional tag to apply to an order to identify it (alphanumeric, max 20 chars)" — 20 characters, alphanumeric only.
  - Directly relevant to idempotency: 20 alnum chars is enough for a base36 UUID-ish key (~13 chars) or a hash prefix, but NOT a full UUID4 (36 chars with hyphens; hyphens are not alphanumeric anyway). The orders response also carries a `tags` array and a `guid` field described as "Unusable request id to avoid order duplication". Kite does NOT offer a client-supplied idempotency key — dedupe is on you.
- **VERIFIED** Order statuses: common terminal/steady states are OPEN, COMPLETE, CANCELLED, REJECTED; documented interim states are PUT ORDER REQ RECEIVED, VALIDATION PENDING, OPEN PENDING, MODIFY VALIDATION PENDING, MODIFY PENDING, TRIGGER PENDING, CANCEL PENDING, AMO REQ RECEIVED.
  - Docs explicitly warn the list is not exhaustive: "An order can traverse through several interim and temporary statuses during its lifetime... Some of these are highlighted below." Also: "Successful placement of an order via the API does not imply its successful execution." Build the state machine as allow-list of terminal states (COMPLETE/CANCELLED/REJECTED) with everything else treated as in-flight — never as an exhaustive enum.
- **VERIFIED** Postback checksum = SHA-256(order_id + order_timestamp + api_secret). The payload is sent as a raw HTTP POST body ("You will have to read the raw body and then decode it"). Trigger statuses are COMPLETE, CANCEL, REJECTED, UPDATE, where UPDATE covers modification and partial fills.
  - No signature header — the checksum is a field inside the JSON. Docs note: "Postback API works even when the user is not logged in." Crucially: "This Postback API is meant for platforms and public apps where a single api_key will place orders for multiple users... For individual developers, Postbacks over WebSocket is recommended, where, orders placed for a particular user anywhere, for instance, web, mobile, or desktop platforms, are sent." That is KiteTicker's on_order_update(ws, data) callback, fired on text frames with data['type'] == 'order'.
- **VERIFIED** Instruments dump: GET https://api.kite.trade/instruments returned HTTP 200 with content-type text/csv and 9,405,746 bytes — 115,290 lines (115,289 instruments) — when I downloaded it live, with no Authorization header at all.
  - 12 columns: instrument_token, exchange_token, tradingsymbol, name, last_price, expiry, strike, tick_size, lot_size, instrument_type, segment, exchange. Docs: "The dump is generated once everyday", "it's best to request it once a day (ideally at around 08:30 AM) and store in a database at your end", and "use a combination of exchange and tradingsymbol as the unique key, not the numeric instrument token. Exchanges may reuse instrument tokens for different derivative instruments after each expiry." ~9.4 MB parsed into Python dicts is roughly 150–250 MB RSS — on an 8 GB laptop, stream it into SQLite instead of holding kite.instruments() in memory.
- **VERIFIED** Quote endpoint caps: /quote max 500 instruments per request; /quote/ohlc max 1000; /quote/ltp max 1000. Instruments are addressed as `exchange:tradingsymbol` strings.
  - Library: quote(*instruments), ohlc(*instruments), ltp(*instruments) — variadic, so both kite.quote('NSE:INFY','NSE:SBIN') and kite.quote(['NSE:INFY',...]) work. Docs warn: "Always check for the existence of a particular key you've requested... If there's no data for the particular instrument or if it has expired, the key will be missing from the response." Combined with the 1 req/s quote limit, 500 instruments/second is your hard polling ceiling.
- **VERIFIED** historical_data(instrument_token, from_date, to_date, interval, continuous=False, oi=False). Documented intervals are exactly 8: minute, day, 3minute, 5minute, 10minute, 15minute, 30minute, 60minute.
  - GET /instruments/historical/:instrument_token/:interval with from/to as 'yyyy-mm-dd hh:mm:ss'. Returns date, open, high, low, close, volume (+ oi when oi=1). continuous=1 gives stitched futures series. The library does NO chunking — you must loop.
- **VERIFIED** Per-request day caps (Zerodha staff, official forum): minute 60, 3minute 100, 5minute 100, 10minute 100, 15minute 200, 30minute 200, 60minute 400, day 2000. Exceeding it returns an error literally shaped like 'interval exceeds max limit: 60 days'. Undocumented intervals the API also accepts: 2minute (60), 4minute (100), hour/2hour/3hour/4hour (400), week (2000).
  - These caps appear nowhere on kite.trade/docs/connect/v3/historical/ — only in staff forum replies. Depth: staff state "for minute level data it starts somewhere around early 2015" and "There is no fixed date for day candle data" / "For some NSE stocks, day candles are back filled till late 1990s". Combined with the 3 req/s historical limit: one instrument's full minute history since 2015 is ~70 requests ≈ 24s minimum. Backfilling a few hundred symbols is an hours-long batch job — design it as a resumable job, not a request handler.
- **VERIFIED** Historical data no longer costs extra. Zerodha's live pricing page shows two tiers: 'Personal (Free)' — "Full fledged order, GTT, alerts management. Margin computation, portfolio management etc." — and 'Connect' — "Full suite of APIs with realtime WebSocket streaming and historical candle data for ₹ 500 / month".
  - Zerodha's support FAQ confirms: "₹500/month per API key", and on historical + live market data, "Both are included at no additional cost with the paid Kite Connect plan" — though "you must subscribe to Kite Connect first before you can access the historical API". The free Personal tier can place and manage orders but gets NO market data (no WebSocket, no historical) — usable for an order-execution-only teaching module at zero cost.
- **VERIFIED** KiteTicker WebSocket: wss://ws.kite.trade with api_key + access_token query params. Docs: max 3000 instruments on a single connection, and "Single API key can have upto 3 websocket connections" — so 9000 instruments max per api_key.
  - Wire protocol: {"a":"subscribe","v":[tokens]}, {"a":"unsubscribe","v":[tokens]}, {"a":"mode","v":["full",[tokens]]}. Python: subscribe(list), unsubscribe(list), set_mode(mode, list); MODE_LTP='ltp', MODE_QUOTE='quote', MODE_FULL='full'; default mode on subscribe is quote. A 1-byte heartbeat arrives every few seconds and can be ignored. KiteTicker(api_key, access_token, debug=False, root=None, reconnect=True, reconnect_max_tries=50, reconnect_max_delay=60, connect_timeout=30); min reconnect delay 5s, max tries 300, exponential backoff.
- **VERIFIED** Binary packet sizes and exact per-mode fields (from ticker.py _parse_binary): LTP = 8 bytes → instrument_token, last_price (+tradable, mode). Quote = 44 bytes → adds last_traded_quantity, average_traded_price, volume_traded, total_buy_quantity, total_sell_quantity, ohlc{open,high,low,close}, change. Full = 184 bytes → adds last_trade_time, oi, oi_day_high, oi_day_low, exchange_timestamp, depth{buy:[{quantity,price,orders}×5], sell:[...×5]}.
  - Indices use different packets: 28 bytes (quote) / 32 bytes (full, adds exchange_timestamp) with tradable=False, ohlc and change but no volume/depth. Prices are integers divided by 100, except CDS segment /10000000 and BCD /10000 — segment is derived from the low 8 bits of instrument_token via EXCHANGE_MAP {nse:1, nfo:2, cds:3, bse:4, bfo:5, bcd:6, mcx:7, mcxsx:8, indices:9}. One WebSocket frame packs many packets; the library unpacks them into a list passed to on_ticks.
- **VERIFIED** KiteTicker callbacks: on_ticks(ws, ticks), on_connect(ws, response), on_close(ws, code, reason), on_error(ws, code, reason), on_reconnect(ws, attempts_count), on_noreconnect(ws), on_open(ws), on_message(ws, payload, is_binary), on_order_update(ws, data).
  - They are assigned as plain attributes (ticker.on_ticks = fn), not registered via decorator, and every one of them executes on the Twisted reactor thread. resubscribe() replays the stored subscribed_tokens dict, and _on_open auto-resubscribes after a reconnect.
- **VERIFIED** Zerodha still offers no sandbox. Its own support article states: "No, Zerodha does not offer an API sandbox environment, but Zerodha offers Kite Connect API."
  - There is no paper-trading or simulated-fill endpoint. For a curriculum this means: build your own fake broker behind an interface (replay historical candles over a local WebSocket, simulate fills), and reserve the live api_key for a read-only/1-share smoke test. Zerodha does publish zerodha/kiteconnect-mocks on GitHub with sample response payloads you can fixture against.

### Pitfalls you will actually hit

- Symptom: your FastAPI app hangs or throughput collapses under two concurrent users. Cause: every KiteConnect method is blocking `requests` with a 7-second default timeout; calling kite.quote()/place_order() directly in an `async def` endpoint stalls the whole event loop. Fix: `await asyncio.to_thread(kite.place_order, ...)` or declare the endpoint as plain `def` so Starlette runs it in the threadpool.
- Symptom: `RuntimeError: Cannot run the event loop while another loop is running` (or the app just freezes) when you call ticker.connect() from a FastAPI startup/lifespan handler. Cause: KiteTicker.connect() calls twisted's reactor.run(). Fix: connect(threaded=True) from a non-async context, or run the ticker in its own process.
- Symptom: `twisted.internet.error.ReactorNotRestartable` on the second connect — this is the shipped examples/threaded_ticker.py failing, open as pykiteconnect issue #185 since 2023. Cause: a Twisted reactor can be run exactly once per process and KiteTicker.stop() calls reactor.stop(). Fix: never call stop() unless you are tearing the process down; use close()/stop_retry() and let the built-in reconnect handle drops.
- Symptom: `twisted.internet.error.ReactorAlreadyInstalledError: reactor already installed` the moment you try asyncioreactor.install(). Cause: `import kiteconnect` alone installs the default reactor, because __init__.py imports ticker.py which imports twisted.internet.reactor at module scope. There is no import of KiteConnect that avoids pulling in Twisted.
- Symptom (Windows-only): `TypeError: ProactorEventLoop is not supported`. Cause: Twisted's asyncioreactor needs a SelectorEventLoop but Windows/CPython 3.13 defaults to ProactorEventLoop. Even after forcing WindowsSelectorEventLoopPolicy, reactor.startRunning() does not pump Twisted timed calls on Twisted 26.4.0 — abandon the shared-loop idea entirely.
- Symptom: ticks silently stop being processed, or you get 'attached to a different loop' errors. Cause: on_ticks runs on the Twisted reactor thread and you touched an asyncio.Queue / awaited something from it. Fix: from on_ticks use only loop.call_soon_threadsafe(q.put_nowait, tick) or asyncio.run_coroutine_threadsafe(coro, loop) — capture the loop object once at startup.
- Symptom: HTTP 429 on a dashboard that refreshes every second for 3 symbols. Cause: /quote is capped at 1 request per second for the whole api_key, not per symbol. Fix: batch up to 500 instruments into one quote() call, or use the WebSocket, which is what it exists for.
- Symptom: your order tag is silently truncated or the order is rejected. Cause: tag is capped at 20 alphanumeric characters — a UUID4 string will not fit and hyphens are not alphanumeric. Fix: base36/hex-encode a short hash and keep the full idempotency key in your own DB, joined on the returned order_id.
- Symptom: place_order() returns an order_id and you assume the trade happened. The docs are explicit: "Successful placement of an order via the API does not imply its successful execution." You must poll order_history/orders or subscribe to order updates; and the status enum is explicitly non-exhaustive, so treat anything that is not COMPLETE/CANCELLED/REJECTED as still in flight.
- Symptom: your 6:05 AM cron works for a week then everything 403s. Cause: access_token expires at 6 AM IST the next day and there is no unattended renewal for individual developers (refresh_token is approved-platforms-only). Fix: register kite.set_session_expiry_hook() to fail loudly, store the token with its issue date, and accept a daily manual browser login.
- Symptom: kite.instruments() spikes memory and the laptop starts swapping. The live dump today is 9.4 MB of CSV / 115,289 rows; materialising it as Python dicts costs hundreds of MB on an 8 GB machine. Fix: fetch the raw CSV (it is served unauthenticated at https://api.kite.trade/instruments) and COPY it straight into SQLite/Postgres once a day around 08:30 IST.
- Symptom: your instrument_token→symbol mapping silently points at the wrong contract after an expiry. Docs: "Exchanges may reuse instrument tokens for different derivative instruments after each expiry." Key your own tables on (exchange, tradingsymbol), never on the numeric token.
- Symptom: 'interval exceeds max limit: 60 days' from historical_data. The per-interval day caps (60/100/200/400/2000) are documented nowhere in the official docs — only in forum replies — so you will discover them at runtime. The library does no chunking; write the windowing loop yourself and rate-limit it to 3 req/s.
- Symptom: keys missing from your quote() response dict and a KeyError in production. Docs: "If there's no data for the particular instrument or if it has expired, the key will be missing from the response." Always .get() and reconcile against what you asked for.
- Symptom: postbacks never arrive during development. They require a publicly reachable HTTPS postback_url registered on the app, and for a single-developer setup the docs actually steer you to WebSocket order updates (on_order_update) instead. Also note the postback checksum is a JSON field, not a header, and is SHA-256(order_id + order_timestamp + api_secret) — the timestamp is the order_timestamp string exactly as it appears in the payload.
- Symptom: you build against Python 3.13 and hit a dependency wall later. It installs and imports fine today (I verified 5.2.1 on 3.13.2/Windows), but 3.13 is outside the project's CI matrix (3.8–3.12) and the stack hangs on a hard-pinned autobahn==19.11.2 from 2019. Pin your venv to 3.12 for anything you intend to keep running.

### Outdated - distrust any tutorial that says these

- Historical data as a separate paid add-on is gone. Older tutorials say Kite Connect is ₹2000/month plus a ₹2000/month historical data subscription. Today Zerodha's own page lists one paid tier: 'Connect' at ₹500/month, described as 'Full suite of APIs with realtime WebSocket streaming and historical candle data', and the support FAQ says live + historical data are 'included at no additional cost'.
- There is now a free 'Personal' tier (orders, GTT, alerts, margins, portfolio — no market data). Guides written before this claim you must pay to touch the API at all; you can now learn the whole order/portfolio surface for ₹0.
- Bracket Orders (variety='bo', PRODUCT_BO) are discontinued and no longer appear in the docs' glossary of constants. Cover Orders (variety='co') survive. New varieties added since most tutorials: iceberg and auction. New product: MTF (Margin Trading Facility) — note the library has no PRODUCT_MTF constant, pass the string.
- Python 2.7 support was removed in pykiteconnect 5.0.0 (2023-10-16). Any tutorial using `from kiteconnect import KiteConnect` with print statements or six-based py2 idioms is dead; install kiteconnect>=5.
- The library's own README install instructions (Visual C++ 14.0 for Python 3.5-3.6, apt-get libffi-dev, xcode-select) are obsolete on Python 3 — I installed 5.2.1 on Windows/3.13 from wheels only, no compiler. The README's version table stops at Python 3.4.
- New order parameters most material predates: market_protection (added in 5.1.0, Mar 2026 — percentage 0-100 or -1 for auto, applies only to MARKET and SL-M), autoslice / place_autoslice_order() (5.2.0, Apr 2026 — auto-splits orders above exchange freeze limits), and algo_id (5.2.1, Jul 2026 — in the library but not yet in the web docs).
- Advice to 'just poll kite.quote() in a loop' is now actively harmful: the quote endpoint is rate-limited to 1 request/second per api_key. The intended design is one WebSocket connection carrying up to 3000 instruments.
- 'Use twisted's asyncioreactor to run KiteTicker inside FastAPI' — occasionally suggested in forum threads — does not work on the current stack. I verified three independent blockers: importing kiteconnect pre-installs the default reactor (ReactorAlreadyInstalledError), Windows defaults to ProactorEventLoop (TypeError), and reactor.run() inside a live loop raises RuntimeError while startRunning() alone never pumps timed calls. Thread-plus-queue or a separate process are the only real options.

<details>
<summary>Sources (29)</summary>

- Local empirical verification in a Python 3.13.2 venv on Windows 11 (scratchpad: C:\Users\Satyum\AppData\Local\Temp\claude\d--Projects-MyGit\b8a2c5c2-62b4-418e-bee1-4aaa990734d5\scratchpad\kcenv) — kiteconnect 5.2.1 install, import-time reactor installation, ReactorAlreadyInstalledError, ProactorEventLoop TypeError, RuntimeError from reactor.run() inside a live asyncio loop, ReactorNotRestartable, and the working threaded-reactor + callFromThread pattern
- https://api.github.com/repos/zerodha/pykiteconnect/releases
- https://api.kite.trade/instruments
- https://docs.python.org/3/library/asyncio-dev.html
- https://docs.twisted.org/en/stable/api/twisted.internet.asyncioreactor.html
- https://github.com/zerodha/pykiteconnect
- https://github.com/zerodha/pykiteconnect/issues/185
- https://kite.trade/docs/connect/v3/
- https://kite.trade/docs/connect/v3/exceptions/
- https://kite.trade/docs/connect/v3/historical/
- https://kite.trade/docs/connect/v3/market-quotes/
- https://kite.trade/docs/connect/v3/orders/
- https://kite.trade/docs/connect/v3/postbacks/
- https://kite.trade/docs/connect/v3/user/
- https://kite.trade/docs/connect/v3/websocket/
- https://kite.trade/forum/discussion/14149/historical-data-retention-policy
- https://kite.trade/forum/discussion/comment/26514/
- https://pypi.org/project/kiteconnect/
- https://pypi.org/pypi/autobahn/19.11.2/json
- https://pypi.org/pypi/kiteconnect/json
- https://raw.githubusercontent.com/zerodha/pykiteconnect/master/.github/workflows/test.yml
- https://raw.githubusercontent.com/zerodha/pykiteconnect/master/kiteconnect/__init__.py
- https://raw.githubusercontent.com/zerodha/pykiteconnect/master/kiteconnect/__version__.py
- https://raw.githubusercontent.com/zerodha/pykiteconnect/master/kiteconnect/connect.py
- https://raw.githubusercontent.com/zerodha/pykiteconnect/master/kiteconnect/ticker.py
- https://raw.githubusercontent.com/zerodha/pykiteconnect/master/setup.py
- https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/api-sandbox
- https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs
- https://zerodha.com/products/api/

</details>

---

## Python Async Backend Stack

<sub>2 report(s) &middot; 44 verified, 4 likely &middot; 32 pitfalls &middot; 38 outdated patterns &middot; 101 sources</sub>

### Facts

- **VERIFIED** FastAPI current stable is 0.141.1 (released 2026-07-29); requires Python >=3.10, starlette>=0.46.0, pydantic>=2.9.0, typing-extensions>=4.8.0.
  - FastAPI is still pre-1.0 and ships breaking-ish changes in minor bumps, so pin exactly in uv.lock. Note the floor is pydantic 2.9 — there is no Pydantic v1 path any more.
- **VERIFIED** Startup/shutdown must use the `lifespan` async context manager; `@app.on_event("startup"/"shutdown")` is deprecated and is silently ignored if a lifespan is provided.
  - Docs: "If you provide a `lifespan` parameter, `startup` and `shutdown` event handlers will no longer be called. It's all `lifespan` or all events, not both." Pattern: `@asynccontextmanager async def lifespan(app: FastAPI): ...setup...; yield; ...teardown...` then `app = FastAPI(lifespan=lifespan)`. This is where the async engine and redis pool are created and disposed.
- **VERIFIED** `Annotated[T, Depends(...)]` is the documented-preferred dependency style; docs say verbatim "Prefer to use the `Annotated` version if possible." Same applies to `Query()`, `Header()`, `Path()`, `Form()`.
  - Lets you alias dependencies once — `SessionDep = Annotated[AsyncSession, Depends(get_session)]` — and keeps the real return type visible to mypy/ty. The old `db: AsyncSession = Depends(get_session)` form lies to the type checker about the default value.
- **VERIFIED** FastAPI ships a CLI (`fastapi[standard]`): `fastapi dev` (reload, binds 127.0.0.1, sets FASTAPI_ENV=development) and `fastapi run` (no reload, binds 0.0.0.0). The app location can be declared in pyproject.toml as `[tool.fastapi]` / `entrypoint = "app.main:app"`.
  - Replaces hand-typed `uvicorn app.main:app --reload`. The pyproject entrypoint key is recent and is not in most tutorials.
- **VERIFIED** Recommended layout for a non-toy app (official 'Bigger Applications' guide): `app/{__init__.py,main.py,dependencies.py,routers/{items.py,users.py},internal/admin.py}`, with `APIRouter(prefix=..., tags=[...], dependencies=[Depends(...)], responses={...})` per router and `app.include_router(...)` in main.py.
  - `prefix` must not end in `/`. Router-level `dependencies=[...]` run for every route in that router and their return values are discarded — use them for auth/rate-limit gates, not for injecting a session.
- **VERIFIED** `BackgroundTasks` runs in the same process as the app; the official caveat directs you to a real queue (Celery et al.) for heavy work, and it has no retries, no persistence, and dies with the worker.
  - Docs: use BackgroundTasks only for "small background tasks (like sending an email notification)" or when you need in-process variables. For a trading platform, anything touching a broker API or a fill reconciliation belongs in a durable queue.
- **VERIFIED** FastAPI WebSockets: `@app.websocket("/ws")`, `await ws.accept()/receive_text()/send_text()`, catch `WebSocketDisconnect`, raise `WebSocketException(code=status.WS_1008_POLICY_VIOLATION)`; `Depends/Security/Cookie/Header/Path/Query` all work in websocket endpoints. Requires the `websockets` package.
  - Docs explicitly warn the in-memory `ConnectionManager` broadcast pattern "only works while the process is running, and only with a single process" and point to encode/broadcaster (Redis/Postgres backend) for real fan-out. Critical for a live-quote UI behind more than one uvicorn worker.
- **VERIFIED** Pydantic current stable is 2.13.4 (2026-05-06); pydantic-settings is a separate package, current 2.15.0 (2026-08-07), imported as `from pydantic_settings import BaseSettings, SettingsConfigDict`.
  - `BaseSettings` was removed from the `pydantic` namespace in v2. SettingsConfigDict keys you actually need: `env_file`, `env_prefix`, `env_nested_delimiter='__'`, `extra`.
- **VERIFIED** Pydantic v2 renames, all with the v1 names still present but emitting DeprecationWarning: `class Config`→`model_config = ConfigDict(...)`, `orm_mode`→`from_attributes`, `@validator`→`@field_validator`, `@root_validator`→`@model_validator`, `.dict()`→`.model_dump()`, `.json()`→`.model_dump_json()`, `parse_obj`→`model_validate`, `parse_raw`→`model_validate_json`, `allow_population_by_field_name`→`populate_by_name`.
  - Docs: "we have retained the deprecated methods with their old names to help ease migration, but calling them will emit DeprecationWarnings." Run pytest with `-W error::DeprecationWarning` to flush these out of a tutorial-derived codebase.
- **VERIFIED** `@field_validator` requires `@classmethod` directly beneath it and supports mode='before'|'after'(default)|'wrap'|'plain'; `@model_validator(mode='after')` is an *instance* method taking and returning `self` (`-> Self`), while mode='before'/'wrap' are classmethods.
  - Decorator order matters: `@field_validator(...)` on top, `@classmethod` under it. Getting the model_validator 'after' form wrong (writing it as a classmethod taking `cls, values`) is the single most common v1→v2 porting bug.
- **VERIFIED** `@computed_field` includes a property in serialization output; it implicitly converts the method to a property but docs say "it is preferable to explicitly use the `@property` decorator for type checking purposes."
  - Use for derived response values (e.g. `pnl_pct`) so they appear in `model_dump()` and in the OpenAPI schema without storing them.
- **VERIFIED** SQLAlchemy current stable is 2.0.52 (2026-08-11). 2.1 is still beta — 2.1.0b3 (2026-06-27). Do not build a curriculum on 2.1 yet.
  - 2.1 will change the default PostgreSQL driver from psycopg2 to psycopg (v3), stop installing the asyncio `greenlet` dependency by default (you must install the `[asyncio]` extra), represent `Row` column types via PEP 646, and add `tstring()` for Python 3.14 t-strings.
- **VERIFIED** Async ORM shape: `create_async_engine("postgresql+asyncpg://user:pass@host/db")` + `async_sessionmaker(engine, expire_on_commit=False)` + `async with async_session() as session:`. `sessionmaker(class_=AsyncSession)` is the superseded form.
  - `expire_on_commit=False` is not optional in practice: with the default True, every attribute access after `await session.commit()` triggers a refresh, which is I/O, which is exactly what async forbids.
- **VERIFIED** Lazy loading is structurally broken under asyncio because "any programming statement that can potentially result in IO being invoked must have an `await` call" — an unloaded relationship or expired column attribute would do IO with no await. Fixes, in order of preference: `select(A).options(selectinload(A.bs))`, `relationship(..., lazy="raise")` to make the mistake loud, or the `AsyncAttrs` mixin with `await obj.awaitable_attrs.bs` (added 2.0.13).
  - `lazy="raise"` on every relationship in the models is the highest-value habit for an async codebase — it converts a runtime greenlet error deep in a serializer into an immediate, obvious failure at the query site.
- **VERIFIED** The ORM `Query` object is officially legacy: "The ORM Query object is a legacy construct as of SQLAlchemy 2.0." It is not being removed — it now translates itself into a 2.0-style `select()` internally — but new code uses `select()` + `session.execute()` / `session.scalars()`.
  - `session.query(X)` does not exist on `AsyncSession` in a usable way anyway; the async API is `result = await session.execute(select(X).where(...)); rows = result.scalars().all()`.
- **VERIFIED** Alembic current stable is 1.17.1 (2025-10-29). Async projects must bootstrap with `alembic init -t async <dir>` (there is also a newer `pyproject_async` template); the async env.py wraps the sync migration API via `connection.run_sync(...)`.
  - Running the default (sync) template against a `postgresql+asyncpg://` URL fails immediately. Autogenerate limits worth teaching: it does not detect column *type* changes unless `compare_type=True`, does not detect server-default changes unless `compare_server_default=True`, sees a rename as drop+add, and ignores anything not attached to `target_metadata`.
- **VERIFIED** PostgreSQL current stable is 18.6 (released 2026-08-13, alongside 17.11/16.15/15.19/14.24 and PostgreSQL 19 Beta 3). PostgreSQL 14 goes EOL 2026-11-12.
  - That 2026-08-13 set fixed 28 security vulnerabilities, so a curriculum should teach pinning a minor and patching, not `postgres:latest`.
- **VERIFIED** TimescaleDB current release is 2.29.1 (2026-08-04); 2.29.0 removed PostgreSQL 15 support, so it supports PG 16/17/18 only. Licensing is unchanged dual-license: Apache 2.0 for the OSS edition, Timescale/Tiger License (TSL, effective 2025-06-17 under the TigerData rename) for Community Edition.
  - The features you would actually adopt TimescaleDB *for* are all TSL, not Apache-2: columnstore/Hypercore compression (`convert_to_columnstore`, `add_columnstore_policy`), continuous aggregates, retention policies and background jobs, and gapfill hyperfunctions (`time_bucket_gapfill`, `locf`, `interpolate`). TSL is free to self-host; it only forbids offering it as a hosted DBaaS.
- **VERIFIED** redis-py current is 8.1.0 (2026-07-30), Python >=3.10, supporting Redis 7.2 through 8.8. The async client is built in: `import redis.asyncio as redis`. aioredis is dead — its repo was archived 2023-02-21 with the notice "Aioredis is now in redis-py 4.2.0rc1+".
  - There is no async `__del__` in Python, so you must `await client.aclose()` explicitly (the older `close()` is deprecated). Install `redis[hiredis]` (hiredis>=3.2.0) for the compiled parser — free speedup, zero code change.
- **VERIFIED** Worker landscape as of now: Celery 5.6.3 (2026-03-26) has still no native `async def` task support; arq 0.28.0 (2026-04-16) is explicitly "in maintenance only mode" per its README (issue #510); Dramatiq 2.2.0 (2026-06-17) has had asyncio support since 1.15.0 and documented it in 2.0.0; TaskIQ 0.12.4 (2026-05-08) is async-native by design with Redis/NATS/RabbitMQ/Kafka brokers and FastAPI DI integration; RQ 2.11.0 (2026-08-17) is very actively released but fork-per-job and sync; APScheduler stable is 3.11.3 (2026-06-28) while 4.0 is still alpha (4.0.0a6, 2025-04-27).
  - Recommendation for a small single-machine trading platform: TaskIQ as the queue (async-native, so broker-API calls and asyncpg writes inside a task need no `asyncio.run()` wrapper, and it reuses your FastAPI dependencies), with Dramatiq 2.x as the conservative alternative if you value maturity over async ergonomics. Use APScheduler 3.11.x — not 4.0 — for market-open/close cron, or TaskIQ's own scheduler. Actively avoid arq (maintenance-only, the historical FastAPI-tutorial pick) and Celery (no native async, prefork memory cost on 8 GB).
- **VERIFIED** Auth: PyJWT 2.13.0 (2026-05-21) is the current pick — the official FastAPI OAuth2-JWT tutorial now runs `uv add pyjwt` and `import jwt / from jwt.exceptions import InvalidTokenError`. python-jose (3.5.0, 2025-05-28) is effectively abandoned upstream and was hit by CVE-2024-33663 (algorithm confusion) and CVE-2024-33664 (JWE decompression bomb DoS), both fixed only in 3.4.0.
  - Every FastAPI auth tutorial older than ~2024 installs python-jose[cryptography]. FastAPI's own docs moved off it.
- **VERIFIED** Password hashing: passlib's last release is 1.7.4 (2020-10-08) and it is unmaintained; the FastAPI tutorial now uses `uv add "pwdlib[argon2]"` / `from pwdlib import PasswordHash`. pwdlib is at 0.3.1 (2026-08-12). Direct alternatives: bcrypt 5.0.0 (2025-09-25) or argon2-cffi 25.1.0 (2025-06-03).
  - Two concrete traps: passlib 1.7.4 + bcrypt >=4.1 produces `AttributeError: module 'bcrypt' has no attribute '__about__'` (trapped, logged as a warning, sometimes fatal); and bcrypt 5.0.0 now "raises a ValueError" for passwords over 72 bytes instead of silently truncating. passlib also breaks on Python 3.13+ where the stdlib `crypt` module was removed.
- **VERIFIED** Testing stack: pytest 9.1.1 (2026-06-19); pytest-asyncio 1.4.0 (2026-05-26) — the `event_loop` fixture was **removed** in 1.0.0; config keys are `asyncio_mode` (default `strict`), `asyncio_default_test_loop_scope` (default `function`), `asyncio_default_fixture_loop_scope` (defaults to the fixture's own scope), `asyncio_debug` (added 1.2.0); custom loops now go through the `pytest_asyncio_loop_factories` hook.
  - In pyproject.toml: `[tool.pytest.ini_options]` with `asyncio_mode = "auto"` (so you can drop the per-test marker) and an explicit `asyncio_default_fixture_loop_scope = "session"` if you want one engine per test session.
- **VERIFIED** Async app testing is `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`. httpx stable is 0.28.1 (2024-12-06) — 1.0 is still only dev pre-releases. The `app=...` shortcut was deprecated in 0.27.0 and **removed** in 0.28.0.
  - FastAPI docs also warn that `AsyncClient` does *not* run lifespan events — wrap with `LifespanManager` from asgi-lifespan if your engine/redis pool is created in lifespan, otherwise every test sees `None`. `TestClient` still works for sync tests but "uses internal magic that doesn't work inside async functions".
- **VERIFIED** Supporting test libs: respx 0.23.1 (2026-04-08) for mocking outbound httpx (broker/market-data APIs); testcontainers 4.15.0 (2026-07-24) for a real Postgres in Docker; pytest-postgresql 8.1.0 (2026-05-15) as the lighter, psycopg3-based, sync-fixture alternative; time-machine 3.4.0 (2026-08-10) vs freezegun 1.5.5 (2025-08-09).
  - For a trading platform, prefer time-machine — it patches at the C level rather than swapping datetime classes, so it is far faster in tight loops and does not confuse `isinstance` checks. On an 8 GB laptop, pytest-postgresql (local postgres binary) is materially cheaper than spinning testcontainers per session.
- **VERIFIED** Observability versions: structlog 26.1.0 (2026-06-06); opentelemetry-sdk 1.44.0 (2026-07-16) with instrumentation packages on the separate 0.x beta track — opentelemetry-instrumentation-fastapi 0.65b0 (2026-07-16); prometheus-client 0.26.0 (2026-07-24); prometheus-fastapi-instrumentator 8.1.0 (2026-07-26); Prometheus server 3.13.2 (2026-07-29); Grafana Loki 3.7.6 (2026-08-06).
  - The instrumentation packages are still versioned 0.NNbN and must be pinned in lockstep with the 1.x SDK (SDK 1.44.0 ↔ instrumentation 0.65b0); mixing generations gives import errors. Zero-code path: install `opentelemetry-distro` + `opentelemetry-exporter-otlp`, run `opentelemetry-bootstrap -a install`, then launch via `opentelemetry-instrument fastapi run` — note the docs flag that bootstrap has known friction under uv.
- **VERIFIED** Packaging/tooling: uv 0.12.5 (2026-08-14) — official docs position it as "a single tool to replace pip, pip-tools, pipx, poetry, pyenv, twine, virtualenv, and more", workflow `uv init` / `uv add` / `uv lock` / `uv sync` / `uv run` with pyproject.toml + a universal uv.lock. Ruff 0.16.3 (2026-08-13) — `ruff format` is a documented drop-in Black replacement (>99.9% identical lines on Django/Zulip).
  - Ruff still needs two commands: `ruff check --select I --fix` for import sorting, then `ruff format`; a unified command is only planned. On a 4-core laptop, uv + ruff are the single biggest quality-of-life wins in this whole stack.
- **VERIFIED** Type checkers: mypy stable is 2.3.1 (2026-08-15). mypy 2.0 (2026-05-06) changed defaults — `--local-partial-types` on by default, `--strict-bytes` on by default (bytearray/memoryview no longer assignable to bytes), `--allow-redefinition` now means the newer permissive semantics, Python 3.9 targets dropped, SQLite cache and a native parser by default, plus experimental `--num-workers N` parallel checking claiming "up to 5x" on 8 workers. Astral's `ty` is still beta at 0.0.72 (2026-08-14) with no stable API; Meta's pyrefly reached 1.2.0 and is marked Production/Stable (default checker for Instagram's ~20M-line codebase, used by PyTorch and JAX).
  - For a curriculum: mypy 2.x is the safe default (and `--num-workers` makes it tolerable on the Ryzen 3); pyrefly is a credible fast second opinion; ty should be treated as a preview, not a dependency.
- **VERIFIED** Driver/server versions: asyncpg 0.31.0 (2025-11-24) supports PostgreSQL 9.5–18 and Python 3.9–3.14; uvicorn 0.52.3 (2026-08-13).
  - asyncpg's README claims ~5x psycopg3 throughput. Note asyncpg does its own statement caching, which is what breaks against PgBouncer in transaction mode — set `statement_cache_size=0` or use `NullPool` if a pooler is in front.
- **VERIFIED** PostgreSQL 18 is the current stable major; latest minor is 18.6, released 2026-08-13. PostgreSQL 19 is at Beta 3 (2026-08-13), not GA.
  - Supported lines as of 2026-08-13: 18.6, 17.11, 16.15, 15.19, 14.24 (14 EOL 2026-11-12). Choosing 'PostgreSQL 18' for the curriculum is correct today, and PG19 will not be a production option during the course. Source: https://www.postgresql.org/
- **VERIFIED** DuckDB 1.5.5 was released 2026-07-22 — the version number and date in the claim are correct.
  - Sixth patch in the 1.5 'Variegata' line; bugfixes, performance improvements and security patches. PyPI `duckdb` 1.5.5 requires Python >=3.10 and ships cp310–cp314 win_amd64 wheels, so `pip install duckdb` is a single binary wheel on this Windows laptop. Sources: https://duckdb.org/2026/07/22/announcing-duckdb-155 , https://pypi.org/pypi/duckdb/json
- **VERIFIED** CORRECTION to the claim's implicit stability framing: DuckDB 1.5.x is NOT an LTS line. 1.4.x is the LTS ('Andium'), and it reaches end of life 2026-09-16. The next LTS is 2.0.0, targeted Fall 2026.
  - DuckDB makes every other minor an LTS with one year of community support. For a multi-month curriculum, pinning 1.5.5 means you will be asked to move to 2.0.0 within months; 1.4.5 LTS expires next month. Next scheduled patch is 1.5.6 on 2026-09-16. Source: https://duckdb.org/release_calendar
- **VERIFIED** CORRECTION: 'TimescaleDB pins you to a PG major it supports' overstates the lag. TimescaleDB 2.29.1 (2026-08-04) supports PostgreSQL 16, 17 and 18 — i.e. it is current with the newest stable Postgres.
  - 2.29.0 removed PG15 support (deprecation announced in 2.28.0, June 2026). The 'no PG19' point is trivially true only because PG19 is still beta. The real, defensible version-coupling cost is the *drop* cadence: a supported PG major gets removed roughly annually, forcing an upgrade on Timescale's schedule, not yours. Source: https://github.com/timescale/timescaledb/releases
- **VERIFIED** On Windows specifically, TimescaleDB binaries lag the source releases: the official Windows install page still links TimescaleDB 2.26.2 zips for PG15/16/17/18, while the current release is 2.29.1.
  - This is the single strongest concrete argument for the claim's recommendation on THIS machine. A Nov-2025 feature request (issue #8935, now closed) recorded that Windows users on PG18 had to either stay on PG17 or build from source. Windows prereqs also include OpenSSL 3.x and the VC++ 2015 redistributable. Sources: https://github.com/timescale/docs/blob/latest/self-hosted/install/installation-windows.md , https://github.com/timescale/timescaledb/issues/8935
- **VERIFIED** The 'TSL-gated' part of the claim is verified: continuous aggregates (src/continuous_aggs/), compression (src/compression/), and time-series query optimization (src/nodes/) live under the Timescale License, not Apache 2.0.
  - Hypertables and time_bucket remain Apache 2.0. TSL is source-available and FREE for internal use and for embedding in value-added products; the prohibition is on offering it as time-sharing/DBaaS, and deployments must be called 'TimescaleDB Community Edition'. So 'TSL-gated' means a licence restriction, not a paywall — do not teach it as 'you have to pay for continuous aggregates'. Sources: https://raw.githubusercontent.com/timescale/timescaledb/main/tsl/README.md , https://www.tigerdata.com/legal/licenses
- **VERIFIED** BRIN on the timestamp column is the right index choice for an append-only tick/OHLCV table, and PostgreSQL's own docs justify it.
  - BRIN stores summary info per block range for columns with 'some natural correlation with their physical location within the table' (the docs' own example is a date column where earlier orders appear earlier in the table). It is lossy — the executor rechecks tuples — but 'a BRIN index is very small, scanning the index adds little overhead compared to a sequential scan'. Source: https://www.postgresql.org/docs/18/brin.html
- **VERIFIED** PostgreSQL 18 still has NO automatic partition creation — declarative partitioning requires you to create each partition manually or generate the DDL yourself.
  - Docs: 'Inserting data into the parent table that does not map to one of the existing partitions will cause an error; an appropriate partition must be added manually', and recommend writing a script to generate monthly DDL. The curriculum must budget for a partition-maintenance job (pg_partman, or a cron/APScheduler task) as part of the 'operational store' module. Source: https://www.postgresql.org/docs/18/ddl-partitioning.html
- **VERIFIED** PostgreSQL 18 did materially improve many-partition workloads: partitionwise joins are enabled in more cases with reduced memory usage, planning across many partitions is more efficient, and VACUUM/ANALYZE now process inheritance children with a new ONLY option.
  - Reduced planner memory for partitionwise joins is directly relevant on 8 GB. Note autovacuum still does not process the partitioned parent itself. Source: https://www.postgresql.org/docs/18/release-18.html
- **VERIFIED** PostgreSQL 18's headline async I/O will NOT be the fast path on this Windows laptop: io_method defaults to `worker`, and `io_uring` requires a build with --with-liburing/-Dliburing (a Linux facility).
  - io_method is settable only at server start; values are worker (default), io_uring, sync. Teaching PG18 AIO benchmarks copied from Linux blog posts will not reproduce on Windows. Source: https://www.postgresql.org/docs/18/runtime-config-resource.html
- **VERIFIED** The 'in-process, zero external dependencies, no server' description of DuckDB is verbatim correct.
  - 'DuckDB does not run as a separate process, but completely embedded within a host process'; 'DuckDB has no external dependencies, neither for compilation nor during run-time'; 'there is no DBMS server software to install, update and maintain.' Source: https://duckdb.org/why_duckdb
- **VERIFIED** CORRECTION to 'no server RAM budget': DuckDB defaults memory_limit to 80% of physical RAM and threads to the CPU core count — on this 8 GB machine that is ~6.4 GB, which will fight Postgres and the browser unless explicitly capped.
  - Config defaults: memory_limit = '80% of RAM', threads = '# CPU cores', temp_directory = <db>.tmp, max_temp_directory_size = '90% of available disk space'. The curriculum should teach `SET memory_limit='3GB'; SET threads=4;` as a first step. Sources: https://duckdb.org/docs/current/configuration/overview , https://duckdb.org/docs/current/guides/performance/environment.html
- **VERIFIED** DuckDB's own sizing guidance is 1–4 GB of memory per thread (minimum 125 MB/thread); aggregation-heavy work wants 1–2 GB/thread and join-heavy work 3–4 GB/thread.
  - On 8 GB total, that budget supports roughly 2–4 DuckDB threads for scan/aggregate backtests and only ~1–2 for join-heavy ones. DuckDB does process larger-than-memory workloads by spilling to disk — out-of-core support covers grouping, joining, sorting and windowing — but the temp directory must be on the SSD. Source: https://duckdb.org/docs/current/guides/performance/environment.html
- **VERIFIED** You do not have to choose between the two stores at query time: DuckDB's `postgres` core extension can ATTACH a live PostgreSQL instance and read (and write) it directly.
  - `INSTALL postgres; LOAD postgres; ATTACH 'dbname=... host=127.0.0.1' AS db (TYPE postgres);` with a READ_ONLY flag available. Schema info is cached — call pg_clear_cache() after external DDL. This makes the 'Postgres for operational, DuckDB for scans' split a teachable single-query story rather than an export chore. Source: https://duckdb.org/docs/current/core_extensions/postgres/overview.html
- **VERIFIED** The inverse option — running DuckDB inside Postgres via pg_duckdb — is production-labelled but lags: latest release is v1.1.1 (2025-12-18), embedding DuckDB v1.4.3.
  - pg_duckdb declared production readiness at v1.0.0 (2025-09-04) and has made PG18 the default in its Docker images. But it is ~8 months and two DuckDB minors behind 1.5.5, and there is no Windows story — so for this laptop the standalone-DuckDB + postgres-extension direction is the lower-friction one. Source: https://api.github.com/repos/duckdb/pg_duckdb/releases
- *likely* For a single-machine tick/OHLCV store on 8 GB RAM, plain PostgreSQL 18 declarative partitioning (+ BRIN on the timestamp) for the operational store, plus DuckDB 1.5.5 (2026-07-22) over Parquet for backtest scans, is a better fit than TimescaleDB.
  - Judgement, from verified inputs: TimescaleDB pins you to a PG major it supports (no PG19), adds an extension-upgrade axis to every Postgres patch, and its compelling features are TSL-gated; DuckDB is in-process with zero external dependencies and no server RAM budget, which matters on a 4-core/8 GB Ryzen 3 7320U. Reach for TimescaleDB only once continuous aggregates on a live hypertable are genuinely the bottleneck.
- *likely* The target CPU is 4 cores / 8 threads: AMD Ryzen 3 7320U, Zen 2 cores on the 6 nm Mendocino platform, 2.4 GHz base / 4.1 GHz boost.
  - Confirmed consistently across CPU spec aggregators (cpu-monkey, nanoreview, LaptopMedia); AMD's own product page returned a connection error on fetch, so not marked verified. The claim's '4-core' figure is right; note it is Zen 2, an older core generation than the '7000' name suggests, so per-core throughput is closer to a 2019 laptop chip.
- *likely* OVERALL VERDICT: the recommendation stands, but two of its three supporting arguments need replacing.
  - Keep: DuckDB is genuinely in-process with no server to run, and TSL does gate continuous aggregates/compression. Drop: 'TimescaleDB pins you to a PG major' (it supports PG18 today) and 'no server RAM budget' (DuckDB grabs 80% of RAM by default). Replace them with the two verified frictions that actually bite here: TimescaleDB's Windows binaries trail the source releases by three minor versions, and TimescaleDB requires shared_preload_libraries plus a server restart, so every Postgres minor bump must be matched by a rebuilt extension binary before the server will start.
- *likely* TimescaleDB must be added to shared_preload_libraries and requires a PostgreSQL restart to take effect; a version-mismatched extension binary produces 'FATAL: extension "timescaledb" must be preloaded' and the server will not start.
  - Consistent across timescaledb-tune docs (the tool writes shared_preload_libraries='timescaledb' and states the change 'takes effect when you next restart') and issue #6809. Inferred from search snippets and issue titles rather than a fetched doc page, so not marked verified. This is the concrete form of the claim's 'extension-upgrade axis on every Postgres patch'.

### Pitfalls you will actually hit

- `MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here` — you touched `order.user` or any unloaded relationship after the await that loaded `order`. Fix at the query (`selectinload`), not at the access site.
- `DetachedInstanceError` or a mysterious extra SELECT right after `await session.commit()` — you left `expire_on_commit` at its default True on `async_sessionmaker`.
- SQLAlchemy 2.1 (when it lands) will stop installing `greenlet` by default: async code that worked on 2.0 will die at import with a greenlet error until you install `sqlalchemy[asyncio]`.
- Async tests appear to pass but nothing ran — `asyncio_mode` defaults to `strict`, so an `async def test_` without `@pytest.mark.asyncio` is collected, warned about, and effectively skipped. Set `asyncio_mode = "auto"` in pyproject.toml.
- `PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset` on every run — set it explicitly; it is not just noise, the default will change.
- Copy-pasting a 2023 test helper gives `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'` — `app=` was removed in httpx 0.28.0; use `transport=ASGITransport(app=app)`.
- Tests blow up with `engine is None` / `AttributeError on app.state` — `httpx.AsyncClient` + `ASGITransport` does NOT run lifespan events, so nothing you created in `lifespan` exists. Wrap with `LifespanManager` from asgi-lifespan.
- Any blocking call inside an `async def` endpoint — `requests.get`, psycopg2, a pandas/ta-lib crunch, `time.sleep` — freezes the entire event loop for every connected user. On a 4-core Ryzen 3 with one uvicorn worker this is instantly fatal to a live-quote WebSocket. Either use a plain `def` endpoint (FastAPI runs it in a threadpool) or push it to the worker queue.
- `[passlib.handlers.bcrypt:WARNING] (trapped) error reading bcrypt version` / `AttributeError: module 'bcrypt' has no attribute '__about__'` — passlib 1.7.4 (2020) against any bcrypt >= 4.1. There is no upstream fix coming.
- Registration suddenly raises `ValueError` on long passwords after a bcrypt upgrade — bcrypt 5.0.0 raises instead of silently truncating at 72 bytes. Pre-hash with SHA-256 or switch to argon2.
- `ValidationError: Extra inputs are not permitted` the moment your `.env` contains a variable your Settings class doesn't declare — pydantic-settings defaults `extra` to `forbid`, unlike plain BaseModel. Set `extra='ignore'` deliberately, or declare every key.
- Alembic autogenerate produces an empty migration after you changed a column's type or server default — it compares neither by default. Pass `compare_type=True, compare_server_default=True` to `context.configure()`. It also renders a rename as drop-column + add-column, which silently destroys data in production.
- `alembic upgrade head` fails with a driver/loop error on an asyncpg URL — you scaffolded with plain `alembic init` instead of `alembic init -t async` (or `-t pyproject_async`).
- WebSocket broadcasts reach only some clients once you run more than one uvicorn worker — the `ConnectionManager` list is per-process. You need a Redis/Postgres pub-sub layer (encode/broadcaster).
- Prometheus counters reset or read wrong under multiple gunicorn/uvicorn workers — each worker keeps its own registry; you need prometheus-client's multiprocess mode with a shared PROMETHEUS_MULTIPROC_DIR.
- OpenTelemetry `ImportError`/version mismatch — the instrumentation packages use a separate 0.NNbN version line from the 1.x SDK and must be upgraded together (SDK 1.44.0 ↔ instrumentation 0.65b0). Also, `opentelemetry-bootstrap -a install` is documented as problematic under uv.
- You install TimescaleDB and then can't upgrade Postgres — TimescaleDB 2.29 dropped PG15 and does not yet cover PG19; the extension, not Postgres, sets your upgrade cadence.
- `async def` Celery tasks are never awaited — Celery 5.6 still has no native coroutine support, so the task returns a coroutine object and does nothing. You end up wrapping every task body in `asyncio.run()`, which spins a fresh loop and defeats connection pooling.
- You pick arq because a 2022 FastAPI blog post recommended it, then find the README says "In maintenance only mode".
- You build a scheduler on APScheduler 4.0 because it has the nice async API — it has been in alpha since 2022 and 4.0.0a6 (Apr 2025) is still the newest prerelease.
- asyncpg behind PgBouncer in transaction pooling mode throws prepared-statement errors — asyncpg caches statements per connection; set `statement_cache_size=0` and/or use `NullPool`.
- redis-py leaves sockets open / emits 'coroutine was never awaited' at shutdown — there is no async `__del__`; you must `await client.aclose()` in the lifespan teardown.
- You install PostgreSQL 18.6 on Windows from the EDB installer, then try to add TimescaleDB and find the official Windows zip is version 2.26.2 while the current release is 2.29.1 — you are silently three minor versions behind, or you are told to build from source on Windows.
- You start Postgres after dropping in a TimescaleDB build compiled for a different PG minor and the server refuses to start with 'FATAL: extension "timescaledb" must be preloaded'. Because shared_preload_libraries is set, this is a hard startup failure, not a degraded mode — the database is simply down until the binary matches.
- You open DuckDB alongside a running Postgres on 8 GB and the machine starts swapping: DuckDB defaults memory_limit to 80% of physical RAM (~6.4 GB here) and threads to all 4 cores. Always `SET memory_limit` and `SET threads` before a backtest scan.
- A join-heavy backtest query dies or crawls even though the Parquet files are only a few GB — DuckDB's own guidance is 3–4 GB of memory per thread for joins, so 8 GB total means roughly one or two usable threads for that shape of query. It will spill to disk rather than fail, but the temp directory must be on the SSD or the spill is the bottleneck.
- You partition by month with declarative partitioning, then an INSERT for a new month errors out with 'no partition of relation found for row'. PostgreSQL 18 still has no auto-partition creation; you must run a maintenance job that pre-creates partitions ahead of the clock.
- You add a BRIN index on the timestamp and see no speedup — BRIN only helps when physical order correlates with the column. After heavy UPDATE/DELETE churn or an out-of-order bulk load, correlation degrades and BRIN silently falls back to near-seqscan cost. It is a fit for append-only ingest, not for a table you rewrite.
- You benchmark PostgreSQL 18's asynchronous I/O expecting the numbers from Linux write-ups. On Windows io_method defaults to `worker` and io_uring is unavailable (it needs a --with-liburing build), so the AIO win largely does not materialise.
- You pin the curriculum to DuckDB 1.5.5 assuming it is the stable long-lived choice. It is not an LTS — 1.4.x is, and 1.4 LTS itself expires 2026-09-16, with 2.0.0 due in Fall 2026. Expect a major-version migration mid-course.
- You reach for pg_duckdb to get 'both in one server' and find it is at v1.1.1 embedding DuckDB 1.4.3 — two minors behind — with no Windows packaging.
- You read 'TSL-gated' as 'paid'. TimescaleDB Community Edition features (continuous aggregates, compression) are free to self-host; the licence only forbids reselling them as a database-as-a-service, and requires you to call the deployment 'TimescaleDB Community Edition'.

### Outdated - distrust any tutorial that says these

- `@app.on_event("startup")` / `@app.on_event("shutdown")` → a single `@asynccontextmanager async def lifespan(app)` passed as `FastAPI(lifespan=lifespan)`.
- `def endpoint(db: AsyncSession = Depends(get_db))` → `db: Annotated[AsyncSession, Depends(get_db)]`, usually behind a type alias `SessionDep`.
- `q: str = Query(None, max_length=50)` → `q: Annotated[str | None, Query(max_length=50)] = None`.
- `uvicorn app.main:app --reload` in docs/Makefiles → `fastapi dev` (with `[tool.fastapi] entrypoint` in pyproject.toml).
- Pydantic `class Config:` inner class → `model_config = ConfigDict(...)`.
- `orm_mode = True` and `Model.from_orm(obj)` → `from_attributes=True` and `Model.model_validate(obj)`.
- `@validator("x")` / `@root_validator` → `@field_validator("x")` + `@classmethod`, and `@model_validator(mode="after")` as an instance method returning `Self`.
- `.dict()` / `.json()` / `parse_obj()` / `parse_raw()` → `.model_dump()` / `.model_dump_json()` / `.model_validate()` / `.model_validate_json()`.
- `allow_population_by_field_name` → `populate_by_name`.
- `from pydantic import BaseSettings` → `from pydantic_settings import BaseSettings, SettingsConfigDict` (separate package since v2).
- `Base = declarative_base()` with `id = Column(Integer, primary_key=True)` → `class Base(DeclarativeBase)` with `id: Mapped[int] = mapped_column(primary_key=True)` (real typing, and `Mapped[list["Order"]]` for relationships).
- `session.query(Model).filter(...).all()` → `await session.scalars(select(Model).where(...))`; `Query` is officially declared legacy as of SQLAlchemy 2.0.
- `sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)` → `async_sessionmaker(engine, expire_on_commit=False)`.
- Relying on default lazy relationship access in an async app → explicit `selectinload()`/`joinedload()` per query, plus `lazy="raise"` on the relationship so mistakes fail loudly.
- psycopg2 as the assumed Postgres driver → asyncpg for the async app, and psycopg (v3) for sync/tooling — SQLAlchemy 2.1 makes psycopg3 the default `postgresql://` driver.
- `python-jose[cryptography]` (still in thousands of FastAPI auth tutorials) → PyJWT; python-jose is effectively abandoned and carried CVE-2024-33663 / CVE-2024-33664.
- `passlib.context.CryptContext(schemes=["bcrypt"])` → `pwdlib.PasswordHash.recommended()` (argon2), or call `bcrypt` / `argon2-cffi` directly. passlib's last release was 2020 and it breaks against modern bcrypt and Python 3.13+.
- `import aioredis` → `import redis.asyncio as redis`; the aioredis repo has been archived since Feb 2023.
- `httpx.AsyncClient(app=app)` → `httpx.AsyncClient(transport=ASGITransport(app=app))` (removed, not just deprecated, in httpx 0.28.0).
- `TestClient(app)` used inside `async def` tests → `httpx.AsyncClient` + `ASGITransport` (+ `LifespanManager`). TestClient remains fine for purely sync tests.
- Overriding the `event_loop` fixture in conftest.py → removed in pytest-asyncio 1.0.0; use `asyncio_default_test_loop_scope` / `asyncio_default_fixture_loop_scope`, or the `pytest_asyncio_loop_factories` hook.
- Omitting `asyncio_mode` from config and sprinkling `@pytest.mark.asyncio` everywhere → set `asyncio_mode = "auto"` once in `[tool.pytest.ini_options]`.
- `requirements.txt` + `python -m venv` + `pip install -r` → `uv init` / `uv add` / `uv sync` with pyproject.toml and a committed uv.lock. (`requirements-dev.txt` → dependency groups.)
- black + isort + flake8 + pyupgrade + autoflake as four tools → `ruff format` and `ruff check --fix` (with `--select I` for imports).
- `poetry` / `pip-tools` / `pyenv` / `pipx` as separate installs → all covered by uv per its own docs.
- freezegun as the reflexive time-mocking choice → time-machine (C-level patching, much faster, actively released 3.4.0 Aug 2026).
- `requests` for outbound broker/market-data calls in an async service → `httpx.AsyncClient`, mocked in tests with respx rather than responses/requests-mock.
- Reaching for Celery by default in a FastAPI project → TaskIQ or Dramatiq 2.x for an async-native single-machine setup; Celery still cannot await an `async def` task.
- arq as "the async Celery for FastAPI" → it is in maintenance-only mode; pick TaskIQ or Dramatiq.
- `from typing import Optional, List, Dict` → `X | None`, `list[X]`, `dict[K, V]` (FastAPI now requires Python >=3.10 anyway).
- Assuming TimescaleDB is the automatic answer for time-series → for a single-machine setup, PG18 declarative partitioning + BRIN for the operational store and DuckDB/Parquet for backtest scans; TimescaleDB's compression/continuous-aggregate features are TSL-licensed and pin your Postgres major version.
- 'TimescaleDB is behind on Postgres majors' — outdated as a general claim. TimescaleDB 2.29.1 (2026-08-04) supports PG 16, 17 and 18. The live problem is not source support but Windows binary lag (docs still ship 2.26.2) and the fact that PG15 support was *removed* in 2.29.0.
- 'TimescaleDB supports PostgreSQL 15' — removed in 2.29.0; 2.28.0 was the final minor to support PG15. Any tutorial pairing TimescaleDB with PG13/14/15 is now unrunnable on current releases.
- 'Timescale Inc. / Timescale Cloud' branding — the company rebranded to TigerData in June 2025; licences now live at tigerdata.com/legal/licenses and the managed service is Tiger Cloud. The extension itself is still named timescaledb.
- 'DuckDB releases are all equivalent, just take the newest' — obsolete since 1.4.0 (Sept 2025) introduced the LTS scheme: every other minor is LTS with one year of support. Version pinning advice written before Sept 2025 does not account for this.
- 'DuckDB is only for read-only analytics over files' — the postgres core extension has supported writing to a live PostgreSQL (CREATE/INSERT/UPDATE/DELETE/ALTER, postgres_query, postgres_execute) for some time; treating it as read-only understates the integration.
- 'Use effective_io_concurrency=0 / it does nothing on systems without fadvise' — PostgreSQL 18's AIO subsystem makes effective_io_concurrency and maintenance_io_concurrency meaningful above zero even on platforms lacking fadvise().
- 'initdb does not enable data checksums by default' — PostgreSQL 18 enables data checksums by default (disable with --no-data-checksums), which changes the baseline write overhead assumption in older tuning guides.

<details>
<summary>Sources (101)</summary>

- https://alembic.sqlalchemy.org/en/latest/cookbook.html
- https://api.github.com/repos/duckdb/pg_duckdb/releases
- https://docs.astral.sh/ruff/formatter/
- https://docs.astral.sh/uv/
- https://docs.celeryq.dev/en/stable/userguide/tasks.html
- https://docs.sqlalchemy.org/en/20/intro.html
- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html
- https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html
- https://docs.sqlalchemy.org/en/21/changelog/migration_21.html
- https://dramatiq.io/changelog.html
- https://duckdb.org/2026/07/22/announcing-duckdb-155
- https://duckdb.org/docs/current/configuration/overview
- https://duckdb.org/docs/current/core_extensions/postgres/overview.html
- https://duckdb.org/docs/current/guides/performance/environment.html
- https://duckdb.org/release_calendar
- https://duckdb.org/why_duckdb
- https://fastapi.tiangolo.com/advanced/async-tests/
- https://fastapi.tiangolo.com/advanced/events/
- https://fastapi.tiangolo.com/advanced/websockets/
- https://fastapi.tiangolo.com/fastapi-cli/
- https://fastapi.tiangolo.com/tutorial/background-tasks/
- https://fastapi.tiangolo.com/tutorial/bigger-applications/
- https://fastapi.tiangolo.com/tutorial/dependencies/
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- https://github.com/aio-libs-abandoned/aioredis-py
- https://github.com/celery/celery/discussions/9049
- https://github.com/duckdb/duckdb/releases
- https://github.com/encode/httpx/blob/master/CHANGELOG.md
- https://github.com/fastapi/fastapi/discussions/11773
- https://github.com/fastapi/fastapi/discussions/9587
- https://github.com/fastapi/fastapi/releases
- https://github.com/grafana/loki/releases
- https://github.com/prometheus/prometheus/releases
- https://github.com/pyca/bcrypt/issues/792
- https://github.com/python-arq/arq
- https://github.com/taskiq-python/taskiq
- https://github.com/timescale/docs/blob/latest/self-hosted/install/installation-windows.md
- https://github.com/timescale/timescaledb/issues/6809
- https://github.com/timescale/timescaledb/issues/8935
- https://github.com/timescale/timescaledb/releases
- https://mypy-lang.blogspot.com/
- https://opentelemetry.io/docs/zero-code/python/
- https://pydantic.dev/docs/validation/latest/concepts/fields/
- https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
- https://pydantic.dev/docs/validation/latest/concepts/validators/
- https://pydantic.dev/docs/validation/latest/get-started/migration/
- https://pypi.org/project/APScheduler/#history
- https://pypi.org/project/PyJWT/#history
- https://pypi.org/project/argon2-cffi/#history
- https://pypi.org/project/arq/#history
- https://pypi.org/project/asyncpg/#history
- https://pypi.org/project/bcrypt/#history
- https://pypi.org/project/celery/#history
- https://pypi.org/project/duckdb/#history
- https://pypi.org/project/fastapi/#history
- https://pypi.org/project/freezegun/#history
- https://pypi.org/project/httpx/#history
- https://pypi.org/project/mypy/#history
- https://pypi.org/project/opentelemetry-instrumentation-fastapi/#history
- https://pypi.org/project/opentelemetry-sdk/#history
- https://pypi.org/project/passlib/#history
- https://pypi.org/project/prometheus-client/#history
- https://pypi.org/project/prometheus-fastapi-instrumentator/#history
- https://pypi.org/project/pwdlib/#history
- https://pypi.org/project/pytest-asyncio/#history
- https://pypi.org/project/pytest/#history
- https://pypi.org/project/python-jose/#history
- https://pypi.org/project/redis/#history
- https://pypi.org/project/respx/#history
- https://pypi.org/project/rq/#history
- https://pypi.org/project/ruff/#history
- https://pypi.org/project/sqlalchemy/#history
- https://pypi.org/project/structlog/#history
- https://pypi.org/project/taskiq/#history
- https://pypi.org/project/testcontainers/#history
- https://pypi.org/project/time-machine/#history
- https://pypi.org/project/ty/#history
- https://pypi.org/project/uv/#history
- https://pypi.org/project/uvicorn/#history
- https://pypi.org/pypi/alembic/json
- https://pypi.org/pypi/dramatiq/json
- https://pypi.org/pypi/duckdb/json
- https://pypi.org/pypi/fastapi/json
- https://pypi.org/pypi/pydantic-settings/json
- https://pypi.org/pypi/pydantic/json
- https://pypi.org/pypi/pyrefly/json
- https://pypi.org/pypi/pytest-postgresql/json
- https://pytest-asyncio.readthedocs.io/en/latest/reference/changelog.html
- https://pytest-asyncio.readthedocs.io/en/latest/reference/configuration.html
- https://raw.githubusercontent.com/timescale/timescaledb/main/tsl/README.md
- https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
- https://www.cpu-monkey.com/en/cpu-amd_ryzen_3_7320u
- https://www.postgresql.org/
- https://www.postgresql.org/docs/18/brin.html
- https://www.postgresql.org/docs/18/ddl-partitioning.html
- https://www.postgresql.org/docs/18/release-18.html
- https://www.postgresql.org/docs/18/runtime-config-resource.html
- https://www.postgresql.org/download/windows/
- https://www.tigerdata.com/docs/about/latest/timescaledb-editions
- https://www.tigerdata.com/legal/licenses

</details>

---

## React and TypeScript Frontend Stack

<sub>2 report(s) &middot; 39 verified, 1 likely &middot; 27 pitfalls &middot; 24 outdated patterns &middot; 81 sources</sub>

### Facts

- **VERIFIED** React stable is 19.2.8; there is no React 20. React 19.2 (Oct 1, 2025) is the newest feature minor.
  - registry.npmjs.org/react/latest returns version 19.2.8. @types/react is ^19.2.18. For a Vite SPA the useful React 19 features are: ref-as-prop (delete every forwardRef), <Context> usable directly as provider instead of <Context.Provider>, ref cleanup functions, and use() for reading context conditionally. Actions/useActionState/useFormStatus/useOptimistic are form-and-mutation ergonomics — they work in an SPA but a trading dashboard's mutations (place/cancel order) go through TanStack Query useMutation, so they are largely irrelevant. Document metadata hoisting and the preload/preinit APIs are SSR-oriented: skip.
- **VERIFIED** React Compiler hit v1.0 stable on Oct 7, 2025; babel-plugin-react-compiler is 1.0.0 and Vite now ships a first-class `react-compiler-ts` scaffold template.
  - react.dev/blog lists 'React Compiler v1.0' dated 2025-10-07. create-vite's README lists templates: react, react-compiler, react-ts, react-compiler-ts. Manual wiring on Vite 8 needs `npm i -D babel-plugin-react-compiler @rolldown/plugin-babel`, then in vite.config: `import react, { reactCompilerPreset } from '@vitejs/plugin-react'; import babel from '@rolldown/plugin-babel'; plugins: [react(), babel({ presets: [reactCompilerPreset()] })]`. Note this reintroduces Babel into an otherwise Rust toolchain — a real build-time cost on an 8 GB / Ryzen 3 machine. Compiler works best on React 19, supports 17/18.
- **VERIFIED** React `memo` does NOT stop a re-render when a context the component consumes changes. This is the exact mechanism behind the tick-driven-UI performance collapse.
  - react.dev/reference/react/memo states a memoized component still re-renders if its own state changes or 'a context it uses changes', and 'Memoization only has to do with props that are passed to the component from its parent.' So the classic <TickContext.Provider value={ticks}> pattern re-renders every single consumer on every message, and wrapping children in memo() does nothing. React Compiler does not fix this either — it memoizes props/values, not context subscriptions.
- **VERIFIED** The fix for tick fan-out is useSyncExternalStore: `const snapshot = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?)`.
  - react.dev: subscribe(callback) must return an unsubscribe fn; getSnapshot must return an immutable value compared with Object.is. Critical caveat, quoted from the docs: returning a fresh object every call ('return { todos: myStore.todos }') causes an infinite re-render loop — return a cached reference. Practical shape for a dashboard: one WebSocket writes into a plain JS Map outside React; each price cell calls useSyncExternalStore with a getSnapshot that returns the primitive number for its own symbol. Only cells whose number actually changed re-render. Zustand is built on this same primitive.
- **VERIFIED** Zustand is 5.0.15; `useShallow` is imported from `zustand/react/shallow` and is required whenever a selector returns a new object or array.
  - npm registry: zustand@5.0.15, all peerDeps optional (react >=18, use-sync-external-store >=1.2.0). Zustand's default equality is Object.is, so `useStore(s => ({a: s.a, b: s.b}))` returns a new object every tick and re-renders forever. `useStore(useShallow(s => ({a: s.a, b: s.b})))` compares top-level properties instead. For a tick stream the better answer is still one primitive per selector: `useStore(s => s.prices[symbol])`.
- **VERIFIED** Vite stable is 8.2.1, requires Node `^20.19.0 || >=22.12.0`, and uses Rolldown (Rust) as its single bundler — esbuild and Rollup are both gone.
  - registry.npmjs.org/vite/latest: version 8.2.1, engines.node '^20.19.0 || >=22.12.0'. Vite 8 replaces esbuild with Oxc for JS transform and minification, Rollup with Rolldown for bundling, and Lightning CSS for CSS minification. Migration-guide breaking changes: `build.rollupOptions` renamed to `build.rolldownOptions` (same for `worker.rollupOptions`), `build.commonjsOptions` is now a no-op, object form of `manualChunks` unsupported, `build.rollupOptions.watch.chokidar` removed, esbuildOptions auto-converted but esbuild is deprecated. Note Node 20 is EOL as of Mar 24, 2026 — use Node 24 (Krypton) or 22 (Jod).
- **VERIFIED** Vite dev proxy for a FastAPI backend, including the WebSocket, is configured under `server.proxy` with `ws: true` for the socket route.
  - vite.dev/config/server-options: proxy is `Record<string, string | ProxyOptions>`, built on http-proxy-3. Working shape: `server: { proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true }, '/ws': { target: 'ws://localhost:8000', ws: true } } }`. Proxying the WS through Vite means the browser connects same-origin, so you avoid CORS and cookie-domain problems in dev. `rewriteWsOrigin` exists but the docs explicitly warn it 'can leave the proxying open to CSRF attacks' — do not enable it casually.
- **VERIFIED** Vite env vars: only `VITE_`-prefixed keys reach client code via `import.meta.env`, and they are statically replaced at build time, not read at runtime.
  - Always available: MODE, BASE_URL, PROD, DEV, SSR. Prefix configurable via `envPrefix`. Load order (later wins): .env, .env.local, .env.[mode], .env.[mode].local. Existing shell env vars are never overwritten. Type them in src/vite-env.d.ts with `interface ImportMetaEnv { readonly VITE_API_URL: string }` and `interface ImportMeta { readonly env: ImportMetaEnv }` — the docs warn that adding any `import` statement to that file breaks the type augmentation. Because values are inlined at build time, a VITE_ var is public: never put a broker API secret there.
- **VERIFIED** Vite 8 has a built-in `resolve.tsconfigPaths` option (default `false`) that resolves tsconfig `paths` natively.
  - vite.dev/config/shared-options. Set `resolve: { tsconfigPaths: true }` and the vite-tsconfig-paths plugin becomes unnecessary for `@/*` style aliases. Pairs awkwardly with TypeScript 7, which removed `baseUrl` — write paths relative to the tsconfig instead.
- **VERIFIED** TypeScript 7.0 went GA on July 8, 2026. It is the Go-native rewrite (8–12x faster full builds) and 6.0 (March 23, 2026) was the last JavaScript-based release.
  - devblogs.microsoft.com/typescript lists 'Announcing TypeScript 7.0' 2026-07-08 and 'Announcing TypeScript 6.0' 2026-03-23. npm `typescript@latest` is 7.0.2. Microsoft's own benchmark: VS Code type-check 125.7s (TS6) → 10.6s (TS7), memory down 6–26%. On a Ryzen 3 7320U with 8 GB this is the single biggest quality-of-life win available in the stack.
- **VERIFIED** TypeScript 7.0 ships with NO stable programmatic API, which breaks typescript-eslint, ts-jest, ts-morph, and Vue/Svelte/Astro template checking. The stable API is deferred to 7.1.
  - The TS7 announcement says 'We expect TypeScript 7.1 to ship with a new (and different) API' and directs API consumers to the compatibility package. The escape hatch is aliasing: `"typescript": "npm:@typescript/typescript6@^6.0.2"` in devDependencies, which supplies a `tsc6` binary and re-exports the 6.0 API so ESLint runs on 6.0 while `tsc` runs the native compiler. Community reporting puts 7.1 around October 2026 (that date is not from an official source).
- **VERIFIED** TypeScript 7 removes ES5 target, CommonJS/AMD/UMD/SystemJS module output, `baseUrl`, and classic module resolution; `strict` defaults to true and `types` defaults to `[]`.
  - From the TS7 announcement: also removed are `downlevelIteration`, setting `esModuleInterop`/`allowSyntheticDefaultImports` to false, the `module` namespace keyword, and `asserts` on imports. `stableTypeOrdering: true` is forced. `rootDir` now defaults to `./`, so projects whose tsconfig sits above src must set it explicitly. `types: []` means you must explicitly list `"types": ["vite/client"]` — otherwise import.meta.env stops type-checking.
- **VERIFIED** create-vite's react-ts template currently pins `typescript: ~6.0.2` (not 7), uses `oxlint` instead of ESLint, and its tsconfig.app.json omits `strict` entirely.
  - Raw template package.json: react/react-dom ^19.2.8, typescript ~6.0.2, vite ^8.2.0, @vitejs/plugin-react ^6.0.5, @types/node ^24.13.3, oxlint ^1.76.0 (oxlint@latest is 1.78.0). tsconfig.app.json compilerOptions: target es2023, lib [ES2023, DOM], module esnext, types ["vite/client"], moduleResolution "bundler", jsx "react-jsx", verbatimModuleSyntax true, erasableSyntaxOnly true, moduleDetection "force", noEmit true, allowImportingTsExtensions true, allowArbitraryExtensions true, skipLibCheck true, noUnusedLocals/noUnusedParameters/noFallthroughCasesInSwitch true. The pin to TS6 is the pragmatic signal: stay on 6.0.x until 7.1 restores the API, unless you drop type-aware linting.
- **VERIFIED** `verbatimModuleSyntax: true` is on by default in the Vite React template and forces `import type` for every type-only import.
  - typescriptlang.org/tsconfig: the rule is 'what you write is what you get' — imports without the `type` modifier are preserved in emitted JS, imports with it are erased entirely. In practice this means `import type { ReactNode } from 'react'` and `import { type Dispatch, useState } from 'react'`. It exists so a bundler never has to guess whether an import has side effects. Paired with `erasableSyntaxOnly: true`, which bans enums, parameter properties and namespaces — TS syntax that can't be erased by a type-stripping transform.
- **VERIFIED** React.FC is no longer idiomatic. Use a plain function with a typed props parameter.
  - The React TypeScript Cheatsheet states 'the general consensus today is that React.FunctionComponent (or the shorthand React.FC) is not needed', and calls it a stylistic choice at best on React 18+/TS 5.1+. Write `function PriceCell({ symbol }: { symbol: string }) {}`. Since React 19 makes ref a normal prop, typed props also absorb `ref?: Ref<HTMLDivElement>` without forwardRef.
- **VERIFIED** React Router is at 8.3.0 — v8.0.0 shipped June 17, 2026. It is ESM-only, the `react-router-dom` package is gone, and it requires Node 22.22+ and React 19.2.7+.
  - npm react-router@latest is 8.3.0 with peerDeps react >=19.2.7, react-dom >=19.2.7 (optional). Imports move to `import { Link } from 'react-router'` and `import { RouterProvider } from 'react-router/dom'`. Three additive modes remain: declarative (URL matching only), data (loaders/actions via createBrowserRouter, route config outside React), framework (SSR, file routes, typed routes, needs Vite). For a Vite SPA trading dashboard, framework mode is dead weight — you have no SSR and your data comes from TanStack Query, not loaders. Use declarative mode, or data mode only if you want route-level pending states.
- **VERIFIED** TanStack Router is 1.170.29 and its differentiator is fully type-safe, schema-validated search params — the strongest argument for a dashboard.
  - npm @tanstack/react-router@1.170.29, peerDeps react >=18. Its comparison table claims typesafe path params, typesafe search params with JSON search params + validation + custom serialization, and typesafe relative navigation, all of which React Router marks as absent or partial. Concretely: a dashboard's whole view state (symbol, timeframe, indicator set, layout) belongs in the URL, and TanStack Router validates and types that object. Cost: it is a much larger API surface to learn than declarative React Router.
- **VERIFIED** TanStack Query is 5.101.4 (peer: react ^18 || ^19). v5 uses a single object signature everywhere.
  - `useQuery({ queryKey, queryFn, staleTime })`, `queryClient.invalidateQueries({ queryKey: ['orders'] })`. Invalidation is prefix-matching by default: `{ queryKey: ['todos'] }` invalidates ['todos'] and ['todos', {page:1}]; add `exact: true` to hit only the literal key; use `predicate: (query) => ...` for anything else. Design keys hierarchically for a dashboard — ['positions'], ['orders', accountId], ['candles', symbol, timeframe] — so one WS event can invalidate a whole subtree.
- **VERIFIED** Bridging WebSocket pushes into the Query cache has two patterns: `invalidateQueries` (simple, refetches) and `setQueriesData` (no network round-trip, but untyped).
  - From TkDodo (TanStack Query maintainer): the invalidation pattern is recommended — on message, derive a queryKey and call `queryClient.invalidateQueries({ queryKey })`; if nothing is currently observing that key, nothing happens, which self-limits work. The partial-update pattern uses `queryClient.setQueriesData(key, (oldData) => ...)` to merge the payload directly. Documented gotchas: set `staleTime: Infinity` globally once the socket is your source of truth (otherwise refetch logic fights the socket), and the partial-update path 'lacks TypeScript support'. Do NOT route per-tick price updates through Query at all — at 10+ msg/sec that thrashes the cache. Ticks go to an external store; Query holds the slow-moving REST resources (positions, orders, instrument metadata).
- **VERIFIED** TanStack Query's three built-in render brakes are structural sharing, tracked properties, and `select` — and object rest destructuring silently disables tracked properties.
  - Structural sharing keeps the original object reference when refetched JSON is deep-equal, so referential equality survives polling (disable with `structuralSharing: false`). Tracked properties use a Proxy so a re-render only fires for fields your component actually reads — but the docs note that rest destructuring (`const { data, ...rest } = useQuery(...)`) touches everything and turns the optimization off. `select: (d) => d.length` subscribes to a derived slice only; wrap it in useCallback or hoist it so it stays referentially stable.
- **VERIFIED** lightweight-charts is 5.2.1, Apache-2.0, and v5 replaced `addCandlestickSeries()` with `addSeries(CandlestickSeries, options)`.
  - Exact v5 shape: `import { createChart, CandlestickSeries, HistogramSeries, LineSeries } from 'lightweight-charts'`, then `const chart = createChart(container); const s = chart.addSeries(CandlestickSeries, { upColor:'#26a69a', downColor:'#ef5350' })`. The rewrite exists for tree-shaking — unused series types now drop from the bundle. Other v5 breaks: `series.setMarkers()` is gone, use the `createSeriesMarkers()` primitive; the watermark left core options and became `createTextWatermark()`; ISeriesPrimitivePaneView/Renderer renamed to IPrimitivePaneView/IPrimitivePaneRenderer.
- **VERIFIED** lightweight-charts live updates use `update(bar: TData, historicalUpdate?: boolean): void`, and `setData()` only for bulk initialization.
  - From ISeriesApi docs: update() 'Adds new data item to the existing set (or updates the latest item if times of the passed/latest items are equal)'. So the realtime loop is — call update() with the same timestamp repeatedly to mutate the forming candle, then call it with a greater timestamp to append the next one. `historicalUpdate` (default false) allows amending older points but is explicitly slower. Crucially, update() writes straight to canvas: the chart must live in a ref-held imperative object, NOT in React state, or you re-render the component tree on every tick.
- **VERIFIED** lightweight-charts' Apache-2.0 license carries a real attribution obligation, satisfiable by the built-in `attributionLogo` chart option.
  - The README requires you to reproduce the NOTICE-file attribution and a link to https://www.tradingview.com/ on your site or app, and says the `attributionLogo` chart option 'will satisfy the link requirement' by rendering the link on the chart itself. This is the cheapest compliance path — enable it and you are done. For comparison, the alternatives: uPlot 1.6.32 (MIT, tiny, fastest for dense line/OHLC but you build the candle rendering and crosshair yourself), ECharts 6.1.0 (Apache-2.0, has candlestick + dataZoom out of the box but is a heavy dependency), Recharts 3.10.1 (SVG, no candlestick primitive, will stutter on thousands of bars), visx 4.0.0 (primitives only — you author the whole chart). Recommendation: lightweight-charts for the price/volume/indicator pane (it is purpose-built for exactly candles + histogram volume + line overlays, canvas-rendered, and its update() API matches a tick feed); uPlot only if you need many small sparkline panes; skip Recharts and visx for the main chart.
- **VERIFIED** Typed client from FastAPI: openapi-typescript 7.13.0 + openapi-fetch 0.17.0 + openapi-react-query 0.5.4 is the lightest path; hey-api/openapi-ts 0.99.0 and orval 8.24.0 generate more.
  - openapi-typescript supports OpenAPI 3.0 and 3.1 including discriminators — FastAPI emits 3.1, so it is a direct match — and can read a live URL (`npx openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.d.ts`). It emits ONLY types, zero runtime. openapi-fetch is a ~6 kB min typed fetch wrapper over those types; openapi-react-query (peer: openapi-fetch ^0.17.0, @tanstack/react-query ^5.80.0) layers useQuery/useMutation/useSuspenseQuery/useInfiniteQuery on top. Best DX for a learner: this trio, because the generated artifact is one .d.ts you can actually read, and nothing is generated per-endpoint. hey-api (self-described 'production-grade SDKs, Zod schemas, TanStack Query hooks, 20+ plugins') and orval generate full hook sets — more magic, more regeneration churn, both still pre-1.0 for hey-api.
- **VERIFIED** TanStack Table jumped to v9 (9.1.2) with breaking API changes; TanStack Virtual is 3.14.9.
  - v9 replaces `useReactTable` with `useTable({ features, ... })`, makes features tree-shakable/opt-in, moves state through `table.state`/`table.store`/per-slice atoms rather than `getState()`, and makes data and columns readonly. The subtle trap: row/column/cell methods now live on shared prototypes and rely on `this`, so destructuring them (`const { getValue } = cell`) breaks with `this` undefined in strict mode. Payoff is memory — reported ~86% lower retained heap (2.71 GB → 380 MB on 1M rows x 8 cols), which matters on an 8 GB laptop. Migration escape hatch: `useLegacyTable` from `@tanstack/react-table/legacy` accepts the v8 shape on the v9 engine. Most tutorials and shadcn/ui data-table examples are still v8.
- **VERIFIED** Testing: Vitest 4.1.10, React Testing Library 16.3.2, Playwright 1.62.1, MSW 2.15.0.
  - Vitest 4 peer-supports vite ^6/^7/^8. Breaking in v4: browser-mode providers split into separate packages — install `@vitest/browser-playwright`, `@vitest/browser-webdriverio`, or `@vitest/browser-preview` rather than `@vitest/browser`; browser context now imports from `vitest/browser` not `@vitest/browser/context`; the `basic` reporter was removed (use default with `summary: false`). RTL 16.3.2 peers react ^18||^19 and requires @testing-library/dom ^10 as a separate install. MSW v2 uses `import { http, HttpResponse } from 'msw'` and `setupWorker` from `msw/browser` (browser) or `setupServer` from `msw/node` (Vitest), plus a one-time `npx msw init public/ --save`. On 8 GB RAM, prefer jsdom + MSW for unit tests and keep Playwright to a thin smoke suite — each Playwright browser download is hundreds of MB.
- **VERIFIED** react-use-websocket's latest published version is 4.13.0, published 2025-02-04T05:13:32.627Z — the exact date is now confirmed, not inferred.
  - The npm registry search endpoint (https://registry.npmjs.org/-/v1/search?text=react-use-websocket) returns a first-class `date` field of "2025-02-04T05:13:32.627Z" for version 4.13.0. This independently confirms the previous researcher's inference from the `_npmOperationalInternal.tmp` timestamp 1738646012429. The original claim can be upgraded from 'likely' to 'verified' and the hedge about the date being approximate can be dropped.
- **VERIFIED** react-use-websocket's GitHub repo has had no pushes since 2025-02-04 and carries 95 open issues, but is NOT archived.
  - https://api.github.com/repos/robtaussig/react-use-websocket returns pushed_at 2025-02-04T05:15:22Z, open_issues_count 95, stargazers_count 1888, archived false, default_branch master. As of 2026-08-18 that is ~18.5 months with zero commits. 'Appears unmaintained' is a fair reading of this evidence, but state it as evidence (no commits, no releases, unanswered issues) rather than as a declared status — the author has not archived or deprecated the package.
- **VERIFIED** react-use-websocket@4.13.0 genuinely declares NO peerDependencies key at all — nothing pins it to any React version.
  - Fetched the published tarball's manifest at https://unpkg.com/react-use-websocket@4.13.0/package.json: the `peerDependencies` key is absent entirely, as is `dependencies`. (Historically it did declare one — v0.9.7 in the registry doc lists peerDependencies {"react": ">=16.8.0"} — so the declaration was dropped at some point, not merely never added.) Practical consequence: `npm install` will never warn you about React incompatibility with this package; you will only find out at runtime.
- **VERIFIED** There are open, unanswered React 19 compatibility issues on react-use-websocket, the newest filed 2026-02-05.
  - GitHub issue search on repo:robtaussig/react-use-websocket for open React 19 issues returns 4 results including "Does react-use-websocket run on React 19?" (2024-12-06) and "React 19.0 support in the purview" (2026-02-05). Note carefully: these are compatibility *requests/questions*, not confirmed breakage reports — do NOT teach 'it breaks on React 19'. The verified statement is 'compat with React 19 is unaddressed by the maintainer.'
- **VERIFIED** React's current latest npm release is 19.2.8, published 2026-07-21.
  - npm registry search for `react` returns version 19.2.8, date 2026-07-21T15:41:28.716Z. This is the React line a 2026 learner will actually install, and it is two major-minor generations past react-use-websocket's last build (which devDepends on react 18.3.1 per its package.json on master).
- **VERIFIED** partysocket's latest version is 1.3.0, published 2026-06-23T08:46:43.072Z — actively maintained.
  - npm registry search `date` field for partysocket: 2026-06-23T08:46:43.072Z, version 1.3.0. Its monorepo, https://api.github.com/repos/cloudflare/partykit, shows pushed_at 2026-08-03T15:14:06Z, 38 open issues, archived false. The 'actively maintained' half of the original claim is confirmed.
- **VERIFIED** CORRECTION: partysocket already ships React hooks — you do not have to wire it into a hook yourself.
  - https://unpkg.com/partysocket@1.3.0/package.json declares subpath exports ".", "./ws", "./react", "./use-ws", "./event-target-polyfill", and an OPTIONAL peerDependency `react: >=17`. The source at packages/partysocket/src/react.ts exports `usePartySocket` (default + named) and re-exports `useWebSocket` from './use-ws'. So `import useWebSocket from "partysocket/use-ws"` is close to a drop-in shape for the react-use-websocket API. The original claim framed partysocket as a raw socket library only; that framing is wrong.
- **VERIFIED** CORRECTION: partysocket's real default backoff is min 3000ms × 1.3^(retries-1) capped at 10000ms, with NO jitter — not the `1000 * 2**attempt` capped at 30s that the claim suggests.
  - From packages/partysocket/src/ws.ts on cloudflare/partykit main: DEFAULT minReconnectionDelay 3000, maxReconnectionDelay 10000, reconnectionDelayGrowFactor 1.3, connectionTimeout 4000, maxRetries Infinity, maxEnqueuedMessages Infinity, startClosed false, debug false. _getNextDelay() is: `delay = minReconnectionDelay * reconnectionDelayGrowFactor ** (this._retryCount - 1)` then clamped to maxReconnectionDelay, and returns 0 when _retryCount is 0 (first reconnect is immediate). The teaching formula `Math.min(30000, 1000 * 2 ** attempt)` is still pedagogically fine, but present it as *your* choice, not as what the reference library does — and note that the reference implementation deliberately caps far lower (10s) and adds no jitter, which is itself a discussable design flaw (thundering herd on mass server restart).
- **VERIFIED** partysocket is downloaded ~8.16M times/week vs react-use-websocket's ~425K/week.
  - https://api.npmjs.org/downloads/point/last-week/partysocket → 8,159,411 for 2026-08-09..2026-08-15. Same endpoint for react-use-websocket → 425,312 for the identical window. Caveat (inference, not verified): partysocket's volume is likely dominated by transitive installs via Cloudflare's Agents/PartyKit stack rather than direct developer choice, so do not read it as '19x more popular for this use case'.
- **VERIFIED** partysocket's own README advertises reconnect, message buffering while disconnected, connection timeouts, changeable server URL between reconnections, multi-platform, dependency-free — it does NOT advertise a heartbeat/ping.
  - Read from github.com/cloudflare/partykit/tree/main/packages/partysocket. Tagline confirmed as "A better WebSocket that Just Works™". It is a fork of the `reconnecting-websocket` project. 'Dependency free' is marketing-approximate: the published package.json lists one dependency, `event-target-polyfill ^0.0.4`. The absence of heartbeat matters — a half-open TCP connection produces no 'close' event, so neither partysocket nor react-use-websocket will notice a silently dead link without an app-level ping.
- **VERIFIED** The browser WebSocket API exposes no ping/pong control-frame API to JavaScript and performs no automatic reconnection — so an app-level heartbeat must be JSON/text messages you define yourself.
  - MDN https://developer.mozilla.org/en-US/docs/Web/API/WebSocket documents only the events open/message/close/error and properties readyState, bufferedAmount, binaryType, extensions, protocol, url. There is no ping()/pong() method and no reconnect behavior. RFC 6455 ping/pong frames are handled by the browser below the JS layer. This validates the original claim's advice to write your own heartbeat timer, and it is the single strongest argument for hand-rolling the socket module as a learning exercise.
- **VERIFIED** WebSocket.close(code, reason) throws InvalidAccessError unless code is 1000 or in 3000–4999, and throws SyntaxError if reason exceeds 123 UTF-8 bytes.
  - MDN https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/close. Directly relevant to the hand-rolled-module exercise: a learner who writes `ws.close(1006)` or `ws.close(4000 + status)` without bounds-checking, or who reuses a server-sent close code when tearing down, will hit a DOMException. Also note reason is byte-limited, not char-limited, so non-ASCII reasons overflow earlier than expected.
- **VERIFIED** useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?) requires getSnapshot to return a cached/immutable value; returning a fresh object each call causes an infinite re-render loop.
  - React docs https://react.dev/reference/react/useSyncExternalStore. React compares snapshots with Object.is(). Docs state "While the store has not changed, repeated calls to getSnapshot must return the same value." The failure surfaces as the warning "The result of getSnapshot should be cached to avoid an infinite loop." `subscribe` must be stable (module scope or useCallback) or React resubscribes every render. `getServerSnapshot` is required if the app server-renders, otherwise React throws during hydration — relevant the moment the learner puts this store into a Next.js app.
- *likely* react-use-websocket (4.13.0) appears unmaintained since roughly February 2025; partysocket 1.3.0 is the actively maintained reconnecting-WebSocket option.
  - The npm registry metadata for react-use-websocket@4.13.0 carries an internal timestamp of 1738646012429 (≈2025-02-04) and it declares no peerDependencies at all, so nothing pins it to a React version. Publish date is inferred from that internal field, not a documented `time` entry — treat the exact date as approximate. partysocket describes itself as 'A better WebSocket that Just Works' and handles reconnection/backoff for you. For learning purposes, write the native WebSocket yourself: a module-scope singleton holding the socket, an exponential-backoff reconnect (e.g. `delay = Math.min(30000, 1000 * 2 ** attempt)` plus jitter, reset on open), a heartbeat/ping timer, and a subscribe(symbol, cb) registry — then feed useSyncExternalStore from it. That is ~80 lines and teaches the actual failure modes.

### Pitfalls you will actually hit

- You put the tick stream in React Context, wrap the expensive children in memo(), and nothing improves — the whole dashboard still re-renders 20 times a second. memo does not intercept context updates; only the provider's value identity matters and it changes on every message. Symptom: React DevTools Profiler shows every consumer flashing on each tick even though its props are identical.
- You move ticks to useSyncExternalStore and the app freezes with 'Maximum update depth exceeded' or 'The result of getSnapshot should be cached'. Cause: getSnapshot returns a fresh object/array literal each call, so Object.is always reports a change. Return a primitive or a reference you cache in the store.
- You install typescript@latest (7.0.2) and `npm run lint` dies with an error about the TypeScript API, or ts-jest/ts-morph blow up. TS7 has no stable programmatic API until 7.1. Either stay on typescript ~6.0.2 (which is what create-vite itself pins) or alias `"typescript": "npm:@typescript/typescript6@^6.0.2"` for the linter while running native tsc separately.
- You upgrade to TS7 and get flooded with errors about `import.meta.env` being untyped and path aliases not resolving. TS7 changed the default `types` to `[]` (add `"types": ["vite/client"]`) and removed `baseUrl` (rewrite paths relative to the tsconfig, or use Vite 8's `resolve.tsconfigPaths: true`).
- You upgrade to Vite 8 and the build errors on an unknown `rollupOptions` key or a Rollup-only plugin. Vite 8 is Rolldown-only: rename to `build.rolldownOptions`, drop `build.commonjsOptions` (no-op), and replace object-form `manualChunks`.
- Every `import { SomeType } from './types'` errors with a message about verbatimModuleSyntax. The Vite template turns it on: type-only imports must be written `import type { SomeType }` or `import { type SomeType }`. Same flag plus erasableSyntaxOnly means TypeScript `enum` is banned — use a const object with `as const`.
- You copy any React Router tutorial and get 'Cannot find module react-router-dom'. v8 deleted that package. Import from `react-router`, and DOM-specific exports like RouterProvider from `react-router/dom`. v8 also demands Node 22.22+ and React 19.2.7+.
- You route every WebSocket tick through queryClient.setQueryData and the UI degrades as message rate rises. Query's cache is designed for request/response resources, not a firehose. Keep ticks in an external store; use Query for positions/orders/instruments and let the socket trigger invalidateQueries on those slower keys.
- Your useQuery component re-renders on every background refetch even though the data is identical. You destructured with rest (`const { data, ...rest } = useQuery(...)`), which touches every property through the tracking Proxy and disables tracked-properties optimization. Destructure only the fields you need.
- Your Zustand selector `useStore(s => ({ bid: s.bid, ask: s.ask }))` re-renders forever. The selector allocates a new object each call and the default comparator is Object.is. Wrap it: `useStore(useShallow(s => ({...})))` — imported from 'zustand/react/shallow' — or select one primitive per hook call.
- You follow a lightweight-charts tutorial and `chart.addCandlestickSeries is not a function`. That method was removed in v5. Import the series type and call `chart.addSeries(CandlestickSeries, options)`. Same class of break: `series.setMarkers()` is now `createSeriesMarkers()`.
- You store the chart instance or the candle array in useState and every tick re-mounts or re-renders the chart. lightweight-charts is imperative: hold the chart and series in refs, create once in an effect, and call `series.update(bar)` directly from the socket handler without touching React state at all.
- You ship the chart and miss the license obligation. Apache-2.0 here requires the NOTICE attribution plus a link to tradingview.com on your page; enabling the `attributionLogo` chart option is the sanctioned shortcut.
- You follow a TanStack Table tutorial and `useReactTable` doesn't exist, or destructured cell methods throw 'Cannot read properties of undefined'. v9 renamed it to `useTable({ features, ... })` and moved methods onto shared prototypes that need `this`, so destructuring breaks them. Use `useLegacyTable` from '@tanstack/react-table/legacy' if you must follow v8 material.
- You enable Vitest browser mode and it fails to find a provider. v4 split them out — install `@vitest/browser-playwright` (or webdriverio/preview) explicitly, and import browser context from 'vitest/browser', not '@vitest/browser/context'.
- You put your broker key in `VITE_BROKER_SECRET` and assume it is server-side. Vite statically inlines every VITE_ variable into the shipped bundle at build time — it is public. Secrets stay in FastAPI.
- Your WebSocket works against localhost:8000 directly but breaks on cookies/CORS. Proxy it through Vite (`'/ws': { target: 'ws://localhost:8000', ws: true }`) so the browser sees a same-origin connection. Avoid `rewriteWsOrigin`, which the Vite docs flag as a CSRF risk.
- You add React Compiler to a Vite 8 project and builds get noticeably slower on a low-power CPU. The compiler still runs through Babel via @rolldown/plugin-babel, reintroducing a JS-speed pass into an otherwise Rust pipeline. Scaffold with `--template react-compiler-ts` if you want it, but measure before keeping it on an 8 GB machine.
- You install Node 20 because a tutorial says it is LTS. Node 20 reached EOL on 2026-03-24. Use Node 24 (Krypton) or 22 (Jod); React Router v8 needs 22.22+ anyway.
- Your hand-rolled socket module's reconnect will fire TWICE per mount in React 18/19 StrictMode dev — the effect mounts, cleans up, remounts. Symptom: two sockets in the Network tab and duplicate messages in dev but not in prod build. Guard with a module-scope refcount, not with a `useRef(false)` 'did I already run' flag (that one silently breaks Fast Refresh).
- Symptom: console warning "The result of getSnapshot should be cached to avoid an infinite loop" plus a frozen tab. Cause: your getSnapshot builds `{ price, ts }` fresh on every call. Fix: keep one snapshot object in the store module and only replace it inside the message handler.
- Symptom: `Error: Missing getServerSnapshot, which is required for server-rendered content` the first time you move the store into Next.js. The third argument to useSyncExternalStore is optional only for client-only apps.
- Symptom: the UI shows 'connected' forever while no ticks arrive, and no 'close' event ever fires. Cause: half-open TCP (laptop slept, wifi switched, NAT timeout). Neither the browser WebSocket API nor partysocket detects this — you need your own ping timer plus a 'no pong within Ns → ws.close() and reconnect' watchdog.
- Symptom: `InvalidAccessError` from ws.close(). You passed a code outside {1000} ∪ [3000,4999] — commonly by echoing back a server close code like 1006 or 1011.
- Symptom: `npm install react-use-websocket` on React 19.2.x produces zero warnings, so you assume it is supported. It declares no peerDependencies at all (verified against the 4.13.0 tarball manifest), so npm cannot warn you. Absence of a warning is not evidence of compatibility here.
- Symptom: mass reconnect storm hammering your FastAPI backend after a restart. Both the naive `2 ** attempt` formula and partysocket's default 1.3^n are jitter-free — every disconnected client retries in lockstep. Add randomized jitter yourself; the reference library does not.
- partysocket buffers messages sent while disconnected and flushes them on open (maxEnqueuedMessages defaults to Infinity). For a market-data or chat app that means stale messages can be delivered minutes late after a long outage — cap maxEnqueuedMessages or clear the queue on reconnect.

### Outdated - distrust any tutorial that says these

- Create React App — long dead. Scaffold with `npm create vite@latest my-app -- --template react-ts` (or `react-compiler-ts` for the compiler pre-wired).
- `Component.defaultProps` on function components — REMOVED in React 19, not merely warned about. Use ES6 default parameters: `function X({ text = 'hi' })`.
- `propTypes` — REMOVED in React 19; checks are silently ignored. TypeScript is the replacement.
- `forwardRef` — obsolete in React 19; ref is an ordinary prop on function components. Still works but is slated for removal.
- `<Context.Provider>` — superseded by rendering `<Context>` directly in React 19.
- `ReactDOM.render`, `ReactDOM.hydrate`, `ReactDOM.unmountComponentAtNode`, `ReactDOM.findDOMNode` — all REMOVED in React 19. Use createRoot/hydrateRoot/root.unmount()/refs.
- String refs (`ref='input'`), `React.createFactory`, legacy context (`contextTypes`/`getChildContext`), module pattern factories — all REMOVED in React 19.
- `react-dom/test-utils` including its `act` — REMOVED; `act` now comes from the `react` package. `react-test-renderer` is deprecated; use React Testing Library.
- useEffect + fetch + useState as the data-fetching pattern — superseded by TanStack Query for server state (caching, dedup, invalidation, retries you would otherwise hand-roll badly).
- `chart.addCandlestickSeries()`, `addLineSeries()`, `addHistogramSeries()` — replaced in lightweight-charts v5 by `chart.addSeries(CandlestickSeries, opts)` with the series type imported explicitly. Also gone: `series.setMarkers()` (now `createSeriesMarkers()`) and the built-in watermark option (now `createTextWatermark()`).
- Legacy Redux boilerplate — hand-written action-type constants, switch-statement reducers, connect()/mapStateToProps, redux-thunk wired manually, immutable spread gymnastics. Redux Toolkit's createSlice is the only sanctioned Redux today, and for a dashboard Zustand is usually the better fit; plain Context is actively wrong for high-frequency ticks.
- `useReactTable` from TanStack Table v8 — replaced by `useTable({ features, ... })` in v9, with tree-shakable opt-in features and readonly data/columns.
- MSW v1 handler syntax (`rest.get(url, (req, res, ctx) => res(ctx.json(...)))`) — v2 uses `http.get(url, () => HttpResponse.json(...))` with standard Request/Response objects.
- Jest + babel-jest + ts-jest for a Vite app — Vitest reuses your Vite config and transform pipeline. (Bonus: ts-jest is additionally blocked on TypeScript 7 until 7.1.)
- `react-router-dom` as a package name — deleted in React Router v8; everything imports from `react-router`.
- `baseUrl` in tsconfig for path aliases, and `"target": "es5"` / `"module": "commonjs"` — all removed in TypeScript 7. Modern Vite tsconfigs use target es2023, module esnext, moduleResolution bundler, and relative `paths`.
- esbuild-specific Vite config (`build.rollupOptions`, `esbuildOptions`, `optimizeDeps.esbuildOptions`) — Vite 8 runs Rolldown + Oxc; rename to `build.rolldownOptions` and migrate to Oxc options, as esbuild support is deprecated.
- react-use-websocket as the default recommendation — last release 4.13.0 with no publish activity since roughly Feb 2025 and no declared React peer dependency. Prefer a hand-written native WebSocket singleton (better for learning) or partysocket.
- `React.FC<Props>` as the standard component annotation — community consensus dropped it; use a plain function with typed props.
- ESLint as the only linter choice for a new Vite app — create-vite's own React template now ships oxlint (Rust, ~50-100x faster), which matters a lot on a low-power CPU and sidesteps the typescript-eslint/TS7 deadlock for non-type-aware rules.
- Treating react-use-websocket as the default React WebSocket hook. It is at 4.13.0 with no publish and no repo commit since 2025-02-04 (verified), 95 open issues, and open unanswered React 19 compatibility threads — while React itself is at 19.2.8 (2026-07-21). It still works for many people and is not deprecated or archived, but it is not a safe default to teach in 2026.
- The previous researcher's framing that partysocket is a low-level socket you must wrap in your own hook. Wrong as of 1.3.0: it exports `partysocket/react` (usePartySocket) and `partysocket/use-ws` (useWebSocket) with an optional react >=17 peerDependency.
- Citing github.com/partykit/partykit or a standalone reconnecting-websocket package as partysocket's home. The package now lives in the cloudflare/partykit monorepo under packages/partysocket (its published package.json repository field points there). The README's line 'the source for this has been moved to the partyserver repository' is stale/confusing — partyserver is a sibling package in that same monorepo, not a separate home for partysocket.
- Assuming a package with no peerDependencies field is 'flexible about React versions'. For react-use-websocket the field was present in the 0.9.x era (react >=16.8.0) and is gone in 4.13.0 — the practical effect is that npm's compatibility check is disabled, not that compatibility is broad.

<details>
<summary>Sources (81)</summary>

- https://api.github.com/repos/cloudflare/partykit
- https://api.github.com/repos/robtaussig/react-use-websocket
- https://api.github.com/search/issues?q=repo:robtaussig/react-use-websocket+is:issue+is:open+React+19
- https://api.npmjs.org/downloads/point/last-week/partysocket
- https://api.npmjs.org/downloads/point/last-week/react-use-websocket
- https://devblogs.microsoft.com/typescript/
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/close
- https://github.com/cloudflare/partykit/tree/main/packages/partysocket
- https://github.com/tradingview/lightweight-charts
- https://mswjs.io/docs/integrations/browser
- https://nodejs.org/en/about/previous-releases
- https://openapi-ts.dev/introduction
- https://raw.githubusercontent.com/cloudflare/partykit/main/packages/partysocket/src/react.ts
- https://raw.githubusercontent.com/cloudflare/partykit/main/packages/partysocket/src/ws.ts
- https://raw.githubusercontent.com/robtaussig/react-use-websocket/master/package.json
- https://raw.githubusercontent.com/vitejs/vite/main/packages/create-vite/README.md
- https://raw.githubusercontent.com/vitejs/vite/main/packages/create-vite/template-react-ts/package.json
- https://raw.githubusercontent.com/vitejs/vite/main/packages/create-vite/template-react-ts/tsconfig.app.json
- https://react-typescript-cheatsheet.netlify.app/docs/basic/getting-started/function_components
- https://react.dev/blog
- https://react.dev/blog/2024/04/25/react-19-upgrade-guide
- https://react.dev/blog/2024/12/05/react-19
- https://react.dev/blog/2025/10/01/react-19-2
- https://react.dev/learn/react-compiler/installation
- https://react.dev/reference/react/memo
- https://react.dev/reference/react/useSyncExternalStore
- https://reactrouter.com/upgrading/v7
- https://registry.npmjs.org/-/v1/search?text=partysocket
- https://registry.npmjs.org/-/v1/search?text=react
- https://registry.npmjs.org/-/v1/search?text=react-use-websocket
- https://registry.npmjs.org/@hey-api/openapi-ts/latest
- https://registry.npmjs.org/@playwright/test/latest
- https://registry.npmjs.org/@tanstack/react-query/latest
- https://registry.npmjs.org/@tanstack/react-router/latest
- https://registry.npmjs.org/@tanstack/react-table/latest
- https://registry.npmjs.org/@tanstack/react-virtual/latest
- https://registry.npmjs.org/@testing-library/react/latest
- https://registry.npmjs.org/@visx/xychart/latest
- https://registry.npmjs.org/@vitejs/plugin-react/latest
- https://registry.npmjs.org/babel-plugin-react-compiler/latest
- https://registry.npmjs.org/echarts/latest
- https://registry.npmjs.org/eslint-plugin-react-hooks/latest
- https://registry.npmjs.org/lightweight-charts/latest
- https://registry.npmjs.org/msw/latest
- https://registry.npmjs.org/openapi-fetch/latest
- https://registry.npmjs.org/openapi-react-query/latest
- https://registry.npmjs.org/openapi-typescript/latest
- https://registry.npmjs.org/orval/latest
- https://registry.npmjs.org/oxlint/latest
- https://registry.npmjs.org/partysocket/latest
- https://registry.npmjs.org/react-router/latest
- https://registry.npmjs.org/react-use-websocket/latest
- https://registry.npmjs.org/react/latest
- https://registry.npmjs.org/recharts/latest
- https://registry.npmjs.org/typescript/latest
- https://registry.npmjs.org/uplot/latest
- https://registry.npmjs.org/vite/latest
- https://registry.npmjs.org/vitest/latest
- https://registry.npmjs.org/zustand/latest
- https://tanstack.com/blog/announcing-tanstack-table-v9
- https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation
- https://tanstack.com/query/latest/docs/framework/react/guides/render-optimizations
- https://tanstack.com/query/latest/docs/reference/streamedQuery
- https://tanstack.com/router/latest/docs/framework/react/comparison
- https://tkdodo.eu/blog/using-web-sockets-with-react-query
- https://tradingview.github.io/lightweight-charts/docs
- https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesApi
- https://tradingview.github.io/lightweight-charts/docs/migrations/from-v4-to-v5
- https://tradingview.github.io/lightweight-charts/docs/series-types
- https://unpkg.com/partysocket@1.3.0/package.json
- https://unpkg.com/react-use-websocket@4.13.0/package.json
- https://vite.dev/blog/announcing-vite8
- https://vite.dev/config/server-options
- https://vite.dev/config/shared-options
- https://vite.dev/guide/env-and-mode
- https://vite.dev/guide/migration
- https://vitest.dev/blog/vitest-4
- https://www.typescriptlang.org/tsconfig/verbatimModuleSyntax.html
- https://zustand.docs.pmnd.rs/reference/hooks/use-shallow

</details>

---

# For Document 3 - ML Algorithmic Trading Engine

## Quant and ML Trading Research Stack

<sub>1 report(s) &middot; 26 verified, 3 likely &middot; 14 pitfalls &middot; 12 outdated patterns &middot; 56 sources</sub>

### Facts

- **VERIFIED** pandas 3.0 is the current major series: 3.0.5 is latest, 3.0.0 shipped 2026-01-21, requires Python >=3.11 and numpy >=1.26.
  - Copy-on-Write is now enforced (mode.copy_on_write deprecated, removed in 4.0); every indexing op behaves as a copy, chained assignment `df[col][row] = v` silently does nothing, and SettingWithCopyWarning is GONE — so the old warning that used to catch this bug no longer fires. Methods with inplace=True now return self instead of None. Strings infer to a dedicated `str` dtype (PyArrow-backed if pyarrow installed, numpy object fallback otherwise); pyarrow is OPTIONAL, not required. pytz is no longer a dependency — tz is zoneinfo.ZoneInfo. String-parsed datetimes now default to datetime64[us], not [ns].
- **VERIFIED** numpy is at 2.5.2 and requires_python is >=3.12.
  - Practical consequence on an 8 GB Windows box: your Python floor is effectively 3.12 if you want current numpy. Cross-check against nannyml, which caps at <3.13 — the two only overlap on Python 3.12.
- **VERIFIED** NumPy 2.x removed aliases that appear in almost every pre-2024 trading tutorial; `ruff check --select NPY201` auto-fixes most of them.
  - Removed/renamed: np.float_→np.float64, np.int_→np.intp, np.complex_→np.complex128, np.NaN→np.nan, np.Inf/np.Infinity/np.infty→np.inf, np.NINF→-np.inf, np.string_, np.unicode_, np.cfloat, np.longfloat. np.in1d→np.isin, np.row_stack→np.vstack, np.trapz→np.trapezoid, np.product→np.prod, np.cumproduct→np.cumprod, np.asfarray gone. NEP 50 promotion: np.float32(3) + 3. now returns float32 (was float64) — silent precision loss in indicator code. np.array(..., copy=False) semantics changed; use np.asarray(). ndarray.ptp() and .newbyteorder() removed. Default int is 64-bit on 64-bit Windows now.
- **VERIFIED** scikit-learn is 1.9.0, requires Python >=3.11; polars/pandas interop now goes through the `narwhals` library.
  - 1.9 adds an experimental callbacks API (sklearn.callback.ProgressBar, ScoringMonitor) supported by Pipeline, GridSearchCV, RandomizedSearchCV, Halving*SearchCV, StandardScaler, LogisticRegression(lbfgs) — genuinely useful on a slow CPU to see whether a grid search is progressing. Also sklearn.set_config(sparse_interface="sparray").
- **VERIFIED** TimeSeriesSplit signature is `TimeSeriesSplit(n_splits=5, *, max_train_size=None, test_size=None, gap=0)` and it has NO purging and NO embargo.
  - `gap` only drops N samples from the END of each train fold — a one-sided buffer. It cannot remove earlier training rows whose forward-looking labels overlap the test window, which is exactly the leak that triple-barrier / n-bar-forward labels create. This is the precise gap that Purged K-Fold fills.
- **VERIFIED** scikit-learn 1.9 deprecated `probability=True` on SVC/NuSVC (not thread-safe) and directs users to CalibratedClassifierCV instead; LogisticRegressionCV's default scoring changes from accuracy to neg_log_loss in 1.11.
  - Also deprecated: tree criterion="friedman_mse" → "squared_error"; TargetEncoder shuffle/random_state. For trading you want calibrated probabilities (position sizing keys off P(win)), so CalibratedClassifierCV wrapping an already-fitted or CV-fitted booster is the right pattern — but its internal cv must itself be time-aware or you re-introduce leakage.
- **VERIFIED** LightGBM 4.7.0 (2026-07-18), requires Python >=3.10; the repo moved from github.com/microsoft/LightGBM to github.com/lightgbm-org/LightGBM in March 2026.
  - 4.7.0 adds native polars input support via narwhals, first ROCm builds, multi-GPU via NCCL. PyPI wheels bundle a compiled library with CPU support out of the box on Windows — no build toolchain needed. Minimum pyarrow bumped to 16.0. The org move (Microsoft was considering archiving the repo) is 'likely' rather than fully verified but the lightgbm-org repo is the live canonical one.
- **VERIFIED** XGBoost is 3.4.1 and now requires Python >=3.12 — a harder floor than LightGBM's >=3.10.
  - XGBoost 3.0 introduced ExtMemQuantileDMatrix for external-memory (out-of-core) training with the hist method on CPU and GPU, extended external memory to categorical data and all objectives, and made QuantileDMatrix work with all prediction types with CPU prediction on par with plain DMatrix. On 8 GB RAM, QuantileDMatrix/ExtMemQuantileDMatrix are the memory levers that matter.
- **VERIFIED** CatBoost is 1.2.10 (2026-02-18) and declares no requires_python at all.
  - 1.2.9 and 1.2.10 landed a day apart (2026-02-17/18) after a gap since 1.2.8 (2025-04-13). The absent requires_python means pip will happily install it on a Python it wasn't tested against. For a weak CPU, CatBoost's ordered boosting is the slowest of the three on wide tabular data; LightGBM's leaf-wise histogram algorithm is the pragmatic default, with CatBoost reserved for genuinely high-cardinality categoricals (sector, symbol id).
- **VERIFIED** TA-Lib now ships prebuilt Windows wheels on PyPI — version 0.6.6 includes ta_lib-0.6.6-cp39/310/311/312/313-win_amd64.whl (plus win32 and win_arm64).
  - This kills the single most-cited reason to avoid TA-Lib. The old advice ('you must compile the C library / hunt for Gohlke wheels / use conda') is obsolete: `pip install TA-Lib` works on Windows for CPython 3.9–3.13. requires_python is >=3.9. Note the import name is `talib` and the PyPI name is `TA-Lib`.
- **VERIFIED** pandas-ta is effectively dead: last release 0.4.71b0 on 2025-09-14, github.com/twopirllc/pandas-ta returns 404, and its documentation domain pandas-ta.dev no longer resolves in DNS.
  - I got a live 404 on the GitHub repo and ENOTFOUND on www.pandas-ta.dev. Reports indicate the project was slated for archival absent sponsorship by 2026-07-01. Any tutorial that opens with `import pandas_ta as ta` is now pointing at an unmaintained, undocumented package.
- **VERIFIED** pandas-ta-classic 0.6.52 (2026-06-24) is the live community fork: 193 indicators + 62 candlestick patterns, requires Python >=3.10, numpy>=2.0, pandas>=2.0.
  - Repo github.com/xgboosted/pandas-ta-classic. It declares pandas>=2.0 but does not explicitly claim pandas 3.0 support — expect Copy-on-Write friction where the old DataFrame-extension accessor pattern mutated frames in place. pandas-ta-openbb is a second fork (NumPy 2 / OpenBB oriented).
- **VERIFIED** The `ta` package (bukosabino/ta) is at 0.11.0, last released 2023-11-02 — nearly three years stale as of now.
  - Pre-dates numpy 2 and pandas 3 entirely. For a learner who should understand the math, the correct call is: hand-roll ~10 indicators (SMA/EMA, RSI, ATR, Bollinger, MACD, rolling z-score, realized vol, returns) in ~150 lines of pandas/numpy, and use TA-Lib 0.6.6 purely as a numerical cross-check oracle in unit tests. Hand-rolling is also the only way you will notice your own centered-window look-ahead bugs.
- **VERIFIED** backtrader's last PyPI release is 1.9.78.123 from 2023-04-19 — unmaintained for over three years.
  - It will still run, but it predates pandas 2.x behavioural changes, numpy 2, and pandas 3 CoW. Treat any backtrader tutorial as legacy.
- **VERIFIED** vectorbt (open source) was revived and is now at 1.1.0 (2026-07-05), after 1.0.0 (2026-04-22) and 0.28.x through March 2026 — it is explicitly 'the open-source community edition of VectorBT PRO'.
  - Licence is 'fair-code': Apache 2.0 WITH Commons Clause — source is public and free to use, but you may not sell a product or service that is primarily this software. Supports Python 3.11–3.14. vectorbtpro is NOT on public PyPI (404) — it is a paid private repo. The widely repeated claim that open-source vectorbt is abandoned in favour of PRO is now out of date.
- **VERIFIED** backtesting.py is at 0.6.6 (2026-07-22) and actively maintained; nautilus_trader is at 1.231.0 with win_amd64 wheels and requires Python >=3.12,<3.15.
  - backtesting.py is single-instrument, vectorised-ish, tiny API, supports a commission parameter — ideal as the cross-check oracle for a hand-built engine on one symbol. NautilusTrader is a Rust-native deterministic event-driven engine — architecturally the model to imitate, but heavy for 8 GB. zipline-reloaded 3.1.1 (requires >=3.10) is the maintained Zipline; QuantConnect Lean is Apache-2.0 C#/Python and now wants the dotnet 10 SDK with LEAN CLI as the recommended path — too much surface area for a laptop-scale learner.
- **VERIFIED** Metrics libraries: quantstats 0.0.81 (2026-01-13) is alive; original empyrical is dead (0.5.5, 2020-10-13); the live forks are empyrical-reloaded 0.5.12 and pyfolio-reloaded 0.9.9 (2025-06-02), both by Stefan Jansen.
  - pyfolio-reloaded depends on empyrical-reloaded>=0.5.9. Use quantstats for the tearsheet, empyrical-reloaded for individual ratio functions. Do not `pip install empyrical` or `pip install pyfolio` — you get 2020-era code.
- **VERIFIED** DuckDB is at 1.5.5 (requires Python >=3.10); TimescaleDB is at 2.24.0 and the company renamed itself from Timescale to TigerData on 2025-06-17.
  - DuckDB version verified from PyPI; the TimescaleDB version/rename is 'likely' (search-sourced). TimescaleDB remains dual-licensed: Apache 2.0 core plus a source-available Timescale/Tiger License for the community-edition extras. For hobby-scale NSE OHLCV, Parquet-on-disk partitioned by symbol/year + DuckDB querying it in place is the right answer: zero server process, zero RAM baseline, and DuckDB reads Parquet directly without an ingest step. TimescaleDB only earns its keep once you are streaming ticks continuously.
- **VERIFIED** MLflow is at 3.15.1 (requires Python >=3.10) and the Model Registry REQUIRES a database-backed store — the default file-based ./mlruns directory will not give you a registry.
  - Local, fully offline setup: `mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000`. Plain file store works for tracking only (`mlflow server --port 5000`, logs to ./mlruns). MLflow 3 model URIs are `models:/<model_id>`; legacy forms `runs:/<run_id>/<artifact_path>` and `models:/<name>/<version>` still work. DVC is 3.67.1 (>=3.9), wandb is 0.28.2 (>=3.10) and is cloud-first with self-managed only as an enterprise deployment — for an offline 8 GB laptop, MLflow+SQLite is the low-friction choice and DVC is worth it only once datasets exceed what git can hold.
- **VERIFIED** Drift tooling: evidently 0.7.21 (requires >=3.10) is actively developed; nannyml is stuck at 0.13.1 (2025-07-12) and is pinned to `<3.13,>=3.9`.
  - The nannyml Python cap is a real install trap: current numpy (2.5.2) requires >=3.12, so nannyml and current numpy coexist only on Python 3.12 exactly. nannyml's distinctive feature is CBPE/DLE — estimating post-deployment performance without labels, which matters in trading because labels arrive only after the holding period elapses.
- **VERIFIED** mlfinlab is no longer installable from PyPI (404); the maintained sklearn-compatible route to purged CV is skfolio 0.20.2, which ships `CombinatorialPurgedCV(n_folds=10, n_test_folds=8, purged_size=0, embargo_size=0)`.
  - Hudson & Thames' mlfinlab went closed/limbo over a broken licensing system. skfolio (requires >=3.10) exposes Combinatorial Purged CV and Walk Forward as ordinary sklearn splitters. Semantics: n_folds>=3, n_test_folds>=2, train uses the remaining n_folds - n_test_folds; purged_size trims training observations at BOTH ends of each contiguous train block that temporally overlap test labels; embargo_size drops observations immediately AFTER the test block. A `n_test_paths` property reports how many full backtest paths can be reconstructed from the C(n_folds, n_test_folds) combinations — this is the point of CPCV: many paths, not one.
- **VERIFIED** Zerodha brokerage (live from zerodha.com/charges): equity delivery = ZERO; equity intraday, equity futures, currency futures, commodity futures = 0.03% or ₹20 per executed order, whichever is LOWER; all options (equity, currency, commodity) = flat ₹20 per executed order.
  - Note 'per executed order', not per trade — one order filling in five parts is still one ₹20 charge, but a strategy that slices into five orders pays 5×₹20. That asymmetry is a real cost-model detail.
- **VERIFIED** STT was HIKED in Budget 2026 effective 2026-04-01: futures went 0.02% → 0.05% (sell side), options went to 0.15% on premium (sell side) and 0.15% of intrinsic value on exercise. Equity delivery (0.1% on BOTH buy and sell) and intraday (0.025% sell side only) were unchanged.
  - Cross-verified on Zerodha's charges page and ClearTax. This is a ~150% increase on futures and up to ~50% on options and is almost certainly absent from any pre-2026 training data or tutorial. Anyone modelling F&O costs with 0.0125%/0.02% futures STT or 0.0625%/0.10% options STT is now materially wrong. Equity MF/ETF sale STT remains 0.001%.
- **VERIFIED** The remaining Zerodha/statutory charge stack, verbatim: NSE exchange transaction charge equity 0.00307%, NSE futures 0.00183%, NSE options 0.03553% on premium; BSE equity 0.00375%, BSE futures 0%, BSE options 0.0325% on premium. SEBI charges ₹10 per crore. GST 18% on (brokerage + SEBI charges + transaction charges). Stamp duty (BUY side only): delivery 0.015% or ₹1500/crore, intraday 0.003% or ₹300/crore, futures 0.002% or ₹200/crore, options 0.003% or ₹300/crore. DP charge ₹15.34 per scrip on SELL (₹3.5 CDSL + ₹9.5 Zerodha + ₹2.34 GST).
  - Enough to reproduce a Zerodha contract note. Two details learners get wrong: GST is NOT charged on STT or stamp duty; and the DP charge is per scrip per day regardless of quantity, so it dominates for small delivery positions — selling ₹5,000 of one stock costs ₹15.34 in DP alone, i.e. ~31 bps, on top of 10 bps STT.
- **VERIFIED** Zerodha Kite Connect: a free 'Personal' plan covers orders, GTT and alerts but NOT market data; the paid Connect plan is ₹500/month per API key and includes realtime WebSocket streaming AND historical candle data.
  - Documented rate limits (kite.trade/docs/connect/v3/exceptions): quote 1 req/sec, historical candle data 3 req/sec, order placement 10 req/sec, all other endpoints 10 req/sec; hard caps of 10 orders/second, 400 orders/minute, 5,000 orders/day per user/API key, and max 25 modifications per order. The 3 req/sec historical limit is the binding constraint when backfilling: ~1,800 symbol-days per 10 minutes at best.
- **VERIFIED** The canonical citations for backtest-overfitting statistics: Deflated Sharpe Ratio — Bailey & López de Prado (2014), Journal of Portfolio Management Vol. 40 No. 5, pp. 94–107, SSRN abstract 2460551. Probability of Backtest Overfitting — Bailey, Borwein, López de Prado & Zhu (2013), SSRN abstract 2326253, which introduces Combinatorially Symmetric Cross-Validation (CSCV).
  - DSR builds on the Probabilistic Sharpe Ratio and corrects for two inflation sources: selection bias from multiple testing (N trials) and non-normal returns (it uses the third and fourth moments — skew and kurtosis — plus sample length). PBO/CSCV is model-free and non-parametric: split the returns matrix into S even sub-periods, form all C(S, S/2) in-sample/out-of-sample partitions, and measure how often the in-sample-best configuration lands in the bottom half out-of-sample. Both papers are free at davidhbailey.com/dhbpapers/. Purged cross-validation itself is López de Prado (2017), Advances in Financial Machine Learning, ch. 7.
- *likely* NSE market structure changed on 2026-08-03: a Closing Auction Session (CAS) now sets the closing price for stocks with active F&O contracts. Their continuous session ends at 3:15 PM (not 3:30), CAS runs 3:15–3:35 PM, and all index/stock futures and options now close uniformly at 3:40 PM.
  - CAS sub-windows: 3:00–3:15 reference price computed from recent trades; 3:15–3:20 reference price published, no order entry; 3:20–3:25 market and limit orders accepted with running auction data published; 3:25–3:30 limit orders only, with a RANDOM order-entry freeze between 3:28 and 3:30; 3:30–3:35 matching, equilibrium price determined, constrained to ±3% of the reference price. Non-F&O stocks are unchanged: continuous to 3:30 PM with closing price = VWAP of the last 30 minutes (3:00–3:30). VWAP is now only the fallback for CAS stocks when circuit breakers halt trading. A further afternoon-framework phase reportedly rolled out 2026-09-07. Sourced from two secondary outlets, not an NSE circular (nseindia.com blocks automated fetches) — verify against the NSE circular before hard-coding.
- *likely* NSE pre-open session is 9:00–9:15 AM (9:00–9:07 order entry/modify, 9:07–9:08 exchange matches and sets the opening price, 9:08–9:15 buffer with no new orders). Settlement is T+1 as standard, with optional T+0 same-day settlement available for the top 500 stocks.
  - Pre-open timings verified from Zerodha's support article; the T+0 status (beta launched 2024-03-28 for 25 scrips, widened to the top 500 in phases from 2025-01-31, still optional and running in parallel to T+1) is search-sourced. Backtest consequence: your first tradable bar is 9:15, and the 9:15 open is an auction-discovered price — a strategy that 'buys the open' is buying at a price that was set by a matching process you were not part of unless you submitted into pre-open.
- *likely* Slippage anchors from NSE's own impact-cost measure: Nifty 50 impact cost was 0.02% for a ₹50 lakh order (March 2026), and Nifty 50 inclusion requires a stock to have traded at ≤0.50% average impact cost for a ₹10 crore basket in 90% of observations over six months.
  - So for hobby-size orders in Nifty 50 names, 2–5 bps one-way slippage is defensible; the 0.50% figure is the WORST any index-eligible stock is allowed to be at institutional size. Outside the F&O/Nifty-500 universe, spreads alone can exceed 50 bps and a ₹10 lakh order can move an illiquid name 2–5%. Practical rule: model slippage as max(half_spread, k × (order_value / ADV)) and refuse to backtest names whose median 20-day traded value is below ~₹5 crore. A flat 30 bps all-in (commission + tax + slippage) is a common conservative blanket assumption for portfolio-level work.

### Pitfalls you will actually hit

- pandas 3.0 removed SettingWithCopyWarning. Your chained assignment (`df[df.symbol=='X']['signal'] = 1`) now fails SILENTLY with no warning at all — the frame is simply unchanged and your feature column is all NaN/zero. Symptom: a feature that is stubbornly constant, or a model with suspiciously chance-level accuracy. Fix: always `df.loc[mask, 'signal'] = 1`.
- numpy 2.5.2 requires Python >=3.12 but nannyml pins <3.13, so on any Python other than exactly 3.12 pip will either refuse to resolve or silently downgrade numpy. Symptom: `ResolutionImpossible`, or a resolver that quietly installs numpy 1.26 and then pandas 3 warnings about minimum versions.
- `pip install pandas_ta` still succeeds and imports fine, but the GitHub repo is 404 and pandas-ta.dev does not resolve — so when an indicator behaves oddly there is no documentation and no issue tracker to consult. Symptom: you cannot find the docs for a function you are already calling.
- Predicting the same bar's return from that bar's close. If your feature row is timestamped at bar t's close and your label is (close_t - close_{t-1})/close_{t-1}, you have encoded the answer in the question. Symptom: near-perfect accuracy, Sharpe over 5, an equity curve that is a straight line. The label must be forward-looking from t: (close_{t+h} - close_t)/close_t, and the feature must use only data available at or before t's close — and even then you cannot trade at close_t, you trade at open_{t+1}.
- Centered rolling windows. `df.rolling(20, center=True)` and `scipy.signal.savgol_filter` and any `.interpolate()` over gaps peek forward by construction. Symptom: an indicator that turns exactly at local tops and bottoms. Every window in a trading feature must be trailing (`center=False`, the default) — but pandas will not stop you from passing center=True.
- Fitting StandardScaler (or any imputer, PCA, or target encoder) on the full dataset before splitting. The test-fold mean and variance leak backwards into training. Symptom: cross-validated score materially better than a strict walk-forward score on the same data. Fix: put every transform inside an sklearn Pipeline and pass the Pipeline to the CV splitter, never fit_transform the whole frame first.
- Using TimeSeriesSplit with multi-bar labels. If your label looks forward h bars, then the last h training rows before each test fold have labels computed from prices INSIDE the test window. `gap=h` patches the trailing edge but does nothing for the leading edge in a combinatorial scheme, and nothing at all for serial correlation after the test block. Symptom: CV Sharpe that degrades sharply when you switch to purged CV with an embargo.
- Survivorship bias in the NSE universe. Backtesting today's Nifty 50 constituents over 2015–2026 tests a basket selected for having survived and grown. Symptom: an implausibly good buy-and-hold benchmark that your strategy struggles to beat. You need point-in-time index membership (with the index reconstitution dates) plus delisted and suspended symbols, which most free NSE data sources do not provide.
- Retroactively adjusted split/bonus/dividend prices. Adjusted series rewrite history: a 1:10 split applied to the whole back-series means your 2018 'price' was never quotable in 2018, and any absolute-price feature (round-number levels, price bands, tick-size regime) becomes fiction. Symptom: features keyed to price levels work in backtest and die live. Keep both raw and adjusted series and be explicit about which each feature uses.
- Assuming a fill at a price your order could not have reached — filling at the exact low of the bar, at the close of the same bar your signal fired, or at any price when the stock was at its circuit limit with no counterparty. Symptom: backtest fills cluster suspiciously at bar extremes. Model fills at next-bar open plus slippage, and drop bars where the stock was locked in upper/lower circuit.
- The ₹15.34 DP charge is per scrip per sell day regardless of quantity, and stamp duty is buy-side only. A cost model that applies a symmetric percentage to both legs will understate the cost of small delivery trades by a wide margin — on a ₹5,000 position the DP charge alone is ~31 bps one way.
- F&O stocks stopped trading continuously at 3:30 PM on 2026-08-03. If your bar pipeline still assumes a 3:30 close for F&O names, your last 15-minute bar (3:15–3:30) is now an auction window, not continuous trading, and your 'close' is no longer the 30-minute VWAP for those stocks. Symptom: a discontinuity in your last intraday bar's volume and range starting August 2026.
- Reporting the best walk-forward result out of many configurations tried, without any multiple-testing correction. If you tested 200 parameter sets, the best observed Sharpe is an order statistic, not an estimate. Symptom: a strategy that is excellent in backtest and mediocre live. Report the number of trials N, compute the Deflated Sharpe Ratio, and compute PBO via CSCV.
- XGBoost 3.4.1 requires Python >=3.12 while LightGBM only needs >=3.10 and CatBoost declares no floor at all. Symptom: `pip install xgboost` on a 3.11 env installs an ancient 2.x version without an obvious error, and your code silently runs against a different API.

### Outdated - distrust any tutorial that says these

- 'TA-Lib is a nightmare on Windows — compile the C library, use conda, or hunt for Gohlke wheels.' OBSOLETE: TA-Lib 0.6.6 ships official win_amd64, win32 and win_arm64 wheels for CPython 3.9–3.13. `pip install TA-Lib` just works.
- 'Use pandas-ta, it's the pure-Python alternative to TA-Lib.' OBSOLETE: the repo is gone (404), the docs domain does not resolve, and the last release was 2025-09-14. Use pandas-ta-classic 0.6.52 or hand-roll.
- 'Enable Copy-on-Write with pd.options.mode.copy_on_write = True' and 'watch for SettingWithCopyWarning'. OBSOLETE in pandas 3.0: CoW is enforced, the option is deprecated and removed in 4.0, and SettingWithCopyWarning no longer exists.
- 'Use dtype_backend="pyarrow" to get PyArrow-backed strings.' PARTLY OBSOLETE: pandas 3.0 infers a dedicated `str` dtype by default, PyArrow-backed when pyarrow is installed. pyarrow remains optional, not required — the widely-repeated 'pandas 3 will make PyArrow a hard dependency' plan did not land that way.
- 'Open-source vectorbt is abandoned; the author only develops vectorbtpro now.' OUT OF DATE: open-source vectorbt reached 1.0.0 in April 2026 and 1.1.0 in July 2026. Caveat: its licence is Apache 2.0 WITH Commons Clause, so it is 'fair-code', not OSI open source — you cannot build a commercial product that is primarily vectorbt.
- 'STT on futures is 0.0125% (or 0.02%) and on options 0.0625% (or 0.10%) of premium.' WRONG since 2026-04-01: Budget 2026 raised futures to 0.05% sell side and options to 0.15% on premium and 0.15% of intrinsic value on exercise.
- 'NSE equity trades continuously 9:15 AM to 3:30 PM and the closing price is the last 30-minute VWAP.' WRONG for F&O stocks since 2026-08-03: they now stop continuous trading at 3:15 PM and their close is set by the Closing Auction Session equilibrium price; derivatives contracts run to 3:40 PM. Only non-F&O stocks still use the 3:00–3:30 VWAP.
- 'Indian settlement is T+2.' OBSOLETE: T+1 is the standard cycle, with optional same-day T+0 available for the top 500 stocks.
- 'pip install empyrical / pyfolio / mlfinlab.' OBSOLETE: empyrical's last release was 2020, pyfolio is superseded by pyfolio-reloaded 0.9.9 and empyrical-reloaded 0.5.12, and mlfinlab is no longer on PyPI at all (404). For purged and combinatorial purged CV, use skfolio 0.20.2.
- 'np.float_, np.NaN, np.in1d, np.trapz, arr.ptp()' and friends. REMOVED in NumPy 2.0 — and NEP 50 changed scalar promotion so mixed float32/Python-float arithmetic now yields float32 instead of silently upcasting.
- 'LightGBM lives at github.com/microsoft/LightGBM.' MOVED (March 2026) to github.com/lightgbm-org/LightGBM after Microsoft considered archiving it; same maintainers, and PyPI installs are unaffected.
- 'Timescale' as a company name. Renamed to TigerData in June 2025; documentation now lives at docs.tigerdata.com.

<details>
<summary>Sources (56)</summary>

- https://cleartax.in/s/securities-transaction-tax-stt
- https://docs.tigerdata.com/about/latest/timescaledb-editions/
- https://github.com/QuantConnect/Lean
- https://github.com/lightgbm-org/LightGBM
- https://github.com/polakowo/vectorbt
- https://hudsonthames.org/mlfinlab-on-pypi-index/
- https://kernc.github.io/backtesting.py/
- https://kite.trade/docs/connect/v3/exceptions/
- https://mlflow.org/docs/latest/ml/tracking/
- https://numpy.org/doc/stable/numpy_2_0_migration_guide.html
- https://pandas.pydata.org/docs/whatsnew/index.html
- https://pandas.pydata.org/docs/whatsnew/v3.0.0.html
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
- https://pypi.org/project/catboost/#history
- https://pypi.org/project/lightgbm/#history
- https://pypi.org/project/vectorbt/#history
- https://pypi.org/pypi/TA-Lib/json
- https://pypi.org/pypi/backtesting/json
- https://pypi.org/pypi/backtrader/json
- https://pypi.org/pypi/catboost/json
- https://pypi.org/pypi/duckdb/json
- https://pypi.org/pypi/dvc/json
- https://pypi.org/pypi/empyrical-reloaded/json
- https://pypi.org/pypi/empyrical/json
- https://pypi.org/pypi/evidently/json
- https://pypi.org/pypi/lightgbm/json
- https://pypi.org/pypi/mlflow/json
- https://pypi.org/pypi/nannyml/json
- https://pypi.org/pypi/nautilus_trader/json
- https://pypi.org/pypi/numpy/json
- https://pypi.org/pypi/pandas-ta-classic/json
- https://pypi.org/pypi/pandas-ta/json
- https://pypi.org/pypi/pandas/json
- https://pypi.org/pypi/polars/json
- https://pypi.org/pypi/pyfolio-reloaded/json
- https://pypi.org/pypi/quantstats/json
- https://pypi.org/pypi/scikit-learn/json
- https://pypi.org/pypi/skfolio/json
- https://pypi.org/pypi/ta/json
- https://pypi.org/pypi/vectorbt/json
- https://pypi.org/pypi/wandb/json
- https://pypi.org/pypi/xgboost/json
- https://pypi.org/pypi/zipline-reloaded/json
- https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- https://scikit-learn.org/stable/whats_new/v1.9.html
- https://skfolio.org/generated/skfolio.model_selection.CombinatorialPurgedCV.html
- https://support.zerodha.com/category/trading-and-markets/trading-faqs/articles/what-are-the-market-timings
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
- https://www.nseindia.com/static/products-services/indices-nifty50-index
- https://www.outlookmoney.com/invest/nse-extended-fo-timings-and-new-closing-auction-session-rules-explained
- https://www.sahi.com/blogs/closing-auction-session-cas-explained-nse-bse-closing-price-rules-2026
- https://xgboost.readthedocs.io/en/stable/changes/v3.0.0.html
- https://zerodha.com/charges/
- https://zerodha.com/products/api/

</details>

---

