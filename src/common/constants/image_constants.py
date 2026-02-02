# Magic bytes for image formats
PNG_MAGIC = b"\x89PNG"
JPG_MAGIC = b"\xff\xd8\xff"
GIF_MAGIC = b"GIF8"
BMP_MAGIC = b"BM"
WEBP_MAGIC = b"RIFF"

# Allowed extensions
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/bmp",
    "image/webp",
}

# Allowed PIL formats
ALLOWED_PIL_FORMATS = {"PNG", "JPEG", "GIF", "BMP", "WEBP"}

# File size limits
MAX_FILE_SIZE_MB = 50  # 50 MB for images
MAX_DIMENSIONS = (8192, 8192)  # Max width x height
MIN_DIMENSIONS = (1, 1)

# Cache configuration
CACHE_DIR = "cache/images"
CACHE_ENABLED = True

# EXIF data - metadata to strip (contains sensitive info)
EXIF_TAGS_TO_STRIP = {
    "DateTime",
    "DateTimeOriginal",
    "DateTimeDigitized",
    "GPSInfo",
    "Make",
    "Model",
    "Software",
    "Copyright",
    "Artist",
}
