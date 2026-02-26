import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 52428800))
DOWNLOADS_DIR = "downloads"
