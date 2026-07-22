"""
Build the PowerPoint deck and the speaker-notes document.

    python code/02_build_deck.py
    # -> presentation/psi_ml_llm.pptx
    # -> presentation/SPEAKER_NOTES.md

The .pptx is a real, editable PowerPoint file: open it and restyle freely.
Speaker notes land in the notes pane of each slide as well as in the markdown
file, so you can present from either.
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "presentation" / "figures"
OUT = ROOT / "presentation"

W, H = Inches(13.333), Inches(7.5)          # 16:9
INK = RGBColor(0x0B, 0x0B, 0x0B)
INK2 = RGBColor(0x52, 0x51, 0x4E)
BLUE = RGBColor(0x2A, 0x78, 0xD6)
SURFACE = RGBColor(0xFC, 0xFC, 0xFB)
FONT = "Helvetica Neue"

# (title, figure | None, body lines, speaker notes, kind)
#   kind: "title" | "section" | "figure" | "bullets" | "do"
DECK = [
    ("Machine Learning & Language Models", None,
     ["Two very different tools.",
      "Today we use both on a real cancer dataset."],
     "Introduce yourself in 20 seconds. Set the frame: these are two separate "
     "tools for two separate jobs, not versions of each other. We are going to "
     "USE the first one on real data from real patients, and then take the "
     "second one apart to see what is inside.",
     "title"),

    ("One of these women survived. One did not.", "two_patients",
     [],
     "DO NOT explain the picture yet. Ask them to guess which is which, and "
     "why. Take 2-3 guesses out loud. Most will guess based on the amount of "
     "orange -- point out that both are ~50% immune cells, it is printed right "
     "there. Then say: hold that thought, we will come back to this in 20 "
     "minutes and you will be able to answer it with code you wrote.",
     "figure"),

    ("What is machine learning?", None,
     ["Finding patterns in data — without being told the rule.",
      "",
      "You never wrote down 'a cat has pointy ears and whiskers.'",
      "You learned what a cat is by seeing lots of cats."
      ],
     "Keep this short. The key move is 'nobody wrote the rule down.' Ask: how "
     "would you write instructions for recognizing your friend's face? You "
     "can't. But you can show a computer 10,000 examples.",
     "bullets"),

    ("Two jobs, two tools", None,
     ["CLASSIFICATION — you have the answers, you want to predict new ones.",
      "     spam / not spam · is this mole dangerous?",
      "",
      "CLUSTERING — nobody has the answers. Find the groups.",
      "     what kinds of customers does this shop have?",
      "",
      "Today: mostly clustering. Nobody labeled 200,000 cells by hand."],
     "This is the one slide of vocabulary that matters. Classification = you "
     "have a teacher. Clustering = no teacher, find the structure yourself. "
     "Ask for one more example of each from the room before moving on.",
     "bullets"),

    ("Where the data comes from", "mask_vs_phenotype",
     [],
     "41 women with triple-negative breast cancer -- the aggressive kind with "
     "no targeted treatment. A machine measured 36 proteins in every cell of a "
     "tumor sample. ~200,000 cells. Step 1: outline every cell. Step 2: work "
     "out what each one is. We come back to HOW in part two.",
     "figure"),

    ("Notebook 1 — open it now", None,
     ["Clustering 20,000 cells",
      "",
      "You will find cell types that nobody told the computer about."],
     "Get everyone into notebook 1. Wait for the slowest person. Run the setup "
     "cell together. Then let them work through Part 1 while you circulate.",
     "do"),

    ("We found six groups", "cluster_heatmap",
     [],
     "Let them stare at this and guess before revealing. The wins: cluster "
     "with MPO only = neutrophils. CD20 = B cells. CD3/CD4/CD8 = T cells. "
     "Keratins = tumor. Ask 'which row is the T cells?' and wait. Someone "
     "will get it, and that moment is the point of the whole hour.",
     "figure"),

    ("Squishing 16 measurements into 2 dimensions", "pca",
     [],
     "Each dot is one cell. PCA finds the two directions that spread the data "
     "out the most. The colors were NOT used to build the picture -- they are "
     "painted on afterwards. The structure was already there.",
     "figure"),

    ("Same idea, fancier math", "umap",
     [],
     "OPTIONAL / CUT FIRST. UMAP is what you will see in real papers. Same "
     "job as PCA, better at keeping neighbors together. Mention the name so "
     "they recognize it later, then move on.",
     "figure"),

    ("So: does WHICH cells you have predict survival?", "km_composition_null",
     [],
     "This is a Kaplan-Meier curve -- the line drops every time a patient "
     "dies. Two groups, found by clustering patients on their cell makeup. "
     "The lines sit on top of each other. p = 0.18, which means 'this could "
     "easily be chance.' Say plainly: this is a real negative result and it is "
     "not a failure. It is a clue.",
     "figure"),

    ("Back to these two", "two_patients",
     [],
     "NOW answer the opening question. Both ~50% immune. Left: immune cells "
     "in their own territory, walled off. Right: immune cells mixed all "
     "through the tumor. Same ingredients, different architecture. Ask: how "
     "would you turn that difference into a NUMBER?",
     "figure"),

    ("Turning a picture into one number", None,
     ["For every patient:",
      "",
      "mixing score  =    immune cells touching tumor cells",
      "                        ─────────────────────────────",
      "                        immune cells touching each other",
      "",
      "Low = walled off.        High = all mixed together."],
     "Let them propose ideas first -- some will invent this themselves. Then "
     "show it. It is a ratio, so it does not care how many immune cells there "
     "are, only how they are arranged. That is exactly what we need.",
     "bullets"),

    ("Notebook 1 — Part 4", None,
     ["Write the mixing score yourself.",
      "",
      "Then compare it to what the scientists published."],
     "This is the centerpiece. ~6 lines with a KD-tree. Circulate. Expect "
     "questions about query_pairs -- explain it as 'give me every pair of "
     "cells within 30 pixels'.",
     "do"),

    ("Your score vs. the published labels", "mixing_dotplot",
     [],
     "33 patients, 33 correct. A Stanford lab published these labels in Cell, "
     "one of the top journals in biology. The students just reproduced them "
     "from scratch. Say that out loud -- they will not realize it is "
     "impressive unless you tell them.",
     "figure"),

    ("Where the cells are — that DOES predict survival", "km_mixing",
     [],
     "THE PAYOFF SLIDE. Same patients, same math, one different question. "
     "5.2x the risk of dying. p = 0.032. Which cells you have: nothing. Where "
     "they are: everything. Pause here. Let it land before moving on.",
     "figure"),

    ("Part 2 — How do you get numbers out of a picture?", None,
     ["Every number we just used started as a photograph."],
     "Transition. Everything so far assumed a tidy table. Somebody had to make "
     "that table.",
     "section"),

    ("Notebook 2 — follow along", None,
     ["Threshold → find centers → flood outwards",
      "",
      "Three lines of math. No AI at all."],
     "Instructor-driven -- do not make them type this. Project it, run it, "
     "narrate. Threshold: bright = cell. Distance transform: find the middle "
     "of each blob. Watershed: pour water from each center until floods meet.",
     "do"),

    ("On easy cells, it works", "watershed_easy",
     [],
     "158 cells really there, ~177 found, 72% of outlines right. Old-fashioned "
     "math, no neural network, works fine. Now watch what happens on the real "
     "thing.",
     "figure"),

    ("On real tissue, it falls apart", "watershed_hard",
     [],
     "Same code, real densely-packed tumor. Look at the big merged blobs -- "
     "it glued neighboring cells together. Got roughly the right COUNT, but "
     "the SHAPES are wrong, and every protein measurement from a wrong shape "
     "is also wrong. THIS is why the next slide exists.",
     "figure"),

    ("So they used a neural network", None,
     ["Trained on thousands of hand-drawn cell outlines.",
      "",
      "It learned what a cell boundary looks like.",
      "",
      "Every one of the 200,000 outlines you used today came from that model.",
      "",
      "Same idea as: face unlock · reading a cheque · tumor outlines for radiotherapy"],
     "Land the point: we did not start with deep learning, we EARNED it. The "
     "classical method broke, so they needed something that learns from "
     "examples. Give one or two familiar examples and move on -- do not go "
     "down a CNN rabbit hole.",
     "bullets"),

    ("Part 3 — What is actually inside ChatGPT?", None,
     ["Different tool. Different job. Let's take one apart."],
     "Hard reset. Say explicitly: this is NOT the same tool as the first half. "
     "We are switching topics, not scaling up.",
     "section"),

    ("It starts with one neuron", "neuron",
     [],
     "Multiply each input by a weight, add them up, squash to a yes/no. That "
     "is the entire unit. In notebook 3 they train one in ~10 lines to spot "
     "immune cells, and it discovers on its own that CD45 means immune "
     "(positive weight) and keratin means not immune (negative).",
     "figure"),

    ("A model cannot read letters", "tokens",
     [],
     "Text gets chopped into tokens, each token becomes a number. Have them "
     "run their OWN NAME through it in the notebook -- this always gets a "
     "reaction. Note that 1847362 becomes 18/47/362, which is genuinely why "
     "these models are bad at arithmetic and at counting letters in a word.",
     "figure"),

    ("All it does is guess the next word", "next_token",
     [],
     "THE key slide of part 3. Real GPT-2, running on their laptop. 94.6% sure "
     "the next word is 'cancer'. To write a sentence: pick one, stick it on "
     "the end, ask again. That is all writing is, for a language model. Then "
     "let them try their own prompt.",
     "figure"),

    ("Temperature: it re-weights, it does not delete", "temperature_mechanism",
     [],
     "ANSWER THE QUESTION THEY WILL ASK. Temperature is not a cutoff. The "
     "model's raw scores get DIVIDED by the temperature before being turned "
     "into probabilities. Divide by something small (<1) and the gaps get "
     "bigger, so the favorite wins even more often -- 'man' goes 45% -> 77%. "
     "Divide by something big (>1) and the gaps shrink, so long shots get a "
     "real chance -- 'man' drops to 28%. Same seven words on screen the whole "
     "time; nothing is ever removed. If someone asks what DOES remove words, "
     "that is top-k / top-p: keep the best few, throw the rest away. Different "
     "knob.",
     "figure"),

    ("Now hear the difference", "temperature_effect",
     [],
     "Same dial, on the 2024 chat model (GPT-2 is too weak -- it rambles even "
     "at low temperature). Low: fluent. Middle: fluent. High: collapses into "
     "word salad.\n\nTHEN THE REAL POINT: read the first two answers out loud. "
     "Both are confident. BOTH ARE WRONG. The sky is blue because air "
     "scatters short blue wavelengths more than long ones -- Rayleigh "
     "scattering. Answer one literally concludes the sky looks 'white or "
     "gray'. Nothing in the model noticed, because nothing in the model was "
     "checking. A confident sentence is just a LIKELY sentence. This is the "
     "most useful thing they will hear all hour -- do not rush it.",
     "figure"),

    ("How it keeps track of what words mean", "attention",
     [],
     "OPTIONAL / CUT SECOND. 'The nurse examined the patient because SHE was "
     "worried' -- who is she? Inside the model, the word 'she' literally looks "
     "back at 'nurse'. This is attention, the T in GPT. One head out of 144, "
     "picked because it shows the pattern cleanly.",
     "figure"),

    ("The ladder", None,
     ["the neuron you built            3 numbers",
      "GPT-2  (2019)                   124,000,000",
      "the chatbot you just used       500,000,000",
      "ChatGPT / Claude                ~1,000,000,000,000",
      "",
      "Same three operations all the way up: multiply, add, squash."],
     "Close part 3 here. The jump from 3 to a trillion is the only 'wow' they "
     "need. Nothing new appears -- it is the same arithmetic, repeated.",
     "bullets"),

    ("What you did today", None,
     ["Found cell types nobody had labeled.",
      "Reproduced a result from a top biology journal.",
      "Broke a classical algorithm, and saw why deep learning exists.",
      "Ran a real language model and watched it guess.",
      "",
      "All of it in Python. All of it free."],
     "End on what THEY did, not on what the tools are. Mention the notebooks "
     "stay theirs forever, and the 'if you have time' sections at the bottom "
     "of each one. Point at the stretch exercises. Take questions.",
     "bullets"),
]


def add_text(slide, text, left, top, width, height, size, color=INK,
             bold=False, align=PP_ALIGN.LEFT, spacing=1.0):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.line_spacing = spacing
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.color.rgb = color
            run.font.bold = bold
            run.font.name = FONT
    return box


def fit_picture(slide, path, top, max_h):
    """Insert an image centerd in the box below the title.

    Wide figures end up much shorter than max_h, so centring vertically as well
    as horizontally keeps them from hugging the title with a dead band beneath.
    """
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    max_w = W - Inches(1.0)
    h, w = max_h, Emu(int(max_h * iw / ih))
    if w > max_w:
        w = max_w
        h = Emu(int(max_w * ih / iw))
    slide.shapes.add_picture(str(path), Emu(int((W - w) / 2)),
                             Emu(int(top + (max_h - h) / 2)),
                             width=w, height=h)


def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    blank = prs.slide_layouts[6]

    for title, fig, body, notes, kind in DECK:
        slide = prs.slides.add_slide(blank)
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = SURFACE

        if kind == "title":
            add_text(slide, title, Inches(1), Inches(2.4), W - Inches(2),
                     Inches(1.6), 46, INK, bold=True, align=PP_ALIGN.CENTER)
            add_text(slide, "\n".join(body), Inches(1), Inches(4.1),
                     W - Inches(2), Inches(1.6), 22, INK2,
                     align=PP_ALIGN.CENTER, spacing=1.4)
        elif kind == "section":
            add_text(slide, title, Inches(1), Inches(2.7), W - Inches(2),
                     Inches(1.6), 38, BLUE, bold=True, align=PP_ALIGN.CENTER)
            add_text(slide, "\n".join(body), Inches(1), Inches(4.2),
                     W - Inches(2), Inches(1.2), 22, INK2,
                     align=PP_ALIGN.CENTER)
        elif kind == "do":
            add_text(slide, title, Inches(1), Inches(2.2), W - Inches(2),
                     Inches(1.2), 40, BLUE, bold=True, align=PP_ALIGN.CENTER)
            add_text(slide, "\n".join(body), Inches(1), Inches(3.7),
                     W - Inches(2), Inches(2.2), 24, INK,
                     align=PP_ALIGN.CENTER, spacing=1.5)
        elif kind == "figure":
            add_text(slide, title, Inches(0.6), Inches(0.32), W - Inches(1.2),
                     Inches(0.9), 30, INK, bold=True, align=PP_ALIGN.CENTER)
            fit_picture(slide, FIGS / f"{fig}.png", Inches(1.32),
                        H - Inches(1.85))
        else:   # bullets
            add_text(slide, title, Inches(0.9), Inches(0.6), W - Inches(1.8),
                     Inches(1.0), 34, INK, bold=True)
            add_text(slide, "\n".join(body), Inches(1.1), Inches(2.0),
                     W - Inches(2.2), Inches(4.6), 23, INK2, spacing=1.45)

        slide.notes_slide.notes_text_frame.text = notes

    path = OUT / "psi_ml_llm.pptx"
    prs.save(path)
    print(f"  {path.name}  ({len(DECK)} slides)")
    return len(DECK)


TIMING = """# Speaker notes — Machine Learning & Language Models

