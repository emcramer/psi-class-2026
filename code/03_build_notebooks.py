"""
Generate the three student Colab notebooks.

    python code/03_build_notebooks.py     # -> code/notebook_*.ipynb

Written as a builder rather than by hand so the shared header (data URL,
imports, plot style) stays identical across all three and can be changed in one
place.
"""

import json
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "code"

# Students fetch the four small files straight from the public class repo.
# These are the files in data/processed/, none larger than 3 MB.
DATA_URL = ("https://raw.githubusercontent.com/emcramer/psi-class-2026/"
            "main/data/processed")

STYLE = '''# --- setup: run me first! ---
import pandas as pd, numpy as np, matplotlib.pyplot as plt

DATA = "{data_url}"

plt.rcParams.update({{"figure.figsize": (8, 5.5), "font.size": 13,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e1e0d9",
                     "figure.facecolor": "white", "axes.facecolor": "white"}})
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
print("ready")
'''


def md(text):
    return nbf.v4.new_markdown_cell(text.strip("\n"))


def code(text):
    return nbf.v4.new_code_cell(text.strip("\n"))


def write(name, cells):
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": []},
    }
    path = OUT / name
    path.write_text(nbf.writes(nb))
    print(f"  {name}  ({len(cells)} cells)")


# ===========================================================================
# Notebook 1 -- the four kinds of machine learning, on real tumor cells
# ===========================================================================
def notebook_1():
    return [
        md("""
# The four kinds of machine learning 🔬

Forty-one women had a piece of their breast tumor photographed with a machine
that measures **36 proteins in every single cell** — about 200,000 cells in all.

We'll use that data to meet the **four main kinds of machine learning**. You
don't have to write anything: every cell already works. Run them in order with
`Shift + Enter`, then look for the **🎛️ Try it** boxes and change a number to
see what happens.

|  | predict a **category** | predict a **number** |
|---|---|---|
| **have labels** (supervised) | ① Classification | ② Regression |
| **no labels** (unsupervised) | ③ Clustering | ④ Dimensionality reduction |
"""),
        code(STYLE.format(data_url=DATA_URL)),
        code('''
cells = pd.read_csv(f"{DATA}/cells_sample.csv")
print(cells.shape, "-> 20,000 cells, 16 protein measurements each")
cells.head()
'''),
        md("""
Each **row** is one cell; each **column** is how much of one protein it has —
a fingerprint 16 numbers long. The `celltype` column is the **answer key**:
what a biologist said each cell is. We'll use it, hide it, and predict it.

---
# ① Classification — *supervised, predict a category*

**Supervised** means we *have* the answers and teach the computer to copy them.
We'll show it labeled cells, then test it on cells it has never seen.
"""),
        code('''
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

MARKERS = ["CD45", "CD3", "CD8", "CD4", "CD20", "CD68", "CD11c", "MPO",
           "Pan-Keratin", "Beta catenin", "Keratin17", "Vimentin", "SMA",
           "CD31", "FoxP3", "HLA-DR"]

X = StandardScaler().fit_transform(cells[MARKERS])
y = cells["celltype"]

# split: teach on 70% of the cells, test on the other 30%
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                    random_state=0)

model = RandomForestClassifier(n_estimators=120, random_state=0)
model.fit(X_train, y_train)

print(f"accuracy on cells it never saw: {model.score(X_test, y_test):.1%}")
'''),
        md("""
Around **90% correct** on cells it was never taught. Let's *see* the rule it
learned. With just two markers — Keratin (tumor) and CD45 (immune) — we can
draw the decision it makes everywhere on the map.
"""),
        code('''
from matplotlib.colors import ListedColormap
from sklearn.linear_model import LogisticRegression

def coarse(labels):
    return np.where(labels == "Tumor", "tumor",
            np.where(np.isin(labels, ["Endothelial", "Mesenchymal"]),
                     "other", "immune"))

two = StandardScaler().fit_transform(cells[["Pan-Keratin", "CD45"]])
yc = coarse(cells.celltype.values)
mini = LogisticRegression(max_iter=1000).fit(two, yc)

xx, yy = np.meshgrid(np.linspace(two[:,0].min(), two[:,0].max(), 300),
                     np.linspace(two[:,1].min(), two[:,1].max(), 300))
Z = mini.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
order = {"tumor":0, "immune":1, "other":2}
plt.figure(figsize=(7.5, 6.5))
plt.pcolormesh(xx, yy, np.vectorize(order.get)(Z),
               cmap=ListedColormap(["#cfe0f6","#f9d9c6","#cdeee0"]), shading="auto")
for k, c in [("tumor", BLUE), ("immune", ORANGE), ("other", GREEN)]:
    m = yc == k
    plt.scatter(two[m,0][:1500], two[m,1][:1500], s=6, c=c, alpha=.6, label=k)
plt.xlabel("Keratin  (more = tumor)"); plt.ylabel("CD45  (more = immune)")
plt.legend(markerscale=3); plt.xticks([]); plt.yticks([]); plt.grid(False)
plt.title("The rule the computer drew"); plt.show()
'''),
        md("""
The shaded regions are the rule: land in the blue zone and it calls you a
tumor cell. That is *all a classifier is* — a boundary learned from examples.

> ### 🎛️ Try it
> - In the accuracy cell, swap `RandomForestClassifier(...)` for
>   `LogisticRegression(max_iter=500)`. Simpler model — does it do worse?
> - In the picture, change `["Pan-Keratin", "CD45"]` to `["CD3", "CD8"]`
>   (two T-cell markers). Can those two alone separate the cell types?

---
# ② Regression — *supervised, predict a number*

Same idea — we have answers — but now the answer is a **number**, not a
category. Real question from the paper: a pathologist eyeballs each tumor and
gives it a "TILs" immune score from 1 to 4. **Can the computer's cell count
predict that human score?**
"""),
        code('''
patients = pd.read_csv(f"{DATA}/patients.csv")
all_cells = pd.read_csv(f"{DATA}/cells_xy.csv.gz")
all_cells["type"] = coarse(all_cells.celltype.values)

# for each patient: what fraction of cells are immune?
immune_frac = all_cells.groupby("SampleID").type.apply(lambda t: (t=="immune").mean())
data = patients.assign(immune_frac=patients.SampleID.map(immune_frac)).dropna(subset=["TIL_score"])

slope, intercept = np.polyfit(data.immune_frac, data.TIL_score, 1)
r2 = np.corrcoef(data.immune_frac, data.TIL_score)[0,1] ** 2

xs = np.linspace(0, data.immune_frac.max(), 50)
plt.figure(figsize=(7.5, 6))
plt.plot(xs, intercept + slope*xs, color=BLUE, lw=2.5, label=f"fitted line (R²={r2:.2f})")
plt.scatter(data.immune_frac, data.TIL_score, s=90, c=ORANGE, edgecolors="white", zorder=3)
plt.xlabel("immune fraction the COMPUTER counted")
plt.ylabel("TIL score a PATHOLOGIST gave")
plt.legend(); plt.title("Predicting a number"); plt.show()

print(f"R² = {r2:.2f}   (1.0 = perfect, 0 = useless)")
'''),
        md("""
The dots trend up the line: more immune cells counted, higher the human score.
The computer's automatic count agrees with the expert's eye about **two-thirds
of the way** (R² = 0.66). That's regression — fit a line, predict a number.

> ### 🎛️ Try it
> - Predict a patient yourself: if the computer counts **40%** immune cells,
>   run `intercept + slope * 0.40`. What TIL score does the line guess?
> - `TIL_score` runs 1–4. What in the data might keep R² from reaching 1.0?

---
# ③ Clustering — *unsupervised, no answer key*

Now we **hide the answers**. Unsupervised learning gets no labels at all — it
just looks for groups that naturally hang together. Watch it rediscover the
cell types on its own.
"""),
        code('''
from sklearn.cluster import KMeans

labels = KMeans(n_clusters=6, n_init=20, random_state=0).fit_predict(X)
print("the computer sorted 20,000 cells into 6 piles:", np.bincount(labels))

profile = pd.DataFrame(X, columns=MARKERS).groupby(labels).mean()
plt.figure(figsize=(11, 4.5))
plt.imshow(profile, cmap="RdBu_r", vmin=-2.5, vmax=2.5, aspect="auto")
plt.xticks(range(len(MARKERS)), MARKERS, rotation=45, ha="right")
plt.yticks(range(6), [f"pile {i}" for i in range(6)])
plt.colorbar(label="how much of this protein"); plt.grid(False)
plt.title("Red = lots of it.  Which pile is which cell type?"); plt.show()
'''),
        md("""
### 🔍 Be the biologist

It grouped the cells with **no answer key**. Use the cheat sheet to name each
pile from its red squares, then run the next cell to check.

| marker | cell |
|---|---|
| CD3, CD4, CD8 | T cell |
| CD20 | B cell |
| MPO | neutrophil |
| CD68 | macrophage |
| Pan-Keratin, Keratin17 | tumor |
"""),
        code('''
answer = pd.crosstab(labels, cells.celltype)
for i in range(6):
    top = profile.loc[i].sort_values(ascending=False).head(3)
    print(f"pile {i}: high in {', '.join(top.index):40s} -> really mostly {answer.loc[i].idxmax()}")
'''),
        md("""
It found T cells, B cells, neutrophils and tumor cells — **without ever being
told they existed.** That's the difference: classification *reproduces* labels
you have; clustering *discovers* groups you don't.

> ### 🎛️ Try it
> Change `n_clusters=6` to `3`, or to `10`. With more piles, do rare cell
> types split off into their own group?

---
# ④ Dimensionality reduction — *unsupervised, simplify*

Each cell is 16 numbers — a point in *16-dimensional* space we can't picture.
**PCA** squashes those 16 numbers down to 2 so we can put every cell on a map.
"""),
        code('''
from sklearn.decomposition import PCA

xy2 = PCA(n_components=2).fit_transform(X)
plt.figure(figsize=(7.5, 6.5))
for k, c in [("other", GREEN), ("tumor", BLUE), ("immune", ORANGE)]:
    m = coarse(cells.celltype.values) == k
    plt.scatter(xy2[m,0], xy2[m,1], s=4, c=c, alpha=.5, label=k)
plt.legend(markerscale=4); plt.xticks([]); plt.yticks([]); plt.grid(False)
plt.title("16 numbers per cell, squashed onto a 2-D map"); plt.show()
'''),
        md("""
Tumor cells settle in one region, immune cells in another — and the colors
were **painted on afterwards**, never used to build the map. The structure was
already in the numbers. That's the fourth kind: keep the shape of the data
while throwing away dimensions you can't see.

---
# ⑤ Capstone: inventing your own feature 🏆

The four kinds are the toolkit. Real science comes from **feeding them the
right numbers.** Here's the actual finding from this dataset.

First, an honest failure. Does *which* cells a patient has predict survival?
"""),
        code('''
composition = pd.crosstab(all_cells.SampleID, all_cells.celltype, normalize="index")
composition = composition.loc[composition.index.isin(patients.SampleID)]
groups = KMeans(2, n_init=50, random_state=0).fit_predict(
    StandardScaler().fit_transform(composition))
surv = pd.DataFrame({"SampleID": composition.index, "group": groups}).merge(patients)

def survival_curve(days, died):
    order = np.argsort(days); days, died = np.array(days)[order], np.array(died)[order]
    t, s, alive, n = [0], [1.0], 1.0, len(days)
    for i, d in enumerate(days):
        if died[i]: alive *= 1 - 1/n; t.append(d/365.25); s.append(alive)
        n -= 1
    return t + [days.max()/365.25], s + [alive]

for g, c in [(0, BLUE), (1, ORANGE)]:
    s = surv[surv.group == g]; t, sv = survival_curve(s.survival_days, s.event)
    plt.step(t, sv, where="post", color=c, lw=2.5, label=f"group {g} (n={len(s)})")
plt.ylim(0,1.02); plt.xlabel("years"); plt.ylabel("fraction alive")
plt.title("Grouped by WHICH cells they have"); plt.legend(); plt.show()
'''),
        md("""
The two lines sit on top of each other — cell *composition* tells us almost
nothing about survival. So we invent a better number. Look at two patients with
the **same amount** of immune cells:
"""),
        code('''
fig, axes = plt.subplots(1, 2, figsize=(13, 6.5))
for ax, pid in zip(axes, [3, 12]):
    g = all_cells[all_cells.SampleID == pid]
    for k, c in [("other", GREEN), ("tumor", BLUE), ("immune", ORANGE)]:
        s = g[g.type == k]; ax.scatter(s.x, s.y, s=3, c=c, alpha=.75)
    ax.set_title(f"Patient {pid} — {(g.type=='immune').mean():.0%} immune")
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False); ax.set_aspect("equal")
plt.show()
'''),
        md("""
Left: immune cells **walled off** in their own territory. Right: **mixed**
right in among the tumor. Same ingredients, different architecture. Let's turn
that into a number — the **mixing score**:

> mixing score = immune cells touching tumor cells ÷ immune cells touching each other
"""),
        code('''
from scipy.spatial import cKDTree

rows = []
for pid, g in all_cells.groupby("SampleID"):
    pairs = cKDTree(g[["x","y"]].values).query_pairs(30, output_type="ndarray")
    a, b = g.type.values[pairs[:,0]], g.type.values[pairs[:,1]]
    imm_imm = ((a=="immune") & (b=="immune")).sum()
    imm_tum = (((a=="immune") & (b=="tumor")) | ((a=="tumor") & (b=="immune"))).sum()
    rows.append({"SampleID": pid, "mixing": imm_tum/max(imm_imm,1),
                 "n_immune": (g.type=="immune").sum()})
scores = pd.DataFrame(rows)

warm = scores[scores.n_immune >= 250].merge(patients, on="SampleID")
warm["label"] = np.where(warm.mixing < 0.26, "walled off", "mixed")
for lab, c in [("walled off", BLUE), ("mixed", ORANGE)]:
    s = warm[warm.label == lab]; t, sv = survival_curve(s.survival_days, s.event)
    plt.step(t, sv, where="post", color=c, lw=2.5, label=f"{lab} (n={len(s)})")
plt.ylim(0,1.02); plt.xlabel("years"); plt.ylabel("fraction alive")
plt.title("Grouped by WHERE their cells are"); plt.legend(); plt.show()
'''),
        md("""
## That gap is the whole point.

Patients whose immune cells were **mixed into** the tumor did far worse —
about **5× the risk of dying** — than those whose immune cells were **walled
off**. *Which* cells you have: told us nothing. *Where* they are: told us a lot.

You just reproduced a finding from a paper in *Cell*, one of the top journals
in biology, in about ten lines of code.

> ### 🎛️ Try it
> - Change `30` (the touching distance) to `50`. Does the survival gap hold?
> - Change the `0.26` cutoff. How far can you push it before it breaks?
"""),
    ]

