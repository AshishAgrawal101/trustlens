from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image
from tqdm import tqdm


def stable_bucket(value: str, seed: int = 2026) -> float:
    raw = f"{seed}:{value}".encode("utf-8", errors="ignore")
    h = hashlib.sha256(raw).digest()
    return int.from_bytes(h[:8], "big") / float(2**64 - 1)


def train_val_split(label: int, model_name: str, image_name: str, real_source: str, seed: int) -> str:
    """Hold out whole fake generators for validation; split real images by identity."""
    if label == 1:
        x = stable_bucket(model_name or "unknown-generator", seed)
    else:
        x = stable_bucket(f"{real_source}|{image_name}", seed)
    return "train" if x < 0.90 else "val"


def safe_name(text: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in text)[:120]


def is_nsfw(row: dict) -> bool:
    value = row.get("nsfw_flag")
    if value is True:
        return True
    return str(value).strip().lower() in {"true", "1", "yes"}


def decode_image(row: dict) -> Image.Image | None:
    try:
        return Image.open(io.BytesIO(row["image_data"])).convert("RGB")
    except Exception:
        return None


def save_row(out: Path, row: dict, split: str, count: int, dataset_name: str) -> dict | None:
    label = int(row["label"])
    cls = "ai" if label == 1 else "real"
    image_name = str(row.get("image_name") or f"row_{count}.png")
    img = decode_image(row)
    if img is None:
        return None

    # Uniform JPEG re-encoding prevents the classifier from exploiting original
    # PNG-vs-JPEG container format as an easy class shortcut.
    filename = f"{count:06d}_{safe_name(image_name)}.jpg"
    path = out / split / cls / filename
    img.save(path, format="JPEG", quality=95, subsampling=0)
    relpath = path.relative_to(out).as_posix()
    return {
        "path": str(path),
        "relpath": relpath,
        "split": split,
        "label": label,
        "model_name": str(row.get("model_name") or ""),
        "architecture": row.get("architecture"),
        "real_source": str(row.get("real_source") or ""),
        "subset": row.get("subset"),
        "original_format": row.get("format"),
        "dataset": dataset_name,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Create a local Community Forensics train/val subset plus the official unseen-generator test set."
    )
    ap.add_argument("--out", default="data/cf_local")
    ap.add_argument("--train-per-class", type=int, default=5000)
    ap.add_argument("--val-per-class", type=int, default=1000)
    ap.add_argument("--test-per-class", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--shuffle-buffer", type=int, default=10000)
    ap.add_argument("--max-stream-rows", type=int, default=300000)
    ap.add_argument(
        "--internal-test",
        action="store_true",
        help="Use held-out generators from CommunityForensics-Small instead of the official CommunityForensics-Eval test.",
    )
    args = ap.parse_args()

    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install requirements-ai.txt before preparing Community Forensics data.") from exc

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for split in ("train", "val", "test"):
        for cls in ("real", "ai"):
            (out / split / cls).mkdir(parents=True, exist_ok=True)

    metadata_path = out / "metadata.jsonl"
    counts = {s: defaultdict(int) for s in ("train", "val", "test")}
    models = {s: set() for s in ("train", "val", "test")}
    real_sources = {s: set() for s in ("train", "val", "test")}

    total_target = 2 * (args.train_per_class + args.val_per_class + args.test_per_class)
    pbar = tqdm(total=total_target, desc="Saving images")

    with metadata_path.open("w", encoding="utf-8") as meta:
        small = load_dataset("OwensLab/CommunityForensics-Small", split="train", streaming=True)
        small = small.shuffle(seed=args.seed, buffer_size=args.shuffle_buffer)

        for i, row in enumerate(small):
            if i >= args.max_stream_rows:
                break
            if is_nsfw(row):
                continue
            label = int(row["label"])
            model_name = str(row.get("model_name") or "")
            image_name = str(row.get("image_name") or f"row_{i}.png")
            real_source = str(row.get("real_source") or "")

            if args.internal_test:
                # 80/10/10 generator-disjoint fake split for legacy/internal testing.
                if label == 1:
                    x = stable_bucket(model_name or "unknown-generator", args.seed)
                else:
                    x = stable_bucket(f"{real_source}|{image_name}", args.seed)
                split = "train" if x < 0.80 else ("val" if x < 0.90 else "test")
            else:
                split = train_val_split(label, model_name, image_name, real_source, args.seed)

            target = {
                "train": args.train_per_class,
                "val": args.val_per_class,
                "test": args.test_per_class,
            }[split]
            if counts[split][label] >= target:
                continue

            rec = save_row(out, row, split, counts[split][label], "CommunityForensics-Small")
            if rec is None:
                continue
            meta.write(json.dumps(rec, ensure_ascii=False) + "\n")
            counts[split][label] += 1
            if label == 1:
                models[split].add(model_name)
            else:
                real_sources[split].add(real_source)
            pbar.update(1)

            need_train_val = all(
                counts[s][y] >= ({"train": args.train_per_class, "val": args.val_per_class}[s])
                for s in ("train", "val") for y in (0, 1)
            )
            if need_train_val and not args.internal_test:
                break
            if args.internal_test:
                done = all(
                    counts[s][y] >= ({"train": args.train_per_class, "val": args.val_per_class, "test": args.test_per_class}[s])
                    for s in ("train", "val", "test") for y in (0, 1)
                )
                if done:
                    break

        if not args.internal_test:
            # Official CompEval contains models held out from the training set and
            # is the paper/dataset authors' recommended comprehensive evaluation.
            comp = load_dataset("OwensLab/CommunityForensics-Eval", split="CompEval", streaming=True)
            comp = comp.shuffle(seed=args.seed, buffer_size=args.shuffle_buffer)
            for row in comp:
                if is_nsfw(row):
                    continue
                label = int(row["label"])
                if counts["test"][label] >= args.test_per_class:
                    continue
                rec = save_row(out, row, "test", counts["test"][label], "CommunityForensics-Eval")
                if rec is None:
                    continue
                meta.write(json.dumps(rec, ensure_ascii=False) + "\n")
                counts["test"][label] += 1
                if label == 1:
                    models["test"].add(rec["model_name"])
                else:
                    real_sources["test"].add(rec["real_source"])
                pbar.update(1)
                if all(counts["test"][y] >= args.test_per_class for y in (0, 1)):
                    break

    pbar.close()

    print("\nSaved counts:")
    for s in ("train", "val", "test"):
        print(
            f"  {s}: real={counts[s][0]}, ai={counts[s][1]}, "
            f"fake_generators={len(models[s])}, real_sources={len(real_sources[s])}"
        )

    train_val_overlap = models["train"] & models["val"]
    if train_val_overlap:
        raise RuntimeError(f"Train/val generator leakage detected: {list(train_val_overlap)[:5]}")
    if not args.internal_test:
        external_overlap = (models["train"] | models["val"]) & models["test"]
        if external_overlap:
            print(
                "WARNING: generator names overlap with official eval metadata. "
                f"Inspect aliases before reporting unseen-generator results: {list(external_overlap)[:5]}"
            )
    else:
        overlap = (models["train"] & models["test"]) | (models["val"] & models["test"])
        if overlap:
            raise RuntimeError(f"Generator leakage detected: {list(overlap)[:5]}")

    print("Generator-disjoint train/validation check: PASS")
    print("Test source:", "internal held-out generators" if args.internal_test else "CommunityForensics-Eval/CompEval")
    print(f"Metadata: {metadata_path}")


if __name__ == "__main__":
    main()
