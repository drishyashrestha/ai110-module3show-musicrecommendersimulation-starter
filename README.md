# 🎵 Music Recommender Simulation

## Project Summary

This is my **Music Recommender Simulation** (Module 3). I represent each song and a small **taste profile** as data, define a **scoring rule** that turns those into a match score, **rank** the catalog, and reflect on how that compares to real recommenders. The system is **content-based only** (no “users like you” signals): it reads `data/songs.csv`, compares each row’s features to the user’s stated genre, mood, target energy, and acoustic preference, then returns the top matches—with optional short explanations. It is for **learning and demonstration**, not a production music app.


## How The System Works

Big streaming apps mix **collaborative** signals (what similar users did), **content** (what the track is like), and **context** (time, device, session). This project is intentionally smaller: a **content-based** recommender. It compares each song’s row in the CSV to what the user asked for. There is no “people like you also listened to…” step.

**Pipeline in plain language:** read songs → build a user profile from a small dictionary → for each song compute a **numeric match score** → **sort** high to low → return the top *k*. The CLI path uses `load_songs`, `recommend_songs`, and dict rows; the class-based tests use `Song`, `UserProfile`, and `Recommender.recommend` with the same scoring idea.

**What the score emphasizes:** genre and mood matches add fixed points (genre weighted a bit higher than mood). **Energy** is scored by **closeness** to the user’s target (similar intensity wins; it is not “always pick the loudest track”). **Acoustic** taste nudges toward more or less acoustic productions. **Valence, tempo, and danceability** add smaller amounts using mood-shaped targets so extra columns in the CSV still matter without overpowering genre and mood.

### Algorithm recipe (finalized point weights)

| Rule | Points |
|------|--------|
| Genre match (exact string, case-insensitive) | +2.0 |
| Mood match | +1.0 |
| Energy similarity | 2.0 × (1 − \|song.energy − your target energy\|), max 2.0 |
| Acoustic preference | If you like acoustic: 1.5 × song.acousticness; else: 1.5 × (1 − acousticness); max 1.5 |
| Valence, tempo, danceability vs mood-based targets | 0.5 × (1 − \|difference\|) each (tempo uses BPM/200 vs a target “norm”); max 1.5 combined |

**Ranking:** total score, highest first; tie-break by song `id` (stable, predictable).

**Why genre > mood here:** In `songs.csv`, the same **mood** can appear on several rows (e.g. multiple “chill” tracks), while **genre** splits the catalog more narrowly, so I give genre a slightly larger bonus (+2 vs +1).

**Why energy is “similarity”:** The user picks a **target** energy on a 0–1 style scale; we reward tracks **near** that value, not tracks that are simply higher or lower overall.

### Potential biases and limitations (brief)

- **Tiny catalog** — A handful of genres/moods; many real-world styles are missing, so results are not representative of “all music.”
- **Who labeled the data?** Genre and mood are **subjective**; bad or inconsistent tags skew scores.
- **One genre, one mood** — The profile cannot say “I like both X and Y,” so some users are poorly modeled.
- **Weighting choices** — Favoring genre over mood (or the chosen constants) **steers** who gets recommended; different weights would change exposure across rows.
- **No feedback loop** — Unlike real apps, this system does not learn from skips or replays; it only reflects the fixed CSV and the stated prefs.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

