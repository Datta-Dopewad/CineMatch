def handle_missing(frame):
    return frame.dropna(subset=["userId", "movieId", "rating"]).copy()
