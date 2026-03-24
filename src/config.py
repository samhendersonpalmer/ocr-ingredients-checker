from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models" / "easyocr"
FAVICON_PATH = BASE_DIR / "assets" / "favicon.png"
LOGO_PATH = BASE_DIR / "assets" / "logo.png"
JSON_PATH = BASE_DIR / "assets" / "data" / "allergens_cleaned.json"

with open(JSON_PATH, "r", encoding="utf-8") as file:
    ALLERGEN_LIST = json.load(file)

DELIMITERS = {",", ";", ":"}
