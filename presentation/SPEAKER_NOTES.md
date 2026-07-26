# Speaker notes: Machine Learning & Language Models

**Audience:** high school, no coding assumed.
**Nominal length:** about 60 minutes. The deck is built a little long on
purpose, so the cut list below tells you what to drop if you run behind.

## Shape of the hour

| min | what |
|-----|------|
| 0 to 6 | What machine learning is, plus the four-kinds grid (slides 1 to 4) |
| 6 to 10 | Open notebook 1 (slide 5) |
| 10 to 30 | **Notebook 1**, the four examples: classify, regress, cluster, PCA (slides 6 to 9) |
| 30 to 38 | **Capstone**, engineer a feature and predict survival (slides 10 to 12) |
| 38 to 46 | **Notebook 2**, image segmentation (slides 13 to 17) |
| 46 to 58 | **Notebook 3**, language models (slides 18 to 24) |
| 58 to 60 | Wrap (slides 25 to 26) |

## Cut list, in this order, if you are running late

1. **Slide 9 (PCA / dimensionality reduction).** It has the smallest payoff of
   the four examples, so you can name it and move on. Saves about 3 minutes.
2. **Slide 24 (attention).** The language-model story holds together without it.
   Saves about 4 minutes.
3. **Notebook 3, the numpy neuron.** Jump from the neuron diagram straight to
   tokenization. Saves about 4 minutes.
4. **Notebook 2 as slides only.** Show watershed_easy and watershed_hard instead
   of running the code live. Saves about 5 minutes.
5. **Last resort, the capstone (slides 10 to 12).** This is the best science in
   the hour and the biggest payoff, so cut it only if you truly must, and if you
   do, at least show slide 12 (km_mixing) as a still image.

## Before class

- [ ] The notebooks currently point at a **local** data path for testing
      (`DATA = "../data/processed"`). Before you share them with students,
      switch each notebook's `DATA` line back to the GitHub URL, which is kept
      right above it as a comment. Otherwise Colab will not find the data.
- [ ] Open notebook 3 once on the day, because the first GPT-2 download is the
      slowest step and Colab does not cache it between sessions.
- [ ] With the GitHub URL active, run `python code/04_verify.py --live` and
      confirm every check passes.

## If the wifi dies

Notebooks 1 and 2 need only a 4 MB download, while notebook 3 also needs about
1.5 GB of model weights. If the network is bad, present the language-model
section from the slides, since every figure there is a real output from the
models, so you lose only the live interaction.

## Numbers you will be asked about

- **Classification:** about 89% on 2 markers, and **95%** on all 16 (random
  forest, 3-fold cross-validation).
- **Regression:** immune fraction versus pathologist TILs score, **R^2 = 0.66**,
  n = 25.
- 41 patients were imaged, and **38** have both cell data and clinical follow-up.
- **33** patients are scoreable; the other 5 are "cold" (fewer than 250 immune
  cells) and are set aside.
- Mixed versus walled off: **hazard ratio 5.21, p = 0.032** (log-rank p = 0.017).
- The original paper reported HR 4.97, p = 0.03. We are reproducing the finding,
  not matching it to the decimal, because our cell-contact rule is simpler.
- Survival here is **overall survival**, not disease-free survival, so say
  "survival".

## Honest caveats worth saying out loud

- 38 patients is a *small* study. One or two patients moving could change the
  p-value, and a real conclusion would need hundreds.
- We chose the 0.26 cutoff after looking at the data. Tell the students that,
  and then point them at the notebook box that tries other cutoffs.
- The segmentation images in notebook 2 are **simulated** from the real cell
  outlines, because the raw microscope channels are not in the public download.
  The difficulty is real, but the pixels are not.

---

## Per-slide script


### 1. Machine Learning & Language Models
> Teaching computers to find patterns in data

Introduce yourself briefly. Set up the hour: we will meet the four main kinds of machine learning by using each one on real cancer data, and then we will look at how a large language model works. These are two different kinds of tools, and we will treat them separately.

### 2. What is machine learning?
> Finding patterns in data, without being handed the rule.
> You never wrote down that a cat has pointy ears and whiskers.
> You just saw a few thousand cats.
> The computer learns the same way, from examples.

Keep this short. The single idea is that nobody writes the rule down. Ask the students how they would write instructions for a computer to recognize a friend's face. You cannot really do it with rules, but you can show the computer thousands of examples and let it learn the pattern, and that is what machine learning is.

### 3. Four kinds of machine learning
*figure: `ml_grid.png`*

This is the map for the whole first half, so walk through it slowly. The top row is supervised learning, where we have the correct answers, called labels, and we teach the computer to reproduce them. Supervised problems split into predicting a category, which is classification, or predicting a number, which is regression. The bottom row is unsupervised learning, where there are no labels and the computer looks for structure on its own, either by grouping things (clustering) or by simplifying them (dimensionality reduction). We will do one example of each, all on the same tumor data. Come back to this grid between examples so the students keep their bearings.

