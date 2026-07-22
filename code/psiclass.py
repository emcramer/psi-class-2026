"""
Shared analysis + plot styling for the PSI class materials.

Used by the figure scripts and the verification script so that every number on
a slide comes from the same code path. The student notebooks deliberately do
NOT import this -- they re-derive everything inline, which is the point.
"""

from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
FIGS = ROOT / "presentation" / "figures"

# ---------------------------------------------------------------------------
# Palette. Validated with the dataviz validator against surface #fcfcfb:
#   3-slot all-pairs -> PASS (worst CVD dE 9.2, worst normal dE 24.0)
#   AQUA is below 3:1 contrast, so any chart using slot 3 must carry direct
#   labels rather than relying on a legend alone.
# ---------------------------------------------------------------------------
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SERIES = [BLUE, ORANGE, AQUA]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
NEUTRAL = "#f0efec"
RED = "#e34948"

# Diverging ramp for marker z-scores: two opposite hues, neutral gray midpoint.
DIVERGING = LinearSegmentedColormap.from_list("psi_div", [BLUE, NEUTRAL, RED])
# Sequential ramp, one hue light -> dark.
SEQUENTIAL = LinearSegmentedColormap.from_list(
    "psi_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"])

# Cell types collapsed to the three that matter spatially. Three slots is also
# the all-pairs limit for the categorical palette, so scatters stay validated.
COARSE_COLORS = {"tumor": BLUE, "immune": ORANGE, "other": AQUA}

MARKERS = [
    "CD45", "CD3", "CD8", "CD4", "CD20", "CD68", "CD11c", "MPO",
    "Pan-Keratin", "Beta catenin", "Keratin17", "Vimentin", "SMA", "CD31",
    "FoxP3", "HLA-DR",
]

IMMUNE_TYPES = {
    "Treg", "CD4 T cell", "CD8 T cell", "T cell", "NK cell", "B cell",
    "Neutrophil", "Macrophage", "Dendritic cell", "Other immune",
}

MIXING_RADIUS = 30      # px; ~cell-contact scale at this resolution
MIXING_THRESHOLD = 0.26  # separates compartmentalized from mixed
COLD_MIN_IMMUNE = 250    # below this a tumor is "cold" (paper's definition)


def use_slide_style() -> None:
    """Matplotlib defaults tuned for projection: big text, hairline chrome."""
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial",
                            "DejaVu Sans"],
        "font.size": 18,
        "axes.titlesize": 22,
        "axes.labelsize": 19,
        "xtick.labelsize": 17,
        "ytick.labelsize": 17,
        "legend.fontsize": 17,
        "axes.titlecolor": INK,
        "axes.labelcolor": INK2,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "grid.linestyle": "-",        # never dashed
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "figure.dpi": 130,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def coarse_type(celltype: pd.Series) -> pd.Series:
    """Collapse the published phenotype to tumor / immune / other."""
    return np.where(celltype == "Tumor", "tumor",
                    np.where(celltype.isin(IMMUNE_TYPES), "immune", "other"))


def mixing_scores(xy: pd.DataFrame, radius: int = MIXING_RADIUS) -> pd.DataFrame:
    """Per-patient tumor-immune mixing score.

    Following Keren et al.: build the graph of cells within `radius` of each
    other, then take (immune-tumor edges) / (immune-immune edges). A low score
    means immune cells mostly touch other immune cells -- they are walled off
    into their own compartment. A high score means they are mixed in among the
    tumor.
    """
    out = []
    for pid, g in xy.groupby("SampleID"):
        pairs = cKDTree(g[["x", "y"]].values).query_pairs(radius,
                                                          output_type="ndarray")
        kind = g["coarse"].values
        a, b = kind[pairs[:, 0]], kind[pairs[:, 1]]
        imm_imm = ((a == "immune") & (b == "immune")).sum()
        imm_tum = (((a == "immune") & (b == "tumor"))
                   | ((a == "tumor") & (b == "immune"))).sum()
        n_immune = int((kind == "immune").sum())
        out.append({
            "SampleID": pid,
            "mixing_score": imm_tum / max(imm_imm, 1),
            "n_immune": n_immune,
        })
    df = pd.DataFrame(out)
    df["our_class"] = np.where(
        df.n_immune < COLD_MIN_IMMUNE, "cold",
        np.where(df.mixing_score < MIXING_THRESHOLD,
                 "compartmentalized", "mixed"))
    return df


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (cells_sample, cells_xy, patients) with coarse types attached."""
    sample = pd.read_csv(PROC / "cells_sample.csv")
    xy = pd.read_csv(PROC / "cells_xy.csv.gz")
    pat = pd.read_csv(PROC / "patients.csv")
    sample["coarse"] = coarse_type(sample["celltype"])
    xy["coarse"] = coarse_type(xy["celltype"])
    return sample, xy, pat


def km_curve(time: np.ndarray, event: np.ndarray):
    """Kaplan-Meier step function. Returns (times, survival) including t=0."""
    order = np.argsort(time)
    t, e = np.asarray(time)[order], np.asarray(event)[order]
    n = len(t)
    times, surv, s, at_risk = [0.0], [1.0], 1.0, n
    for i, ti in enumerate(t):
        if e[i]:
            s *= (1 - 1 / at_risk)
            times.append(ti)
            surv.append(s)
        at_risk -= 1
    times.append(t.max())
    surv.append(s)
    return np.array(times), np.array(surv)
