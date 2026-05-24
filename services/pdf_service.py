"""
pdf_service.py
~~~~~~~~~~~~~~
Converts a list of image file paths into a single PDF file.

Strategy
--------
1. Try img2pdf first – it produces pixel-perfect, lossless PDFs very fast
   because it embeds JPEG/PNG data directly without re-encoding.
2. Fall back to Pillow for any image that img2pdf cannot handle
   (e.g. palette-mode PNGs, CMYK JPEGs, 16-bit images).
"""

import asyncio
import logging
import os
from pathlib import Path

import img2pdf
from PIL import Image

logger = logging.getLogger(__name__)


def _convert_sync(image_paths: list[str], output_path: str) -> str:
    """
    Blocking conversion – called via asyncio.to_thread so it never
    blocks the event loop.

    Returns the output_path on success, raises on failure.
    """
    # --- normalise images so img2pdf can handle them ---
    prepared: list[str] = []
    cleanup_later: list[str] = []

    for src in image_paths:
        try:
            with Image.open(src) as img:
                # img2pdf only handles RGB / RGBA / L (greyscale)
                if img.mode not in ("RGB", "RGBA", "L"):
                    converted_path = src + "_converted.png"
                    img.convert("RGB").save(converted_path, "PNG")
                    prepared.append(converted_path)
                    cleanup_later.append(converted_path)
                else:
                    prepared.append(src)
        except Exception as exc:
            logger.warning("Could not pre-process %s: %s", src, exc)
            prepared.append(src)  # try as-is

    try:
        pdf_bytes = img2pdf.convert(prepared)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
    except Exception as exc:
        logger.warning("img2pdf failed (%s), falling back to Pillow.", exc)
        _pillow_fallback(prepared, output_path)
    finally:
        for path in cleanup_later:
            try:
                os.remove(path)
            except OSError:
                pass

    return output_path


def _pillow_fallback(image_paths: list[str], output_path: str) -> None:
    """Pure-Pillow PDF writer used when img2pdf fails."""
    images: list[Image.Image] = []
    for path in image_paths:
        img = Image.open(path).convert("RGB")
        images.append(img)

    if not images:
        raise ValueError("No images could be opened for PDF conversion.")

    first, rest = images[0], images[1:]
    first.save(
        output_path,
        "PDF",
        save_all=True,
        append_images=rest,
    )

    for img in images:
        img.close()


async def convert_images_to_pdf(
    image_paths: list[str],
    output_path: str,
) -> str:
    """
    Async wrapper around the blocking _convert_sync function.

    Parameters
    ----------
    image_paths : list of absolute/relative paths to source images
    output_path : where to write the resulting PDF

    Returns
    -------
    output_path (str) – the path of the generated PDF
    """
    if not image_paths:
        raise ValueError("image_paths must not be empty.")

    # Validate all source files exist before doing any work
    for path in image_paths:
        if not Path(path).is_file():
            raise FileNotFoundError(f"Image file not found: {path}")

    logger.info(
        "Converting %d image(s) → %s", len(image_paths), output_path
    )

    result = await asyncio.to_thread(_convert_sync, image_paths, output_path)
    logger.info("PDF created successfully: %s", result)
    return result
