def popular_movies(ratings, movies, favorite_genres=None, limit=10):
    stats = ratings.groupby("movieId").rating.agg(["mean", "count"]).reset_index()
    # Bayesian smoothing penalizes titles with very few votes using the dataset-wide mean.
    prior, minimum = ratings.rating.mean(), 20
    stats["score"] = (stats["count"] * stats["mean"] + minimum * prior) / (stats["count"] + minimum)
    ranked = stats.merge(movies, on="movieId", how="inner")
    if favorite_genres:
        ranked = ranked[ranked.genres.map(lambda value: bool(set(value.split("|")) & set(favorite_genres)))]
    return ranked.sort_values(["score", "count"], ascending=False).head(limit)
