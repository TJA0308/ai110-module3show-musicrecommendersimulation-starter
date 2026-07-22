"""Core scoring and ranking logic for the music recommender simulation."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Mapping, Optional, Tuple


NUMERIC_FIELDS = {
    "id": int,
    "energy": float,
    "tempo_bpm": float,
    "valence": float,
    "danceability": float,
    "acousticness": float,
    "popularity": float,
    "release_decade": int,
    "instrumentalness": float,
    "speechiness": float,
    "duration_min": float,
}

# Each dictionary is a simple scoring strategy. A mode changes weights without
# duplicating the scoring or ranking algorithm.
SCORING_MODES = {
    "genre_first": {
        "genre": 3.0,
        "mood": 2.0,
        "energy": 2.0,
        "tempo_bpm": 0.5,
        "valence": 0.5,
        "danceability": 0.5,
        "acousticness": 0.5,
        "popularity": 0.25,
        "release_decade": 0.25,
        "instrumentalness": 0.25,
        "speechiness": 0.25,
        "duration_min": 0.25,
    },
    "mood_first": {
        "genre": 1.5,
        "mood": 3.0,
        "energy": 2.0,
        "tempo_bpm": 0.5,
        "valence": 1.0,
        "danceability": 0.5,
        "acousticness": 0.75,
        "popularity": 0.1,
        "release_decade": 0.1,
        "instrumentalness": 0.25,
        "speechiness": 0.1,
        "duration_min": 0.2,
    },
    "energy_focus": {
        "genre": 1.5,
        "mood": 2.0,
        "energy": 4.0,
        "tempo_bpm": 1.5,
        "valence": 0.5,
        "danceability": 1.0,
        "acousticness": 0.25,
        "popularity": 0.1,
        "release_decade": 0.1,
        "instrumentalness": 0.1,
        "speechiness": 0.1,
        "duration_min": 0.1,
    },
}

PREFERENCE_KEYS = {
    "genre": "genre",
    "mood": "mood",
    "energy": "energy",
    "tempo_bpm": "tempo_bpm",
    "valence": "valence",
    "danceability": "danceability",
    "acousticness": "acousticness",
    "popularity": "popularity",
    "release_decade": "release_decade",
    "instrumentalness": "instrumentalness",
    "speechiness": "speechiness",
    "duration_min": "duration_min",
}

SIMILARITY_RANGES = {
    "energy": 1.0,
    "tempo_bpm": 100.0,
    "valence": 1.0,
    "danceability": 1.0,
    "acousticness": 1.0,
    "popularity": 100.0,
    "release_decade": 50.0,
    "instrumentalness": 1.0,
    "speechiness": 1.0,
    "duration_min": 5.0,
}


@dataclass
class Song:
    """Represent one song and the attributes used for recommendation."""

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
    popularity: float = 50.0
    release_decade: int = 2020
    instrumentalness: float = 0.0
    speechiness: float = 0.05
    duration_min: float = 3.5


@dataclass
class UserProfile:
    """Represent a listener's main taste preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Provide an object-oriented interface to the shared ranking logic."""

    def __init__(self, songs: List[Song], mode: str = "genre_first"):
        if mode not in SCORING_MODES:
            raise ValueError(f"Unknown scoring mode: {mode}")
        self.songs = songs
        self.mode = mode

    @staticmethod
    def _profile_to_dict(user: UserProfile) -> Dict:
        """Convert a UserProfile into preferences used by score_song."""

        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return up to k Song objects ordered from best to worst match."""

        song_dicts = [asdict(song) for song in self.songs]
        ranked = recommend_songs(
            self._profile_to_dict(user),
            song_dicts,
            k=k,
            mode=self.mode,
            diversify=False,
        )
        songs_by_id = {song.id: song for song in self.songs}
        return [songs_by_id[item[0]["id"]] for item in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain which preferences contributed to a song's score."""

        _, reasons = score_song(
            self._profile_to_dict(user), asdict(song), mode=self.mode
        )
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV and convert numeric fields to numeric values."""

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError("Song CSV must include a header row")

        missing = set(NUMERIC_FIELDS) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Song CSV is missing fields: {sorted(missing)}")

        for row_number, row in enumerate(reader, start=2):
            try:
                for field, converter in NUMERIC_FIELDS.items():
                    row[field] = converter(row[field])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid numeric value on CSV row {row_number}"
                ) from error
            songs.append(dict(row))

    return songs


def _similarity(value: float, target: float, feature_range: float) -> float:
    """Return a bounded 0-to-1 similarity from an absolute numeric gap."""

    return max(0.0, 1.0 - abs(value - target) / feature_range)


def score_song(
    user_prefs: Mapping,
    song: Mapping,
    mode: str = "genre_first",
    weights: Optional[Mapping[str, float]] = None,
) -> Tuple[float, List[str]]:
    """Score one song and return both its numeric score and exact reasons."""

    if mode not in SCORING_MODES:
        raise ValueError(f"Unknown scoring mode: {mode}")
    active_weights = dict(weights or SCORING_MODES[mode])
    reasons: List[str] = []
    score = 0.0

    for feature in ("genre", "mood"):
        if feature not in user_prefs:
            continue
        if str(song[feature]).casefold() == str(user_prefs[feature]).casefold():
            points = active_weights[feature]
            score += points
            reasons.append(f"{feature} match (+{points:.2f})")

    for feature, feature_range in SIMILARITY_RANGES.items():
        preference_key = PREFERENCE_KEYS[feature]
        if preference_key not in user_prefs:
            continue
        similarity = _similarity(
            float(song[feature]), float(user_prefs[preference_key]), feature_range
        )
        # Round each displayed component before adding it so the explanation
        # arithmetic reconciles exactly with the returned total.
        points = round(active_weights[feature] * similarity, 2)
        score += points
        reasons.append(f"{feature} similarity (+{points:.2f})")

    if not reasons:
        reasons.append("no stated preference matched (+0.00)")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Mapping,
    songs: List[Dict],
    k: int = 5,
    mode: str = "genre_first",
    diversify: bool = True,
) -> List[Tuple[Dict, float, str]]:
    """Rank songs, optionally penalizing repeated artists and genres."""

    if k < 1:
        return []

    candidates = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        candidates.append({"song": song, "score": score, "reasons": reasons})

    if not diversify:
        candidates.sort(key=lambda item: (-item["score"], item["song"]["title"]))
        return [
            (item["song"], item["score"], "; ".join(item["reasons"]))
            for item in candidates[:k]
        ]

    selected = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}

    while candidates and len(selected) < k:
        for item in candidates:
            song = item["song"]
            artist_penalty = 1.0 * artist_counts.get(song["artist"], 0)
            genre_penalty = 0.35 * genre_counts.get(song["genre"], 0)
            item["adjusted_score"] = item["score"] - artist_penalty - genre_penalty
            item["penalties"] = []
            if artist_penalty:
                item["penalties"].append(
                    f"repeated artist penalty (-{artist_penalty:.2f})"
                )
            if genre_penalty:
                item["penalties"].append(
                    f"repeated genre penalty (-{genre_penalty:.2f})"
                )

        best = max(
            candidates,
            key=lambda item: (item["adjusted_score"], item["song"]["title"]),
        )
        candidates.remove(best)
        selected.append(best)
        artist = best["song"]["artist"]
        genre = best["song"]["genre"]
        artist_counts[artist] = artist_counts.get(artist, 0) + 1
        genre_counts[genre] = genre_counts.get(genre, 0) + 1

    return [
        (
            item["song"],
            round(item["adjusted_score"], 4),
            "; ".join(item["reasons"] + item["penalties"]),
        )
        for item in selected
    ]
