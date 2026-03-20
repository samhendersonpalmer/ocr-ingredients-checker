import numpy as np
import streamlit as st
from PIL import Image

# Load custom modules
from src.config import ALLERGEN_LIST, DELIMITERS, FAVICON_PATH, LOGO_PATH, MODEL_DIR
from src.annotate import annotate_matched_ingredients
from src.matching import flag_matching_ingredients, normalize_allergen_list
from src.ocr import load_ocr_model, ocr_to_word_records, run_ocr
from src.preprocessing import normalize_text, word_records_to_ingredient_records

st.set_page_config(page_title="AllergyScanner", page_icon=str(FAVICON_PATH))


def render_header():
    col1, col2 = st.columns([5, 1], vertical_alignment="center")

    with col1:
        st.markdown('## Allergy:color[Scanner]{foreground = "#215F9A"}')

    with col2:
        st.image(str(LOGO_PATH), width=90)

    st.markdown(
        "Scan product ingredients to check if it contains one of your contact allergens "
        "or its cousins. Built by "
        "[samhendersonpalmer](https://www.linkedin.com/in/samhendersonpalmer/) - "
        "view project source code on "
        "[GitHub](https://github.com/samhendersonpalmer/ocr-ingredients-checker)"
    )


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
