"""
Generate every slide figure for the PSI class deck.

    python code/01_make_figures.py        # -> presentation/figures/*.png

Colors come from psiclass.py, whose 3-slot categorical palette was checked with
the dataviz validator (all-pairs, light surface): worst CVD dE 9.2, worst
normal-vision dE 24.0. Aqua sits below 3:1 contrast, so every chart that uses
it carries direct labels instead of leaning on a legend.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from lifelines import CoxPHFitter
from lifelines.statistics import logrank_test

import psiclass as P
from psiclass import BLUE, ORANGE, AQUA, MUTED, INK, INK2, GRID, RED

P.use_slide_style()
P.FIGS.mkdir(parents=True, exist_ok=True)

RESULTS: dict[str, str] = {}   # headline numbers, echoed at the end


def save(fig, name: str) -> None:
    fig.savefig(P.FIGS / f"{name}.png")
    plt.close(fig)
    print(f"  {name}.png")


def label_cloud(ax, x, y, text, color):
    """Direct label at a cloud's median, with a surface halo so it stays legible."""
    ax.text(np.median(x), np.median(y), text, color=color, fontsize=19,
            fontweight="bold", ha="center", va="center",
            path_effects=[__import__("matplotlib.patheffects",
                                     fromlist=["x"]).withStroke(
                linewidth=4, foreground=P.SURFACE)])


# ---------------------------------------------------------------------------
# 1. Two patients, side by side -- the whole lesson in one picture
# ---------------------------------------------------------------------------
def fig_two_patients(xy, mix):
    # A MATCHED pair: these two patients have essentially the same fraction of
    # immune cells (50% vs 51%) but a 5x difference in how those cells are
    # arranged. Picking the two score extremes instead would let students read
    # the figure as "more immune cells = better", which is the wrong lesson and
    # is exactly what the composition null disproves.
    comp, mixed = 3, 12

    fig, axes = plt.subplots(1, 2, figsize=(15, 7.4))
    for ax, pid, title in [
        (axes[0], comp, f"Patient {comp} — walled off"),
        (axes[1], mixed, f"Patient {mixed} — mixed together"),
    ]:
        g = xy[xy.SampleID == pid]
        for kind in ["other", "tumor", "immune"]:
            s = g[g.coarse == kind]
            ax.scatter(s.x, s.y, s=3.5, c=P.COARSE_COLORS[kind],
                       alpha=0.75, linewidths=0)
        score = float(mix.loc[mix.SampleID == pid, "mixing_score"].iloc[0])
        pct = (g.coarse == "immune").mean()
        ax.set_title(f"{title}\n{pct:.0%} immune cells · mixing score {score:.2f}",
                     fontsize=20)
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
        ax.set_aspect("equal")
        for sp in ax.spines.values():
            sp.set_visible(True); sp.set_color(P.AXIS)

    handles = [Line2D([], [], marker="o", ls="", ms=13, color=c, label=k)
               for k, c in [("tumor", BLUE), ("immune", ORANGE), ("other", AQUA)]]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.02), fontsize=19)
    fig.suptitle("Same amount of immune cells. Completely different layout.",
                 fontsize=24, y=1.0)
    save(fig, "two_patients")
    return comp, mixed


# ---------------------------------------------------------------------------
# 2. k-means marker heatmap -- students name the clusters
# ---------------------------------------------------------------------------
def fig_cluster_heatmap(sample):
    X = StandardScaler().fit_transform(sample[P.MARKERS].values)
    km = KMeans(6, n_init=20, random_state=0).fit(X)
    prof = pd.DataFrame(X, columns=P.MARKERS).groupby(km.labels_).mean()
    prof = prof.clip(-2.5, 2.5)

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(prof.values, cmap=P.DIVERGING, vmin=-2.5, vmax=2.5,
                   aspect="auto")
    ax.set_xticks(range(len(P.MARKERS)))
    ax.set_xticklabels(P.MARKERS, rotation=45, ha="right")
    ax.set_yticks(range(6))
    ax.set_yticklabels([f"cluster {i}" for i in range(6)])
    ax.grid(False)
    ax.set_title("Six clusters the computer found — which is which?", pad=16)
    cb = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("marker level (z-score)", fontsize=17)
    cb.outline.set_visible(False)
    save(fig, "cluster_heatmap")

    # what each cluster actually is, for the speaker notes
    truth = pd.crosstab(km.labels_, sample["celltype"].values)
    lines = []
    for i in range(6):
        top = prof.loc[i].sort_values(ascending=False).head(3)
        lines.append(f"cluster {i} (n={(km.labels_ == i).sum()}): "
                     f"{', '.join(top.index)} -> mostly {truth.loc[i].idxmax()}")
    RESULTS["cluster_identities"] = "\n    ".join(lines)


