# PhotoSense — The Applied ML/AI Mentor Handbook

A **project-driven** apprenticeship handbook for machine learning. We build **PhotoSense** — a semantic photo search engine that ingests a folder of *your own photos* and makes them searchable by meaning — and every ML topic is introduced **only when the product makes it necessary**, never as isolated theory.

> **The single rule of this handbook:**
> We don't say *"today we learn convolutional neural networks."*
> We say *"PhotoSense must recognize what's IN a photo — that needs a model that understands images — which means we now need to understand CNNs."*
> Then we build it.

Type `"beach sunset with friends"` and PhotoSense returns the right photos from your library — because it classified the scenes, detected the objects, read the text, embedded everything into vectors, and searched them by meaning. Every chapter builds one piece of that machine.

---

## 1. What we are building — and why THIS project teaches THIS stack

PhotoSense is not a toy dataset exercise. It is a real product with real requirements, and each requirement forces a core ML discipline into the curriculum at exactly the moment you need it:

```
"beach sunset with friends"
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                        PhotoSense                           │
│                                                             │
│  Your photo folder                                          │
│        │                                                    │
│        ▼                                                    │
│  [classify scene]──── needs CNNs, transfer learning (04-05) │
│  [detect objects]──── needs object detection      (09)      │
│  [segment regions]─── needs segmentation          (10)      │
│  [read text/OCR]───── needs OCR                   (11)      │
│  [embed meaning]───── needs Transformers, CLIP    (06-07)   │
│        │                                                    │
│        ▼                                                    │
│  [vector index]────── needs vector search         (08)      │
│  [ingest pipeline]─── needs pipeline engineering  (12)      │
│  [API + demo UI]───── needs serving               (13)      │
│  [is it good?]─────── needs evaluation            (14)      │
└─────────────────────────────────────────────────────────────┘
```

**Why this project?** Because semantic photo search happens to require, in a natural order, almost the entire modern applied-ML stack: classic supervised learning, neural networks, CNNs, transfer learning, attention and Transformers, embeddings, vector databases, detection, segmentation, OCR, pipelines, serving, and evaluation. Nothing is bolted on. The product *creates the pain* that justifies each technology:

- We want to search photos by meaning → we *need* embeddings.
- Embeddings are useless without retrieval → we *need* vector search.
- "Sunset" isn't enough; users ask about *things* in photos → we *need* detection.
- Photos contain signs, menus, receipts → we *need* OCR.
- A hundred scripts is not a product → we *need* a pipeline and an API.
- "It seems to work" is not engineering → we *need* evaluation.

Tech is never "assigned" — it *grows out of* the project.

Two chapters (15 unsupervised learning, 16 reinforcement learning) round out your ML literacy after the engine ships — and even those earn their place: clustering organizes your photo library into albums without labels, and RL is the vocabulary you need to understand how modern models are trained beyond supervision.

---

## 2. Scope guardrails — one student, one machine, one project

This handbook is calibrated for **exactly one reader working alone**. To keep it honest:

- **You implement everything yourself.** The handbook explains every line's *why*, but your fingers type the code. No copy-paste-and-move-on.
- **One project, no detours.** If a topic doesn't serve PhotoSense (or your literacy as an ML engineer), it's not here. No Kaggle rabbit holes, no paper-chasing.
- **Small models, real understanding.** We use models that run on your actual machine. Understanding a ResNet-18 deeply beats invoking a 70B model blindly.
- **Chapters are self-contained on theory.** Section 4 of every chapter teaches the concepts well enough that you never *need* to open external material to finish the chapter. Deep-dive links at the end are optional, not homework.
- **Terminology fluency is a first-class goal.** Every new term is **bolded** at first use and defined in place; every chapter ends with a "Vocabulary you now own" list. Chapter 00 gives you the full terminology map of the AI/ML landscape so no acronym ever ambushes you again.
- **No solutions to exercises.** Exercises are implementation tasks against your own PhotoSense build. Struggling with them is the curriculum.

---

## 3. The tech stack — every tool justified by a product need

2026 industry-standard, nothing deprecated, nothing legacy:

| Technology | The PhotoSense need that justifies it |
|---|---|
| **Python 3.12/3.13 + uv** | The ML lingua franca; `uv` gives fast, reproducible environments on a small machine. |
| **PyTorch (CPU wheels) + torchvision** | We build and train neural networks ourselves before trusting pretrained ones. |
| **timm** | Battle-tested pretrained vision backbones for transfer learning (ch 05). |
| **sentence-transformers** (`clip-ViT-B-32`) | CLIP embeddings put photos and text queries in the *same* vector space — the heart of semantic search. (`open_clip` is the research-grade alternative.) |
| **numpy** (brute-force search first) | You must see vector search as plain math before hiding it behind a library. |
| **faiss-cpu** | When your library outgrows brute force, FAISS makes million-scale search fast. (Qdrant-in-Docker is the production-grade note.) |
| **ultralytics (YOLO)** | "Photos with a dog AND a bicycle" needs object detection. (AGPL license caveat covered in ch 09; RT-DETR is the alternative.) |
| **SAM2-small / FastSAM** | Pixel-level masks for region-aware features — chosen at CPU-realistic sizes. |
| **EasyOCR** | Photos of signs, menus, whiteboards become searchable text. (Tesseract noted as the classic alternative.) |
| **FastAPI + ONNX Runtime** | PhotoSense becomes a real service: fast CPU inference behind a typed API. |
| **Gradio** | A demo UI in an afternoon, so you can *show* PhotoSense, not describe it. |
| **scikit-learn** | Classic ML (ch 02, 15): the fastest path to understanding the supervised/unsupervised fundamentals. |
| **matplotlib** | Loss curves, embedding maps, evaluation plots — you can't debug what you can't see. |

---

## 4. The Roadmap

Each chapter introduces its tech only when PhotoSense needs it *now*:

| Chapter | Title | Introduces |
|---|---|---|
| [00-terrain-of-ml.md](00-terrain-of-ml.md) | The terrain: AI, ML, and where everything lives | The full terminology map — AI vs ML vs DL vs GenAI, the model zoo, and where PhotoSense sits in it. |
| [01-toolchain.md](01-toolchain.md) | The ML toolchain on a small machine | Python 3.12/3.13, uv, PyTorch CPU wheels, project layout, and the 8 GB RAM survival kit. |
| [02-first-classifier.md](02-first-classifier.md) | A first classifier: supervised learning end to end | scikit-learn on sklearn digits — train/test split, features, labels, metrics, the whole supervised loop. |
| [03-neural-networks.md](03-neural-networks.md) | Neural networks from the ground up | Neurons, layers, backpropagation, gradient descent — built in PyTorch on CIFAR-10, understood by hand. |
| [04-cnn-image-classifier.md](04-cnn-image-classifier.md) | CNNs: teaching the machine to see | Convolutions, pooling, feature maps — a CIFAR-10 image classifier trained on Colab. |
| [05-transfer-learning-vit.md](05-transfer-learning-vit.md) | Transfer learning and Vision Transformers | timm backbones, fine-tuning on Oxford-IIIT Pets, freezing/unfreezing, and the ViT architecture. |
| [06-attention-and-transformers.md](06-attention-and-transformers.md) | From sequences to attention to Transformers | Attention, self-attention, the Transformer block — the architecture behind everything that follows. |
| [07-embeddings.md](07-embeddings.md) | Embeddings: meaning as geometry | CLIP via sentence-transformers — photos and text as vectors in one shared space, cosine similarity. |
| [08-vector-search.md](08-vector-search.md) | Vector search: the semantic engine | numpy brute-force search first, then faiss-cpu — the first working "search my photos by meaning". |
| [09-object-detection.md](09-object-detection.md) | Object detection: what is in the photo, and where | ultralytics YOLO, bounding boxes, confidence, NMS — object tags enrich the index. |
| [10-segmentation.md](10-segmentation.md) | Segmentation: pixel-level understanding | SAM2-small/FastSAM at CPU-realistic sizes — masks, and when pixels matter more than boxes. |
| [11-ocr.md](11-ocr.md) | OCR: reading text in photos | EasyOCR — text detection vs recognition, making signs and receipts searchable. |
| [12-pipelines.md](12-pipelines.md) | The ingest pipeline: from folder to index | Composing every model into one idempotent pipeline: folder in, searchable index out. |
| [13-serving.md](13-serving.md) | Serving: the PhotoSense API and demo UI | FastAPI + ONNX Runtime for CPU inference, and a Gradio UI you can demo to anyone. |
| [14-evaluation-and-experiments.md](14-evaluation-and-experiments.md) | Evaluation and experiments, like a professional | Retrieval metrics (recall@k, MRR), a labeled eval set from your own photos, experiment discipline. |
| [15-unsupervised-clustering.md](15-unsupervised-clustering.md) | Unsupervised learning: structure without labels | k-means, HDBSCAN, dimensionality reduction — auto-albums from embedding clusters. |
| [16-reinforcement-learning.md](16-reinforcement-learning.md) | Reinforcement learning: a working primer | Agents, rewards, policies, Q-learning — the third paradigm, and where RLHF fits in modern AI. |

