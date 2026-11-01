from scipy.sparse import csr_matrix
import numpy as np

def create_matrix(ratings):
    users = sorted(ratings.userId.astype(str).unique())
    movies = sorted(ratings.movieId.astype(int).unique())
    ui = {v:i for i,v in enumerate(users)}; mi = {v:i for i,v in enumerate(movies)}
    rows = ratings.userId.astype(str).map(ui).to_numpy(); cols = ratings.movieId.astype(int).map(mi).to_numpy()
    matrix = csr_matrix((ratings.rating.astype(float).to_numpy(), (rows, cols)), shape=(len(users), len(movies)), dtype=np.float32)
    return matrix, users, movies
