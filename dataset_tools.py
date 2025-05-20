"""dataset_tools.py – InReDD‑Dataset helper utilities
================================================
Lightweight toolkit for *exploring* the InReDD panoramic‑radiograph corpus via
Python **or** the command line. Now completely decoupled from any hard‑coded
constants: **pass the dataset root as an argument** (or rely on the current
working directory).

Usage
-----
```bash
# Option 1 – from project root where images/ & annotations/ live
python dataset_tools.py

# Option 2 – explicit path, anywhere
python dataset_tools.py /path/to/InReDD --top 20
```

Dependencies: only the Python ≥3.8 standard library; `pip install tqdm` for a
progress bar (optional).
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as stats
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence

try:
    from tqdm import tqdm  # type: ignore
except ImportError:  # pragma: no cover
    tqdm = lambda x, **kw: x  # noqa: E731 – fallback to plain iterator

# ----------------------------------------------------------------------------
# Dataset wrapper (flat layout: images/ & annotations/)
# ----------------------------------------------------------------------------

class InReDDDataset:
    """Access images/ & annotations/ with optional recursive search."""

    IMG_EXTS = (".png", ".jpg", ".jpeg")

    def __init__(
        self,
        root: str | Path = ".",
        *,
        load_images: bool = False,
        transforms=None,
        recursive: bool = True,
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        self.img_dir = self.root / "images"
        self.ann_dir = self.root / "annotations"

        if recursive:
            globber = lambda ext: self.img_dir.rglob(f"*{ext}")  # noqa: E731
        else:
            globber = lambda ext: self.img_dir.glob(f"*{ext}")  # noqa: E731

        self.ids = sorted({p.stem for ext in self.IMG_EXTS for p in globber(ext)})
        if not self.ids:
            raise FileNotFoundError(
                f"No image files with extensions {self.IMG_EXTS} found under {self.img_dir}. "
                "Check that you passed the correct dataset root."
            )

        self.load_images = load_images
        self.transforms = transforms

    # ------------------------------------------------------------------
    # PyTorch‑style API
    # ------------------------------------------------------------------
    def __len__(self) -> int:  # noqa: D401
        return len(self.ids)

    def __getitem__(self, idx: int):  # noqa: D401
        img_id = self.ids[idx]
        ann_path = self.ann_dir / f"{img_id}.json"
        if not ann_path.exists():
            raise FileNotFoundError(f"Annotation not found: {ann_path}")
        with ann_path.open("r", encoding="utf-8") as fh:
            target = json.load(fh)

        image = None
        if self.load_images:
            from PIL import Image  # heavyweight import only if demanded

            for ext in self.IMG_EXTS:
                img_file = next(self.img_dir.rglob(f"{img_id}{ext}"), None)
                if img_file and img_file.exists():
                    image = Image.open(img_file).convert("L")
                    break
            else:
                raise FileNotFoundError(f"Image for id {img_id} not found.")

        if self.transforms is not None:
            image, target = self.transforms(image, target)

        return image, target

    # Convenience generator ---------------------------------------------
    def iter_annotations(self):
        for i in range(len(self)):
            yield self[i][1]

# ----------------------------------------------------------------------------
# Stats helpers
# ----------------------------------------------------------------------------

class DatasetStats:
    """Aggregates statistics in a single pass."""

    def __init__(self):
        self.image_status: Counter[str] = Counter()
        self.conditions: Counter[str] = Counter()
        self.tooth_ids: Counter[str] = Counter()
        self.n_boxes_total: int = 0
        self.boxes_per_image: List[int] = []

    def update(self, ann: Dict[str, Any] | Sequence[Dict[str, Any]]):
        objs = ann if isinstance(ann, Sequence) else [ann]
        self.boxes_per_image.append(len(objs))
        self.n_boxes_total += len(objs)

        for obj in objs:
            if (tid := obj.get("tooth_id")) is not None:
                self.tooth_ids.update([str(tid)])
            self.conditions.update([c for c, v in obj.get("conditions", {}).items() if v])
            if (status := obj.get("image_status")):
                self.image_status.update([status])

    # ------------------------------------------------------------------
    def summary(self) -> Dict[str, Any]:
        return {
            "images": len(self.boxes_per_image),
            "boxes": self.n_boxes_total,
            "boxes_per_image": {
                "mean": round(stats.mean(self.boxes_per_image), 2),
                "median": stats.median(self.boxes_per_image),
                "min": min(self.boxes_per_image),
                "max": max(self.boxes_per_image),
            },
        }

# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------

def describe(root: str | Path = ".", *, verbose: bool = True) -> Dict[str, Any]:
    """Return dataset statistics."""

    ds = InReDDDataset(root, load_images=False)
    acc = DatasetStats()

    iterator = tqdm(ds.iter_annotations(), desc="Scanning") if verbose else ds.iter_annotations()
    for ann in iterator:
        acc.update(ann)

    out = acc.summary()
    out["image_status"] = acc.image_status
    out["conditions"] = acc.conditions
    out["tooth_ids"] = acc.tooth_ids
    return out

# ----------------------------------------------------------------------------
# CLI – human‑readable report
# ----------------------------------------------------------------------------

def _fmt_counter(cnt: Counter[str], *, top: int | None = None) -> str:
    pad = max((len(k) for k in cnt), default=1)
    return "\n".join(f"{k.rjust(pad)} : {v}" for k, v in cnt.most_common(top))


def main(argv: List[str] | None = None) -> None:  # noqa: D401
    parser = argparse.ArgumentParser(description="Show InReDD statistics")
    parser.add_argument("root", nargs="?", default=os.getcwd(), help="Dataset root (default: cwd)")
    parser.add_argument("--top", type=int, default=10, help="Top‑K rows to display")
    args = parser.parse_args(argv)

    stats = describe(args.root)

    print("\n=== InReDD‑Dataset ===")
    print(f"Root               : {Path(args.root).resolve()}")
    print(f"Images             : {stats['images']}")
    print(f"Bounding boxes     : {stats['boxes']}")
    bpi = stats["boxes_per_image"]
    print(
        "Boxes / image      : "
        f"mean {bpi['mean']}  median {bpi['median']}  min {bpi['min']}  max {bpi['max']}"
    )

    print("\n--- Image‑level status ---")
    print(_fmt_counter(stats["image_status"]))

    print(f"\n--- Top {args.top} tooth IDs ---")
    print(_fmt_counter(stats["tooth_ids"], top=args.top))

    print(f"\n--- Top {args.top} conditions ---")
    print(_fmt_counter(stats["conditions"], top=args.top))


if __name__ == "__main__":
    main(sys.argv[1:])