**Why this order?** The same pain-chain logic as any real product: fundamentals (00–03) → seeing (04–05) → the architecture of meaning (06–07) → the search engine ships (08) → richer understanding (09–11) → productization (12–14) → literacy beyond the project (15–16). By chapter 08 you already have a working semantic search engine; everything after makes it *better* and makes *you* broader.

---

## 5. Decisions locked in

So that every chapter stays consistent, these decisions are **pinned** — chapters reference them, never re-litigate them:

- **Product:** PhotoSense ingests a folder of the reader's photos and makes them searchable by meaning: classify scenes, detect objects, read text (OCR), embed everything, answer natural-language queries via vector search.
- **Language & env:** Python 3.12/3.13, managed with **uv**. One project venv, `pyproject.toml` as the source of truth.
- **Deep learning:** PyTorch with **CPU wheels** locally, + torchvision + timm.
- **Embeddings:** sentence-transformers with model **`clip-ViT-B-32`**. `open_clip` is the noted research-grade alternative — mentioned, not required.
- **Vector search:** numpy brute-force *first*, **faiss-cpu** when scale earns it, Qdrant-in-Docker as the production note.
- **Detection:** **ultralytics** YOLO (AGPL caveat is an explicit industry-lens point), RT-DETR as the alternative.
- **Segmentation:** SAM2-small / FastSAM, chosen for CPU realism.
- **OCR:** **EasyOCR**, with Tesseract as the classic alternative.
- **Serving:** **FastAPI + ONNX Runtime**; **Gradio** for the demo UI.
- **Classic ML & plots:** scikit-learn, matplotlib.
- **Datasets pinned:** sklearn digits (ch 02) → CIFAR-10 (ch 03–04) → Oxford-IIIT Pets (ch 05) → *your own photo folder* for the engine itself.
- **Training location:** anything beyond toy scale trains on **free Google Colab**, never locally (see hardware strategy below).
- **Terminology:** every term **bolded** at first use; every chapter ends with "Vocabulary you now own"; ch 00 holds the full terminology map.

If a chapter ever appears to contradict this list, this list wins.

---

## 6. How each chapter is structured

Every chapter follows the same 10-step rhythm:

| Step | What happens |
|------|--------------|
| 1 | **What we are building** — one concrete capability for PhotoSense. |
| 2 | **Why the project needs it** — the pain that makes it necessary *now*. |
| 3 | **New technologies required** — a table: tech → why now. |
| 4 | **Concepts** — the theory, taught properly but without textbook sprawl; enough to finish the chapter with no external reading. |
| 5 | **Implementation plan** — every file, and the single responsibility of each. |
| 6 | **Build it piece by piece** — code snippets, each followed by what/why. Never one giant final dump. |
| 7 | **Run and verify** — exact PowerShell commands, expected output, proof it works. |
| 8 | **How it flows** — an ascii trace of the request/data flow you just built. |
| 9 | **A senior's review** — what production would demand; tradeoffs table (chosen vs alternative vs when the alternative wins). |
| 10 | **Exercises** — 3–5 implementation tasks. No solutions. |

