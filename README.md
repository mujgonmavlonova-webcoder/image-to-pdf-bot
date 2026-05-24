# 🖼️ Image → PDF Telegram Bot

A clean, production-ready Telegram bot that converts JPG/PNG images into a
single PDF file. Built with **Python 3.11+**, **Aiogram 3**, **Pillow**, and
**img2pdf**.

---

## ✨ Features

| Feature | Detail |
|---|---|
| Image formats | JPG, JPEG, PNG |
| Multi-image | Queue up to 20 images → one PDF |
| File validation | Type check + size limit per image |
| Async I/O | Non-blocking downloads & conversion |
| Auto-cleanup | Temp files deleted after every session |
| Secure config | Secrets via `.env` / env variables |
| Render-ready | Zero-config deployment on Render.com |

---

## 🤖 Bot Commands

| Command | Action |
|---|---|
| `/start` | Welcome message & instructions |
| `/help` | Same as `/start` |
| `/convert` | Convert queued images to PDF |
| `/cancel` | Clear the current image queue |

---

## 🗂 Project Structure

```
image2pdf_bot/
├── main.py                 # Entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/
│   ├── __init__.py
│   └── settings.py         # Loads .env, validates BOT_TOKEN
│
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start and /help
│   └── image.py            # photo/document upload, /convert, /cancel
│
├── services/
│   ├── __init__.py
│   └── pdf_service.py      # img2pdf + Pillow conversion logic
│
├── utils/
│   ├── __init__.py
│   └── file_helpers.py     # Validation, temp paths, cleanup
│
└── temp/                   # Auto-created; holds in-flight files
    └── .gitkeep
```

---

## 🚀 Local Setup

### 1. Prerequisites

- Python 3.11 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### 2. Clone the repository

```bash
git clone https://github.com/<your-username>/image2pdf-bot.git
cd image2pdf-bot
```

### 3. Create a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your token:

```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxYZ
```

### 6. Run the bot

```bash
python main.py
```

You should see:

```
2024-01-01 12:00:00 | INFO     | __main__ | Starting Image → PDF Bot…
2024-01-01 12:00:00 | INFO     | __main__ | Bot is running. Press Ctrl+C to stop.
```

Open Telegram, find your bot, and send `/start`. 🎉

---

## ☁️ Deploying to Render

Render offers a **free tier** that is perfect for hobby bots.

### Step 1 – Push to GitHub

```bash
# Inside the project folder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/image2pdf-bot.git
git push -u origin main
```

### Step 2 – Create a new Render Web Service

1. Go to [https://render.com](https://render.com) and sign in.
2. Click **New** → **Web Service**.
3. Connect your GitHub account and select the `image2pdf-bot` repository.

### Step 3 – Configure the service

| Setting | Value |
|---|---|
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |
| **Instance Type** | Free (or Starter for always-on) |

### Step 4 – Add environment variable

In the **Environment** tab of your Render service:

| Key | Value |
|---|---|
| `BOT_TOKEN` | `123456789:ABCdefGhIJKlmNoPQRsTUVwxYZ` |

> ⚠️ **Never** commit your real `.env` file to GitHub.
> The `.gitignore` already excludes it.

### Step 5 – Deploy

Click **Create Web Service**. Render will:
1. Pull your code from GitHub.
2. Run `pip install -r requirements.txt`.
3. Start `python main.py`.

Every future `git push` to `main` automatically triggers a re-deploy.

---

## ⚙️ Configuration Reference

All options live in `.env` (or as Render environment variables).

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | *(required)* | Telegram bot token |
| `MAX_FILE_SIZE_MB` | `20` | Max size per uploaded image |
| `MAX_IMAGES_PER_SESSION` | `20` | Max images per conversion |
| `TEMP_DIR` | `temp` | Directory for temporary files |

---

## 🛠 Tech Stack

- [Python 3.11+](https://www.python.org/)
- [Aiogram 3](https://docs.aiogram.dev/) – async Telegram Bot API framework
- [img2pdf](https://pypi.org/project/img2pdf/) – lossless image-to-PDF conversion
- [Pillow](https://pillow.readthedocs.io/) – image processing & fallback PDF writer
- [python-dotenv](https://pypi.org/project/python-dotenv/) – `.env` loader

---

## 📄 License

MIT – use freely, attribution appreciated.
