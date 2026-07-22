# Speaker notes — Machine Learning & Language Models

**Audience:** high school, no coding assumed.
**Nominal length:** ~60 min. Built long on purpose — see the cut list.

## Shape of the hour

| min | what |
|-----|------|
| 0–6 | What ML is + the four-kinds grid (slides 1–4) |
| 6–10 | Open notebook 1 (slide 5) |
| 10–30 | **Notebook 1** — the four vignettes: classify, regress, cluster, PCA (slides 6–9) |
| 30–38 | **Capstone** — invent a feature, predict survival (slides 10–12) |
| 38–46 | **Notebook 2** — image segmentation (slides 13–17) |
| 46–58 | **Notebook 3** — language models (slides 18–24) |
| 58–60 | Wrap (slide 25) |

## Cut list — in this order, if you are running late

1. **Slide 9 (PCA / dimensionality reduction)** — the weakest-payoff of the four
   vignettes; name it and move on. *saves ~3 min*
2. **Slide 23 (attention)** — the LLM story survives without it. *saves ~4 min*
3. **Notebook 3 Part 1 (the numpy neuron)** — jump from the neuron diagram
   straight to tokenization. *saves ~4 min*
4. **Notebook 2 becomes slides only** — show watershed_easy / watershed_hard
   instead of running it live. *saves ~5 min*
5. **Last resort: the capstone (slides 10–12).** It's the best science in the
   hour and the biggest wow, so cut it only if you truly must — and if you do,
   at least show slide 12 (km_mixing) as a still.

## Before class

- [ ] Notebooks pull data from the public GitHub repo already — just share the
      Colab links (badges in the README).
- [ ] Open notebook 3 once on the day — the first GPT-2 download is the slowest
      step and Colab caches nothing between sessions.
- [ ] Run `python code/04_verify.py --live` and confirm every check passes.

## If the wifi dies

Notebook 1 and 2 need only a 4 MB download; notebook 3 needs ~1.5 GB of model
weights. If the network is bad, present part 3 from the slides — every figure
in it is a real output from the models, so nothing is lost but the interaction.

## Numbers you will be asked about

- **Classification:** ~89% on 2 markers, **95%** on all 16 (random forest, 3-fold CV).
- **Regression:** immune fraction vs pathologist TIL score, **R² = 0.66**, n = 25.
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


### 1. Machine Learning & Language Models
> Teaching computers to find patterns —
> then taking a language model apart.

Introduce yourself in 20 seconds. Frame the hour: first we meet the four main kinds of machine learning by using them on real cancer data, then we look at how a language model works. Two different tools.

### 2. What is machine learning?
> Finding patterns in data — without being handed the rule.
> You never wrote down 'a cat has pointy ears and whiskers.'
> You saw a few thousand cats.
> The computer learns the same way: from examples.

Keep this short. The one idea: nobody writes the rule down. Ask how you'd write instructions to recognize a friend's face -- you can't, but you can show 10,000 examples. That's ML.

### 3. Four kinds of machine learning
*figure: `ml_grid.png`*

THE BACKBONE SLIDE. Walk the 2x2 slowly. Top row SUPERVISED = you have the answers and teach the computer to copy them; splits into predicting a CATEGORY (classification) or a NUMBER (regression). Bottom row UNSUPERVISED = no answers, find structure yourself; either group things (clustering) or simplify them (dimensionality reduction). We'll do one example of each, all on the same tumor data. Come back to this grid between vignettes so they never lose the map.

### 4. Where the data comes from
*figure: `mask_vs_phenotype.png`*

41 women with triple-negative breast cancer -- the aggressive kind with no targeted treatment. A machine measured 36 proteins in every cell. ~200,000 cells. Every cell was outlined and labeled. That labeled table is what feeds all four kinds of ML.

### 5. Notebook 1 — open it now
> The four kinds of machine learning,
> on 20,000 real tumor cells.
> Everything runs as-is. Look for the 🎛️ Try it boxes.

Get everyone into notebook 1. Wait for the slowest laptop. Run the setup and load cells together. Emphasize: nothing is broken or blank -- they run cells and then tinker with the knobs. You'll drive the concepts from the slides while they follow along and play.

### 6. ① Classification — predict a category
*figure: `classification.png`*

SUPERVISED. We HAVE labels (a biologist named every cell), so we teach the computer to copy them, then test on cells it never saw: ~90% right. The picture is the rule it learned on two markers -- land in the blue zone, it calls you a tumor cell. That shaded boundary IS the classifier. The full 16-marker model hits 95%.

### 7. ② Regression — predict a number
*figure: `regression.png`*

Still supervised, but the answer is a NUMBER now, not a category. A pathologist eyeballs each tumor and gives an immune score 1-4. Can the computer's automatic immune-cell count predict that human score? The fitted line says yes, about two-thirds of the way (R^2 = 0.66). Regression = fit a line, read off a number. This is also the bridge from images to the clinic.

### 8. ③ Clustering — find groups with no answer key
*figure: `cluster_heatmap.png`*

Now HIDE the labels -- unsupervised. k-means sorted 20,000 cells into 6 piles knowing nothing. Let them read the heatmap and guess before the reveal: MPO = neutrophils, CD20 = B cells, CD3/CD4/CD8 = T cells, keratins = tumor. The punchline: classification COPIES labels you have; clustering DISCOVERS groups you don't. Same data, opposite philosophy.

### 9. ④ Dimensionality reduction — draw a map
*figure: `pca.png`*

