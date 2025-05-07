import logging
import yt_dlp
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Application
from googleapiclient.discovery import build
import os

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# YouTube API setup
YOUTUBE_API_KEY = "AIzaSyDQS3urJ1EH-uA-vPe5iSyyJUF8AQGTsmc"
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Telegram bot token
TELEGRAM_TOKEN = '7958349245:AAEeqmkY9a8B4poweWOvVyeDr3mH-pByZCg'

# Function to fetch video metadata
def get_video_metadata(url):
    video_id = url.split('v=')[-1]
    request = youtube.videos().list(part='snippet,contentDetails', id=video_id)
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        video_info = response['items'][0]
        title = video_info['snippet']['title']
        description = video_info['snippet']['description']
        return title, description
    return None, None

# Command to start the bot
async def start(update: Update, context):
    await update.message.reply_text("Welcome! Send me a YouTube link to get started.")

# Function to download the YouTube video or audio
async def download_video(update: Update, context):
    url = update.message.text.strip()

    # Fetch metadata
    title, description = get_video_metadata(url)
    if title and description:
        await update.message.reply_text(f"Video: {title}\nDescription: {description}")
    else:
        await update.message.reply_text("Could not fetch video details.")

    # Download audio or video using yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            await update.message.reply_text(f"Download complete: {filename}")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

# Main function to set up the bot
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))

    # Run the bot
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
  
