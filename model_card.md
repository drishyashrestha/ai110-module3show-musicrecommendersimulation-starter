# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

A content-based music recommender that matches songs to a listener's stated genre, mood, energy level, and acoustic preference using a weighted scoring formula.

---

## 2. Intended Use

**What it does:** VibeMatch reads a small catalog of songs and suggests the top 5 that best fit a user's taste profile. It explains why each song was chosen in plain language.

**Who it is for:** This is a classroom learning tool built for AI 110, Module 3. It is not a real app and is not meant for actual music listeners.

**What it assumes:** It assumes the user can describe their taste with a single genre, a single mood, a target energy level (0.0 to 1.0), and a yes/no preference for acoustic sound. Real listeners are more complex than that.

**What it should NOT be used for:** Do not use this system to make decisions for real users. It has a 10-song catalog, no user feedback loop, no collaborative signals, and no understanding of lyrics or cultural context. Using it to drive real recommendations would give poor and potentially biased results.

---

## 3. How the Model Works

Every song in the catalog gets a numeric score based on how well it matches the user's preferences. The song with the highest score is recommended first.

Here is how points are awarded:

- **Genre match:** If the song's genre exactly matches what the user said they like, it gets +2 points. This is the biggest single bonus in the system.
- **Mood match:** If the song's mood matches the user's preferred mood, it gets +1 point.
- **Energy closeness:** The user picks a target energy level between 0 (very quiet) and 1 (very loud). A song gets up to 2 points depending on how close its energy is to that target. A perfect match earns the full 2 points; a song that's far away earns less.
- **Acoustic preference:** If the user likes acoustic music, songs that sound more acoustic earn more points (up to 1.5). If the user prefers produced, electric, or studio-heavy sound, then less-acoustic songs earn more.
- **Valence, tempo, and danceability:** Each of these adds a small amount (up to 0.5 points each) based on targets that are linked to the user's mood. For example, a "happy" mood profile expects higher valence and danceability than a "chill" profile.

Once every song has a score, the system sorts them from highest to lowest and returns the top 5. If two songs tie on score, the one with the lower catalog ID comes first, which keeps results consistent.

---

## 4. Data

The catalog is `data/songs.csv` — a file with 10 songs.

Each song has these fields: a unique ID, title, artist, genre, mood, energy (0.0–1.0), tempo in BPM, valence (how "positive" the song sounds, 0.0–1.0), danceability (0.0–1.0), and acousticness (0.0–1.0).

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop.

**Moods represented:** happy, chill, intense, relaxed, moody, focused.

**What is missing:** No country, hip-hop, R&B, classical, Latin, electronic dance music, or metal. No songs in languages other than English are represented. The catalog heavily reflects one narrow slice of Western popular music. Lofi has 3 songs (30% of the catalog), while rock, jazz, ambient, synthwave, and indie pop each have only 1.

Genre and mood labels were assigned by hand. Two people might label the same song differently, and the system has no way to handle that disagreement.

---

## 5. Strengths

**It works well when the user matches the catalog.** If you ask for pop/happy or lofi/chill, those genres have multiple songs with matching moods, so the top results feel right. The scoring rewards both categorical match (genre, mood) and numeric closeness (energy), which is a reasonable balance.

**The energy-by-closeness approach is intuitive.** Rather than always picking the loudest or most intense song, the system rewards songs that are near the user's target. A user who wants medium energy (0.5) gets different results than one who wants high energy (0.9), which is correct behavior.

**Explanations make the score transparent.** Every recommendation comes with a plain-English reason: "Genre match (+2 pts). Energy very close to target (similarity 92%, +1.84 pts)." A user can see exactly why a song was chosen, which real streaming apps rarely show.

**Results are stable and predictable.** The same profile always returns the same results because there is no randomness. This makes it easy to test and compare.

---

## 6. Limitations and Bias

**Genre depth creates a filter bubble for lofi users.** The catalog contains 3 lofi songs but only 1 each of rock, jazz, ambient, and synthwave. Because genre match awards a fixed +2.0 bonus, a lofi/chill user has three separate songs that can each earn that bonus, giving them far more high-scoring options than, for example, a rock/intense user who has exactly one genre-matching song (Storm Runner) and is ranked almost entirely by audio features after that.

**"indie pop" is treated as a completely different genre from "pop."** The scoring logic uses exact string matching after lowercasing, so Rooftop Lights (genre = "indie pop") earns zero genre bonus for a user whose favorite genre is "pop," even though the two are closely related styles. This is a labeling bias — the system's fairness depends entirely on whoever wrote the genre tags in the CSV, not on any musical reality.

**Low-energy users are structurally disadvantaged.** The energy similarity formula `1 − |song.energy − target|` is linear with no floor adjustment for catalog gaps. The quietest song in the catalog (Spacewalk Thoughts) has energy 0.28, meaning a user who wants energy 0.0 can never score above 1.44 out of a possible 2.0 on that component. A user targeting energy 0.5 can reach near-perfect energy scores. Extreme preferences — very low or very high energy — are penalized not because the songs are bad matches, but simply because the catalog does not extend to those ranges.

