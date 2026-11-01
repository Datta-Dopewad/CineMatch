# CineMatch deployment

## Architecture

- **Vercel:** static React/Vite app from the `client` directory. Bundled local movie artwork is served with the site.
- **Render:** the Node/Express API and private-service calls to the FastAPI recommender, declared in `render.yaml`.
- **MongoDB Atlas:** persistent application records and admin-uploaded image binaries.

## Before publishing

1. Push the repository to GitHub, GitLab, or Bitbucket. The working directory currently has no Git remote, so connect/push it before creating linked Render and Vercel projects.
2. Rotate the temporary Atlas database-user password that was pasted into chat. Use the replacement only in Render's secret environment variable and in a private local `.env` when needed; do not commit or paste it again.
3. In Atlas Network Access, allow the outbound IP addresses shown for the Render API service. Keep the allowlist restricted; do not open the cluster to every IP.
4. Confirm the Atlas database user has read/write access to the database selected in the URI. The current URI without a database path selects `test`, where the 9,742 MovieLens records have already been seeded. Keep that same URI on the deployed API to use those records. If choosing a different database, set its name in the URI and seed that database once with `npm --prefix server run sync:movielens`.

## Deploy order

### 1. Deploy the frontend on Vercel

- Import the Git repository and set **Root Directory** to `client`.
- Build: `npm run build`; output: `dist` (also declared in `client/vercel.json`).
- The first deploy can use the default `/api` value, but API calls will work only after the backend URL is configured below.

### 2. Deploy the API and recommender on Render

- Create a Blueprint from the repository root and apply `render.yaml`.
- Provide `MONGODB_URI` from Atlas when prompted. Do not put it in `render.yaml`.
- Provide `CLIENT_ORIGIN` as the exact Vercel site origin, such as `https://your-project.vercel.app` (no path or trailing slash).
- Set `ADMIN_EMAIL` to the email that should receive admin role when its first account is registered.
- Render generates `JWT_SECRET` and the ML service token. The API receives the same ML token and internal ML host from the Blueprint.
- The Python build downloads the official MovieLens dataset once at build time. The runtime recommendation service reads that bundled dataset.

The API health check is `/api/health`; the Python health check is `/health`. The Render plan is set to `free` in the Blueprint, so services may cold-start after idle periods. Choose an always-on plan in Render if that delay is unsuitable.

### 3. Connect Vercel to the API

In Vercel project settings, add `VITE_API_URL` for Production and Preview with the API URL ending in `/api`, for example `https://your-api.onrender.com/api`. Redeploy the frontend so Vite embeds this public API base URL. `VITE_API_URL` is not a secret.

If the Vercel domain changes, update Render's `CLIENT_ORIGIN` and redeploy the API. For multiple allowed origins, separate exact origins with commas.

## First-use setup

1. Open the Vercel URL and register the account whose email matches `ADMIN_EMAIL`; that account receives the admin role.
2. Sign in again after any role change so the JWT contains the current role.
3. Confirm movie listings load, test registration/login, save a film, rate it, and open the admin panel.
4. After a few ratings, confirm the personalized recommendation request succeeds. If it does not, check both Render health endpoints and their service logs without exposing environment values.

## Storage and security notes

- Original and generated artwork is bundled in `client/public/assets/movies` and deploys with Vercel.
- Admin-uploaded JPG/PNG/WebP images (up to 5 MB) are stored in MongoDB and served from `/api/images/:id`; no Render filesystem persistence is assumed.
- Keep Atlas `MONGODB_URI`, `JWT_SECRET`, and `ML_SERVICE_TOKEN` on the backend only. Never add them as `VITE_*` variables.
- Local API startup refuses to use an Atlas URI unless `NODE_ENV=production`; deployed Render sets production mode through the Blueprint. The local frontend remains proxy-configured for local development.
