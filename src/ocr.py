import easyocr
import streamlit as st


# cache so we don't have to reload it everytime a change is made (new allergen selected etc)
@st.cache_resource
def load_ocr_model(model_dir):
    reader = easyocr.Reader(
        "en",
        model_storage_directory=str(model_dir),
        gpu=False,
    )
    return reader


def run_ocr(reader, image):
    return reader.readtext(
        image,
        width_ths=0,
        adjust_contrast=0.5,
        paragraph=False,
    )


def ocr_to_word_records(ocr_result, normalize_text):
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
