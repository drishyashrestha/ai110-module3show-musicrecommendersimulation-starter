"""
CLI for the Music Recommender Simulation.

Run from project root: python -m src.main
"""

from __future__ import annotations

from src.recommender import load_songs, recommend_songs


def _divider(char: str = "-", width: int = 64) -> str:
    return char * width


# ── Standard user profiles ────────────────────────────────────────────────────
PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.90,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
    },
    # ── Adversarial / edge-case profiles ─────────────────────────────────────
    # Genre not in the catalog at all → no genre bonus for any song
    "Genre Ghost (country)": {
        "genre": "country",
        "mood": "happy",
        "energy": 0.70,
        "likes_acoustic": True,
    },
    # Conflicting signals: high energy target but calm/low-energy mood profile
    "Conflicted Soul": {
        "genre": "ambient",
        "mood": "relaxed",
        "energy": 0.95,
        "likes_acoustic": False,
    },
    # Extreme low energy + acoustic lover: does the system bottleneck on one feature?
    "Whisper Mode": {
        "genre": "jazz",
        "mood": "focused",
        "energy": 0.0,
        "likes_acoustic": True,
    },
}


def _print_profile_results(
    label: str,
    user_prefs: dict,
    songs: list,
    k: int = 5,
) -> None:
    """Print top-k recommendations for one user profile."""
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print()
    print(_divider("="))
    print(f"  PROFILE: {label}")
    bits = [f"genre={user_prefs['genre']!r}", f"mood={user_prefs['mood']!r}", f"energy={user_prefs['energy']}"]
    if "likes_acoustic" in user_prefs:
        bits.append(f"likes_acoustic={user_prefs['likes_acoustic']}")
    print("  Prefs:   " + ", ".join(bits))
    print(_divider("="))

    if not recommendations:
        print("  No recommendations (empty catalog).")
        print()
        return

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        title = song.get("title", "?")
        artist = song.get("artist", "")
        line = f"  #{rank}  {title}"
        if artist:
            line += f"  |  {artist}"
        print(line)
        print(f"       Score: {score:.3f}")
        print(_divider("-", 64))
        sentences = [s.strip() for s in explanation.split(". ") if s.strip()]
        for i, sentence in enumerate(sentences):
            line_out = sentence if sentence.endswith(".") else sentence + "."
            prefix = "       Why:  " if i == 0 else "             "
            print(prefix + line_out)
        print()

    print(_divider("="))


def main() -> None:
    songs = load_songs("data/songs.csv")
    k = min(5, len(songs)) if songs else 0

    for label, prefs in PROFILES.items():
        _print_profile_results(label, prefs, songs, k=k)

    print()


if __name__ == "__main__":
    main()
