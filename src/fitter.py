import base64
import io
import pandas as pd
from scipy.optimize import minimize
import streamlit as st

from utils import floor_magnitude, img_to_bytes, log_likelihood


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

    # Initialize data verification and file variable
    v = False
    file_csv = False

    gu = st.radio('Generate toy data or upload?',
                  ['Generate', 'Upload'])
    if gu == 'Upload':
        file_csv = st.file_uploader('''Upload a CSV file''',
                                    type=['csv'])
    elif gu == 'Generate':
        # Generation parameters
        scale = st.number_input('Scale', 100, 1000000, 20000, 100)
        shape = st.slider('Shape', 0.2, 5.0, 1.5, 0.01)
        # Create distribution object
        dgen = dist(a=1, loc=0, c=shape, scale=scale)

        mag = floor_magnitude(dgen.ppf(0.99))
        cutoff = st.slider('Maintenance Interval', int(mag*0.2),
                           min([int(mag*10), 1000000]),
                           int(mag*0.9), 100)

        # Trials
        rows = st.number_input('Rows to generate', 500, 10000, 2500, 100)
        gbutton = st.button('Generate')
        if gbutton:
            tot = []
            for _ in range(rows):
                t = 0
                trial = dgen.rvs()
                if trial > cutoff:
                    t += cutoff
                    tot.append([cutoff, 0])
                else:
                    t += trial
                    tot.append([trial, 1])
            # Automatic verification
            v = True
            df = pd.DataFrame(tot, columns=['duration', 'status'])
            csv = df.to_csv(index=False)

            # Strings <-> bytes conversion
            b64 = base64.b64encode(csv.encode()).decode()
            href = '''<a href="data:file/csv;base64,{}"
                download="{}">Download generated data</a>'''
            filename = st.text_input('Filename (e.g. gen.csv)', 'gen.csv')

            st.markdown(href.format(b64, filename), unsafe_allow_html=True)

    # If file is uploaded
    if file_csv:
        encoded = file_csv.read().encode('utf8')
        df = pd.read_csv(io.BytesIO(encoded))
        df.columns = [x.lower() for x in df.columns]
        if ('duration' in df.columns) and ('status' in df.columns):
            st.write('First 5 rows of the data')
            st.write(df.head(5))
            v = st.checkbox('Verify?')
        else:
            st.error('''Failed to load data. Ensure column name
            requirement is satisfied''')

    if v:
        st.subheader('Distribution Fitting')
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
