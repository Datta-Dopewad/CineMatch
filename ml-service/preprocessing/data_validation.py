def validate(frame):
    frame = frame.copy()
    frame["rating"] = frame["rating"].astype(float)
    frame = frame[frame["rating"].between(0.5, 5.0)]
    frame["userId"] = frame["userId"].astype(str)
    frame["movieId"] = frame["movieId"].astype(int)
    if "timestamp" in frame: frame["timestamp"] = frame["timestamp"].astype("int64")
    return frame
