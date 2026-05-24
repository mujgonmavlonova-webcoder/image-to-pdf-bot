import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # ── Bot ──────────────────────────────────────────────────────────────
    BOT_TOKEN: str = ""

    # ── File limits ──────────────────────────────────────────────────────
    MAX_FILE_SIZE_MB: int = 20          # per image
    MAX_IMAGES_PER_SESSION: int = 20    # max images combined into one PDF

    # ── Paths ────────────────────────────────────────────────────────────
    TEMP_DIR: str = "temp"

    def __post_init__(self) -> None:
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        if not self.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN is not set. "
                "Please copy .env.example to .env and fill in your token."
            )
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
        self.MAX_IMAGES_PER_SESSION = int(os.getenv("MAX_IMAGES_PER_SESSION", "20"))
        self.TEMP_DIR = os.getenv("TEMP_DIR", "temp")

        # Ensure temp directory exists
        os.makedirs(self.TEMP_DIR, exist_ok=True)


settings = Settings()
