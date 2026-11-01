import numpy as np
def predict(user_index, ratings, similarities, user_neighbors=40):
    sims = similarities[user_index].toarray().ravel() if hasattr(similarities[user_index], "toarray") else np.asarray(similarities[user_index]).ravel()
    sims[user_index] = 0
    neighbors = np.argsort(sims)[::-1][:user_neighbors]
    weights = sims[neighbors]
    numerator = weights @ ratings[neighbors]
    denominator = np.abs(weights) @ (ratings[neighbors] != 0)
    return np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype=float), where=denominator > 0)
