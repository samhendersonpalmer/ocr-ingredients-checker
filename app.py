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


def render_allergen_tab():
    st.subheader("1. Select your contact allergens")

    selected_allergens = st.multiselect(
        label="All contact allergens",
        label_visibility="hidden",
        placeholder="Type to search",
        options=ALLERGEN_LIST,
    )

    return selected_allergens


def render_scan_tab(reader, selected_allergens):
    st.subheader("2. Scan the product ingredients")

    uploaded_file = st.file_uploader(
        label="Take picture of ingredients list",
        label_visibility="hidden",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is None:
        return

    input_image = Image.open(uploaded_file)

    with st.spinner("Scanning image"):
        result = run_ocr(reader, input_image)
        img = np.array(input_image)

        word_records = ocr_to_word_records(result, normalize_text)
        ingredients = word_records_to_ingredient_records(word_records, DELIMITERS)
        normalized_allergens = normalize_allergen_list(
            selected_allergens, normalize_text
        )
        ingredients_match = flag_matching_ingredients(ingredients, normalized_allergens)
        output_img = annotate_matched_ingredients(img, ingredients_match)

        col1, col2 = st.columns([2, 2], vertical_alignment="top")

        with col1:
            st.image(output_img)

        with col2:
            positive_allergens = []

            for ingredient in ingredients_match:
                if ingredient["is_match"]:
                    # Incase matched_allergen key doesn't exist return empty list
                    for allergen in ingredient.get("matched_allergens", []):
                        if allergen not in positive_allergens:
                            positive_allergens.append(allergen)

            st.markdown("### Potential allergens detected:")

            if positive_allergens:
                for allergen in positive_allergens:
                    st.markdown(f"### - :color[{allergen}]{{foreground='#bd500c'}}")
            else:
                st.markdown("### :color[None]{foreground='#215F9A'}")


# MAIN #
reader = load_ocr_model(MODEL_DIR)

render_header()

st.space()

tab1, tab2 = st.tabs(["1. Select your allergens", "2. Scan ingredients"])

with tab1:
    selected_allergens = render_allergen_tab()
with tab2:
    render_scan_tab(reader, selected_allergens)
