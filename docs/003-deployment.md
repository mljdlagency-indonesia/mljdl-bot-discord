# 003 — Deployment Guide

## Perbandingan Server Gratis & Murah

| Platform | Free Tier | Always On? | Limit | Cocok Untuk |
|----------|-----------|------------|-------|-------------|
| **Railway** | $5 credit/bulan | ✅ Ya | Habis credit = stop | Bot kecil, paling gampang setup |
| **Render** | Free tier | ❌ Sleep 15 min idle | 750 jam/bulan | Web service (bukan bot) |
| **Fly.io** | 3 shared VMs | ✅ Ya | 256MB RAM, 3GB disk | Bot 24/7, stabil |
| **Oracle Cloud** | Always Free | ✅ Ya | 1GB RAM, 1 CPU | **Terbaik gratis** — VPS full |
| **Google Cloud** | e2-micro free | ✅ Ya | 1GB RAM | VPS, perlu setup manual |
| **Replit** | Free tier | ❌ Sleep | Limited | Testing saja |
| **VPS Murah** | ~$3-5/bulan | ✅ Ya | Tergantung plan | Contabo, Hetzner, DigitalOcean |

### Rekomendasi:
1. **Gratis terbaik** → Oracle Cloud Free Tier (VPS selamanya gratis, 1GB RAM)
2. **Paling gampang** → Railway (connect GitHub, auto deploy)
3. **Murah & reliable** → Fly.io atau VPS $3-5/bulan

---

## Option 1: Railway (Paling Gampang)

### Step 1: Siapkan file deployment

Buat file `Procfile` di root project:
```
worker: python run.py
```

> **Penting:** pakai `worker`, bukan `web`. Bot Discord bukan web server.

### Step 2: Push ke GitHub
```bash
git add -A
git commit -m "ready for deploy"
git push
```

### Step 3: Deploy di Railway
1. Buka [railway.app](https://railway.app) → Login pakai GitHub
2. **New Project** → **Deploy from GitHub Repo**
3. Pilih repo `mljdl-bot-discord`
4. Railway akan auto-detect Python

### Step 4: Set Environment Variables
Di Railway dashboard → project → **Variables** tab:
```
DISCORD_TOKEN=your_token
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":...}
SPREADSHEET_ID=your_sheet_id
SHEET_NAME=Sheet1
GITHUB_TOKEN=ghp_xxxx
GITHUB_REPO=username/repo
GITHUB_POLL_INTERVAL=300
GITHUB_NOTIF_CHANNEL_ID=123456789
```

> **Tips:** Untuk `GOOGLE_SERVICE_ACCOUNT_JSON`, paste isi JSON langsung (bukan file path). Bot sudah support JSON string.

### Step 5: Deploy
Railway auto-deploy setiap push ke GitHub. Cek **Logs** tab untuk pastiin bot jalan.

---

## Option 2: Fly.io

### Step 1: Install Fly CLI
```bash
# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Login
fly auth login
```

### Step 2: Buat Dockerfile
Buat file `Dockerfile` di root project:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

Buat file `.dockerignore`:
```
.git
.env
__pycache__
*.pyc
db/
bot.log
```

### Step 3: Launch App
```bash
cd mljdl-bot-discord

# Buat app (pilih region terdekat, misal sin = Singapore)
fly launch --no-deploy

# Set environment variables
fly secrets set DISCORD_TOKEN=your_token
fly secrets set GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
fly secrets set SPREADSHEET_ID=your_sheet_id
fly secrets set SHEET_NAME=Sheet1
fly secrets set GITHUB_TOKEN=ghp_xxxx
fly secrets set GITHUB_REPO=username/repo
fly secrets set GITHUB_POLL_INTERVAL=300
fly secrets set GITHUB_NOTIF_CHANNEL_ID=123456789
```

### Step 4: Edit fly.toml
Pastikan `fly.toml` TIDAK ada `[http_service]` section (bot bukan web server).
Tambahkan:
```toml
[processes]
  app = "python run.py"
```

### Step 5: Deploy
```bash
fly deploy
fly logs  # cek log
```

---

## Option 3: Oracle Cloud Free Tier (VPS Gratis Selamanya)

### Step 1: Daftar Oracle Cloud
1. Buka [cloud.oracle.com](https://cloud.oracle.com) → Sign Up
2. Pilih region (Singapore/Tokyo recommended)
3. Perlu kartu kredit untuk verifikasi, tapi **TIDAK dicharge**

### Step 2: Buat VM Instance
1. Dashboard → **Compute** → **Instances** → **Create Instance**
2. Image: **Ubuntu 22.04** (atau 24.04)
3. Shape: **VM.Standard.E2.1.Micro** (Always Free)
4. Download SSH key pair
5. Create

### Step 3: Connect via SSH
```bash
ssh -i path/to/private_key ubuntu@<public-ip>
```

### Step 4: Setup di Server
```bash
# Install Python
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# Clone repo
git clone https://github.com/username/mljdl-bot-discord.git
cd mljdl-bot-discord

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Buat .env
nano .env
# Paste semua environment variables, save (Ctrl+X, Y, Enter)

# Test run dulu
python run.py
# Kalau jalan, Ctrl+C untuk stop
```

### Step 5: Jalankan sebagai System Service (Auto-start)
```bash
sudo nano /etc/systemd/system/discord-bot.service
```

Paste ini:
```ini
[Unit]
Description=Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/mljdl-bot-discord
ExecStart=/home/ubuntu/mljdl-bot-discord/venv/bin/python run.py
Restart=always
RestartSec=10
EnvironmentFile=/home/ubuntu/mljdl-bot-discord/.env

[Install]
WantedBy=multi-user.target
```

```bash
# Enable & start
sudo systemctl enable discord-bot
sudo systemctl start discord-bot

# Cek status
sudo systemctl status discord-bot

# Lihat logs
sudo journalctl -u discord-bot -f
```

### Step 6: Auto-update dari GitHub (Optional)
```bash
# Buat script update
nano ~/update-bot.sh
```
```bash
#!/bin/bash
cd /home/ubuntu/mljdl-bot-discord
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart discord-bot
echo "Bot updated and restarted!"
```
```bash
chmod +x ~/update-bot.sh
# Setiap mau update: ~/update-bot.sh
```

---

## File Deployment yang Perlu Ditambahkan

### Procfile (untuk Railway/Render)
```
worker: python run.py
```

### Dockerfile (untuk Fly.io/Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

### .dockerignore
```
.git
.env
__pycache__
*.pyc
db/
bot.log
```

### .gitignore (kalau belum ada)
```
.env
__pycache__/
*.pyc
db/
bot.log
venv/
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot offline setelah beberapa jam | Pakai `worker` di Procfile, bukan `web`. Atau pakai VPS |
| `ModuleNotFoundError` | Pastikan `requirements.txt` lengkap dan `pip install` jalan |
| Bot crash loop | Cek logs, biasanya token salah atau env var kosong |
| Google Sheets error | Pastikan service account email sudah di-share ke spreadsheet |
| GitHub rate limit | Naikkan `GITHUB_POLL_INTERVAL` ke 600+ detik |
| Database hilang setelah redeploy | Normal di Railway/Fly.io (ephemeral storage). Pakai volume untuk persist |

### Persist Database di Fly.io
```bash
# Buat volume
fly volumes create bot_data --size 1 --region sin

# Tambah di fly.toml
[mounts]
  source = "bot_data"
  destination = "/app/db"
```

### Persist Database di Railway
Railway otomatis persist filesystem antar deploy (selama pakai disk yang sama).
