
Deploy frontend and backend as separate Heroku apps:

#### Backend Deployment 

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