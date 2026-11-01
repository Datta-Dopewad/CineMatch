import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
def rating_metrics(actual, predicted):
    return {"rmse":float(np.sqrt(mean_squared_error(actual,predicted))),"mae":float(mean_absolute_error(actual,predicted))}
def precision_recall_at_k(recommendations, relevant, k=10):
    rec=set(recommendations[:k]); relevant=set(relevant); hits=len(rec&relevant)
    return {"precision_at_k":hits/max(1,k),"recall_at_k":hits/max(1,len(relevant))}
