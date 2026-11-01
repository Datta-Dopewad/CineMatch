import time
from collections import OrderedDict
import hashlib
import pandas as pd
from preprocessing.clean_data import clean
from preprocessing.rating_matrix import create_matrix
from recommendation.cold_start import popular_movies
from recommendation.cosine_similarity import topk_similarity
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import numpy as np
from optimization.model_config import CONFIG

class Recommender:
    version = "cinematch-cf-1.0"
    trained = False
    def __init__(self):
        self._cache = OrderedDict()
    def fit(self, ratings):
        self.ratings = clean(ratings)
        self.matrix, self.users, self.movie_ids = create_matrix(self.ratings)
        self.item_similarities = topk_similarity(self.matrix, axis=1, neighbors=100)
        self.trained = True
    def recommend(self, user_id, ratings, movies, limit=10, favorite_genres=None):
        started = time.perf_counter()
        frame = clean(ratings)
        personal = frame.loc[frame.userId.astype(str) == str(user_id), ["movieId", "rating"]].sort_values("movieId")
        if not self.trained and len(personal) >= 3:
            self.fit(frame.loc[frame.userId.astype(str) != str(user_id)])
        fingerprint = hashlib.sha256(pd.util.hash_pandas_object(personal, index=False).values.tobytes()).hexdigest()
        cache_key = (str(user_id), fingerprint, tuple(sorted(favorite_genres or [])), self.version, int(limit))
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            return self._cache[cache_key]
        rated = set(personal.movieId.astype(int))
        if len(rated) < 3:
            popularity_ratings = self.ratings if self.trained else frame.loc[frame.userId.astype(str) != str(user_id)]
            picks = popular_movies(popularity_ratings, movies, favorite_genres=favorite_genres, limit=limit)
            picks = picks[~picks.movieId.isin(rated)]
            results = [{"movie_id": int(row.movieId), "score": float(row.score), "reason": "Popular with highly rated MovieLens users"} for row in picks.head(limit).itertuples()]
        else:
            matrix, users, movie_ids = self.matrix, self.users, self.movie_ids
            movie_index = {value:index for index,value in enumerate(movie_ids)}
            user_vector = np.zeros(len(movie_ids),dtype=np.float32)
            for row in personal.itertuples():
                if int(row.movieId) in movie_index: user_vector[movie_index[int(row.movieId)]]=float(row.rating)
            similarities = cosine_similarity(csr_matrix(user_vector.reshape(1,-1)),matrix).ravel()
            if str(user_id) in users: similarities[users.index(str(user_id))]=0
            neighbor_indices = similarities.argsort()[::-1][:CONFIG["user_neighbors"]]
            weights = similarities[neighbor_indices]
            user_numerator = weights @ matrix[neighbor_indices].toarray()
            user_denominator = np.abs(weights) @ (matrix[neighbor_indices].toarray()!=0)
            user_scores = np.divide(user_numerator,user_denominator,out=np.zeros_like(user_numerator,dtype=float),where=user_denominator>0)
            item_numerator = np.asarray(self.item_similarities @ user_vector).ravel()
            item_denominator = np.asarray(abs(self.item_similarities) @ (user_vector!=0).astype(float)).ravel()
            item_scores = np.divide(item_numerator,item_denominator,out=np.zeros_like(item_numerator,dtype=float),where=item_denominator>0)
            scores = (user_scores + item_scores) / 2
            results = [{"movie_id": int(movie_ids[i]), "score": float(scores[i]), "reason": "Collaborative filtering"} for i in scores.argsort()[::-1] if movie_ids[i] not in rated and scores[i] > 0][:limit]
        for result in results: result["generation_ms"] = round((time.perf_counter()-started)*1000, 2)
        self._remember(cache_key, results)
        return results
    def _remember(self, key, value):
        self._cache[key] = value
        self._cache.move_to_end(key)
        while len(self._cache) > 512: self._cache.popitem(last=False)
    def similar(self, movie_id, ratings, movies, limit=10):
        if not self.trained: self.fit(ratings)
        ids=self.movie_ids
        if int(movie_id) not in ids: return []
        idx = ids.index(int(movie_id)); row=self.item_similarities.getrow(idx).toarray().ravel()
        return [{"movie_id": int(ids[i]), "score": float(row[i])} for i in row.argsort()[::-1] if row[i] > 0][:limit]
    def neighbors(self, user_id, ratings):
        if not self.trained: self.fit(ratings)
        matrix, users = self.matrix, self.users
        if str(user_id) not in users: return []
        similarities=topk_similarity(matrix,axis=0,neighbors=10)
        sims = similarities.getrow(users.index(str(user_id))).toarray().ravel()
        return [{"user_id": users[i], "similarity": float(sims[i])} for i in sims.argsort()[::-1][1:11] if sims[i] > 0]
