import os
import uuid
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}


def is_valid_image(filename: str, mime_type: str | None = None) -> bool:
    """Return True if the file extension (and optional MIME type) are allowed."""
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        return False
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        return False
    return True


def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert bytes to megabytes, rounded to 2 decimal places."""
    return round(file_size_bytes / (1024 * 1024), 2)


def build_temp_path(directory: str, extension: str = "") -> str:
    """Return a unique file path inside *directory*."""
    filename = f"{uuid.uuid4().hex}{extension}"
    return os.path.join(directory, filename)


def cleanup_files(*paths: str) -> None:
    """Silently delete every file path supplied."""
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                logger.debug("Deleted temp file: %s", path)
        except OSError as exc:
            logger.warning("Could not delete %s: %s", path, exc)
