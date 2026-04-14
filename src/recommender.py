from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Algorithm recipe (see README): genre > mood; energy by closeness; lighter audio terms.
GENRE_BONUS = 2.0
MOOD_BONUS = 1.0
W_ENERGY = 2.0
W_ACOUSTIC = 1.5
W_VALENCE = 0.5
W_TEMPO = 0.5
W_DANCEABILITY = 0.5

_MOOD_TARGETS: Dict[str, Dict[str, float]] = {
    "happy": {"valence": 0.85, "tempo_norm": 0.62, "danceability": 0.78},
    "chill": {"valence": 0.62, "tempo_norm": 0.38, "danceability": 0.58},
    "intense": {"valence": 0.55, "tempo_norm": 0.76, "danceability": 0.70},
    "relaxed": {"valence": 0.72, "tempo_norm": 0.45, "danceability": 0.54},
    "moody": {"valence": 0.50, "tempo_norm": 0.55, "danceability": 0.70},
    "focused": {"valence": 0.60, "tempo_norm": 0.40, "danceability": 0.60},
}

_DEFAULT_MOOD_TARGET = {"valence": 0.65, "tempo_norm": 0.50, "danceability": 0.60}
_TEMPO_NORM_DIVISOR = 200.0


def _mood_targets(mood: str) -> Dict[str, float]:
    """Return valence/tempo_norm/danceability targets for a user mood label."""
    return dict(_MOOD_TARGETS.get(mood.strip().lower(), _DEFAULT_MOOD_TARGET))


@dataclass
class Song:
    """Represents a song and its attributes (tests)."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """User taste preferences (tests)."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def song_from_dict(row: Dict[str, Any]) -> Song:
    """Build a Song from one CSV row dict (normalized strings, typed numbers)."""
    return Song(
        id=int(row["id"]),
        title=str(row["title"]),
        artist=str(row["artist"]),
        genre=str(row["genre"]).strip().lower(),
        mood=str(row["mood"]).strip().lower(),
        energy=float(row["energy"]),
        tempo_bpm=float(row["tempo_bpm"]),
        valence=float(row["valence"]),
        danceability=float(row["danceability"]),
        acousticness=float(row["acousticness"]),
    )


def user_prefs_to_profile(user_prefs: Dict[str, Any]) -> UserProfile:
    """Map CLI-style prefs dict (genre, mood, energy, likes_acoustic) to UserProfile."""
    return UserProfile(
        favorite_genre=str(user_prefs.get("genre", "")).strip().lower(),
        favorite_mood=str(user_prefs.get("mood", "")).strip().lower(),
        target_energy=float(user_prefs["energy"]),
        likes_acoustic=bool(user_prefs.get("likes_acoustic", False)),
    )


def _score_parts(user: UserProfile, song: Song) -> Tuple[float, Dict[str, float]]:
    """Compute total score and per-component point breakdown for explainability."""
    parts: Dict[str, float] = {}

    g = song.genre.strip().lower()
    m = song.mood.strip().lower()
    fg = user.favorite_genre.strip().lower()
    fm = user.favorite_mood.strip().lower()

    parts["genre_match"] = GENRE_BONUS if g == fg else 0.0
    parts["mood_match"] = MOOD_BONUS if m == fm else 0.0

    energy_sim = 1.0 - abs(song.energy - user.target_energy)
    parts["energy"] = W_ENERGY * energy_sim

    if user.likes_acoustic:
        parts["acoustic"] = W_ACOUSTIC * song.acousticness
    else:
        parts["acoustic"] = W_ACOUSTIC * (1.0 - song.acousticness)

    mt = _mood_targets(user.favorite_mood)
    valence_sim = 1.0 - abs(song.valence - mt["valence"])
    parts["valence"] = W_VALENCE * valence_sim

    tempo_norm = song.tempo_bpm / _TEMPO_NORM_DIVISOR
    tempo_sim = 1.0 - abs(tempo_norm - mt["tempo_norm"])
    parts["tempo"] = W_TEMPO * tempo_sim

    dance_sim = 1.0 - abs(song.danceability - mt["danceability"])
    parts["danceability"] = W_DANCEABILITY * dance_sim

    return sum(parts.values()), parts


