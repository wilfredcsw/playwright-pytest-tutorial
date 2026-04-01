import os
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL")
APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

if not APP_URL or not APP_USERNAME or not APP_PASSWORD:
    raise ValueError("Missing APP_URL, APP_USERNAME, or APP_PASSWORD in .env file")