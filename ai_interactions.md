# AI Interactions Log

## Agentic Workflow: Additional Song Attributes

**Task given to the agent**

> Solve the project according to the grading criteria and requirements. Use the easiest genre-first scoring approach, complete the required implementation and documentation, add relevant stretch features, and verify the result.

**Follow-up design constraints**

> Keep the algorithm explainable. Use exact genre and mood matches plus numerical similarity, make the explanations agree with the score, and evaluate three distinct profiles.

**What the agent generated or changed**

- Expanded `data/songs.csv` from 10 to 20 songs and broadened its genres and moods.
- Added five attributes not present in the starter design: `popularity`, `release_decade`, `instrumentalness`, `speechiness`, and `duration_min`.
- Updated CSV loading, the `Song` dataclass, preference profiles, and scoring logic so the new fields are converted and scored consistently.
- Implemented the functional and OOP recommendation paths in `src/recommender.py`.
- Added three evaluation profiles, a weight-shift experiment, and formatted output in `src/main.py`.
- Completed the README and Model Card and expanded the test suite.

**Manual verification and corrections**

- Checked that the CSV contains 20 data rows and loads without errors.
- Manually verified a perfect core match: genre `3.0` + mood `2.0` + energy `2.0` = `7.0`.
- Ran all three profiles and confirmed that their first recommendations matched their intended tastes.
- Confirmed that the energy-focused mode changed the pop profile's third result.
- Reworked the first generated terminal layout because its unwrapped explanation column was too wide to read.
- Ran the complete test suite and obtained `10 passed`.

## Diversity, Novelty, and Fairness

The agent suggested a greedy reranking step rather than permanently modifying each song's base score. After each selection, remaining songs lose `1.0` point per already-selected appearance of the same artist and `0.35` per appearance of the same genre. This preserves the original preference score while discouraging a repetitive final list. The penalty is appended to the recommendation explanation so the adjustment is visible rather than hidden.

I checked that the lofi profile applies both artist and genre penalties to `Focus Flow` after another LoRoom song and other lofi songs have already been selected.

## Design Pattern: Scoring Strategy

**Pattern used**

A lightweight **Strategy pattern** implemented through the `SCORING_MODES` configuration mapping.

**How AI contributed**

AI compared duplicating three scoring functions with keeping one scoring algorithm and injecting different weight dictionaries. The shared-algorithm approach was chosen because all strategies use the same features and similarity formula; only their priorities change.

**How it appears in the code**

`SCORING_MODES` defines `genre_first`, `mood_first`, and `energy_focus`. Both `score_song()` and `Recommender` accept a mode name, and `main.py` exposes the choice through `--mode`. A user can run `python -m src.main --mode mood_first` without rewriting ranking logic.

## Visual Output

The first table placed all explanation text on one extremely wide line. The final `format_table()` function uses fixed column widths and wraps the Reasons column across additional rows. It uses only Python's standard library, so users do not need another package to see titles, artists, scores, and full explanations in a readable table.

## Final Audit Refinements

AI-assisted auditing identified three final documentation and precision issues: the missing explicit pop-versus-rock comparison, unanswered reflection prompts, and small differences between totals and independently rounded explanation components. I reviewed and accepted fixes that added the missing comparison and reflection answers, rounded each numerical score component before accumulation, and added a regression test proving that explanation components sum to the returned score.
