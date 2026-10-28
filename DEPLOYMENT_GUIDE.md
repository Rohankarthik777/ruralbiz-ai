# 🚀 RuralBiz AI - Deployment Guide

This guide covers all options to deploy your **RuralBiz AI** web application:
1. **Render.com** (Recommended — 100% Free, Automated HTTPS)
2. **Railway.app** (Great for persistent SQLite storage)
3. **Instant Public URL (Cloudflare Tunnel / Ngrok)** (Demo in 60 seconds from your PC)
4. **Docker / Cloud VPS (AWS, DigitalOcean, Azure, Linode)**
5. **Local Network / Wi-Fi Access (Testing on Mobile Phone)**

---

## Option 1: Free Cloud Deployment via Render.com (Recommended)

Render provides free hosting for Python web services with automatic HTTPS (`https://your-app.onrender.com`).

### Steps:
1. **Push your code to GitHub**:
   - Create a new repository on [github.com](https://github.com) (e.g., `ruralbiz-ai`).
   - Push your project files to the repository.

2. **Connect to Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and sign up/log in (using GitHub).
   - Click **"New +"** → **"Web Service"**.
   - Select your `ruralbiz-ai` repository.

3. **Configure Settings** (Render will auto-fill from `render.yaml`):
   - **Name**: `ruralbiz-ai`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Instance Type**: `Free`

4. **Environment Variables** (Optional):
   - `SESSION_SECRET`: Any random secret string
   - `GEMINI_API_KEY`: *(Optional)* Your Google Gemini API key if you want live dynamic LLM responses.

5. Click **"Deploy Web Service"**.
   - Within 2-3 minutes, your live site will be accessible at:
     👉 `https://ruralbiz-ai.onrender.com`

---

## Option 2: Railway.app (Persistent Storage)

Railway is optimal for apps with SQLite databases because it allows attaching a persistent volume to preserve transaction records across redeployments.

### Steps:
1. Push project to GitHub.
2. Go to [railway.app](https://railway.app) and click **"New Project"** → **"Deploy from GitHub repo"**.
3. Railway automatically detects `railway.json` and `Procfile`.
4. In Settings → **Networking**, click **"Generate Domain"** to get a public URL (e.g., `https://ruralbiz-ai.up.railway.app`).

---

## Option 3: Instant Public Demo URL in 60 Seconds (Zero Cloud Setup)

If you have a demonstration, pitch, or presentation and want judges or users to access the live app on their phones **right now** directly from your running local instance:

### Using Cloudflare Tunnel (Free, No Account Needed):
1. Download [cloudflared for Windows](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe).
2. Open PowerShell and run:
   ```powershell
   .\cloudflared-windows-amd64.exe tunnel --url http://127.0.0.1:8000
   ```
3. Cloudflare will print an instant public HTTPS URL, for example:
   👉 `https://rural-business-tamil.trycloudflare.com`
   Anyone anywhere in the world can open this link on their mobile browser immediately!

### Or Using Ngrok:
```powershell
ngrok http 8000
```

---

## Option 4: Docker Container Deployment

The project includes a production `Dockerfile` and `docker-compose.yml`.

### Build & Run locally or on any Linux VPS:
```bash
# 1. Build the Docker image
docker build -t ruralbiz-ai .

# 2. Run container
docker run -d -p 8000:8000 --name ruralbiz ruralbiz-ai
```

### Or using Docker Compose:
```bash
docker compose up -d
```
Visit `http://localhost:8000`.

---

## Option 5: Accessing from Your Mobile Phone on the Same Wi-Fi (LAN)

Because `run.py` is configured to listen on `0.0.0.0`, any device on your local Wi-Fi network (like your phone or tablet) can access it immediately!

1. Find your computer's local IP address:
   ```powershell
   ipconfig
   ```
   Look for `IPv4 Address` (e.g., `192.168.1.45`).

2. On your mobile phone (connected to the same Wi-Fi), open Chrome or Safari and type:
   👉 `http://192.168.1.45:8000`

---

## 🔒 Production Checklist

- [x] Host set to `0.0.0.0` for container & cloud compatibility.
- [x] Port dynamically configured via `PORT` environment variable.
- [x] SQLite database auto-initializes on startup with tables & indexes.
- [x] Salted PBKDF2 password hashing enabled.
- [x] Static assets and CSS configured for production caching.
- [x] Optional Gemini API key configurable via env or in-app UI.
