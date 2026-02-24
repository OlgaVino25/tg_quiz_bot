from pathlib import Path
from environs import Env


env = Env()
env.read_env()

# Базовые пути
BASE_DIR = Path(__file__).parent
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
PHRASES_PATH = BASE_DIR / "dialog_flow" / "phrases.json"

# Telegram
TG_TOKEN = env.str("TG_TOKEN")
ADMIN_CHAT_ID = env.str("ADMIN_CHAT_ID")
