from pathlib import Path
from zipfile import ZipFile
import requests

ROOT = Path(__file__).resolve().parent
URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"

def ensure_dataset(update: bool = False) -> Path:
    target = ROOT / "ml-latest-small"
    required = [target / name for name in ("movies.csv", "ratings.csv", "tags.csv", "links.csv")]
    if not update and all(p.exists() for p in required):
        return target
    archive = ROOT / "ml-latest-small.zip"
    ROOT.mkdir(parents=True, exist_ok=True)
    with requests.get(URL, timeout=60, stream=True) as response:
        response.raise_for_status()
        with archive.open("wb") as out:
            for block in response.iter_content(chunk_size=1024 * 1024):
                if block:
                    out.write(block)
    with ZipFile(archive) as zf:
        zf.extractall(ROOT)
    archive.unlink(missing_ok=True)
    validate_dataset(target)
    return target

def validate_dataset(path: Path) -> dict:
    missing = [name for name in ("movies.csv", "ratings.csv", "tags.csv", "links.csv") if not (path / name).is_file()]
    if missing:
        raise ValueError(f"MovieLens dataset is incomplete: {', '.join(missing)}")
    return {"directory": str(path), "files": 4}

if __name__ == "__main__":
    print(ensure_dataset())