# ---------------------------------------------------------------------------
# 3. PCA / UMAP -- one dot per cell, colored by phenotype
# ---------------------------------------------------------------------------
def _embedding_panel(ax, emb, coarse, title):
    for kind in ["other", "tumor", "immune"]:
        m = coarse == kind
        ax.scatter(emb[m, 0], emb[m, 1], s=4, c=P.COARSE_COLORS[kind],
                   alpha=0.5, linewidths=0)
    for kind in ["tumor", "immune", "other"]:
        m = coarse == kind
        label_cloud(ax, emb[m, 0], emb[m, 1], kind, P.COARSE_COLORS[kind])
    ax.set_title(title)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)


def fig_embeddings(sample):
    X = StandardScaler().fit_transform(sample[P.MARKERS].values)
    coarse = sample["coarse"].values
    pca = PCA(2)
    emb = pca.fit_transform(X)
    var = pca.explained_variance_ratio_.sum()

    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    _embedding_panel(ax, emb, coarse,
                     f"PCA — 16 measurements squashed into 2\n"
                     f"({var:.0%} of the variation kept)")
    ax.set_xlabel("PC 1"); ax.set_ylabel("PC 2")
    save(fig, "pca")

    try:
        import umap
        u = umap.UMAP(random_state=0, n_neighbors=25).fit_transform(X)
        fig, ax = plt.subplots(figsize=(8.5, 7.5))
        _embedding_panel(ax, u, coarse, "UMAP — the fancier version")
        save(fig, "umap")
    except ImportError:
        print("  [skip] umap not importable in this interpreter")


# ---------------------------------------------------------------------------
# 4. The null result: composition clusters do NOT split survival
# ---------------------------------------------------------------------------
def fig_composition_null(sample_all, pat):
    comp = pd.crosstab(sample_all.SampleID, sample_all.celltype,
                       normalize="index")
    comp = comp.loc[comp.index.isin(pat.SampleID)]
    X = StandardScaler().fit_transform(comp.values)
    km = KMeans(2, n_init=50, random_state=0).fit(X)
    df = (pd.DataFrame({"SampleID": comp.index, "grp": km.labels_})
          .merge(pat, on="SampleID"))

    lr = logrank_test(*[df[df.grp == g].survival_days for g in (0, 1)],
                      *[df[df.grp == g].event for g in (0, 1)])
    RESULTS["composition_null_p"] = f"{lr.p_value:.3f}"

    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    for g, color, name in [(0, BLUE, "cluster A"), (1, ORANGE, "cluster B")]:
        s = df[df.grp == g]
        t, sv = P.km_curve(s.survival_days.values / 365.25, s.event.values)
        ax.step(t, sv, where="post", color=color, lw=2.5,
                label=f"{name}  (n={len(s)})")
    ax.set_ylim(0, 1.02); ax.set_xlabel("years"); ax.set_ylabel("surviving")
    ax.set_title("Grouping patients by WHICH cells they have\n"
                 f"p = {lr.p_value:.2f} — no difference", fontsize=21)
    ax.legend(loc="lower left")
    save(fig, "km_composition_null")


