"""Tests for both functional and object-oriented recommender interfaces."""

from pathlib import Path

import pytest

from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    load_songs,
    recommend_songs,
    score_song,
)


def make_small_recommender() -> Recommender:
    """Create a deterministic two-song recommender for OOP tests."""

    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_load_songs_converts_numeric_fields():
    """CSV loading should return 20 songs with usable numeric values."""

    songs = load_songs(str(Path("data/songs.csv")))

    assert len(songs) == 20
    assert isinstance(songs[0]["id"], int)
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["release_decade"], int)


def test_score_song_rewards_exact_matches_and_energy_similarity():
    """A perfect core match should receive all core genre/mood/energy points."""

    song = {"genre": "pop", "mood": "happy", "energy": 0.8}
    preferences = {"genre": "pop", "mood": "happy", "energy": 0.8}

    score, reasons = score_song(preferences, song)

    assert score == pytest.approx(7.0)
    assert "genre match (+3.00)" in reasons
    assert "mood match (+2.00)" in reasons
    assert "energy similarity (+2.00)" in reasons


def test_recommend_songs_sorts_highest_score_first():
    """Ranking should place the closest preference match first."""

    songs = load_songs("data/songs.csv")
    preferences = {"genre": "pop", "mood": "happy", "energy": 0.82}

    results = recommend_songs(preferences, songs, k=3, diversify=False)

    assert len(results) == 3
    assert results[0][0]["title"] == "Sunrise City"
    assert results[0][1] >= results[1][1] >= results[2][1]


def test_different_modes_can_change_ranking():
    """A weight-shift strategy should be able to alter the top-three ordering."""

    songs = load_songs("data/songs.csv")
    preferences = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "tempo_bpm": 125,
        "danceability": 0.85,
    }

    genre_titles = [
        item[0]["title"]
        for item in recommend_songs(
            preferences, songs, k=3, mode="genre_first", diversify=False
        )
    ]
    energy_titles = [
        item[0]["title"]
        for item in recommend_songs(
            preferences, songs, k=3, mode="energy_focus", diversify=False
        )
    ]

    assert genre_titles != energy_titles


def test_diversity_penalty_is_explained():
    """Repeated genres should be penalized transparently during reranking."""

    songs = load_songs("data/songs.csv")
    preferences = {"genre": "pop", "mood": "happy", "energy": 0.8}

    results = recommend_songs(preferences, songs, k=3, diversify=True)

    assert any("repeated genre penalty" in explanation for _, _, explanation in results)


def test_recommend_returns_songs_sorted_by_score():
    """The OOP interface should rank a matching pop song first."""

    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    results = make_small_recommender().recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    """The OOP explanation should be readable and non-empty."""

    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    recommender = make_small_recommender()

    explanation = recommender.explain_recommendation(user, recommender.songs[0])

    assert isinstance(explanation, str)
    assert "genre match" in explanation


def test_empty_catalog_returns_empty_recommendations():
    """An empty catalog should be handled without an exception."""

    assert recommend_songs({"genre": "pop"}, [], k=5) == []


def test_non_positive_k_returns_empty_recommendations():
    """Requesting zero results should return an empty list."""

    songs = load_songs("data/songs.csv")

    assert recommend_songs({"genre": "pop"}, songs, k=0) == []


def test_unknown_scoring_mode_raises_value_error():
    """Invalid strategy names should fail clearly instead of silently."""

    with pytest.raises(ValueError, match="Unknown scoring mode"):
        score_song({"genre": "pop"}, {"genre": "pop"}, mode="unknown")
