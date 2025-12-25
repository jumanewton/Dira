# Heroku Deployment Fix for "Unexpected token '<'" Error

## Problem
The frontend is getting an HTML response instead of JSON when calling the backend API. This happens because:
1. The frontend doesn't know the backend API URL on Heroku
2. When `REACT_APP_API_URL` is empty, requests go to the wrong server

## Solution

### Option 1: Single Heroku App (Current Setup - Backend Only)

Your current `heroku.yml` deploys only the backend. To serve the frontend from the same app:

**Step 1:** Modify the backend to serve the frontend static files

Add this to your `Dockerfile` before the CMD:

```dockerfile
# Copy frontend build (you need to build frontend locally first)
COPY frontend/build ./frontend/build
```

**Step 2:** Build the frontend locally before deploying:

```bash
cd frontend
npm run build
cd ..
git add frontend/build
git commit -m "Add frontend build for Heroku"
git push heroku main
```

**Step 3:** Configure the JAC server to serve static files or use a web server (like nginx)

---

### Option 2: Separate Frontend & Backend Apps (Recommended)

Deploy frontend and backend as separate Heroku apps:

#### Backend Deployment (Already Done)

Your backend is already deployed with the current setup.

#### Frontend Deployment

**Step 1:** Create a new Heroku app for the frontend:

```bash
heroku create your-app-name-frontend
```

**Step 2:** Set the backend API URL as an environment variable:

```bash
heroku config:set REACT_APP_API_URL=https://your-backend-app.herokuapp.com -a your-app-name-frontend
```

Replace `your-backend-app.herokuapp.com` with your actual backend Heroku app URL.

**Step 3:** Create a `heroku-frontend.yml` in the root:

```yaml
build:
  docker:
    web: docker/Dockerfile.heroku_frontend
```

**Step 4:** Deploy the frontend:

```bash
git push heroku main:main
```

Or if you want to use a different branch/config:

```bash
heroku stack:set container -a your-app-name-frontend
git push https://git.heroku.com/your-app-name-frontend.git main
```

---

### Option 3: Quick Fix - Set Environment Variable

If your frontend is already deployed somewhere:

**On Heroku:**

```bash
heroku config:set REACT_APP_API_URL=https://your-backend-app.herokuapp.com
```

**For local testing:**

```bash
cd frontend
REACT_APP_API_URL=https://your-backend-app.herokuapp.com npm start
```

**Or create a `.env` file in the frontend directory:**

```env
REACT_APP_API_URL=https://your-backend-app.herokuapp.com
```

---

## Verification

After setting the API URL, check:

1. **Environment variable is set:**
   ```bash
   heroku config -a your-app-name
   ```

2. **Backend is accessible:**
   ```bash
   curl https://your-backend-app.herokuapp.com/walker/IntakeAgent
   ```

3. **Frontend can reach backend:** Open browser console and check the network tab when submitting a report.

---

## Current Architecture

Based on your setup:

- ✅ Backend: JAC server + NLP service + DB API (running on Heroku)
- ❓ Frontend: Unknown deployment location

### What to Do Next?

1. **Find where your frontend is deployed** (check Heroku apps list: `heroku apps`)
2. **Set `REACT_APP_API_URL` to point to your backend**
3. **Rebuild/redeploy the frontend** (environment variables must be set at build time for React)

```bash
# List all your Heroku apps
heroku apps

# For each app, check its config
heroku config -a app-name
```

