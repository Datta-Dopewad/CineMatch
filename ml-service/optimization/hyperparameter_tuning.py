from evaluation.evaluate_model import evaluate_models
def tune(ratings):
    # Evaluates implemented baselines; the lowest held-out RMSE selects the recorded baseline.
    results=evaluate_models(ratings)["results"]
    return min(results,key=lambda row:row["rmse"]) if results else None
