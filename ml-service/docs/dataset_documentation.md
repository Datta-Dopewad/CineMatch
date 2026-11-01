# Dataset
The downloader retrieves MovieLens Latest Small from GroupLens' official file distribution on first use and keeps `ml-latest-small/` locally. Required files are movies.csv, ratings.csv, tags.csv, and links.csv. The sync script imports catalog metadata into MongoDB and preserves local placeholder paths. MovieLens does not include posters; add only licensed local images.
