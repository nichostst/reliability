import streamlit as st

from utils import img_to_bytes


def validation():
    banner = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes("./static/banner-validation.png")
    )
    st.markdown(banner, unsafe_allow_html=True)
    st.markdown('')
    st.markdown('')
    st.markdown('''Implementation of Sequential Probability Ratio Test (SPRT)
                to test hypotheses with a statistical framework''')