# ---------------------------------------------------------------------------
# 5. The hit: spatial architecture DOES split survival
# ---------------------------------------------------------------------------
def fig_mixing_survival(mix, pat):
    df = mix.merge(pat, on="SampleID")
    warm = df[df.our_class != "cold"].copy()
    warm["is_mixed"] = (warm.our_class == "mixed").astype(int)

    cox = CoxPHFitter().fit(warm[["survival_days", "event", "is_mixed"]],
                            "survival_days", "event").summary
    hr, pval = float(cox["exp(coef)"].iloc[0]), float(cox["p"].iloc[0])
    lr = logrank_test(*[warm[warm.is_mixed == v].survival_days for v in (0, 1)],
                      *[warm[warm.is_mixed == v].event for v in (0, 1)])
    RESULTS["mixing_HR"] = f"{hr:.2f}"
    RESULTS["mixing_cox_p"] = f"{pval:.3f}"
    RESULTS["mixing_logrank_p"] = f"{lr.p_value:.3f}"
    RESULTS["agreement"] = (
        f"{(warm.our_class == warm.published_class).mean():.2f} "
        f"(n={len(warm)})")

    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    for v, color, name in [(0, BLUE, "walled off"), (1, ORANGE, "mixed")]:
        s = warm[warm.is_mixed == v]
        t, sv = P.km_curve(s.survival_days.values / 365.25, s.event.values)
        ax.step(t, sv, where="post", color=color, lw=2.5,
                label=f"{name}  (n={len(s)})")
    ax.set_ylim(0, 1.02); ax.set_xlabel("years"); ax.set_ylabel("surviving")
    ax.set_title("Grouping patients by WHERE their cells are\n"
                 f"{hr:.1f}× the risk of dying,  p = {pval:.3f}", fontsize=21)
    ax.legend(loc="lower left")
    save(fig, "km_mixing")

    # dot plot: every patient's score, colored by the published label
    fig, ax = plt.subplots(figsize=(11, 5.8))
    d = df.sort_values("mixing_score").reset_index(drop=True)
    # "cold" tumors are drawn hollow: they have too few immune cells for the
    # ratio to mean anything, so they are set aside rather than classified.
    cold = d[d.our_class == "cold"]
    ax.scatter(cold.index, cold.mixing_score, s=140, facecolors="none",
               edgecolors=MUTED, linewidths=2, zorder=3)
    for cls, color in [("compartmentalized", BLUE), ("mixed", ORANGE)]:
        s = d[(d.published_class == cls) & (d.our_class != "cold")]
        ax.scatter(s.index, s.mixing_score, s=140, c=color, zorder=3,
                   edgecolors=P.SURFACE, linewidths=2)
    ax.axhline(P.MIXING_THRESHOLD, color=MUTED, lw=1.2, zorder=1)
    ax.set_yscale("log")
    ax.text(len(d) - 0.5, P.MIXING_THRESHOLD * 1.18, "our cutoff = 0.26",
            ha="right", color=INK2, fontsize=17)
    lo, hi = np.log(d.mixing_score.min()), np.log(d.mixing_score.max())
    warm_d = d[d.our_class != "cold"]
    for cls, color, yfrac in [("compartmentalized", BLUE, 0.05),
                              ("mixed", ORANGE, 0.97)]:
        s = warm_d[warm_d.published_class == cls]
        ax.text(np.median(s.index.values), np.exp(lo + yfrac * (hi - lo)),
                f"{cls}\n(paper's label)", color=color, fontsize=18,
                fontweight="bold", ha="center", va="center", linespacing=1.3)
    ax.text(np.median(cold.index.values), np.exp(lo + 0.72 * (hi - lo)),
            "hollow = too few\nimmune cells to score", color=INK2, fontsize=15,
            ha="center", va="center", linespacing=1.3)
    ax.set_xlabel("patients, sorted by our score")
    ax.set_ylabel("mixing score")
    ax.set_xticks([])
    ax.set_title("Our score vs. the labels published in the paper", pad=14)
    save(fig, "mixing_dotplot")


# ---------------------------------------------------------------------------
# 6. Segmentation: works on easy nuclei, breaks on real tissue
# ---------------------------------------------------------------------------
def fig_segmentation():
    from scipy import ndimage as ndi
    from skimage.segmentation import watershed
    from skimage.feature import peak_local_max
    from skimage.filters import threshold_otsu, gaussian

    d = np.load(P.PROC / "seg_demo.npz")

    def segment(img, min_distance):
        sm = gaussian(img, 1.0)
        mask = sm > threshold_otsu(sm)
        dist = ndi.distance_transform_edt(mask)
        peaks = peak_local_max(dist, min_distance=min_distance, labels=mask)
        seed = np.zeros(dist.shape, bool)
        seed[tuple(peaks.T)] = True
        return watershed(-dist, ndi.label(seed)[0], mask=mask)

    def iou(truth, seg):
        vals = []
        for lab in np.unique(truth):
            if lab == 0:
                continue
            m = truth == lab
            ov = seg[m][seg[m] > 0]
            if len(ov) == 0:
                vals.append(0.0); continue
            c = np.bincount(ov); s = c.argmax()
            vals.append(c[s] / ((m | (seg == s)).sum()))
        return np.array(vals)

    rng = np.random.default_rng(1)
    for name, img, truth, mind, caption in [
        ("watershed_easy", d["easy"], d["nuclei"], 4,
         "Well-separated nuclei"),
        ("watershed_hard", d["hard"], d["truth"], 5,
         "Real, densely packed tissue"),
    ]:
        seg = segment(img, mind)
        sc = iou(truth, seg)
        n_true = len(np.unique(truth)) - 1
        n_found = len(np.unique(seg)) - 1
        RESULTS[f"{name}_iou"] = f"{sc.mean():.2f}"
        RESULTS[f"{name}_counts"] = f"{n_true} true / {n_found} found"

        shuf = np.concatenate([[0], rng.permutation(np.arange(1, seg.max() + 1))])
        fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.6))
        axes[0].imshow(img, cmap="gray")
        axes[0].set_title("what the computer sees", fontsize=20)
        axes[1].imshow(np.where(seg > 0, shuf[seg], np.nan), cmap="tab20",
                       interpolation="nearest")
        axes[1].set_title("cells it found", fontsize=20)
        for ax in axes:
            ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
        fig.suptitle(f"{caption}\n{n_true} cells really there · {n_found} found · "
                     f"only {sc.mean():.0%} of the outlines are right",
                     fontsize=21)
        save(fig, name)