### 4. Where the data comes from
*figure: `mask_vs_phenotype.png`*

The data comes from 41 women with triple-negative breast cancer, which is an aggressive form with no targeted treatment. A machine measured 36 proteins in every cell, which comes to about 200,000 cells. Every cell was outlined and then labeled with its type, and that labeled table is what feeds all four kinds of machine learning. We will see how the images become a table in the second example.

### 5. Notebook 1: open it now
> The four kinds of machine learning,
> on 20,000 real tumor cells.
> Every cell runs on its own. Look for the 🎛️ Try it boxes.

Get everyone into notebook 1 and wait for the slowest laptop. Run the setup cell and load the cells together. Remind the students that nothing is broken or blank: they run each cell in order and then experiment with the knobs in the Try it boxes. You will drive the concepts from the slides while they follow along and play with the code.

### 6. ① Classification: predict a category
*figure: `classification.png`*

This is supervised learning. We have labels, because a biologist named every cell, so we teach the computer to reproduce them and then test it on cells it never saw. It gets about 90 percent right using two markers, and about 95 percent using all 16. The picture shows the rule it learned, which we call a decision boundary. If a cell lands in the blue region, the computer calls it a tumor cell, and that shaded boundary is the whole idea of a classifier.

### 7. ② Regression: predict a number
*figure: `regression.png`*

This is still supervised, but the answer is a number now instead of a category. A pathologist looks at each tumor and gives it a tumor-infiltrating lymphocyte score, or TILs score, from 1 to 4, based on how much immune presence they see. The question is whether the computer's automatic immune-cell count can predict that human score. The fitted line says it can, about two thirds of the way there, with an R-squared of 0.66. Regression means fitting a line and reading off a number, and this example is also the bridge from images to the clinic.

### 8. ③ Clustering: find groups with no labels
*figure: `cluster_heatmap.png`*

Now we hide the labels, which makes this unsupervised. k-means sorted 20,000 cells into 6 clusters knowing nothing about cell types. Let the students read the heatmap and name each cluster before the reveal: MPO marks neutrophils, CD20 marks B cells, CD3, CD4 and CD8 mark T cells, and the keratins mark tumor cells. The point to make is that classification reproduces labels you already have, while clustering discovers groups you did not know were there. Same data, opposite starting point.

### 9. ④ Dimensionality reduction: draw a map
*figure: `pca.png`*

This is also unsupervised. Each cell is 16 numbers, which is a point in 16-dimensional space that we cannot picture. PCA squashes those 16 numbers down to 2 while keeping the most important information, so every cell becomes a dot on a map. Tumor and immune cells land in different regions, and we add the colors afterward, so they were never used to build the map. The structure was already in the numbers. UMAP is a fancier version of the same idea that the students will run into in papers.

### 10. ⑤ Capstone: does composition predict survival?
*figure: `km_composition_null.png`*

Now we use the toolkit on the real research question. We start with a first feature, which is the mix of cell types each patient has. We cluster the patients on their cell composition and then look at survival. The two curves sit almost on top of each other and are not statistically different, so composition on its own tells us very little about survival. That is not a dead end, because it tells us we need a better feature, which sets up feature engineering on the next slides.

### 11. Same amount of immune cells, different layout
*figure: `two_patients.png`*

Both of these patients have about half immune cells, which is printed on each panel, so the difference is where those immune cells sit. On the left they are walled off in their own territory, and on the right they are mixed all through the tumor. Cell composition cannot see this difference, because the counts are the same. Ask the students how they might turn walled-off versus mixed into a single number, because that number is the feature we are about to engineer.

### 12. Feature engineering: where the cells are
*figure: `km_mixing.png`*

This is the payoff. We engineered a new feature called the mixing score, which measures how much the immune and tumor cells touch each other, and we fed it the same survival data. Patients whose immune cells were mixed into the tumor did much worse, with about 5 times the risk of dying, and the split matches the paper's published labels for all 33 scoreable patients. The lesson is that the four kinds of machine learning are the tools, and the skill is engineering the right feature to give them. We could not have found this second feature without the first one that failed.

### 13. Example 2: Bio-imaging
> Every number we just used started as a photograph.

This is the transition to the second example. All four vignettes assumed a tidy table of numbers, but somebody had to build that table from raw microscope images, and that is the job of image analysis.

### 14. Notebook 2: run it yourself
> Watershed: threshold, find the centers, flood outwards.
> Three lines of math, and no AI at all.

The students can run this one as well. The watershed method has a nice analogy: imagine each cell is a bathtub with its own shape, and we fill all the tubs with water at the same time, stopping just before they overflow, so the rising water traces the edges. In code it is three steps: threshold the bright pixels as cells, find the center of each blob, and flood outward from those centers until the floods meet. There is no neural network here, just classical image processing.

### 15. On easy cells, it works
*figure: `watershed_easy.png`*

On tidy, well-separated cells the classical method works well. There are 158 cells actually present, it finds about 177, and roughly 72 percent of the outlines are right. Old-fashioned math with no AI does the job here. Then we try it on real tissue.