**Audience:** high school, no coding assumed.
**Nominal length:** ~60 min. Built long on purpose — see the cut list.

## Shape of the hour

| min | what |
|-----|------|
| 0–5 | Hook + what ML is (slides 1–4) |
| 5–8 | The dataset (slide 5) |
| 8–20 | **Notebook 1, Parts 1–2** — clustering + PCA (slides 6–9) |
| 20–24 | The composition null (slide 10) |
| 24–34 | **Notebook 1, Parts 3–4** — mixing score + survival (slides 11–15) |
| 34–42 | **Notebook 2** — segmentation, instructor-driven (slides 16–20) |
| 42–56 | **Notebook 3** — LLMs (slides 21–27) |
| 56–60 | Wrap (slide 28) |

## Cut list — in this order, if you are running late

1. **Slide 9 (UMAP)** — pure bonus, say the word and move on. *saves ~2 min*
2. **Slide 26 (attention)** — the concept survives without it. *saves ~4 min*
3. **Notebook 3 Part 1 (the numpy neuron)** — go straight from the neuron
   diagram to tokenization. *saves ~5 min*
4. **Notebook 2 becomes slides only** — do not run the code live, just show
   watershed_easy and watershed_hard. *saves ~5 min*
5. **Last resort: slide 10, the composition null.** It is the best scientific
   lesson in the hour, so cut it only if you must.

