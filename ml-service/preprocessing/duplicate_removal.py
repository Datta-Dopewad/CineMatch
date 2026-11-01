def remove_duplicates(frame):
    return frame.drop_duplicates(subset=["userId", "movieId"], keep="last").copy()
