"""
Build the small, student-facing data files for the PSI coding class.

Run this ONCE (by the instructor). Students never touch the raw data:
the raw cellData.csv is 88 MB and the 41 label-mask TIFFs are ~330 MB.
Everything students need adds up to a few MB and downloads in seconds
on Colab.

Outputs (data/processed/):
    cells_sample.csv    20,000 cells x 16 markers + published cell type
    cells_xy.csv.gz     all ~197k cells: SampleID, x, y, celltype
    patients.csv        40 patients: class, survival, event, TIL, age
    seg_demo.npz        one 300x300 crop for the segmentation demo

Usage:
    python code/00_build_class_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image
from scipy import ndimage as ndi

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "TNBC_shareCellData"
OUT = ROOT / "data" / "processed"

# The 16 markers students will cluster on. Chosen to be teachable: each one
# has a one-line explanation a high schooler can hold onto.
MARKERS = [
    "CD45", "CD3", "CD8", "CD4", "CD20", "CD68", "CD11c", "MPO",
    "Pan-Keratin", "Beta catenin", "Keratin17", "Vimentin", "SMA", "CD31",
    "FoxP3", "HLA-DR",
]

# Group codes from the dataset readme.
GROUP = {
    1: "Unidentified", 2: "Immune", 3: "Endothelial",
    4: "Mesenchymal", 5: "Tumor", 6: "Tumor",
}
IMMUNE = {
    1: "Treg", 2: "CD4 T cell", 3: "CD8 T cell", 4: "T cell", 5: "NK cell",
    6: "B cell", 7: "Neutrophil", 8: "Macrophage", 9: "Dendritic cell",
    10: "Dendritic cell", 11: "Neutrophil", 12: "Other immune",
}

# Coarse label used for the spatial mixing score.
COARSE = {"Immune": "immune", "Tumor": "tumor"}

SEG_PATIENT = 23        # crop taken from this patient's label mask
SEG_WINDOW = (600, 900, 600, 900)   # y0, y1, x0, x1


def cell_centroids() -> pd.DataFrame:
    """Centroid (x, y) and pixel area for every segmented object, all patients.

    The label masks are 2048x2048 uint16 images where every cell is a run of
    identical integers. np.bincount over the flattened image gives per-label
    pixel counts in one pass; bincount weighted by the row/column index grids
    gives the coordinate sums. Dividing the two gives centroids. This is ~4 s
    for all 41 images, versus minutes for a per-label loop.
    """
    frames = []
    for p in range(1, 42):
        f = RAW / f"p{p}_labeledcellData.tiff"
        if not f.exists():
            continue
        a = np.array(Image.open(f))
        n = int(a.max()) + 1
        flat = a.ravel()
        area = np.bincount(flat, minlength=n)
        yy, xx = np.indices(a.shape)
        sy = np.bincount(flat, weights=yy.ravel(), minlength=n)
        sx = np.bincount(flat, weights=xx.ravel(), minlength=n)
        ids = np.nonzero(area)[0]
        ids = ids[ids > 0]              # label 0 is background
        frames.append(pd.DataFrame({
            "SampleID": p,
            "cellLabelInImage": ids,
            "x": sx[ids] / area[ids],
            "y": sy[ids] / area[ids],
        }))
    return pd.concat(frames, ignore_index=True)


def label_cells(df: pd.DataFrame) -> pd.Series:
    """Human-readable cell type: immune cells get their specific subtype."""
    coarse = df["Group"].map(GROUP)
    fine = df["immuneGroup"].map(IMMUNE)
    return np.where(coarse == "Immune", fine.fillna("Other immune"), coarse)


def build_segmentation_demo(out: Path) -> None:
    """Save one tissue crop plus a simulated nuclear stain.

    The published data gives us segmentation masks but not the raw marker
    images, so we simulate the kind of image a segmentation algorithm would
    actually be handed. Two versions:

      hard  - signal fills each whole cell, as in real densely packed tissue
      easy  - signal only in each cell's nuclear core, well separated

    Watershed does fine on `easy` and falls apart on `hard`. That contrast is
    the point of the imaging lesson: it earns the deep-learning slide instead
    of just asserting it.
    """
    y0, y1, x0, x1 = SEG_WINDOW
    mask = np.array(Image.open(RAW / f"p{SEG_PATIENT}_labeledcellData.tiff"))
    truth = mask[y0:y1, x0:x1]

    rng = np.random.default_rng(0)
    dist = ndi.distance_transform_edt(truth > 0)

    # hard: whole-cell signal, normalized per cell so each is its own blob
    sig = np.zeros(truth.shape, float)
    core = np.zeros_like(truth)
    for lab in np.unique(truth):
        if lab == 0:
            continue
        m = truth == lab
        d = dist * m
        if d.max() > 0:
            sig[m] = d[m] / d.max()
            core[m & (dist > d.max() * 0.55)] = lab   # inner ~nucleus

    hard = np.clip(ndi.gaussian_filter(sig, 1.5)
                   + rng.normal(0, 0.08, truth.shape), 0, None)
    easy = np.clip(ndi.gaussian_filter((core > 0).astype(float), 1.2)
                   + rng.normal(0, 0.05, truth.shape), 0, None)

    np.savez_compressed(out, truth=truth.astype(np.uint16),
                        nuclei=core.astype(np.uint16),
                        easy=easy.astype(np.float32),
                        hard=hard.astype(np.float32))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    print("reading cellData.csv (88 MB, ~20 s) ...")
    cells = pd.read_csv(RAW / "cellData.csv")

    print("extracting centroids from 41 label masks ...")
    cent = cell_centroids()

    # Inner join drops the phantom samples 42-44 (present in the CSV but with
    # no image) and any object in an image with no matching row.
    df = cells.merge(cent, on=["SampleID", "cellLabelInImage"], how="inner")
    df["celltype"] = label_cells(df)
    df = df[df["celltype"] != "Unidentified"]

    # ---- cells_xy.csv.gz : every cell's position and type -------------------
    xy = df[["SampleID", "x", "y", "celltype"]].copy()
    xy["x"] = xy["x"].round(1)
    xy["y"] = xy["y"].round(1)
    xy.to_csv(OUT / "cells_xy.csv.gz", index=False, compression="gzip")

    # ---- cells_sample.csv : 20k cells for the clustering exercise ----------
    sample = df.sample(20_000, random_state=0)[MARKERS + ["celltype", "SampleID"]]
    sample.round(4).to_csv(OUT / "cells_sample.csv", index=False)

    # ---- patients.csv : one row per patient --------------------------------
    clin = pd.read_csv(RAW / "clinical_data_table.csv", encoding="utf-8-sig")
    clin = clin.rename(columns={"InternalId": "SampleID",
                                "Survival_days_capped*": "survival_days",
                                "AGE_AT_DX": "age"})
    # NOTE: `Censored` is inverted relative to the usual convention --
    # Censored == 1 means the patient was censored, not that an event occurred.
    clin["event"] = 1 - clin["Censored"]
    clin["TIL_score"] = pd.to_numeric(clin["TIL_score"], errors="coerce")

    pclass = pd.read_csv(RAW / "patient_class.csv", header=None,
                         names=["SampleID", "class"])
    # 0 = mixed, 1 = compartmentalized, 2 = cold (per the paper)
    pclass["published_class"] = pclass["class"].map(
        {0: "mixed", 1: "compartmentalized", 2: "cold"})

    pat = (clin[["SampleID", "survival_days", "event", "TIL_score", "age"]]
           .merge(pclass[["SampleID", "published_class"]], on="SampleID")
           .merge(df.groupby("SampleID").size().rename("n_cells"),
                  on="SampleID"))
    pat.to_csv(OUT / "patients.csv", index=False)

    # ---- seg_demo.npz ------------------------------------------------------
    build_segmentation_demo(OUT / "seg_demo.npz")

    print(f"\nwrote to {OUT}")
    for f in sorted(OUT.iterdir()):
        print(f"  {f.name:20s} {f.stat().st_size / 1e6:6.2f} MB")
    print(f"\n{len(df):,} cells, {pat.SampleID.nunique()} patients")
    print(pat.published_class.value_counts().to_string())


if __name__ == "__main__":
    main()