Still unsupervised. Each cell is 16 numbers; PCA squashes them to 2 so every cell becomes a dot on a map. Tumor and immune land in different regions -- and the colors were painted on AFTER, never used to build the map. The structure was already in the numbers. (UMAP is the fancier version they'll see in papers.)

### 10. ⑤ Capstone: which cells? Doesn't matter.
*figure: `km_composition_null.png`*

Now we USE the toolkit on the real question. First an honest failure. Cluster patients by WHICH cells they have, then look at survival: the lines sit on top of each other, p = 0.18. Composition tells us nothing. Say plainly -- a negative result is a real result, and it's a clue.

### 11. Same amount of immune cells, different layout
*figure: `two_patients.png`*

Both patients are ~50% immune -- printed right there. But left, the immune cells are walled off in their own territory; right, they're mixed through the tumor. Composition can't see this. Ask: how would you turn 'walled off vs mixed' into a single number?

### 12. Where the cells are — that DOES predict survival
*figure: `km_mixing.png`*

THE PAYOFF. We invented a feature -- the mixing score -- and fed it the same survival data. 5.2x the risk of dying, p = 0.032, and it matches the paper's published labels 33/33. Which cells you have: nothing. Where they are: everything. The four kinds are the tools; the art is feeding them the right number. Pause here.

### 13. Part 2 — How do you get numbers out of a picture?
> Every number we just used started as a photograph.

Transition. All four vignettes assumed a tidy table. Somebody had to build that table from raw images.

### 14. Notebook 2 — run it yourself
> Threshold → find centers → flood outwards
> Three lines of math. No AI at all.

They can run this one too. Threshold: bright = cell. Distance transform: find each blob's middle. Watershed: pour water from each center until the floods meet. Classic image processing, no neural net.

### 15. On easy cells, it works
*figure: `watershed_easy.png`*

158 cells really there, ~177 found, 72% of outlines right. Old-fashioned math, no AI, works fine on tidy cells. Now the real thing.

### 16. On real tissue, it falls apart
*figure: `watershed_hard.png`*

Same code, real densely-packed tumor. Look at the big merged blobs -- it glued neighbors together. Roughly the right COUNT, but the SHAPES are wrong, and every measurement from a wrong shape is wrong too. THIS earns the next slide.

### 17. So they used a neural network
> Trained on thousands of hand-drawn cell outlines.
> It learned what a cell boundary looks like.
> Every one of the 200,000 outlines you used came from that model.
> Same idea as: face unlock · reading a check · tumor outlines for radiotherapy

Land it: we didn't start with deep learning, we EARNED it -- the simple method broke, so they needed something that learns boundaries from examples. That is itself supervised classification, run once per pixel. Give a familiar example or two and move on; don't rabbit-hole on CNNs.

### 18. Part 3 — What is actually inside ChatGPT?
> A different tool. Let's take one apart.

Hard reset. This is a separate tool from the ML we just did, not a bigger version of it. Switching topics.

### 19. It starts with one neuron
*figure: `neuron.png`*

Multiply each input by a weight, add them up, squash to a yes/no. That's the whole unit. In notebook 3 they train one in ~10 lines to spot immune cells -- and notice, that's a tiny CLASSIFIER, the same job as vignette 1. A language model is this, ~100 billion times over.

### 20. A model cannot read letters
*figure: `tokens.png`*

Text is chopped into tokens, each token becomes a number. Have them run their OWN NAME through it in the notebook -- always gets a reaction. Note 1847362 becomes 18/47/362, which is genuinely why these models fumble arithmetic and letter-counting.

### 21. All it does is guess the next word
*figure: `next_token.png`*

THE key LLM slide. Real GPT-2 on their laptop: 94.6% sure the next word is 'cancer'. To write, it picks one, appends it, asks again. That's all writing is for a language model. (Notice: guess the next word out of 50,000 options is just... classification with 50,000 categories.)

### 22. Temperature: it re-weights, it does not delete
*figure: `temperature_mechanism.png`*

The knob students always ask about. The raw scores get DIVIDED by the temperature before becoming probabilities. Small (<1): gaps grow, the favorite wins more -- 'man' 45% -> 77%. Big (>1): gaps shrink, long shots get a chance -- down to 28%. Same seven words the whole time; nothing is removed. (What DOES remove words is top-k / top-p -- a different knob.)

### 23. Now hear the difference
*figure: `temperature_effect.png`*

Same dial on the 2024 chat model (GPT-2 rambles even when cold). Low: fluent. Middle: fluent. High: word salad. THEN THE REAL POINT: read the first two answers aloud -- both confident, BOTH WRONG (the sky is blue from Rayleigh scattering; answer one literally says 'white or gray'). Nothing in the model was checking. A confident sentence is just a LIKELY sentence. Most important thing they hear all hour -- don't rush it.

### 24. How it keeps track of meaning
*figure: `attention.png`*

OPTIONAL / CUT FIRST. 'The nurse examined the patient because SHE was worried' -- who is she? Inside the model, 'she' literally looks back at 'nurse'. That's attention, the T in GPT. One head out of 144, picked because it shows the pattern cleanly.

### 25. The ladder
> the neuron you built            3 numbers
> GPT-2  (2019)                   124,000,000
> the chatbot you used            500,000,000
> ChatGPT / Claude                ~1,000,000,000,000
> Same three operations all the way up: multiply, add, squash.

Close part 3. The jump from 3 to a trillion is the only 'wow' needed. Nothing new appears at the top -- same arithmetic, repeated.

### 26. What you did today
> Met all four kinds of machine learning — and used each one.
> Invented a feature that predicts survival.
> Broke a classic algorithm, and saw why deep learning exists.
> Ran a real language model and watched it guess.
> All in Python. All free. All yours to keep.

End on what THEY did. The notebooks stay theirs -- point at the 🎛️ Try it boxes and the stretch bits at the bottom of each. Take questions.