**The user profile forces one mood and one genre, ignoring hybrid tastes.** A listener who genuinely enjoys both jazz and lofi, or who shifts between "chill" and "focused" depending on the day, must be collapsed into a single label. Whichever preference is left out scores zero on the categorical bonuses for every song in the catalog, making the system a poor model for real listening behavior.

**Rare moods have almost no representation.** The moods "relaxed," "moody," and "focused" each appear on only one song in the catalog. A user whose favorite mood is "moody" can earn the +1.0 mood bonus on exactly one track (Night Drive Loop) and is evaluated purely on audio features for the remaining nine — effectively turning mood matching off for those users.

---

## 7. Evaluation

I tested six user profiles across two categories — three standard profiles designed to match real listener types, and three adversarial profiles designed to expose weaknesses in the scoring logic.

**Standard profiles tested:**
- *High-Energy Pop* — genre: pop, mood: happy, energy: 0.90, dislikes acoustic
- *Chill Lofi* — genre: lofi, mood: chill, energy: 0.35, likes acoustic
- *Deep Intense Rock* — genre: rock, mood: intense, energy: 0.92, dislikes acoustic

**Adversarial profiles tested:**
- *Genre Ghost* — genre: country (not in catalog), mood: happy, energy: 0.70, likes acoustic
- *Conflicted Soul* — genre: ambient, mood: relaxed, energy: 0.95, dislikes acoustic
- *Whisper Mode* — genre: jazz, mood: focused, energy: 0.0, likes acoustic

**What I looked for:** For each profile I checked whether the top result made intuitive sense — did the song the system ranked #1 match what a real person with those preferences would actually want? I also looked at what showed up in positions #3–5, since those reveal which features are driving rankings once the obvious matches are gone.

**What matched expectations:** High-Energy Pop correctly ranked "Sunrise City" first — it matched on genre, mood, and was close in energy. Chill Lofi correctly surfaced lofi tracks with high acousticness. Deep Intense Rock correctly put "Storm Runner" at #1 as the only rock/intense song in the catalog.

**What surprised me:** Two things were unexpected. First, "Gym Hero" (pop, *intense*) consistently appeared in the top 2 for High-Energy Pop, even though the user asked for a *happy* mood — not intense. The reason is that Gym Hero nearly matches on energy (0.93 vs 0.90 target), has very low acousticness, and gets the genre bonus, so the audio features almost fully compensated for the mood mismatch. Second, in the Conflicted Soul profile (ambient genre, energy 0.95), the system completely ignored the ambient preference and returned high-energy pop and rock songs — because no ambient songs in the catalog have high energy, and energy similarity at twice the weight of genre outcompeted everything else.

**Tests run:** Two automated tests in `tests/test_recommender.py` verify that the highest-scoring song ranks first and that explanations are non-empty. I also ran a weight-shift experiment (doubling `W_ENERGY` from 2.0 to 4.0 and halving `GENRE_BONUS` from 2.0 to 1.0) to observe how sensitive the rankings were to scoring choices.

---

## 8. Future Work

**Support multiple genres and moods per profile.** Right now the user picks one genre and one mood. Adding support for a list — "I like both jazz and lofi" or "I'm okay with happy or chill" — would make the profile far more realistic. The genre and mood bonuses could be awarded if the song matches any item in the list.

**Add a diversity filter.** When the top 5 results all come from the same genre (as happens for lofi/chill users), the playlist feels repetitive. A simple fix would be to limit how many songs from the same genre can appear in the top results — for example, no more than 2 songs per genre — so the list exposes the user to variety even if their favorite genre dominates the scores.

**Expand the catalog significantly and balance it.** Ten songs is too few to surface meaningful differences between profiles. A catalog of 50–100 songs with at least 3–5 tracks per genre and mood would make the recommendations more interesting and reduce the structural advantage that lofi currently has. It would also allow testing with underrepresented moods like "relaxed" and "moody" that currently have almost no depth.

---

## 9. Personal Reflection

My biggest learning moment was realizing that the weights I picked  like giving genre +2 and mood only +1 which were not neutral. They were choices, and those choices decided who the system worked well for. A lofi user got great results because there were 3 lofi songs. A rock user was basically stuck after Storm Runner. I did not think about that until I actually ran it.

The most surprising thing was how "real" the recommendations felt even though it was just addition and subtraction. When the top result matched exactly what I expected, it felt like the system understood me. It didn't — it just did math that happened to align with my intuition. That gap between "feels smart" and "is actually smart" is something I'll think about every time I use Spotify now.

If I kept going with this, I'd want to let users pick more than one genre or mood. Most people don't fit into one box, and forcing them to pick one is probably the biggest reason the system gets things wrong.
