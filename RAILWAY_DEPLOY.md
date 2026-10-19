# Railway Deploy Instructions — Twin Cities Restoration Lead Prototype

## Files ready for Railway
- `gc_lead_prototype.py` — Flask app (updated to use Railway's `$PORT`)
- `requirements.txt` — flask + gunicorn
- `Procfile` — start command

## Deploy steps

1. Create a free Railway account at https://railway.app
2. Create a new project → **Deploy from GitHub repo** (recommended) or use the Railway CLI.
3. If using GitHub:
   - Push these three files into a new repository.
   - Connect the repo to Railway.
4. Railway will detect the Python app and the Procfile.
5. Once deployed, Railway gives you a public URL (e.g. `https://your-app.up.railway.app`).
6. Open that URL for the form; append `/dashboard` for the contractor view.

## Notes
- Leads are stored in memory. They reset if the service restarts or sleeps. This is fine for demos; production would use a database.
- Free tier may sleep after inactivity. The first request after sleep can take a few seconds.
- No environment variables are required for this prototype.

## Optional: Railway CLI alternative
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

After deploy, share the public URL. The form and dashboard will be reachable from any browser.
