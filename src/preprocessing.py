import re


def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def is_delimiter_only(text, delimiters):
    return text.strip() in delimiters


def ends_with_delimiter(text, delimiters):
    text = text.strip()
    return len(text) > 0 and text[-1] in delimiters

def word_records_to_ingredient_records(word_records, delimiters):
    ingredients = []

    current_ingredient = []
    current_ingredient_text = []

    for token in word_records:
        raw_text = token["raw_text"]  # For spotting boundaries between ingredients
        clean_text = token["clean_text"]  # For matching to allergen list

        # This prevents tokens being appended if they're just ";"
        if clean_text:
            # Creating list of current ingredients before appending
            current_ingredient_text.append(clean_text)

            # For drawing bounding box of each ingredient token
            current_ingredient.append(
                {
                    "raw_text": raw_text,
                    "top_left": token["top_left"],
                    "bottom_right": token["bottom_right"],
                }
            )

        # Once we get to a token that ends with a delimiter or is a solo delimiter we append and restart
        if ends_with_delimiter(raw_text, delimiters) or is_delimiter_only(raw_text, delimiters):
            full_current_ingredient_text = " ".join(current_ingredient_text).strip()
            ingredients.append(
                {
                    "ingredient_text": full_current_ingredient_text,
                    "words": current_ingredient.copy(),
                }
            )
            current_ingredient = []
            current_ingredient_text = []
    # Fallback in case there is no delimiter at the end of the ingredients list
    if current_ingredient:
        full_current_ingredient_text = " ".join(current_ingredient_text).strip()
        ingredients.append(
            {
                "ingredient_text": full_current_ingredient_text,
                "words": current_ingredient.copy(),
            }
        )
        current_ingredient = []
        current_ingredient_text = []

    return ingredients