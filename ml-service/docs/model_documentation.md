# Model
User-based estimates weight neighboring users' ratings by cosine similarity. Item-based estimates weight a user's existing ratings by movie cosine similarity. The service blends both estimates and removes rated movies. Fewer than three user ratings use a Bayesian-smoothed popularity prior calculated from observed MovieLens ratings. Model version: `cinematch-cf-1.0`.
