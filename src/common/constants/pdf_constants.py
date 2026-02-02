# Magic bytes for PDF files
PDF_MAGIC = b"%PDF"

# Allowed extensions
ALLOWED_EXTENSIONS = {".pdf"}

# File size limits
MAX_FILE_SIZE_MB = 100  # 100 MB for PDFs
MAX_PAGES = 5000

# Dangerous PDF features
DANGEROUS_FEATURES = {
    "EmbeddedFile",  # Embedded executable files
    "Launch",  # Launch external programs
    "XObject",  # Potential script execution
    "JavaScript",  # JavaScript in PDFs
    "OpenAction",  # Auto-execute on open
    "SubmitForm",  # Can submit to external URLs
}

# Malicious patterns to detect
MALICIOUS_PATTERNS = {
    "/JS",  # JavaScript
    "/OpenAction",  # Auto-execute
    "/AA",  # Additional actions
    "/EmbeddedFile",  # Embedded files
    "/Launch",  # Launch actions
}
