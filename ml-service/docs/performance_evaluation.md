# Evaluation
`POST /recommendations/evaluate` computes RMSE, MAE, Precision@10, and Recall@10 on a seeded 80/20 held-out rating split for both implemented baselines, then writes JSON and CSV reports. Ranking relevance is defined as a held-out rating of at least 4.0. Metrics are computed from the MovieLens dataset and are never hardcoded.
