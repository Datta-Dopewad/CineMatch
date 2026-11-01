def compare(results):
    return sorted(results,key=lambda row:row.get("rmse",float("inf")))
