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

## CLI Screenshots

These screenshots show the Python CLI running in the terminal. The first example shows a normal recommendation run, and the second shows a different profile so you can compare how the rankings change.

### CLI run

![CLI output screenshot](../images/cli.png)

### Diverse profile CLI runs

![Diverse profile CLI output screenshot 1](../images/diverse_profiles_cli.png)

![Diverse profile CLI output screenshot 2](../images/diverse_profiles_cli2.png)

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

- **6 user profiles tested** — 3 standard (High-Energy Pop, Chill Lofi, Deep Intense Rock) and 3 adversarial (Genre Ghost with a missing genre, Conflicted Soul with contradicting energy and genre, Whisper Mode at energy 0.0). Each revealed something different about which features dominate under which conditions.

- **Weight shift experiment** — Doubled `W_ENERGY` from 2.0 to 4.0 and halved `GENRE_BONUS` from 2.0 to 1.0. Energy became so dominant that songs from the wrong genre still scored near the top as long as their energy was close. Gym Hero moved up for almost every high-energy profile regardless of genre. Rankings changed noticeably but did not feel "better" — just more energy-obsessed.

- **Genre Ghost stress test** — Set genre to "country," which has no songs in the catalog. With nobody earning the +2 genre bonus, the whole ranking flattened and fell back on mood + energy + audio features. Rooftop Lights won because it matched on mood (happy) and was closest in energy — not because it was a good country song. This confirmed that genre is the single biggest differentiator in the current system.

- **Conflicted Soul test** — Set genre to "ambient" but energy to 0.95. The system completely ignored the ambient preference and returned pop and rock songs. No ambient song in the catalog has high energy, so energy similarity (weighted 2×) drowned out the genre and mood signals. The system gave back confident-looking results that made no sense for the stated profile.

---

## Limitations and Risks

- Only works on 10 songs — too small to surface real differences between many profiles
- Lofi is over-represented (3 songs vs. 1 for most other genres), giving lofi users an unfair advantage in scoring
- Genre matching is exact string matching — "indie pop" and "pop" score as completely different genres
- The user profile accepts only one genre and one mood — hybrid tastes are not supported
- No feedback loop — the system never learns from what you actually skip or replay
- Low-energy or very-high-energy users are penalized when the catalog doesn't reach their target range

See [model_card.md](model_card.md) for a deeper breakdown of each bias.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

### Profile Pair Comparisons

**High-Energy Pop vs. Chill Lofi**
These two profiles sit at opposite ends of the energy scale — one wants loud, upbeat pop (energy 0.90), the other wants quiet, mellow lofi (energy 0.35). The rankings flipped almost completely: songs that landed in the top 3 for one profile sat near the bottom for the other. This makes sense because energy similarity carries 2× weight in the score. When a song's energy is far from your target, it loses points on every song in the catalog, which is a big gap that genre or mood alone cannot close. What this shows: energy is the strongest continuous filter in the system — pick a target and the algorithm naturally clusters around that range.

**High-Energy Pop vs. Deep Intense Rock**
Both profiles want high energy (0.90 and 0.92), but they differ on genre and mood. The top results overlapped more than expected — "Gym Hero" appeared in the top 2 for both, despite being pop/intense rather than rock/intense for the rock profile. The reason is that with nearly identical energy levels, the audio features dominate, and Gym Hero's low acousticness and strong danceability make it a near-universal winner for anyone who wants loud, produced tracks. This reveals a weakness: when two users want the same energy level but different genres, the system returns suspiciously similar playlists. Genre is only worth +2 points — a strong audio feature match can easily outweigh it.

**Genre Ghost (country) vs. High-Energy Pop**
The country profile is a stress test: no song in the catalog is labeled "country," so nobody gets the +2 genre bonus. With genre knocked out entirely, the rankings fell back to mood match + energy similarity + audio features. The top result ("Rooftop Lights") won because it matched on mood (happy) and was close in energy — not because of anything genre-related. Comparing this to High-Energy Pop (where genre gave Sunrise City a decisive edge) shows exactly how much the genre bonus matters: remove it, and mood + energy together can only weakly separate songs that are fairly similar across the board.

**Conflicted Soul vs. Deep Intense Rock**
Both profiles want high energy (0.95 and 0.92), but Conflicted Soul asks for ambient genre and a relaxed mood — preferences that directly contradict each other in the catalog (ambient songs are all quiet). The result: the system completely ignored the ambient and relaxed preferences and returned the same high-energy pop and rock songs as the rock profile. This is a filter bubble. The user described themselves as an ambient/relaxed listener but got an intense pop playlist — because energy similarity, weighted at 2×, drowned out the genre and mood signals when those signals had no good match in the catalog.

**Whisper Mode vs. Chill Lofi**
Both profiles prefer acoustic sounds, but Whisper Mode sets energy to 0.0 — far below anything in the catalog (minimum: 0.28). Chill Lofi sets energy to 0.35, which closely matches the quietest songs. The difference was stark: Chill Lofi got near-perfect energy scores on Library Rain and Midnight Coding; Whisper Mode was penalized on every single song because the catalog simply doesn't have songs that quiet. The top result for Whisper Mode was Coffee Shop Stories (jazz, energy 0.37) — not because it matched the 0.0 target, but because it was the least wrong option. This shows that when a user's preference falls outside the catalog's range, the system still returns *something* without any indication that nothing is actually a good match.

### What I Learned

Building this recommender made it clear that a scoring system is not neutral — every number you choose (how much to reward genre vs. energy vs. mood) is a decision that advantages some users and disadvantages others. The lofi listener gets three genre matches; the rock listener gets one. The person who wants very quiet music gets penalized by a catalog that doesn't go that low. Real recommender systems face the same problem at a much larger scale: the training data, the feature weights, and even the mood labels all reflect choices made by people, and those choices determine whose taste the system serves well. Understanding that a "recommendation" is the output of arithmetic — not intuition — changes how you think about why an app keeps showing you the same kind of songs.




