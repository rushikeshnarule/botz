import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import base64
import tempfile
from io import BytesIO
import asyncio
from aiohttp import web

# For audio transcription and TTS
import speech_recognition as sr
from gtts import gTTS

# NVIDIA API details
invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Accept": "text/event-stream"
}

# Model for text+image
MULTIMODAL_MODEL = "nvidia/neva-22b"
# Model for text only
TEXT_MODEL = "google/gemma-3n-e4b-it"

CHANNEL_USERNAME = "@Topdeals_Off"  # Updated to your actual channel username

async def force_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception:
        pass
    join_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
    ])
    await update.message.reply_text(
        "You must join our channel to use this bot.",
        reply_markup=join_button
    )
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_subscribe(update, context):
        return
    await update.message.reply_text("Hello! Send me a message, photo, or voice note and I'll reply using NVIDIA's API.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_subscribe(update, context):
        return
    user_message = update.message.text
    payload = {
        "model": TEXT_MODEL,
        "messages": [{"role": "user", "content": user_message}],
        "max_tokens": 512,
        "temperature": 0.20,
        "top_p": 0.70,
        "frequency_penalty": 0.00,
        "presence_penalty": 0.00,
        "stream": True
    }
    await send_nvidia_response(update, payload)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_subscribe(update, context):
        return
    await update.message.reply_text("Sorry, image messages are not supported right now.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_subscribe(update, context):
        return
    await update.message.reply_text("Sorry, audio messages are not supported right now.")

def parse_stream_response(response):
    full_reply = ""
    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith('data: '):
                data = decoded[6:]
                if data == '[DONE]':
                    break
                try:
                    import json
                    chunk = json.loads(data)
                    content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                    full_reply += content
                except Exception:
                    continue
    return full_reply or "(No response from NVIDIA API)"

async def send_nvidia_response(update, payload):
    try:
        response = requests.post(invoke_url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        full_reply = parse_stream_response(response)
    except Exception as e:
        full_reply = f"Error: {e}"
    await update.message.reply_text(full_reply)

async def get_nvidia_response_text(payload):
    try:
        response = requests.post(invoke_url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        return parse_stream_response(response)
    except Exception as e:
        return f"Error: {e}"

def get_app():
    app = ApplicationBuilder().token("8164728305:AAF8JwZ-OlmPT6ySYUsj7c3UhERF8uQUtLU").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    return app

async def health(request):
    return web.Response(text="ok")

async def main():
    # Start Telegram bot
    app = get_app()
    bot_task = asyncio.create_task(app.run_polling())
    # Start aiohttp web server for health check
    app_web = web.Application()
    app_web.router.add_get("/", health)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()
    print("Bot and health server running...")
    await bot_task

if __name__ == "__main__":
    asyncio.run(main()) 