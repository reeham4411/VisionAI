from PIL import Image
import io


ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class InvalidImageError(Exception):
    """Raised when uploaded file is not a valid image."""
    pass


def load_image(image_bytes: bytes) -> Image.Image:
    """
    Loads image safely from raw bytes.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verify integrity
        image = Image.open(io.BytesIO(image_bytes))  # Reload after verify
    except Exception:
        raise InvalidImageError("Uploaded file is not a valid image.")

    if image.format not in ALLOWED_FORMATS:
        raise InvalidImageError(
            f"Unsupported image format: {image.format}. "
            f"Allowed formats: {ALLOWED_FORMATS}"
        )

    return image


def normalize_image(
    image: Image.Image,
    max_size: int = 1024
) -> Image.Image:
    """
    Converts image to RGB and resizes while maintaining aspect ratio.
    """
    image = image.convert("RGB")

    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size))

    return image


def image_to_bytes(image: Image.Image) -> bytes:
    """
    Converts PIL Image back to bytes.
    """
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()
