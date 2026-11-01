def add_features(movies):
    result = movies.copy()
    result["genres_list"] = result.genres.fillna("(no genres listed)").map(lambda value: value.split("|"))
    result["releaseYear"] = result.title.str.extract(r"\((\d{4})\)")[0].astype("Int64")
    return result
