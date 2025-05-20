# InReDD‑Dataset

[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.oooo.2023.12.006-blue.svg)](https://doi.org/10.1016/j.oooo.2023.12.006)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-brightgreen.svg)](https://creativecommons.org/licenses/by/4.0/)
[![PhysioNet](https://img.shields.io/badge/Hosted%20at-PhysioNet-orange.svg)](https://physionet.org/)
[![GitHub stars](https://img.shields.io/github/stars/InReDD/InReDD‑Dataset.svg?style=flat\&label=Star)](https://github.com/InReDD/InReDD-Dataset/stargazers)

<details><summary>Table of Contents</summary><p>

* [Overview](#overview)
* [Why we built InReDD‑Dataset](#why-we-built-inredd‑dataset)
* [Dataset at a glance](#dataset-at-a-glance)
* [Download](#download)
* [Directory structure](#directory-structure)
* [Usage](#usage)

  * [Python / PyTorch](#python--pytorch)
  * [TensorFlow / Keras](#tensorflow--keras)
* [Annotation schema](#annotation-schema)
* [Benchmark](#benchmark)
* [Citation](#citation)
* [License](#license)
* [Contributing](#contributing)
* [Contact](#contact)

</p></details>

## Overview

`InReDD‑Dataset` is a publicly‑available collection of **936 anonymised panoramic dental radiographs** curated by the *Interdisciplinary Research Group in Digital Dentistry* (InReDD) at the University of São Paulo.
Three board‑certified oral and maxillofacial radiologists independently labelled every tooth and adjudicated disagreements through forced consensus, producing high‑quality ground‑truth annotations suitable for training and evaluating computer‑vision models in dentistry.

Each image is accompanied by:

* **Tooth‑level bounding boxes** following the FDI two‑digit numbering system (00‑88).
* **Condition annotations** (binary flags) for 12 common findings, e.g. caries, crown, implant, root‑canal treatment, periapical lesion.
* **Image‑level status**: edentulous / mixed / dentate.
* Acquisition metadata (device, kVp, mAs, pixel spacing, etc.).

All annotations are distributed as JSON files that mirror the COCO format while preserving dental‑specific fields.

## Why we built InReDD‑Dataset

Deep‑learning research in oral radiology is often stifled by **scarce, closed, or weakly‑labelled data**. By releasing InReDD‑Dataset we aim to:

* Provide a **benchmark that is more clinically realistic** than digit handwriting corpora such as MNIST/Fashion‑MNIST.
* Encourage reproducible research on **tooth detection, numbering, and diagnosis**.
* Lower the entry barrier for students and clinicians interested in applying AI to dentistry.

If your algorithm fails on InReDD‑Dataset, it is unlikely to hold in the clinic—yet strong results here are a promising sign.

## Dataset at a glance

| Split | Images | JSON annotations | Total bounding boxes |
| ----- | ------ | ---------------- | -------------------- |
| Train | 748    | 748              | 18 082               |
| Test  | 188    | 188              | 4 532                |

> **Image size**: 2688 × 1400 px (median, 16‑bit PNG)
> **Classes**: 32 tooth positions × 12 conditions + background

## Download

The dataset is hosted on **PhysioNet**. You can either clone the repository (images **not** included) or download the pre‑split tarballs:

| File                        | Size   | MD5                                |
| --------------------------- | ------ | ---------------------------------- |
| `inredd_png_train.tar.gz`   | 9.2 GB | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `inredd_png_test.tar.gz`    | 2.3 GB | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `inredd_annotations.tar.gz` | 3.1 MB | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

```bash
# Example: download and extract train split
wget https://physionet.org/static/published-projects/inredd/inredd_png_train.tar.gz
tar -xzf inredd_png_train.tar.gz
```

## Directory structure

```text
InReDD-Dataset/
├── images/
│   ├── train/
│   │   ├── 000001.png
│   │   ├── 000002.png
│   │   └── …
│   └── test/
├── annotations/
│   ├── train/
│   │   ├── 000001.json
│   │   └── …
│   └── test/
└── metadata.csv
```

## Usage

### Python / PyTorch

```python
from pathlib import Path
from inredd import InReDDDataset
from torch.utils.data import DataLoader

root = Path("/path/to/InReDD-Dataset")
dataset = InReDDDataset(root, split="train", transforms=None)
loader = DataLoader(dataset, batch_size=4, shuffle=True, num_workers=4)

images, targets = next(iter(loader))
```

### TensorFlow / Keras

```python
import tensorflow as tf
from tensorflow.data import TFRecordDataset
from inredd.tf import load_split

train_ds = load_split("/path/to/InReDD-Dataset", split="train")
train_ds = train_ds.batch(4).shuffle(256).prefetch(tf.data.AUTOTUNE)
```

A minimal **reference implementation** of these helpers is provided under [`utils/`](utils).

## Annotation schema

The JSON schema (see `docs/annotation_schema.md`) is summarised below.

| Field            | Type                | Description                          |
| ---------------- | ------------------- | ------------------------------------ |
| `tooth_id`       | int                 | FDI code, 11–48                      |
| `bbox`           | list `[x, y, w, h]` | Axis‑aligned rectangle (pixels)      |
| `conditions`     | object              | Dict of {{condition\_name: bool}}    |
| `radiologist_id` | str                 | `R1`, `R2`, or `consensus`           |
| `image_status`   | str                 | `edentulous` \| `mixed` \| `dentate` |

## Benchmark

We provide baseline results for common architectures (Faster R‑CNN, YOLOv8, and DETR) trained on the default split:

| Model                | mAP\@0.5<sup>†</sup> | Tooth‑ID accuracy | Paper / Code                     |
| -------------------- | -------------------- | ----------------- | -------------------------------- |
| Faster R‑CNN R50‑FPN | 0.842                | 0.915             | [`configs/faster_rcnn`](configs) |
| YOLOv8‑m             | 0.867                | 0.928             | [`configs/yolov8`](configs)      |
| DETR R50             | 0.834                | 0.903             | [`configs/detr`](configs)        |

<sup>†</sup> Evaluated on the test split with IoU 0.5.

You are invited to submit new benchmarks via Pull Request!

## Citation

If you use InReDD‑Dataset in academic work, please cite:

> **Costa et al.** *High‑quality annotated panoramic radiographs for artificial‑intelligence research.* **OOOO** 2024. DOI 10.1016/j.oooo.2023.12.006

BibTeX:

```bibtex
@article{costa2024inredd,
  title   = {High-quality annotated panoramic radiographs for artificial-intelligence research},
  author  = {Costa, R. and Martins, C. U. and Almeida, L. and {InReDD Consortium}},
  journal = {Oral Surgery, Oral Medicine, Oral Pathology and Oral Radiology},
  year    = {2024},
  doi     = {10.1016/j.oooo.2023.12.006}
}
```

## License

All images and annotations are released under the **Creative Commons Attribution 4.0 International** (CC BY 4.0) license.
You are free to share and adapt the material for any purpose, even commercially, provided that you give appropriate credit.

## Contributing

Please read our [contributor guidelines](CONTRIBUTING.md) before opening issues or pull requests. Bug reports, feature requests, and benchmark submissions are very welcome.

## Contact

Questions? Reach the InReDD team on [`#inredd`](https://gitter.im/inredd/dataset) or create a GitHub issue.

---

*This repository is maintained by the InReDD research group at USP Ribeirão Preto.*
*Last updated: 2025-05-20*