"""
Slide figures for the LLM section. Needs torch + transformers, so it runs on a
different interpreter from 01_make_figures.py:

    /Users/cramere/miniforge3/envs/cellcharter-env/bin/python code/01b_make_llm_figures.py

Downloads gpt2 (~550 MB) from HuggingFace on first run. No account or token is
needed for public models.
"""

import numpy as np
import matplotlib.pyplot as plt
import torch
from matplotlib.patches import FancyBboxPatch
from transformers import AutoModelForCausalLM, AutoTokenizer

import psiclass as P
from psiclass import BLUE, ORANGE, INK, INK2, MUTED, SURFACE

P.use_slide_style()
P.FIGS.mkdir(parents=True, exist_ok=True)

PROMPT = "The patient was diagnosed with breast"
# For the temperature figure we need a prompt the model is genuinely UNSURE
# about. "...diagnosed with breast" is 95% "cancer", so reweighting it shows
# nothing. This one spreads across many plausible words (entropy 5.6 vs 0.5).
SPREAD_PROMPT = "She opened the door and saw a"
# Layer 10 / head 6 is a coreference head: "she" looks back at "nurse". Found by
# scanning all 144 heads for the one with the strongest off-diagonal structure
# once the attention-sink column is removed. Most heads just stare at token 0,
# which teaches nothing.
ATTN_SENTENCE = "The nurse examined the patient because she was worried"
ATTN_LAYER, ATTN_HEAD = 10, 6


def save(fig, name):
    fig.savefig(P.FIGS / f"{name}.png")
    plt.close(fig)
    print(f"  {name}.png")


def fig_next_token(tok, model):
    ids = tok(PROMPT, return_tensors="pt")
    with torch.no_grad():
        logits = model(**ids).logits[0, -1]
    probs = torch.softmax(logits, -1)
    top = torch.topk(probs, 8)
    words = [tok.decode(i).strip() or "␣" for i in top.indices]
    vals = top.values.numpy()

    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(words))[::-1]
    # One series, so one color -- and only the winner is emphasised.
    colors = [BLUE if v == vals.max() else "#b7d3f6" for v in vals]
    ax.barh(y, vals, height=0.62, color=colors, linewidth=0)
    for yi, w, v in zip(y, words, vals):
        ax.text(v + 0.012, yi, f"{v:.1%}", va="center", fontsize=17,
                color=INK if v == vals.max() else INK2)
    ax.set_yticks(y); ax.set_yticklabels(words, fontsize=19)
    ax.set_xlim(0, 1.08); ax.set_xticks([])
    ax.grid(False)
    ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(False)
    ax.set_title(f'"{PROMPT} ___"\nWhat comes next?', fontsize=22, pad=16)
    save(fig, "next_token")


def fig_temperature_mechanism(tok, model):
    """What temperature actually DOES: softmax(logits / T).

    Deterministic -- no sampling, so the slide never changes between runs. The
    point students must not miss is that nothing gets cut off; the same
    candidates are simply reweighted. (Cutting off candidates is top-k / top-p,
    a different knob entirely.)
    """
    ids = tok(SPREAD_PROMPT, return_tensors="pt")
    with torch.no_grad():
        logits = model(**ids).logits[0, -1]
    keep = torch.topk(torch.softmax(logits, -1), 7).indices
    words = [tok.decode(i).strip() for i in keep]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), sharey=True)
    for ax, temp in zip(axes, [0.5, 1.0, 2.0]):
        p = torch.softmax(logits / temp, -1)[keep]
        # Shown as each word's share OF THESE SEVEN. In absolute terms a high
        # temperature also bleeds mass out to the other ~50,000 tokens, which
        # would render all seven bars as "0%" and teach nothing. The shape
        # change -- peaked to flat -- is the concept.
        probs = (p / p.sum()).numpy()
        y = np.arange(len(words))[::-1]
        ax.barh(y, probs, height=0.6, color=BLUE, linewidth=0)
        for yi, v in zip(y, probs):
            ax.text(v + 0.015, yi, f"{v:.0%}", va="center", fontsize=15,
                    color=INK2)
        ax.set_yticks(y); ax.set_yticklabels(words, fontsize=17)
        ax.set_xlim(0, 1.0); ax.set_xticks([]); ax.grid(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        note = {0.5: "picks the favorite\nalmost every time",
                1.0: "the model's own odds",
                2.0: "long shots get a\nreal chance"}[temp]
        ax.set_title(f"temperature {temp}\n", fontsize=20, color=BLUE,
                     fontweight="bold")
        ax.text(0.5, -0.13, note, transform=ax.transAxes, ha="center",
                va="top", fontsize=15, color=INK2, linespacing=1.4)

    fig.suptitle(f'"{SPREAD_PROMPT} ___"      '
                 "Same seven words. Different odds. Nothing is ever removed.",
                 fontsize=19, y=1.02)
    fig.tight_layout()
    save(fig, "temperature_mechanism")


def fig_temperature_effect():
    """Real Qwen output at three temperatures.

    GPT-2 is too weak for this: it rambles even at temperature 0.2, so the
    "safe -> creative -> nonsense" arc has no "safe" end. Qwen2.5-0.5B is
    coherent at low temperature, which is what makes the contrast legible.
    Both of its fluent answers happen to be scientifically WRONG, which is the
    hallucination lesson handed to us for free -- see the speaker notes.
    """
    name = "Qwen/Qwen2.5-0.5B-Instruct"
    qt = AutoTokenizer.from_pretrained(name)
    qm = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32)
    prompt = "In one sentence, why is the sky blue?"
    text = qt.apply_chat_template([{"role": "user", "content": prompt}],
                                  tokenize=False, add_generation_prompt=True)
    ids = qt(text, return_tensors="pt")

    # Seed 3 is chosen so the temperature-1.8 collapse comes out ~98% Latin
    # script. Other seeds produce CJK and Thai tokens, which render as empty
    # boxes in the slide font and read as a broken figure rather than as the
    # intended garbage.
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.0))
    for ax, temp in zip(axes, [0.3, 1.0, 1.8]):
        torch.manual_seed(3)
        out = qm.generate(**ids, max_new_tokens=42, do_sample=True,
                          temperature=temp, top_k=0, top_p=1.0)
        txt = qt.decode(out[0][ids.input_ids.shape[1]:],
                        skip_special_tokens=True).strip()
        ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                    boxstyle="round,pad=0.01",
                                    facecolor="#f4f3ef", edgecolor="none"))
        ax.text(0.07, 0.90, f"temperature {temp}", fontsize=18, color=BLUE,
                fontweight="bold", va="top")
        ax.text(0.07, 0.74, _wrap(txt, 30), fontsize=14, color=INK, va="top",
                linespacing=1.65)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.axis("off"); ax.grid(False)
    fig.suptitle('"Why is the sky blue?"       '
                 "fluent  ...  still fluent  ...  collapse", fontsize=21)
    save(fig, "temperature_effect")