# ===========================================================================
def notebook_2():
    return [
        md("""
# How does a computer find cells in a photo? 🖼️

Every number in the last notebook started as a **picture**. Somebody had to
turn the picture into a table — to draw an outline around each cell and say
"this is cell #1, this is cell #2."

That's called **segmentation**. Let's try it.
"""),
        code(STYLE.format(data_url=DATA_URL)),
        code('''
import urllib.request
urllib.request.urlretrieve(f"{DATA}/seg_demo.npz", "seg_demo.npz")
d = np.load("seg_demo.npz")

plt.figure(figsize=(7, 7))
plt.imshow(d["easy"], cmap="gray")
plt.title("A microscope image. How many cells?"); plt.axis("off")
plt.show()
'''),
        md("""
You can see the blobs. Counting them by hand would take a while — and there are
**200,000** of these in the full dataset.

The classic recipe is three steps:

1. **Threshold** — anything brighter than X is a cell, anything darker is background
2. **Distance transform** — find the center of each blob
3. **Watershed** — flood outward from each center until the floods meet
"""),
        code('''
from scipy import ndimage as ndi
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu, gaussian

def find_cells(image, min_distance=4):
    smooth = gaussian(image, 1.0)
    is_cell = smooth > threshold_otsu(smooth)          # 1. threshold
    distance = ndi.distance_transform_edt(is_cell)     # 2. distance to edge
    peaks = peak_local_max(distance, min_distance=min_distance, labels=is_cell)
    seeds = np.zeros(distance.shape, bool); seeds[tuple(peaks.T)] = True
    return watershed(-distance, ndi.label(seeds)[0], mask=is_cell)  # 3. flood

found = find_cells(d["easy"])
print("cells found:", found.max())
print("cells actually there:", len(np.unique(d["nuclei"])) - 1)
'''),
        code('''
def show(image, segmentation, title):
    rng = np.random.default_rng(1)
    shuffle = np.concatenate([[0], rng.permutation(np.arange(1, segmentation.max() + 1))])
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].imshow(image, cmap="gray"); ax[0].set_title("the picture")
    ax[1].imshow(np.where(segmentation > 0, shuffle[segmentation], np.nan),
                 cmap="tab20", interpolation="nearest")
    ax[1].set_title("cells the computer found")
    for a in ax: a.axis("off"); a.grid(False)
    fig.suptitle(title, fontsize=15)
    plt.show()

show(d["easy"], found, "Nice, well-separated cells")
'''),
        md("""
That worked well! Three lines of math, no "AI" at all.

### Now the catch.

Real tumor tissue isn't tidy. Cells are jammed against each other with no gaps.
Here's what an actual sample looks like — **same code, harder picture:**
"""),
        code('''
found_hard = find_cells(d["hard"], min_distance=5)
show(d["hard"], found_hard, "Real, densely packed tissue")

def outline_accuracy(truth, guess):
    scores = []
    for label in np.unique(truth):
        if label == 0: continue
        mask = truth == label
        overlap = guess[mask][guess[mask] > 0]
        if len(overlap) == 0: scores.append(0); continue
        counts = np.bincount(overlap); best = counts.argmax()
        scores.append(counts[best] / (mask | (guess == best)).sum())
    return np.mean(scores)

print(f"easy picture: outlines {outline_accuracy(d['nuclei'], found):.0%} correct")
print(f"real tissue:  outlines {outline_accuracy(d['truth'], found_hard):.0%} correct")
'''),
        md("""
### It falls apart.

Look at the big merged blobs — the algorithm glued neighboring cells together.
It got roughly the right *count*, but the *shapes* are wrong, and every protein
measurement you make from a wrong shape is also wrong.

**This is exactly why the scientists who made our dataset used a neural
network instead.** They trained one on thousands of hand-drawn cell outlines
until it learned what a cell boundary looks like — the same idea as your phone
recognizing a face.

The table you used in notebook 1? A neural network drew every one of those
200,000 outlines.

---
### 🚀 If you have time

- Change `min_distance` and watch cells split apart or merge together.
- Where else does "label every pixel" matter? (Self-driving cars. Tumor
  outlines for radiation therapy. Satellite maps of deforestation.)
"""),
    ]


