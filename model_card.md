# Model Card: VibeRank 1.0

## 1. Model Name

**VibeRank 1.0**

## 2. Goal, Intended Use, and Non-Intended Use

VibeRank suggests songs from a small catalog based on a listener's stated genre, mood, energy, and audio-feature preferences. It is intended for classroom exploration of content-based recommendation, scoring, ranking, explainability, and bias. It assumes that the supplied profile is a reasonable summary of the user's current taste.

VibeRank is not intended for deployment to real users, decisions about artist promotion, or claims about a person's identity or personality. It does not learn from listening history and should not be treated as a production Spotify-like model.

## 3. How the Model Works

The system compares every song with the same user profile. In the default mode, an exact genre match earns 3 points and an exact mood match earns 2 points. Numerical features earn more points when the song is closer to the user's target. Energy can contribute up to 2 points, while tempo, valence, danceability, acousticness, popularity, decade, instrumentalness, speechiness, and duration provide smaller supporting scores.

After every song receives a base score, the system ranks the catalog. The optional diversity step reduces a candidate's score when its artist or genre already appears in the selected list. The output includes the final score and the exact matches, similarities, and penalties that produced it.

VibeRank also provides `genre_first`, `mood_first`, and `energy_focus` strategies. These strategies reuse the same algorithm but change feature weights, making it possible to test how design choices alter the ranking.

## 4. Data

The dataset contains 20 fictional songs representing pop, lofi, rock, ambient, jazz, synthwave, indie pop, EDM, R&B, folk, hip-hop, indie, metal, and Latin music. Each row includes an ID, title, artist, genre, mood, energy, tempo, valence, danceability, acousticness, popularity, release decade, instrumentalness, speechiness, and duration.

The data was designed for controlled testing rather than collected from real listeners or audio files. Some genres have multiple examples while others have only one. The labels are subjective, and the dataset does not include lyrics, language, culture, instrumentation, accessibility needs, or actual listening behavior.

## 5. Strengths and Observed Behavior

VibeRank works well when the catalog contains a close match for a clearly specified profile. `Sunrise City` ranks first for High-Energy Pop because it matches both pop and happy while staying close to the numerical targets. `Library Rain` ranks first for Chill Lofi Study because it exactly matches genre, mood, and target energy. `Storm Runner` ranks first for Deep Intense Rock because it is the only exact rock/intense match and is extremely close to the target energy and tempo.

The explanations are faithful to the scoring process, so a user can see whether a recommendation came from an exact label match, a numerical similarity, or a diversity penalty. The three modes also make the system's assumptions easy to experiment with.

## 6. Limitations and Bias

The main limitation is the small, hand-written catalog. A genre with one song has fewer opportunities to appear than a genre with three songs, even if the user's preferences are equally strong. Exact genre and mood matching can also create a filter bubble because unfamiliar but relevant songs receive no category points. The hand-designed weights encode the developer's idea that genre matters more than several audio features, which may not match every listener. Popularity can also reproduce exposure bias if already-visible music is treated as more desirable.

The diversity penalty improves variety by reducing repeated artists and genres, and it explains each reduction. However, it is only a local ranking rule. It cannot correct missing cultures, genres, languages, or artists in the underlying catalog.

## 7. Evaluation

I ran the recommender on three intentionally different profiles and inspected the top five songs:

- **High-Energy Pop** tested high energy, happiness, danceability, and mainstream pop preferences.
- **Chill Lofi Study** tested low energy, acousticness, instrumentalness, and a slow tempo.
- **Deep Intense Rock** tested intense mood, very high energy, and fast tempo.

The pop and lofi outputs differed as expected: the pop list started with `Sunrise City` and `Golden Weekend`, while the lofi list started with `Library Rain` and `Midnight Coding`. The lofi list also promoted ambient and jazz tracks because their energy and acousticness resembled the study profile.

The lofi and rock outputs showed the largest contrast. Low-energy `Library Rain` led the lofi list, while high-energy `Storm Runner` led the rock list. `Gym Hero` appeared in the rock results despite being pop because its intense mood and energy were close to the rock profile. This was a useful reminder that the algorithm ranks feature combinations rather than enforcing genre as a hard filter.

I also performed a sensitivity experiment. For the pop profile, switching from `genre_first` to `energy_focus` changed the third result from `Gym Hero` to `Rooftop Lights`. Changing weights made the list different, but the outcome depended on mood and other similarities as well as energy. Finally, ten automated tests checked CSV type conversion, exact scoring math, descending ranking, strategy changes, diversity explanations, OOP behavior, empty input, `k=0`, and invalid modes.

## 8. Ideas for Improvement

1. Learn weights from real likes, skips, and repeat plays instead of choosing them manually.
2. Use multi-label or embedding-based genre and mood similarity instead of exact string matches.
3. Evaluate on a larger, balanced catalog with metrics for relevance, catalog coverage, artist diversity, and novelty.
4. Let users control how much familiarity versus discovery they want.

## 9. Personal Reflection

The most important lesson was that recommendation has two separate steps: scoring one item and ranking a collection of items. A simple similarity formula can create output that feels personalized, but that does not make it neutral or intelligent in the same way as a learned production model. The results depend heavily on which attributes exist, how the data is distributed, and which weights the developer chooses.

AI tools were useful for proposing diverse data rows, generating an initial modular implementation, and suggesting edge cases. I still needed to verify that numerical CSV values were converted correctly, check a perfect-match score by hand (`3 + 2 + 2 = 7`), run the CLI, compare profiles, and test whether the weight shift actually changed a result. If I extended the project, I would collect explicit user feedback and compare the hand-built scoring rule with a learned baseline.
