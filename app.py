import numpy as np
import streamlit as st
from PIL import Image

# Load custom modules
from src.config import ALLERGEN_LIST, DELIMITERS, FAVICON_PATH, LOGO_PATH, MODEL_DIR
from src.annotate import annotate_matched_ingredients
from src.matching import flag_matching_ingredients
from src.ocr import load_ocr_model, ocr_to_word_records, run_ocr
from src.preprocessing import normalize_text, word_records_to_ingredient_records

st.set_page_config(page_title="AllergyScanner", page_icon=str(FAVICON_PATH))

allergen_names = [item["item_name"] for item in ALLERGEN_LIST]


def render_header():
    col1, col2 = st.columns([5, 1], vertical_alignment="center")

    with col1:
        st.markdown('## Allergy:color[Scanner]{foreground = "#215F9A"}')

    with col2:
        st.image(str(LOGO_PATH), output_format="PNG")

    st.markdown(
        "Scan product ingredients to check if it contains one of your contact allergens "
        "or its cousins. Built by "
        "[samhendersonpalmer](https://www.linkedin.com/in/samhendersonpalmer/) - "
        "view project source code on "
        "[GitHub](https://github.com/samhendersonpalmer/ocr-ingredients-checker)"
    )


def render_allergen_tab():
    st.subheader("Select your contact allergens")

    selected_allergens = st.multiselect(
        label="All contact allergens",
        label_visibility="hidden",
        placeholder="Type to search",
        options=allergen_names,
    )

    return selected_allergens


def render_scan_tab(selected_allergens, reader):
    st.subheader("Scan the product ingredients")

    uploaded_file = st.file_uploader(
        label="Take picture of ingredients list",
        max_upload_size=50,
        label_visibility="hidden",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is None:
        return

    input_image = Image.open(uploaded_file)
    input_image.thumbnail((1400, 1400))

    with st.spinner("Scanning image"):
        img = np.asarray(input_image)
        input_image.close()
        del input_image

        result = run_ocr(reader, img)

        word_records = ocr_to_word_records(result, normalize_text)
        ingredients = word_records_to_ingredient_records(word_records, DELIMITERS)

        # Return lists of alternative names for selected allergens
        selected_allergen_list = [
            item for item in ALLERGEN_LIST if item["item_name"] in selected_allergens
        ]
        # normalise
        for item in selected_allergen_list:
            item["allergens"] = [a.lower().strip() for a in item["allergens"]]

        ingredients_match = flag_matching_ingredients(
            ingredients, selected_allergen_list
        )
        output_img = annotate_matched_ingredients(img, ingredients_match)
        del img

        col1, col2 = st.columns([2, 2], vertical_alignment="top")

        with col1:
            st.image(output_img)
            del output_img

        with col2:
            positive_allergens = []

            for ingredient in ingredients_match:
                if ingredient["is_match"]:
                    matched = ingredient.get("matched_allergens", [])
                    parents = ingredient.get("parent_allergen", [])
                    urls = ingredient.get("url", [])

                    for allergen, parent, url in zip(matched, parents, urls):
                        display_text = (
                            f"{allergen} (AKA your allergen, [{parent}]({url}))"
                        )

                        if display_text not in positive_allergens:
                            positive_allergens.append(display_text)

            st.markdown("### Potential allergens:")

            if positive_allergens:
                for allergen in positive_allergens:
                    st.markdown(f"- :color[{allergen}]{{foreground='#bd500c'}}")
            else:
                st.markdown(" :color[None detected]{foreground='#215F9A'}")


# MAIN #
render_header()

st.warning(
    "This app is for information purposes only, and should not be used as a substitute for the personal advice received when consulting a doctor, nurse or health professional."
)

st.space()

with st.sidebar:
    selected_allergens = render_allergen_tab()

reader = load_ocr_model(MODEL_DIR)

render_scan_tab(selected_allergens, reader)
