from datetime import datetime, timezone
from pathlib import Path
import json, pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from preprocessing.clean_data import clean
from preprocessing.train_test import split
from preprocessing.rating_matrix import create_matrix
from recommendation.cosine_similarity import topk_similarity
from recommendation.prediction import predict
import numpy as np
from scipy.sparse import csr_matrix
from optimization.model_config import CONFIG

def evaluate_models(ratings):
    data=clean(ratings); train,test=split(data); matrix,users,movies=create_matrix(train); mi={v:i for i,v in enumerate(movies)}; ui={v:i for i,v in enumerate(users)}
    results=[]
    user_sim=topk_similarity(matrix,axis=0,neighbors=CONFIG["user_neighbors"]); item_sim=topk_similarity(matrix,axis=1,neighbors=100); dense=matrix.toarray()
    grouped={str(user):part for user,part in test.groupby(test.userId.astype(str))}
    train_seen={str(user):set(part.movieId.astype(int)) for user,part in train.groupby(train.userId.astype(str))}
    for model in ("user_based","item_based"):
        actual=[];predicted=[];precisions=[];recalls=[]
        for user,part in grouped.items():
            if user not in ui: continue
            user_idx=ui[user]
            if model=="user_based": scores=predict(user_idx,dense,user_sim,CONFIG["user_neighbors"])
            else:
                user_ratings=matrix.getrow(user_idx).toarray().ravel()
                numer=np.asarray(item_sim @ user_ratings).ravel();denom=np.asarray(abs(item_sim) @ (user_ratings!=0).astype(float)).ravel()
                scores=np.divide(numer,denom,out=np.zeros_like(numer,dtype=float),where=denom>0)
            relevant=set(part.loc[part.rating>=4.0,"movieId"].astype(int))
            candidate_scores=scores.copy()
            for seen in train_seen.get(user,set()):
                if seen in mi: candidate_scores[mi[seen]]=-np.inf
            top_indices=np.argsort(candidate_scores)[::-1][:10]
            recommended={movies[idx] for idx in top_indices if np.isfinite(candidate_scores[idx]) and candidate_scores[idx]>0}
            if relevant:
                hits=len(recommended & relevant);precisions.append(hits/10);recalls.append(hits/len(relevant))
            for row in part.itertuples():
                movie=int(row.movieId)
                if movie not in mi: continue
                p=float(scores[mi[movie]])
                if p>0: actual.append(float(row.rating));predicted.append(min(5,max(.5,p)))
        if not actual: continue
        results.append({"model":model,"model_version":"cinematch-cf-1.0","rmse":float(mean_squared_error(actual,predicted)**.5),"mae":float(mean_absolute_error(actual,predicted)),"precision_at_10":float(np.mean(precisions)) if precisions else 0.0,"recall_at_10":float(np.mean(recalls)) if recalls else 0.0,"relevance_threshold":4.0,"test_predictions":len(actual),"evaluation_date":datetime.now(timezone.utc).isoformat()})
    if results:
        out=Path(__file__).resolve().parents[1]/"results";out.mkdir(exist_ok=True)
        (out/"evaluation.json").write_text(json.dumps(results,indent=2));pd.DataFrame(results).to_csv(out/"evaluation.csv",index=False)
    return {"results":results,"note":"Metrics use a seeded held-out split; ranking relevance is defined as a held-out rating of at least 4.0."}
