from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models" / "easyocr"
FAVICON_PATH = BASE_DIR / "assets" / "favicon.png"
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

ALLERGEN_LIST = ["Coconut oil", "Beeswax", "Tocopherol", "Paraben"]

DELIMITERS = {",", ";", ":"}

OCR_LANGUAGES = ["en"]