## Before class

- [ ] Host the four files in `data/processed/` somewhere public and put the URL
      in `DATA_URL` at the top of `code/03_build_notebooks.py`, then re-run it.
- [ ] Upload the three notebooks to Colab and shorten the links.
- [ ] Open notebook 3 once on the day — the first GPT-2 download is the slowest
      step and Colab caches nothing between sessions.
- [ ] Run `python code/04_verify.py` and confirm every check passes.

## If the wifi dies

Notebook 1 and 2 need only a 4 MB download; notebook 3 needs ~1.5 GB of model
weights. If the network is bad, present part 3 from the slides — every figure
in it is a real output from the models, so nothing is lost but the interaction.

## Numbers you will be asked about

- 41 patients imaged; **38** have both cell data and clinical follow-up.
- **33** patients are scoreable; 5 are "cold" (<250 immune cells) and set aside.
- Mixed vs walled off: **hazard ratio 5.21, p = 0.032** (log-rank p = 0.017).
- The original paper reported HR 4.97, p = 0.03 — we are reproducing it, not
  matching it to the decimal, because our cell-contact rule is simpler.
- Survival here is **overall survival**, not disease-free. Say "survival".

## Honest caveats worth saying out loud

- 38 patients is a *small* study. One or two patients moving could change the
  p-value. Real conclusions need hundreds.
- We chose the 0.26 cutoff after looking at the data. Tell them that — then
  point at the notebook exercise that tests other cutoffs.
- The segmentation images in notebook 2 are **simulated** from the real cell
  outlines, because the raw microscope channels are not in the public download.
  The difficulty is real; the pixels are not.

---

## Per-slide script

"""


def build_notes():
    lines = [TIMING]
    for i, (title, fig, body, notes, kind) in enumerate(DECK, 1):
        lines.append(f"### {i}. {title}")
        if fig:
            lines.append(f"*figure: `{fig}.png`*\n")
        if body:
            lines.append("> " + "\n> ".join(b for b in body if b) + "\n")
        lines.append(notes + "\n")
    path = OUT / "SPEAKER_NOTES.md"
    path.write_text("\n".join(lines))
    print(f"  {path.name}")


if __name__ == "__main__":
    print("presentation:")
    build()
    build_notes()
