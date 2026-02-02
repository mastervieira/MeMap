# Default limits for numeric validation
DEFAULT_MIN_VALUE = float("-inf")
DEFAULT_MAX_VALUE = float("inf")

# Common field configurations
FIELD_CONFIGS = {
    "age": {
        "min": 0,
        "max": 150,
        "description": "Age",
    },
    "percentage": {
        "min": 0,
        "max": 100,
        "description": "Percentage",
    },
    "currency": {
        "min": 0,
        "max": float("inf"),
        "decimal_places": 2,
        "description": "Currency amount",
    },
    "phone": {
        "pattern": r"^\+?[1-9]\d{1,14}$",  # E.164 format
        "description": "Phone number",
    },
    "postal_code": {
        "pattern": r"^\d{4}-\d{3}$",  # Portuguese format XXXX-XXX
        "description": "Postal code",
    },
}

# Allowed separators for decimal numbers
DECIMAL_SEPARATORS = {".", ","}

# Type hints
NUMERIC_TYPES = (int, float)
ALLOWED_TYPES = ("int", "float", "decimal", "percentage")

# Precision for floating point comparisons
FLOAT_TOLERANCE = 1e-9
