import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # Render-dagi Environment Variables-dan tokenini to‘g‘ridan-to‘g‘ri o‘qiymiz
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
        
        # Fayl cheklovlari
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
        self.MAX_IMAGES_PER_SESSION = int(os.getenv("MAX_IMAGES_PER_SESSION", "20"))
        
        # Vaqtinchalik papka
        self.TEMP_DIR = os.getenv("TEMP_DIR", "temp")
        
        # Papka mavjudligini tekshirish va yaratish
        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR, exist_ok=True)

settings = Settings()
BOT_TOKEN = settings.BOT_TOKEN