# ---------------------------------------------------------------------------
# 7. Raw label mask vs phenotype render (how the table was made)
# ---------------------------------------------------------------------------
def fig_mask_vs_phenotype(xy, pid):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    mask = np.array(Image.open(
        P.ROOT / "data" / "TNBC_shareCellData" / f"p{pid}_labeledcellData.tiff"))
    rng = np.random.default_rng(0)
    shuf = np.concatenate([[0], rng.permutation(np.arange(1, mask.max() + 1))])

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    axes[0].imshow(np.where(mask > 0, shuf[mask], np.nan), cmap="tab20",
                   interpolation="nearest")
    axes[0].set_title("Step 1: find every cell", fontsize=21)
    g = xy[xy.SampleID == pid]
    for kind in ["other", "tumor", "immune"]:
        s = g[g.coarse == kind]
        axes[1].scatter(s.x, s.y, s=3, c=P.COARSE_COLORS[kind], linewidths=0)
    axes[1].set_ylim(mask.shape[0], 0); axes[1].set_xlim(0, mask.shape[1])
    axes[1].set_aspect("equal")
    axes[1].set_title("Step 2: name every cell", fontsize=21)
    for ax in axes:
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    save(fig, "mask_vs_phenotype")


# ---------------------------------------------------------------------------
# 8. One neuron, drawn
# ---------------------------------------------------------------------------
def fig_neuron():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    inputs = [("CD45 level", 0.78), ("Keratin level", -0.61), ("size", 0.05)]
    for i, (name, w) in enumerate(inputs):
        y = 1 - i
        ax.scatter([0], [y], s=1400, c=P.SURFACE, edgecolors=P.AXIS,
                   linewidths=1.6, zorder=3)
        ax.text(0, y, name.split()[0], ha="center", va="center", fontsize=15,
                zorder=4)
        ax.annotate("", xy=(2.6, 0), xytext=(0.28, y),
                    arrowprops=dict(arrowstyle="-", lw=1 + 4 * abs(w),
                                    color=BLUE if w > 0 else ORANGE,
                                    alpha=0.85))
        ax.text(1.35, y + 0.14 * np.sign(y or 1), f"× {w:+.2f}",
                fontsize=16, color=INK2, ha="center")
    ax.scatter([2.9], [0], s=4200, c=P.SURFACE, edgecolors=INK, linewidths=2,
               zorder=3)
    ax.text(2.9, 0, "add\nthem up", ha="center", va="center", fontsize=15,
            zorder=4)
    ax.annotate("", xy=(4.6, 0), xytext=(3.25, 0),
                arrowprops=dict(arrowstyle="->", lw=2, color=INK))
    ax.text(4.8, 0, "immune cell?\n87% yes", fontsize=17, va="center")
    ax.set_xlim(-0.6, 6.6); ax.set_ylim(-1.7, 1.7)
    ax.axis("off"); ax.grid(False)
    ax.set_title("One neuron: multiply, add, decide", fontsize=23)
    save(fig, "neuron")


def main():
    print("loading ...")
    sample, xy, pat = P.load()
    sample_all = pd.read_csv(P.PROC / "cells_xy.csv.gz",
                             usecols=["SampleID", "celltype"])

    print("computing mixing scores ...")
    mix = P.mixing_scores(xy)
    RESULTS["cold_patients"] = str(
        sorted(mix.loc[mix.our_class == "cold", "SampleID"].tolist()))

    print("figures:")
    comp, mixed = fig_two_patients(xy, mix)
    fig_cluster_heatmap(sample)
    fig_embeddings(sample)
    fig_composition_null(sample_all, pat)
    fig_mixing_survival(mix, pat)
    fig_segmentation()
    fig_mask_vs_phenotype(xy, comp)
    fig_neuron()

    print("\nheadline numbers:")
    for k, v in RESULTS.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