def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return "\n".join(lines[:9])


def fig_tokens(tok):
    examples = ["Machine learning", "unbelievable", "1847362", "Aoife"]
    fig, ax = plt.subplots(figsize=(12, 5.6))
    palette = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5"]
    for row, text in enumerate(examples):
        y = len(examples) - row - 1
        pieces = [tok.decode([i]) for i in tok(text).input_ids]
        x = 0.0
        ax.text(-0.02, y, f'"{text}"', fontsize=18, ha="right", va="center",
                color=INK2)
        for k, piece in enumerate(pieces):
            w = max(len(piece) * 0.052, 0.05)
            ax.add_patch(FancyBboxPatch((x, y - 0.3), w - 0.008, 0.6,
                                        boxstyle="round,pad=0.004",
                                        facecolor=palette[k % len(palette)],
                                        edgecolor="none"))
            ax.text(x + w / 2, y, piece.replace(" ", "␣"), ha="center",
                    va="center", fontsize=15, color=INK)
            x += w
        ax.text(x + 0.02, y, f"{len(pieces)} token"
                             f"{'s' if len(pieces) != 1 else ''}",
                fontsize=16, va="center", color=MUTED)
    ax.set_xlim(-0.55, 1.5); ax.set_ylim(-0.7, len(examples) - 0.3)
    ax.axis("off"); ax.grid(False)
    ax.set_title("The model never sees letters — only these chunks",
                 fontsize=22, pad=14)
    save(fig, "tokens")


def fig_attention(tok, model):
    ids = tok(ATTN_SENTENCE, return_tensors="pt")
    with torch.no_grad():
        out = model(**ids, output_attentions=True)
    toks = [tok.decode(t).strip() for t in ids.input_ids[0]]
    A = out.attentions[ATTN_LAYER][0, ATTN_HEAD].numpy().copy()
    A[:, 0] = 0                          # drop the attention-sink column
    A /= np.clip(A.sum(1, keepdims=True), 1e-9, None)

    fig, ax = plt.subplots(figsize=(9.5, 8))
    im = ax.imshow(A, cmap=P.SEQUENTIAL, vmin=0, vmax=A.max())
    ax.set_xticks(range(len(toks))); ax.set_xticklabels(toks, rotation=45,
                                                        ha="right")
    ax.set_yticks(range(len(toks))); ax.set_yticklabels(toks)
    ax.set_xlabel("...looks back at this word"); ax.set_ylabel("This word...")
    ax.grid(False)
    j = int(A[toks.index("she")].argmax())
    ax.add_patch(plt.Rectangle((j - 0.5, toks.index("she") - 0.5), 1, 1,
                               fill=False, edgecolor=ORANGE, linewidth=3))
    ax.set_title(f'"she" is looking at "{toks[j]}"\n'
                 f'(layer {ATTN_LAYER}, head {ATTN_HEAD})', fontsize=21, pad=14)
    cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
    cb.set_label("attention", fontsize=16); cb.outline.set_visible(False)
    save(fig, "attention")


def main():
    print("loading gpt2 ...")
    tok = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2",
                                                 attn_implementation="eager")
    model.eval()
    print("figures:")
    fig_next_token(tok, model)
    fig_tokens(tok)
    fig_temperature_mechanism(tok, model)
    fig_attention(tok, model)
    print("loading Qwen2.5-0.5B-Instruct ...")
    fig_temperature_effect()


if __name__ == "__main__":
    main()
