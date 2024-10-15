import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG_ENABLED = os.environ["DEBUG_ENABLED"] == "1"

DATABASE_URL = os.environ["DATABASE_URL"]
TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

SESSION_EXPIRE_DAYS = int(os.environ["SESSION_EXPIRE_DAYS"])

MEDIA_STORAGE_PATH = os.path.join(BASE_DIR, "media")
GALLERY_STORAGE_PATH = os.path.join(MEDIA_STORAGE_PATH, "gallery")
AVATARS_STORAGE_PATH = os.path.join(MEDIA_STORAGE_PATH, "avatars")

MAX_IMAGE_SIZE_BYTES = int(os.environ["MAX_IMAGE_SIZE_BYTES"])
