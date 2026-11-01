from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import numpy as np
def similarity(matrix, axis=0):
    return cosine_similarity(matrix if axis == 0 else matrix.T, dense_output=False)

def topk_similarity(matrix, axis=0, neighbors=100):
    """Sparse cosine KNN graph; bounds memory to O(items × neighbors)."""
    features=matrix if axis==0 else matrix.T
    count=features.shape[0]
    if count==0: return csr_matrix((0,0),dtype=np.float32)
    k=min(count, max(1, int(neighbors)+1))
    model=NearestNeighbors(n_neighbors=k,metric="cosine",algorithm="brute",n_jobs=-1).fit(features)
    distances,indices=model.kneighbors(features,return_distance=True)
    rows=[];cols=[];values=[]
    for row,(ds,ids) in enumerate(zip(distances,indices)):
        for distance,col in zip(ds,ids):
            score=max(0.0,1.0-float(distance))
            if int(col)!=row and score>0:
                rows.append(row);cols.append(int(col));values.append(score)
    return csr_matrix((values,(rows,cols)),shape=(count,count),dtype=np.float32)