You write every file. The handbook explains every line's *why* and reviews the design like a senior sitting next to you.

---

## 7. Hardware & cost strategy — 8 GB RAM, no GPU, $0

Your machine: **Windows 11, PowerShell, Ryzen 3 7320U, 8 GB RAM, no dedicated GPU.** The handbook respects that on every page. The strategy:

```
┌──────────────────────────┐        ┌──────────────────────────┐
│   YOUR MACHINE (local)   │        │   GOOGLE COLAB (free)    │
│                          │        │                          │
│  · inference only        │        │  · ALL real training     │
│  · small models only     │  ◄──── │  · GPU runtime (T4)      │
│  · the full PhotoSense   │ models │  · checkpoints → Drive   │
│    engine end to end     │  come  │  · artifacts downloaded  │
│  · every API + UI        │  back  │    back to your machine  │
└──────────────────────────┘        └──────────────────────────┘
```

- **Local = inference.** CLIP-ViT-B-32, YOLO-nano-class models, FastSAM, EasyOCR — all run acceptably on your CPU. Every model choice in this handbook was made with your RAM budget in mind.
- **Colab = training.** Every chapter that trains beyond toy scale (04, 05, and optional experiments later) includes a **Colab workflow note**: which runtime type to select, how to save checkpoints to Google Drive mid-training, and how to download the final artifacts to your machine.
- **RAM-saving practices, everywhere:** small batch sizes, `num_workers=0` in DataLoaders (Windows + 8 GB makes worker processes a liability), resize images before they hit the model, close what you don't need while training locally.
- **Heavy tools always ship with a lightweight path.** FAISS has a numpy fallback, SAM2 has FastSAM, Qdrant is a Docker *note* rather than a requirement.
- **Total cost of the entire handbook: $0.** No paid APIs, no cloud bills, no paid datasets.

> **Industry lens:** This local-inference/remote-training split is not a compromise — it *is* how real ML orgs operate. Production inference runs on cheap CPU fleets with small, optimized (often ONNX/quantized) models, while training happens elsewhere on scheduled GPU clusters, with checkpoints written to durable storage exactly like your Drive workflow. Engineers who can make a model fast and small on CPU are rarer — and often more valuable in production — than engineers who can only make it accurate on an A100.

---

## 8. The End-Goal Checklist

By the last chapter, from memory and understanding, you can:

- [ ] Map the AI/ML landscape and place any new paper, model, or acronym in it without flinching.
- [ ] Take a supervised problem from raw data to trained model to honest metrics, end to end.
- [ ] Explain backpropagation and gradient descent well enough to debug a training run that won't converge.
- [ ] Explain what convolutions and attention actually compute, and why each dominates its domain.
- [ ] Fine-tune a pretrained vision model on your own dataset — on free Colab, with checkpoints you don't lose.
- [ ] Explain embeddings as geometry and CLIP's shared image-text space to a non-ML engineer.
- [ ] Build vector search from raw numpy, then justify exactly when FAISS or a vector DB earns its complexity.
- [ ] Run detection, segmentation, and OCR on CPU and know the accuracy/latency tradeoffs you accepted.
- [ ] Compose many models into one idempotent ingest pipeline: photo folder in, searchable index out.
- [ ] Serve a model behind FastAPI with ONNX Runtime and demo it with a Gradio UI.
- [ ] Evaluate a retrieval system with recall@k and MRR on an eval set you built yourself, and run experiments that produce decisions instead of vibes.
- [ ] Cluster unlabeled data into structure a user would recognize as albums.
- [ ] Hold your own in a conversation about reinforcement learning and RLHF.
- [ ] **Type "beach sunset with friends" into a search engine you built, and watch it work.**

---

**Start here:** [Chapter 00 — The terrain: AI, ML, and where everything lives](00-terrain-of-ml.md), then [Chapter 01 — The ML toolchain on a small machine](01-toolchain.md).

*You are the engineer. I am the senior sitting next to you. Let's build.*
