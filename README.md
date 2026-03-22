# Telegram Media Downloader

A privacy-focused desktop app to bulk download media from your Telegram channels and groups.

## Features

- 📢 Select any channel or group you're a member of
- 🗂 Filter by file type — Photos, Videos, Audio, PDF, Word, Excel, ZIP, or any custom extension
- 🔢 Control how many files — Last 20, 50, 100, All, or custom number
- 📅 Choose download order — Newest first or Oldest first
- 📁 Browse and select your download folder
- ⏸ Pause, resume, and cancel downloads anytime
- 🔄 Incremental sync — resumes from where you left off
- 📋 Download history log
- 💻 100% local — no server, no cloud, no third party
- 🔒 Direct connection to Telegram's official API

## Requirements

- Python 3.8+
- A Telegram account
- API credentials from [my.telegram.org](https://my.telegram.org/apps)

## Installation

```bash
git clone https://github.com/randaft20-cloud/Telegram-media-downloader.git
cd Telegram-media-downloader
pip install -r requirements.txt
python main.py
```

## Getting API Credentials

1. Go to [my.telegram.org](https://my.telegram.org/apps)
2. Log in with your phone number
3. Click **Create Application**
4. Copy your `api_id` and `api_hash`

## Usage

1. Run the app
2. Enter your API ID, API Hash and phone number
3. Click **Login** — enter the OTP sent to your Telegram app
4. Select a channel or group from the dropdown
5. Choose file type and how many files to download
6. Click **Start**

## Build as .exe (Windows)

```bash
pyinstaller --onefile --windowed --name="TelegramDownloader" main.py
```

Find your `.exe` in the `dist/` folder.

## Privacy

- All data stays on your machine
- Session files stored locally only
- No analytics, no telemetry, no ads

## Disclaimer

This tool uses the official Telegram API and only works with channels and groups you are already a member of. Use responsibly and in accordance with Telegram's Terms of Service.

## License

MIT License
