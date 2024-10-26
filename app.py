import asyncio
import os

import dotenv
import requests
from deep_translator import GoogleTranslator
from telegram import Bot
from telegram.error import TelegramError

dotenv.load_dotenv(dotenv_path="./.env")

# Constants for Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
SERVER_AUTH_TOKEN = os.getenv("SERVER_AUTH_TOKEN")
SERVER_URL = os.getenv("SERVER_URL")

# Validate that essential environment variables are set
if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, SERVER_AUTH_TOKEN, SERVER_URL]):
    raise EnvironmentError("One or more required environment variables are missing.")


async def post_to_telegram(message: str):
    """Post a translated message on a Telegram channel asynchronously."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    try:
        translated = GoogleTranslator(source="en", target="fa").translate(message)
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=translated)
        print(f"Post successfully shared on Telegram channel in Dari: {translated}")
    except TelegramError as e:
        print(f"Failed to post on Telegram due to Telegram API error: {e}")
    except Exception as e:
        print(f"Translation failed or other error: {e}")


def fetch_data() -> dict:
    """Fetch job post data from the API."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {SERVER_AUTH_TOKEN}",
    }
    try:
        res = requests.get(url=f"{SERVER_URL}/api/share/", headers=headers)
        res.raise_for_status()  # Raises HTTPError for non-200 responses
        return res.json()
    except requests.RequestException as e:
        print(f"Error fetching data from server: {e}")
        raise


def format_post(data: dict) -> str:
    """Format the job post data into a readable message."""
    post = (
        f"Job Title: {data.get('title', 'N/A')}\n"
        f"Job Vacancy Number: {data.get('vacancy_number', 'N/A')}\n"
        f"Organization: {data.get('organization', {}).get('name', 'N/A')}\n"
        f"Location: {data.get('location', {}).get('name', 'N/A')}\n"
        f"Employment Type: {data.get('employment_type', 'N/A')}\n"
    )
    if data.get("gender"):
        post += f"Gender Requirement: {data.get('gender', 'N/A')}\n"
    if data.get("salary"):
        post += f"Salary: {data.get('salary', 'N/A')}\n"
    post += (
        f"Contract Duration: {data.get('contract_duration', 'N/A')}\n"
        f"Minimum Education: {data.get('minimum_education', 'N/A')}\n"
        f"Application Deadline: {data.get('expire_date', 'N/A')}\n"
        f"\nhttps://www.karyab.org/jobs/{data.get('slug')}"
    )
    return post


async def main():
    """Main function to fetch job post data and post it to Telegram."""
    try:
        data = fetch_data()
        post = format_post(data)
        await post_to_telegram(post)
    except Exception as e:
        print(f"An error occurred during the process: {e}")


if __name__ == "__main__":
    # Run the main function asynchronously
    asyncio.run(main())
