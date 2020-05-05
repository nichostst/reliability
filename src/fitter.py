import io
import pandas as pd
import streamlit as st

from utils import img_to_bytes


def fitter():
    banner = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes("./static/banner-fitter.png")
    )
    st.markdown(banner, unsafe_allow_html=True)
    st.markdown('')
    st.markdown('')
    st.markdown('''Fit data with statistical distributions common in
                survival analysis''')
    st.header('How to Format Your Data?')
    st.markdown('''It should have the field names `duration` and `status`
                (case-insensitive)''')

    st.markdown('''   1. The field `duration` should contain the failure/censoring duration
    2. The field `status` should contain the censoring indicator, 0
    if censored (failure not observed) or 1 if failure is observed
                ''')
    example = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes("./static/csv-example.png")
    )
    st.markdown(example, unsafe_allow_html=True)
    st.markdown('*Example data format*')
    st.markdown('---')
    st.header('Upload')
    file_csv = st.file_uploader('''Upload a CSV file''',
                                type=['csv'])
    if file_csv:
        encoded = file_csv.read().encode('utf8')
        df = pd.read_csv(io.BytesIO(encoded))
        df.columns = [x.lower() for x in df.columns]
        if ('duration' in df.columns) and ('status' in df.columns):
            st.write('First 5 rows of the data')
            st.write(df.head(5))
        else:
            st.error('Failed to load data: No ')
