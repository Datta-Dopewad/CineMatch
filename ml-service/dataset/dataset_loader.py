from pathlib import Path
import pandas as pd
from dataset.dataset_downloader import ensure_dataset

def load_movies():
    return pd.read_csv(ensure_dataset() / "movies.csv")

def load_ratings():
    return pd.read_csv(ensure_dataset() / "ratings.csv")