# ===========================================================================
# Notebook 3 -- what is a language model
# ===========================================================================
def notebook_3():
    return [
        md("""
# What is actually inside ChatGPT? 🤖

Completely different tool, completely different job. Let's take one apart.

We'll build a single neuron by hand, then run a **real** language model — the
same kind of thing behind ChatGPT, just small enough to run on this free
computer.
"""),
        code(STYLE.format(data_url=DATA_URL)),
        md("""
## Part 1 — One neuron, built from scratch

A neuron does three things: **multiply** each input by a weight, **add** them
up, and **squash** the answer to a number between 0 and 1.

That's it. That's the whole thing. Let's teach one to spot immune cells.
"""),
        code('''
cells = pd.read_csv(f"{DATA}/cells_sample.csv")

# two inputs, one answer
X = cells[["CD45", "Pan-Keratin"]].values
y = (~cells.celltype.isin(["Tumor", "Endothelial", "Mesenchymal"])).astype(float).values

X = (X - X.mean(0)) / X.std(0)      # scale
w = np.zeros(2); b = 0.0            # the neuron starts knowing nothing

def squash(z):
    return 1 / (1 + np.exp(-z))

for step in range(300):
    guess = squash(X @ w + b)       # multiply, add, squash
    error = guess - y               # how wrong were we?
    w -= 0.5 * (X.T @ error) / len(y)   # nudge the weights
    b -= 0.5 * error.mean()
    if step % 100 == 0:
        print(f"step {step:3d}  accuracy {((guess > 0.5) == y).mean():.1%}")

print(f"\\nfinal accuracy: {((squash(X @ w + b) > 0.5) == y).mean():.1%}")
print(f"learned weights: CD45 {w[0]:+.2f}, Pan-Keratin {w[1]:+.2f}")
'''),
        md("""
It taught itself that **high CD45 means immune** (positive weight) and **high
keratin means not immune** (negative weight) — which is exactly what a
biologist would tell you.

A language model is this same neuron, roughly **a hundred billion times over**.

---
## Part 2 — Words have to become numbers first

A model can't read letters. Every piece of text gets chopped into **tokens**
and each token becomes a number.
"""),
        code('''
!pip install -q transformers
'''),
        code('''
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("gpt2")

for text in ["Machine learning", "unbelievable", "1847362", "biology"]:
    pieces = [tokenizer.decode([i]) for i in tokenizer(text).input_ids]
    print(f"{text:20s} -> {pieces}")
'''),
        md("""
### 🔍 Your turn

Put **your own name** in the cell below. Does it survive in one piece, or get
chopped up? Try a friend's name, a slang word, an emoji.

*(This is genuinely why models are bad at spelling and counting letters — they
never see letters.)*
"""),
        code('''
my_text = "put your name here"

pieces = [tokenizer.decode([i]) for i in tokenizer(my_text).input_ids]
print(pieces)
print(f"{len(pieces)} tokens")
'''),
        md("""
---
## Part 3 — A real language model

Now we download **GPT-2** — a real model from 2019. When it came out, OpenAI
said it was too dangerous to release publicly.

It's about 500 MB, and it downloads to Google's computer, not yours.
"""),
        code('''
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained("gpt2")
model.eval()
print(f"{sum(p.numel() for p in model.parameters()):,} numbers inside this model")
'''),
        md("""
### All it does is guess the next word.

That's the entire trick. Give it some text, it produces a probability for every
possible next token. Let's watch.
"""),
        code('''
prompt = "The patient was diagnosed with breast"

ids = tokenizer(prompt, return_tensors="pt")
with torch.no_grad():
    logits = model(**ids).logits[0, -1]
probs = torch.softmax(logits, dim=-1)

top = torch.topk(probs, 8)
words = [tokenizer.decode(i).strip() for i in top.indices]

plt.barh(range(8)[::-1], top.values.numpy(), color=BLUE)
plt.yticks(range(8)[::-1], words); plt.xlabel("probability")
plt.title(f'"{prompt} ___"'); plt.grid(False)
plt.show()
'''),
        md("""
It is **94% sure** the next word is "cancer".

To write a sentence, it picks one, sticks it on the end, and asks the same
question again. And again. That's all "writing" is, for a language model.

### 🔍 Your turn — try your own prompt
"""),
        code('''
my_prompt = "The best thing about high school is"

ids = tokenizer(my_prompt, return_tensors="pt")
with torch.no_grad():
    probs = torch.softmax(model(**ids).logits[0, -1], dim=-1)
top = torch.topk(probs, 8)
for p, i in zip(top.values, top.indices):
    print(f"{p:6.1%}  {tokenizer.decode(i)!r}")
'''),
        md("""
---
## Part 4 — The creativity dial

If it always picked the single most likely word it would be boring and
repetitive. So we let it roll dice — and **temperature** decides how loaded
those dice are.

Here's the key thing: temperature does **not** cross any words off the list. It
takes the *same* list and stretches or squashes the odds:

> `temperature < 1` → gaps get bigger → the favorite wins even more often
> `temperature > 1` → gaps get smaller → long shots get a real chance

Watch the same seven words get re-weighted.
"""),
        code('''
ids = tokenizer("She opened the door and saw a", return_tensors="pt")
with torch.no_grad():
    scores = model(**ids).logits[0, -1]      # raw scores, before probabilities

top7 = torch.topk(torch.softmax(scores, -1), 7).indices
words = [tokenizer.decode(i).strip() for i in top7]

fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
for ax, temp in zip(axes, [0.5, 1.0, 2.0]):
    p = torch.softmax(scores / temp, -1)[top7]    # <-- divide by temperature
    p = (p / p.sum()).numpy()                     # share among these seven
    ax.barh(range(7)[::-1], p, color=BLUE)
    ax.set_yticks(range(7)[::-1]); ax.set_yticklabels(words)
    ax.set_title(f"temperature {temp}"); ax.set_xlim(0, 1); ax.grid(False)
plt.tight_layout(); plt.show()
'''),
        md("""
Same seven words every time. Only the odds changed.

*(The knob that genuinely does delete words is a different one, called
**top-k** or **top-p** — it keeps only the best few and throws the rest away.)*

---
## Part 5 — A model that can actually talk

GPT-2 is from 2019 and it rambles. Here's a model from 2024 that's only 4×
bigger but was trained far better — small enough to still run right here.
"""),
        code('''
chat_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
chat_tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
print("loaded")
'''),
        code('''
question = "In one sentence, what is a T cell?"

text = chat_tok.apply_chat_template([{"role": "user", "content": question}],
                                    tokenize=False, add_generation_prompt=True)
ids = chat_tok(text, return_tensors="pt")
out = chat_model.generate(**ids, max_new_tokens=80, do_sample=False)
print(chat_tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True))
'''),
        md("""
### 🔍 Your turn — ask it anything

Change the question above and run it again. Try to catch it being **confidently
wrong** — ask about something you know really well, or something very recent.

That's the most important thing to understand about these tools: it is picking
likely next words. It is not looking anything up, and it does not know when
it's wrong.

---
## Part 6 — Now turn the dial on a model that can talk

Same temperature setting as Part 4, but on a model good enough that you can
*hear* the difference.
"""),
        code('''
question = "In one sentence, why is the sky blue?"
text = chat_tok.apply_chat_template([{"role": "user", "content": question}],
                                    tokenize=False, add_generation_prompt=True)
ids = chat_tok(text, return_tensors="pt")

for temp in [0.3, 1.0, 1.8]:
    torch.manual_seed(3)
    out = chat_model.generate(**ids, max_new_tokens=45, do_sample=True,
                              temperature=temp, top_k=0, top_p=1.0)
    print(f"--- temperature {temp} ---")
    print(chat_tok.decode(out[0][ids.input_ids.shape[1]:],
                          skip_special_tokens=True).strip(), "\\n")
'''),
        md("""
### ⚠️ Read the first two answers carefully.

Both of them sound completely confident. **Both of them are wrong.**

The sky is blue because air scatters short (blue) wavelengths much more than
long ones — *Rayleigh scattering*. It is not about reflection, and it is
certainly not "white or gray."

Nothing in the model flagged those answers as wrong, because nothing in the
model was ever checking. It was picking likely next words, and a confident
sentence is a *likely* sentence.

That's the single most useful thing to know about these tools.

---
## The scale ladder

| model | numbers inside | year |
|---|---|---|
| the neuron you built | **3** | today |
| GPT-2 | 124,000,000 | 2019 |
| the one you just chatted with | 500,000,000 | 2024 |
| ChatGPT / Claude | ~1,000,000,000,000 | now |

Same three operations — multiply, add, squash — all the way up.

---
### 🚀 If you have time

- Ask the chat model a math question. Then a harder one.
- Ask it about a topic you're an expert in and grade its answer.
- Set `do_sample=True, temperature=1.5` on the chat model and watch it lose it.
"""),
    ]


def main():
    OUT.mkdir(exist_ok=True)
    print("notebooks:")
    write("notebook_1_ml.ipynb", notebook_1())
    write("notebook_2_imaging.ipynb", notebook_2())
    write("notebook_3_llm.ipynb", notebook_3())
    print(f"\nnotebooks will fetch data from:\n  {DATA_URL}")


if __name__ == "__main__":
    main()