### 16. On real tissue, watershed struggles
*figure: `watershed_hard.png`*

This is the same code on a real, densely packed tumor. Look at the big merged blobs, where the method glued neighboring cells together. It gets roughly the right count, but the shapes are wrong, and a wrong shape means protein gets attributed to the wrong cell. That error trickles down through the whole analysis, and we would not be able to recover the spatial feature from the first example. This is what motivates the next slide.

### 17. So they used a neural network
> The scientists trained a neural network on thousands of
> hand-drawn cell outlines, until it learned what a cell
> boundary looks like.
> It drew every one of the 200,000 outlines in our data.
> The same idea shows up in self-driving cars, radiation-therapy
> outlines, and satellite maps of forests.

The takeaway is that we did not start with deep learning, we arrived at it because the simple method broke. Real tissue needed something that could learn what a boundary looks like from many examples, and that is a neural network. Segmentation like this is really just classification run once for every pixel. Give the students a familiar example or two, such as self-driving cars or outlining tumors for radiation therapy, and then move on without going deep into how neural networks work.

### 18. Example 3: Deep learning and language models
> What is actually inside ChatGPT? Let's take one apart.

This is a hard reset to the third example. Make it clear that a language model is a different kind of tool from the machine learning we just did, and not simply a bigger version of it. A large language model is a neural network built from a huge number of connected units called neurons, sometimes billions of them.

### 19. It starts with one neuron
*figure: `neuron.png`*

A single neuron does three things: it multiplies each input by a weight, adds the results together, and squashes the total into a yes-or-no answer. That is the whole unit. In notebook 3 the students train one neuron in about ten lines to spot immune cells, which is really a tiny classifier doing the same job as the first example. A language model is this same idea repeated an enormous number of times, with billions of these weights, which we call parameters.

### 20. A model cannot read letters
*figure: `tokens.png`*

A model cannot read letters directly. Text is first chopped into pieces called tokens, and each token becomes a number. Have the students run their own name through the tokenizer in the notebook, which always gets a reaction. Point out that a number like 1847362 gets split into 18, 47 and 362, which is a real reason these models struggle with arithmetic and with counting the letters in a word.

### 21. It guesses the next token in a sequence
*figure: `next_token.png`*

This is the key idea for language models. The real GPT-2 model is running on their laptop, and here it is about 95 percent sure the next token after 'diagnosed with breast' is 'cancer'. To write a sentence, it picks a token, adds it to the end, and asks the same question again. Notice that guessing the next token out of about 50,000 options is really just classification with 50,000 categories, which ties back to the first example.

### 22. Temperature: it re-weights, it does not delete
*figure: `temperature_mechanism.png`*

This is the knob students always ask about. To add some randomness, the model divides its scores by a number called the temperature before turning them into probabilities. A temperature below 1 stretches the gaps, so the favorite token wins more often, and 'man' goes from 45 percent up to 77 percent. A temperature above 1 shrinks the gaps, so long-shot tokens get a real chance, and 'man' drops to 28 percent. The same seven tokens are on screen the whole time, so nothing is ever removed. The knob that actually removes tokens is a different one called top-k or top-p.

### 23. Turning up the temperature
*figure: `temperature_effect.png`*

This is the same dial on the newer 2024 chat model, which is coherent enough that the change is easy to see. At low temperature it is fluent, at medium it is still fluent, and at high temperature it collapses into word salad. Then make the real point: read the first two answers out loud, because both sound confident and both are wrong. The sky is blue because of Rayleigh scattering, and one answer even says the sky looks white or gray. Nothing in the model was checking whether the answer was true, because a confident sentence is just a likely sentence. This is the most useful idea the students will take away, so give it time.

### 24. How it keeps track of meaning
*figure: `attention.png`*

This slide is optional and the first thing to cut for time. In the sentence 'The nurse examined the patient because she was worried', who is she? Inside the model, the token 'she' looks back at 'nurse'. This looking-back is called attention, and it is the T in GPT. This is one attention head out of 144, chosen because it shows the pattern clearly.

### 25. The ladder
> the neuron you built            3 numbers
> GPT-2  (2019)                   124,000,000
> the chatbot you used            500,000,000
> ChatGPT / Claude                ~1,000,000,000,000
> The same three operations all the way up: multiply, add, and squash.

This closes the language-model section. The only thing that needs to land is the jump from 3 numbers to about a trillion. Nothing new appears at the top of the ladder, because it is the same arithmetic repeated an enormous number of times.

### 26. What you did today
> You met all four kinds of machine learning, and used each one.
> You engineered a feature that predicts survival.
> You broke a classic algorithm, and saw why deep learning exists.
> You ran a real language model and watched it guess.
> All in Python, all free, and all yours to keep.

End on what the students did, not on the tools. The notebooks stay theirs, so point them to the Try it boxes and the extra ideas at the bottom of each one, including asking the chatbot how many R's are in the word strawberry. Then take questions.
