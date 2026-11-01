import json
from pathlib import Path
import pandas as pd

def to_records(movies: pd.DataFrame):
    rows = []
    for row in movies.itertuples(index=False):
        year = None
        if isinstance(row.title, str) and row.title[-5:-1].isdigit(): year = int(row.title[-5:-1])
        average = round(float(row.mean), 3) if hasattr(row, "mean") and pd.notna(row.mean) else 0
        count = int(row.count) if hasattr(row, "count") and pd.notna(row.count) else 0
        rows.append({"movieLensId": int(row.movieId), "title": row.title, "genres": [] if row.genres == "(no genres listed)" else row.genres.split("|"), "releaseYear": year, "averageRating": average, "ratingCount": count, "datasetAverageRating": average, "datasetRatingCount": count, "popularity": count, "posterPath": "/assets/movies/placeholders/poster-placeholder.svg", "backdropPath": "/assets/movies/placeholders/backdrop-placeholder.svg"})
    return rows

def write_mapping(movies, output=None):
    output = Path(output or Path(__file__).resolve().parents[2] / "server/data/movieImageMapping.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps([{"movieLensId": m["movieLensId"], "posterPath": m["posterPath"], "backdropPath": m["backdropPath"]} for m in to_records(movies)], indent=2), encoding="utf-8")
    return output

def write_catalog(movies, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(to_records(movies)), encoding="utf-8")
    return output
