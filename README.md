# CineMatch

CineMatch is a full-stack movie discovery and recommendation app: React/Vite frontend, Express/Mongoose API, MongoDB Atlas, and a FastAPI collaborative-filtering service. MovieLens provides the catalog and ratings. The app uses bundled local CineMatch artwork plus two attributed public-domain classic posters; it does not call TMDB, OMDb, or a movie-image API.

## Local development

1. Install Node.js 20+ and Python 3.10+.
2. Copy `.env.example` to `.env`. Set `MONGODB_URI`, `JWT_SECRET`, `ML_SERVICE_TOKEN`, and local service URLs. For the local API, use a local MongoDB URI; the local backend refuses Atlas by default.
3. Install Node packages: `npm ci --prefix server` and `npm ci --prefix client`.
4. Install Python packages from `ml-service`: `python -m pip install -r requirements.txt`.
5. Run `python -m dataset.dataset_downloader` in `ml-service` once, then run `npm run dev` from the repository root.
6. To seed MovieLens records into the selected database, run `npm --prefix server run sync:movielens` with its `MONGODB_URI` set intentionally for that database.

## Production deployment

The checked-in configuration targets a Vercel static frontend and Render Node/Python services. Follow [DEPLOYMENT.md](DEPLOYMENT.md) for the order, environment variables, Atlas allowlist, and verification steps.

- Vercel project root: `client` (`client/vercel.json`)
- Render Blueprint: `render.yaml` (API + recommendation service)
- Hosted secrets belong in deployment environment settings, never in the frontend or checked-in files.
- Admin image uploads are stored as image documents in MongoDB and served by the API, so they persist across Render deploys without a writable app disk.

## Features and data

Users can register/sign in, explore and filter the 9,742 MovieLens titles, view details, rate movies, manage watchlists and viewing history, edit preferences, see similar titles, and request ML recommendations. The admin view supports statistics and local image uploads. The first account whose email matches `ADMIN_EMAIL` is created as an admin.

MovieLens has no movie posters. CineMatch includes unique local abstract artwork for the catalog and clearly attributed classic public-domain posters. See `client/public/assets/movies/ASSET_SOURCES.md`.

MovieLens records provide titles, years, genres, and ratings, so the UI does not invent plot summaries, cast, runtime, or trailers. New users receive genre/popularity cold-start recommendations; personalized recommendations come from the FastAPI service and require ratings plus the service to be available.
