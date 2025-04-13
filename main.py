import os
import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext
from huggingface_hub import hf_hub_download
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load bot token and Hugging Face token from .env file
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
HF_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')

# Hugging Face API setup
hf_model = "CompVis/stable-diffusion-v-1-4-original"  # Choose the appropriate model

# Define the function to generate the thumbnail
def generate_thumbnail(prompt: str):
    # Use Hugging Face's API to generate the image
    headers = {
        'Authorization': f'Bearer {HF_TOKEN}'
    }
    
    response = requests.post(
        f'https://api-inference.huggingface.co/models/{hf_model}',
        headers=headers,
        json={"inputs": prompt}
    )
    
    # Process the image data returned from Hugging Face
    image = Image.open(BytesIO(response.content))

    # Add text overlay
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text = "Hook Text"
    draw.text((10, 10), text, fill="white", font=font)
    
    return image

# Define the start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the Thumbnail Generator Bot! Use /thumbnail command.")

# Define the thumbnail command
def thumbnail(update: Update, context: CallbackContext) -> None:
    prompt = " ".join(context.args)  # Get the user's prompt from the message
    if not prompt:
        update.message.reply_text("Please provide a prompt!")
        return

    # Generate the thumbnail
    image = generate_thumbnail(prompt)

    # Save the image to send it on Telegram
    image_path = "thumbnail.png"
    image.save(image_path)

    # Send the thumbnail to the user
    update.message.reply_photo(photo=open(image_path, 'rb'))

# Main function to run the bot
def main() -> None:
    """Start the bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("thumbnail", thumbnail))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
