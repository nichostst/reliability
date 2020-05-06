import io
import pandas as pd
from scipy.optimize import minimize
import streamlit as st

from utils import img_to_bytes, log_likelihood


def fitter(dist):
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
    # Initialize verification variable
    v = False
    if file_csv:
        encoded = file_csv.read().encode('utf8')
        df = pd.read_csv(io.BytesIO(encoded))
        df.columns = [x.lower() for x in df.columns]
        if ('duration' in df.columns) and ('status' in df.columns):
            st.write('First 5 rows of the data')
            st.write(df.head(5))
            v = st.checkbox('Verify?')
        else:
            st.error('Failed to load data: No ')

    if v:
        optimized = False
        for method in ['BFGS', 'Nelder-Mead']:
            with st.spinner(f'Optimizing with {method}'):
                opt = minimize(lambda x: -log_likelihood(df, dist, x),
                               x0=[1, df['duration'].mean()],
                               method=method,
                               options={'maxiter': 100})
                if opt['success']:
                    nit = opt['nit']
                    opt = opt['x']
                    optimized = True
                    break
                else:
                    st.warning(f'{method} failed to converge')

        if optimized:
            st.info(f'''Fitting successful, optimized with {method} in
                    {nit} iterations''')
            st.subheader('Parameters')
            st.write(f'Scale: `{opt[0]:.2f}`\t Shape: `{int(opt[1])}`')
