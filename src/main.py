"""
CLI for the Music Recommender Simulation.

Run from project root: python -m src.main
"""

from __future__ import annotations

from src.recommender import load_songs, recommend_songs


def _divider(char: str = "-", width: int = 64) -> str:
    return char * width


def main() -> None:
    songs = load_songs("data/songs.csv")
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    k = min(5, len(songs)) if songs else 0

    recommendations = recommend_songs(user_prefs, songs, k=k)

    print()
    print(_divider("="))
    print("  MUSIC RECOMMENDER - results")
    print(_divider("="))
    print(f"  Catalog: {len(songs)} songs")
    profile_bits = [
        f"genre={user_prefs['genre']!r}",
        f"mood={user_prefs['mood']!r}",
        f"energy={user_prefs['energy']}",
    ]
    if "likes_acoustic" in user_prefs:
        profile_bits.append(f"likes_acoustic={user_prefs['likes_acoustic']}")
    print("  Your profile: " + ", ".join(profile_bits))
    print(_divider("="))
    print()

    if not recommendations:
        print("  No recommendations (empty catalog or missing CSV).")
        print()
        return

    width = 64
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        title = song.get("title", "?")
        artist = song.get("artist", "")
        line = f"  #{rank}  {title}"
        if artist:
            line += f"  |  {artist}"
        print(line)
        print(f"       Score: {score:.3f}")
        print(_divider("-", width))
        # One scoring reason per line (explanation uses ". " between clauses).
        sentences = [s.strip() for s in explanation.split(". ") if s.strip()]
        for i, sentence in enumerate(sentences):
            line_out = sentence if sentence.endswith(".") else sentence + "."
            prefix = "       Why:  " if i == 0 else "             "
            print(prefix + line_out)
        print()

    print(_divider("="))
    print()


if __name__ == "__main__":
    main()