def score_song(user: UserProfile, song: Song) -> float:
    """Return total content-based match score for one user-song pair (higher is better)."""
    total, _ = _score_parts(user, song)
    return total


def explain_recommendation(user: UserProfile, song: Song) -> str:
    """Return a short natural-language summary of why the song scored as it did."""
    _, parts = _score_parts(user, song)
    reasons: List[str] = []

    if parts["genre_match"] > 0:
        reasons.append(f"Genre match (+{GENRE_BONUS:g} pts).")
    if parts["mood_match"] > 0:
        reasons.append(f"Mood match (+{MOOD_BONUS:g} pts).")

    energy_sim = parts["energy"] / W_ENERGY if W_ENERGY else 0.0
    if energy_sim >= 0.85:
        reasons.append(
            f"Energy very close to target (similarity {energy_sim:.0%}, +{parts['energy']:.2f} pts)."
        )
    elif energy_sim >= 0.55:
        reasons.append(
            f"Energy reasonably close to target (similarity {energy_sim:.0%}, +{parts['energy']:.2f} pts)."
        )
    else:
        reasons.append(f"Energy partial match (+{parts['energy']:.2f} pts).")

    ac_sim = parts["acoustic"] / W_ACOUSTIC if W_ACOUSTIC else 0.0
    if user.likes_acoustic:
        reasons.append(
            f"Acoustic preference: rewards acoustic sound (+{parts['acoustic']:.2f} pts, ~{ac_sim:.0%} alignment)."
        )
    else:
        reasons.append(
            f"Acoustic preference: rewards produced / less-acoustic sound (+{parts['acoustic']:.2f} pts, ~{ac_sim:.0%} alignment)."
        )

    strong = 0.75
    if parts["valence"] >= W_VALENCE * strong:
        reasons.append(f"Valence vs mood profile (+{parts['valence']:.2f} pts).")
    if parts["tempo"] >= W_TEMPO * strong:
        reasons.append(f"Tempo vs mood profile (+{parts['tempo']:.2f} pts).")
    if parts["danceability"] >= W_DANCEABILITY * strong:
        reasons.append(f"Danceability vs mood profile (+{parts['danceability']:.2f} pts).")

    return " ".join(reasons)


class Recommender:
    """OOP wrapper over the same scoring and ranking rules."""

    def __init__(self, songs: List[Song]):
        """Store the catalog of Song instances to rank against user profiles."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return up to k songs with highest score_song for the given user (tie-break by id)."""
        return sorted(self.songs, key=lambda s: (-score_song(user, s), s.id))[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Delegate to module-level explain_recommendation for one user-song pair."""
        return explain_recommendation(user, song)


def load_songs(csv_path: str) -> List[Dict[str, Any]]:
    """Read songs.csv into a list of dicts with int id and float audio fields."""
    path = Path(csv_path)
    print(f"Loading songs from {path}...")
    if not path.is_file():
        return []

    rows: List[Dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            row = {
                (k or "").strip(): (v.strip() if isinstance(v, str) else v)
                for k, v in raw.items()
            }
            if not row.get("id"):
                continue
            row["id"] = int(row["id"])
            for key in (
                "energy",
                "tempo_bpm",
                "valence",
                "danceability",
                "acousticness",
            ):
                row[key] = float(row[key])
            rows.append(row)
    return rows


def recommend_songs(
    user_prefs: Dict[str, Any],
    songs: List[Dict[str, Any]],
    k: int = 5,
) -> List[Tuple[Dict[str, Any], float, str]]:
    """Score all song dicts, sort by score descending, return top k as (row, score, explanation)."""
    user = user_prefs_to_profile(user_prefs)

    def score_row(row: Dict[str, Any]) -> Tuple[Dict[str, Any], float, str]:
        """Attach score and explanation to one catalog row for sorting."""
        song = song_from_dict(row)
        return row, score_song(user, song), explain_recommendation(user, song)

    ranked = sorted(
        (score_row(row) for row in songs),
        key=lambda item: (-item[1], int(item[0]["id"])),
    )
    return ranked[:k]
