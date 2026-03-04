import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 52428800))
FILE_ID_CACHE_SIZE = int(os.getenv("FILE_ID_CACHE_SIZE", 5000))
DOWNLOADS_DIR = "downloads"
YTDLP_COOKIEFILE = os.getenv("YTDLP_COOKIEFILE", "")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
INSTAGRAM_USER_AGENT = os.getenv("INSTAGRAM_USER_AGENT", os.getenv("USER_AGENT", ""))
INSTAGRAM_X_IG_APP_ID = os.getenv("INSTAGRAM_X_IG_APP_ID", os.getenv("X_IG_APP_ID", ""))
INSTAGRAM_COOKIES = os.getenv("INSTAGRAM_COOKIES", os.getenv("COOKIES", ""))
