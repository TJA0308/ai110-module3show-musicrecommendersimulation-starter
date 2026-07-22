"""Command-line demonstration for the music recommender simulation."""

import argparse
from textwrap import wrap

from src.recommender import SCORING_MODES, load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "tempo_bpm": 125,
        "valence": 0.85,
        "danceability": 0.85,
        "acousticness": 0.10,
        "popularity": 85,
        "release_decade": 2020,
        "instrumentalness": 0.05,
        "speechiness": 0.08,
        "duration_min": 3.4,
    },
    "Chill Lofi Study": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "tempo_bpm": 75,
        "valence": 0.60,
        "danceability": 0.55,
        "acousticness": 0.85,
        "popularity": 55,
        "release_decade": 2020,
        "instrumentalness": 0.75,
        "speechiness": 0.03,
        "duration_min": 2.8,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "tempo_bpm": 150,
        "valence": 0.45,
        "danceability": 0.60,
        "acousticness": 0.10,
        "popularity": 70,
        "release_decade": 2010,
        "instrumentalness": 0.10,
        "speechiness": 0.07,
        "duration_min": 4.0,
    },
}


def format_table(recommendations: list) -> str:
    """Return recommendations as a readable dependency-free ASCII table."""

    headers = ("#", "Title", "Artist", "Score", "Reasons")
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reason_lines = wrap(explanation, width=72) or [""]
        rows.append(
            (str(rank), song["title"], song["artist"], f"{score:.2f}", reason_lines)
        )

    widths = (3, 20, 16, 5, 72)

    def format_row(row: tuple) -> str:
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))

    divider = "-+-".join("-" * width for width in widths)
    lines = [format_row(headers), divider]
    for rank, title, artist, score, reasons in rows:
        for line_number, reason_line in enumerate(reasons):
            prefix = (rank, title, artist, score) if line_number == 0 else ("", "", "", "")
            lines.append(format_row((*prefix, reason_line)))
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Read the ranking mode and diversity options from the command line."""

    parser = argparse.ArgumentParser(description="Run the VibeRank simulation")
    parser.add_argument(
        "--mode",
        choices=SCORING_MODES,
        default="genre_first",
        help="scoring strategy to use for the three profiles",
    )
    parser.add_argument(
        "--no-diversity",
        action="store_true",
        help="disable repeated-artist and repeated-genre penalties",
    )
    return parser.parse_args()


def main() -> None:
    """Load the catalog and display recommendations for three user profiles."""

    args = parse_args()
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Scoring mode: {args.mode}")

    for profile_name, preferences in PROFILES.items():
        recommendations = recommend_songs(
            preferences,
            songs,
            k=5,
            mode=args.mode,
            diversify=not args.no_diversity,
        )
        print(f"\n=== {profile_name} ===")
        print(format_table(recommendations))

    pop_profile = PROFILES["High-Energy Pop"]
    genre_first = recommend_songs(
        pop_profile, songs, k=3, mode="genre_first", diversify=False
    )
    energy_focus = recommend_songs(
        pop_profile, songs, k=3, mode="energy_focus", diversify=False
    )
    print("\n=== Weight-Shift Experiment ===")
    print("Genre-first:", ", ".join(item[0]["title"] for item in genre_first))
    print("Energy-focus:", ", ".join(item[0]["title"] for item in energy_focus))


if __name__ == "__main__":
    main()
