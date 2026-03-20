import numpy as np
import streamlit as st
from PIL import Image

from src.config import (
    ALLERGEN_LIST,
    DELIMITERS,
    FAVICON_PATH,
    LOGO_PATH,
    MODEL_DIR,
    OCR_LANGUAGES,
)
from src.annotate import draw_matched_ingredients
from src.matching import flag_matching_ingredients, normalize_allergen_list
from src.ocr import load_ocr_model, ocr_to_word_records, run_ocr
from src.preprocessing import normalize_text, word_records_to_ingredient_records

st.set_page_config(page_title="AllergyScanner", page_icon=str(FAVICON_PATH))

col1, col2 = st.columns([5, 1], vertical_alignment="center")

with col1:
    st.markdown('## Allergy:color[Scanner]{foreground = "#215F9A"}')
with col2:
    st.image("assets/logo.png", width=90)


st.markdown(
    "Scan product ingredients to check if it contains one of your contact allergens or its cousins. Built by "
    "[samhendersonpalmer](https://www.linkedin.com/in/samhendersonpalmer/) - "
    "view project source code on "
    "[GitHub](https:/github.com/samhendersonpalmer/ocr-ingredients-checker)"
)

st.space()


def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def ocr_to_word_records(ocr_result):
    word_records = []

    for bbox, text, confidence in ocr_result:
        # x and y coordinates of top_left rectangle
        top_left = tuple((int(val) for val in bbox[0]))
        # x and y coordinates of bottom right rectangle
        bottom_right = tuple((int(val) for val in bbox[2]))

        word_records.append(
            {
                "raw_text": text,
                "clean_text": normalize_text(text),
                "top_left": top_left,
                "bottom_right": bottom_right,
            }
        )

    return word_records


def is_delimiter_only(text):
    return text.strip() in DELIMITERS


def ends_with_delimiter(text):
    text = text.strip()
    return len(text) > 0 and text[-1] in DELIMITERS


def word_records_to_ingredient_records(word_records):
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
        if ends_with_delimiter(raw_text) or is_delimiter_only(raw_text):
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


def normalize_allergen_list(allergen_list):
    return {normalize_text(allergen) for allergen in allergen_list}


def mark_matching_ingredients(ingredient_records, normalized_allergens):
    for ingredient in ingredient_records:
        # Does any user defined allergen match this ingredient
        ingredient["is_match"] = any(
            allergen in ingredient["ingredient_text"]
            for allergen in normalized_allergens
        )
    return ingredient_records


def draw_matched_ingredients(img, ingredient_records):
    output_img = img.copy()

    for ingredient in ingredient_records:
        if ingredient["is_match"]:
            for word in ingredient["words"]:
                output_img = cv2.rectangle(
                    output_img, word["top_left"], word["bottom_right"], (0, 255, 0), 2
                )
    return output_img


tab1, tab2 = st.tabs(["1. Select your allergens", "2. Scan ingredients"])

with tab1:
    st.subheader("1. Select your contact allergens")

    selected_allergens = st.multiselect(
        label="All contact allergens",
        label_visibility="hidden",
        placeholder="Type to search",
        options=ALLERGEN_LIST,
    )

with tab2:
    st.subheader("2. Scan the product ingredients")

    uploaded_file = st.file_uploader(
        label="Take picture of ingredients list",
        label_visibility="hidden",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        input_image = Image.open(uploaded_file)

        with st.spinner("Scanning image"):
            result = reader.readtext(
                input_image, width_ths=0, adjust_contrast=0.5, paragraph=False
            )
            img = np.array(input_image)

            DELIMITERS = {",", ";", ":"}

            outputocr = ocr_to_word_records(result)
            ingredients = word_records_to_ingredient_records(outputocr)
            normalised_allergens = normalize_allergen_list(selected_allergens)
            ingredients_match = mark_matching_ingredients(
                ingredients, normalised_allergens
            )
            output_img = draw_matched_ingredients(img, ingredients_match)

            st.image(output_img)
