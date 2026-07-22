# PSI Coding Class 2026 — Machine Learning & Language Models

A ~60 minute segment for high school students, built on the Keren et al. 2018
*Cell* MIBI-TOF triple-negative breast cancer dataset.

Students meet the **four main kinds of machine learning** — classification,
regression, clustering, dimensionality reduction — by using each one on 20,000
real cells. As a capstone they invent a spatial feature that predicts survival,
reproducing a published result. Then they take a language model apart.

The notebooks are **playable demos, not fill-in exercises**: every cell runs
as-is, with 🎛️ *Try it* boxes inviting students to change a number and rerun.

## What's here

```
presentation/
  psi_ml_llm.pptx        29 slides, editable, speaker notes in the notes pane
  SPEAKER_NOTES.md       per-slide script, timings, cut list, FAQ
  figures/               16 PNGs, all regenerable
code/
  00_build_class_data.py   raw data -> 4 MB of student files   (run once)
  01_make_figures.py       analysis figures
  01b_make_llm_figures.py  GPT-2 / Qwen figures   (needs torch)
  02_build_deck.py         -> psi_ml_llm.pptx + SPEAKER_NOTES.md
  03_build_notebooks.py    -> the three student notebooks
  04_verify.py             asserts every headline number; runs the notebooks
  psiclass.py              shared analysis + plot style
  notebook_1_ml.ipynb      students: clustering, PCA, spatial stats, survival
  notebook_2_imaging.ipynb instructor-driven: segmentation
  notebook_3_llm.ipynb     students: neuron, tokenizer, GPT-2, Qwen
data/
  TNBC_shareCellData/    the raw download (420 MB, never touched by students)
  processed/             the 4 small files students actually load
```

## Open in Colab

The notebooks pull their data straight out of this repo, so these links work
with nothing else set up:

| | |
|---|---|
| 1 · Machine learning on real tumors | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/emcramer/psi-class-2026/blob/main/code/notebook_1_ml.ipynb) |
| 2 · Finding cells in an image | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/emcramer/psi-class-2026/blob/main/code/notebook_2_imaging.ipynb) |
| 3 · Inside a language model | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/emcramer/psi-class-2026/blob/main/code/notebook_3_llm.ipynb) |

Students need no account and no API key. Notebooks 1 and 2 download about 4 MB;
notebook 3 also pulls ~1.5 GB of model weights, but that transfer happens
between Google's servers and HuggingFace, not over the room's wifi.

## Getting the raw data

`data/TNBC_shareCellData/` is deliberately not in this repo (~400 MB). You only
need it to re-run `code/00_build_class_data.py`; everything else works from the
committed `data/processed/`. Download it from the paper's release at
<https://mibi-share.ionpath.com>.

## Rebuilding

```bash
PY=/Users/cramere/miniforge3/bin/python
TORCHPY=/Users/cramere/miniforge3/envs/cellcharter-env/bin/python

$PY      code/00_build_class_data.py    # only if the raw data changes
$PY      code/01_make_figures.py
$TORCHPY code/01b_make_llm_figures.py   # downloads gpt2 + Qwen on first run
$PY      code/03_build_notebooks.py
$PY      code/02_build_deck.py
$PY      code/04_verify.py --full       # everything, including the notebooks
```

The LLM figures need `torch`, which lives in the `cellcharter-env` environment;
everything else runs in the miniforge base environment.

## The results students reproduce

| | |
|---|---|
| Classification — cell type from 16 markers | **95%** (16-marker RF), 89% (2 markers) |
| Regression — immune fraction → TIL score | **R² = 0.66**, n = 25 |
| Clustering — k-means, no labels | recovers T / B / neutrophil / tumor cells |
| "Cold" tumors (<250 immune cells) | recovers exactly the paper's 6 |
| Mixing score vs published labels | **33 / 33 correct** |
| Mixed vs walled off → survival | **HR 5.21, p = 0.032** (paper: 4.97, p = 0.03) |
| Cell composition → survival | **p = 0.18 — null, on purpose** |

`04_verify.py` asserts all of these, so a wrong number can't quietly reach a
slide.

## Things to be honest about in the room

- **38 patients is small.** One or two patients moving would change the p-value.
- **The 0.26 cutoff was chosen after looking at the data.** Notebook 1 has an
  exercise that tests other cutoffs.
- **Survival here is overall survival**, not disease-free. The clinical table
  has a separate `RECURRENCE_LABEL`. Say "survival".
- **The segmentation images in notebook 2 are simulated** from the real cell
  outlines — the raw microscope channels aren't in the public download. The
  difficulty is real; the pixels are not.
- **`Censored` is inverted** from the usual convention in this dataset:
  `Censored == 1` means censored, so `event = 1 - Censored`.

## Source

Keren et al., *A Structured Tumor-Immune Microenvironment in Triple Negative
Breast Cancer Revealed by Multiplexed Ion Beam Imaging*, Cell 174, 1373–1387
(2018). Paper PDF in `misc/`.
