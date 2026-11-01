from recommendation.cosine_similarity import topk_similarity
from recommendation.prediction import predict

def user_based(matrix, user_index, k=40):
    similarities = topk_similarity(matrix, axis=0, neighbors=k)
    return predict(user_index, matrix.toarray(), similarities, k)

def item_based(matrix, user_index, k=40):
    item_sim = topk_similarity(matrix, axis=1, neighbors=k)
    user_ratings = matrix.getrow(user_index).toarray().ravel()
    scores = item_sim @ user_ratings
    norms = abs(item_sim) @ (user_ratings != 0).astype(float)
    return scores / norms.clip(min=1e-9)
