import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
import pandas as pd
import time
from recommendation.recommendation_engine import Recommender
from dataset.dataset_loader import load_ratings, load_movies
from results.recommendation_logs import log_generation

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
app = FastAPI(title="CineMatch Recommendation Service", version="1.0.0")
engine = Recommender()
TOKEN = os.getenv("ML_SERVICE_TOKEN", "")

class UserRating(BaseModel):
    movieId: int
    rating: float = Field(ge=0.5, le=5.0)

class UserRatings(BaseModel):
    ratings: list[UserRating] = Field(default_factory=list)
    favoriteGenres: list[str] = Field(default_factory=list, max_length=20)

def authorize(x_service_token: str | None):
    if not TOKEN:
        raise HTTPException(503, "ML service authentication is not configured")
    if x_service_token != TOKEN:
        raise HTTPException(401, "Invalid service credentials")

@app.get("/health")
def health():
    return {"status": "ok", "model_version": engine.version, "trained": engine.trained}

@app.post("/recommendations/user/{user_id}")
@app.get("/recommendations/user/{user_id}")
def recommend(user_id: str, payload: UserRatings | None = None, limit: int = Query(default=10, ge=1, le=10), x_service_token: str | None = Header(default=None)):
    authorize(x_service_token)
    try:
        started = time.perf_counter()
        ratings = load_ratings()
        if payload and payload.ratings:
            personal = pd.DataFrame([rating.model_dump() for rating in payload.ratings])
            personal["userId"] = str(user_id)
            personal["timestamp"] = 0
            ratings = pd.concat([ratings, personal[["userId", "movieId", "rating", "timestamp"]]], ignore_index=True)
        movies = load_movies()
        recommendations = engine.recommend(user_id, ratings, movies, min(limit, 10), payload.favoriteGenres if payload else None)
        log_generation(user_id, (time.perf_counter()-started)*1000, len(recommendations))
        return {"recommendations": recommendations}
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc))

@app.get("/recommendations/movie/{movie_id}")
def similar(movie_id: int, limit: int = Query(default=10, ge=1, le=10), x_service_token: str | None = Header(default=None)):
    authorize(x_service_token)
    return {"recommendations": engine.similar(movie_id, load_ratings(), load_movies(), min(limit, 10))}

@app.post("/recommendations/train")
def train(x_service_token: str | None = Header(default=None)):
    authorize(x_service_token)
    engine.fit(load_ratings())
    return {"status": "trained", "model_version": engine.version}

@app.post("/recommendations/evaluate")
def evaluate(x_service_token: str | None = Header(default=None)):
    authorize(x_service_token)
    from evaluation.evaluate_model import evaluate_models
    return evaluate_models(load_ratings())

@app.get("/recommendations/model-info")
def model_info(x_service_token: str | None = Header(default=None)):
    authorize(x_service_token)
    return {"model": "user-item cosine collaborative filtering", "version": engine.version, "trained": engine.trained}

@app.get("/recommendations/similar-users/{user_id}")
def similar_users(user_id: str, x_service_token: str | None = Header(default=None)):
    authorize(x_service_token)
    return {"users": engine.neighbors(user_id, load_ratings())}
