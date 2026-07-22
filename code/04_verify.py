"""
Verify everything before class.

    python code/04_verify.py            # numbers only  (fast)
    python code/04_verify.py --full     # also executes all three notebooks
    python code/04_verify.py --live     # ...against the published GitHub urls

The assertions exist so a wrong number can never quietly reach a slide. If the
data or the analysis code changes and a headline claim stops holding, this
fails loudly instead of the deck saying something untrue in front of a room of
teenagers.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.statistics import logrank_test
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import psiclass as P

# Notebook 3 needs torch + transformers, which live in a different env.
INTERPRETERS = {
    "notebook_1_ml.ipynb": "/Users/cramere/miniforge3/bin/python",
    "notebook_2_imaging.ipynb": "/Users/cramere/miniforge3/bin/python",
    "notebook_3_llm.ipynb":
        "/Users/cramere/miniforge3/envs/cellcharter-env/bin/python",
}

PASS, FAIL = "  PASS", "  FAIL"
failures: list[str] = []


def check(name: str, got, expected, tol=None) -> None:
    if tol is None:
        ok = got == expected
    else:
        ok = abs(got - expected) <= tol
    print(f"{PASS if ok else FAIL}  {name}: {got}"
          f"{'' if ok else f'  (expected {expected})'}")
    if not ok:
        failures.append(name)


def check_numbers() -> None:
    print("\nheadline numbers")
    sample, xy, pat = P.load()
    mix = P.mixing_scores(xy)

    cold = sorted(mix.loc[mix.our_class == "cold", "SampleID"].tolist())
    check("cold tumors match the paper", cold, [15, 19, 22, 24, 25, 26])

    df = mix.merge(pat, on="SampleID")
    warm = df[df.our_class != "cold"].copy()
    agree = (warm.our_class.map({"compartmentalized": "compartmentalized",
                                 "mixed": "mixed"}) == warm.published_class)
    check("agreement with published labels", round(agree.mean(), 3), 1.0)
    check("patients scored (non-cold)", len(warm), 33)

    warm["is_mixed"] = (warm.our_class == "mixed").astype(int)
    cox = CoxPHFitter().fit(warm[["survival_days", "event", "is_mixed"]],
                            "survival_days", "event").summary
    check("hazard ratio, mixed vs walled off",
          round(float(cox["exp(coef)"].iloc[0]), 2), 5.21, tol=0.05)
    check("Cox p-value", round(float(cox["p"].iloc[0]), 3), 0.032, tol=0.005)

    lr = logrank_test(*[warm[warm.is_mixed == v].survival_days for v in (0, 1)],
                      *[warm[warm.is_mixed == v].event for v in (0, 1)])
    check("log-rank p-value", round(lr.p_value, 3), 0.017, tol=0.005)

    # the deliberate null: composition tells us nothing
    allc = pd.read_csv(P.PROC / "cells_xy.csv.gz",
                       usecols=["SampleID", "celltype"])
    comp = pd.crosstab(allc.SampleID, allc.celltype, normalize="index")
    comp = comp.loc[comp.index.isin(pat.SampleID)]
    g = KMeans(2, n_init=50, random_state=0).fit_predict(
        StandardScaler().fit_transform(comp))
    d = pd.DataFrame({"SampleID": comp.index, "g": g}).merge(pat, on="SampleID")
    null = logrank_test(*[d[d.g == v].survival_days for v in (0, 1)],
                        *[d[d.g == v].event for v in (0, 1)]).p_value
    ok = null > 0.05
    print(f"{PASS if ok else FAIL}  composition null stays null: p={null:.3f}")
    if not ok:
        failures.append("composition null")


def check_data_files() -> None:
    print("\nstudent data files")
    limits = {"cells_sample.csv": 4.0, "cells_xy.csv.gz": 3.0,
              "patients.csv": 0.1, "seg_demo.npz": 1.0}
    for name, cap in limits.items():
        f = P.PROC / name
        if not f.exists():
            print(f"{FAIL}  {name} missing"); failures.append(name); continue
        mb = f.stat().st_size / 1e6
        ok = mb <= cap
        print(f"{PASS if ok else FAIL}  {name}: {mb:.2f} MB (cap {cap})")
        if not ok:
            failures.append(name)


def check_figures() -> None:
    print("\nslide figures")
    expected = ["two_patients", "cluster_heatmap", "pca", "umap",
                "km_composition_null", "km_mixing", "mixing_dotplot",
                "watershed_easy", "watershed_hard", "mask_vs_phenotype",
                "neuron", "next_token", "tokens", "temperature_mechanism",
                "temperature_effect", "attention"]
    missing = [n for n in expected if not (P.FIGS / f"{n}.png").exists()]
    if missing:
        print(f"{FAIL}  missing: {', '.join(missing)}")
        failures.append("figures")
    else:
        print(f"{PASS}  all {len(expected)} figures present")


def run_notebooks(live: bool = False) -> None:
    """Execute each notebook end to end.

    By default the DATA url is rewritten to the local processed folder, so the
    check works offline. With live=True the notebooks run exactly as committed,
    fetching from GitHub -- that is the real student experience and the only
    way to catch a broken or unpushed data URL.
    """
    print(f"\nnotebook execution, {'LIVE urls' if live else 'local files'} "
          "(this takes a few minutes)")
    local = P.PROC.as_uri()
    for name, interpreter in INTERPRETERS.items():
        src = P.ROOT / "code" / name
        if not src.exists():
            print(f"{FAIL}  {name} missing"); failures.append(name); continue
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / name
            # point DATA at the local processed folder instead of the web.
            # Edit the parsed notebook, not the raw JSON -- the quotes around
            # the URL are escaped on disk.
            nb = nbformat.read(src, as_version=4)
            if not live:
                for cell in nb.cells:
                    if cell.cell_type == "code":
                        cell.source = re.sub(r'DATA = "[^"]*"',
                                             f'DATA = "{local}"', cell.source)
            nbformat.write(nb, dst)
            r = subprocess.run(
                [interpreter, "-m", "nbconvert", "--to", "notebook",
                 "--execute", "--inplace", str(dst)],
                capture_output=True, text=True, timeout=3600)
        if r.returncode == 0:
            print(f"{PASS}  {name}")
        else:
            tail = r.stderr.strip().splitlines()[-6:]
            print(f"{FAIL}  {name}\n      " + "\n      ".join(tail))
            failures.append(name)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true",
                    help="also execute the notebooks end to end")
    ap.add_argument("--live", action="store_true",
                    help="run the notebooks against the published GitHub "
                         "urls instead of local files (implies --full)")
    args = ap.parse_args()

    check_data_files()
    check_figures()
    check_numbers()
    if args.full or args.live:
        run_notebooks(live=args.live)

    print()
    if failures:
        print(f"{len(failures)} CHECK(S) FAILED: {', '.join(failures)}")
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
