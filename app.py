import streamlit as st

st.set_page_config(page_title="AllergyScanner", page_icon="img/logo.png")

col1, col2, col3 = st.columns([4, 1, 1], vertical_alignment="top")

with col1:
    st.markdown('# Allergy:color[Scanner]{foreground = "#215F9A"}')

with col3:
    st.image("img/logo.png")


st.markdown(
    "Scan product ingredients to check if it contains one of your contact allergens or its cousins. Built by "
    "[samhendersonpalmer](https://www.linkedin.com/in/samhendersonpalmer/) - "
    "view project source code on "
    "[GitHub](https:/github.com/samhendersonpalmer/ocr-ingredients-checker)"
)

st.space()

tab1, tab2 = st.tabs(["1. Select your allergens", "2. Scan ingredients"])

with tab1:
    st.subheader("1. Select your contact allergens")

    st.multiselect(
        label="All contact allergens",
        label_visibility="hidden",
        placeholder="Type to search",
        options=["Paraben mix", "Propolis", "Bronopol"],
    )

with tab2:
    st.subheader("2. Scan the product ingredients")

    uploaded_file = st.file_uploader(
        label="Take picture of ingredients list",
        label_visibility="hidden",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        st.image(uploaded_file)
