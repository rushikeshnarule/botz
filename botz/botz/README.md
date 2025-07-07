# Telegram NVIDIA Bot for Koyeb

This is a Telegram bot that uses the NVIDIA API for chat completions. It requires users to join a specific channel before using the bot. The bot is ready for deployment on [Koyeb](https://www.koyeb.com/).

## Features
- Text chat with NVIDIA API
- Force subscribe: users must join `@Topdeals_Off` to use the bot
- Health check endpoint for Koyeb

## Requirements
- Python 3.8+
- Telegram bot token
- NVIDIA API key (already in code, replace if needed)
- ffmpeg (for audio, but currently not required)

## Installation
```bash
pip install -r requirements.txt
```

## Environment Variables
- `PORT`: (optional) Port for the health check server (default: 8080)

## Running Locally
```bash
python telegram_nvidia_bot.py
```

## Deploying on Koyeb
1. Push your code to a GitHub repository.
2. Create a new Koyeb service from your repo.
3. Set the build and run command to:
   ```
   python botz/telegram_nvidia_bot.py
   ```
   or use Gunicorn if you want (not required for this async bot).
4. (Optional) Set the `PORT` environment variable if you want a custom port.

## Health Check
Koyeb will check the `/` endpoint (HTTP GET) for a 200 OK response with body `ok`.

## Notes
- The bot only supports text messages. Image and audio messages will receive a not-supported reply.
- Update `CHANNEL_USERNAME` in the code if you change your channel.
- Make sure your bot token is set in the code.

---

For any issues, open an issue or contact the maintainer. 