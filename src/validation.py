import io
import pandas as pd
import streamlit as st

from utils import (
    get_properties,
    img_to_bytes,
    sequential_test,
    test_inputs
    )


def validation():
    banner = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes("./static/banner-validation.png")
    )
    st.markdown(banner, unsafe_allow_html=True)
    st.markdown('')
    st.markdown('')
    st.markdown('Implementation of Sequential Probability Ratio Test (SPRT)')

    st.markdown('''To validate with a statistical framework, the hypothesis of
                whether the MTBF of the asset is as specified. It is a
                modification of the use case as known in reliability
                engineering literature called Reliability Demonstration Test,
                covered in IEC 61124 standard.''')

    # Sidebar section
    st.sidebar.header('Parameters')
    m0 = st.sidebar.number_input('Specified MTBF', 1000, 100000, 20000)
    d = st.sidebar.number_input('Discrimination Ratio', 1.01, 5.0,
                                1.5, 0.01)
    alpha = st.sidebar.slider("Producer's Risk (alpha)", 0.01, 0.3, 0.05, 0.01)
    beta = st.sidebar.slider("Consumer's Risk (beta)", 0.01, 0.3, 0.05, 0.01)
    st.sidebar.header('System')
    noc = st.sidebar.number_input('Number of Components Tested', 1, 100, 10)
    oh = st.sidebar.number_input('Operational Hours (Yearly)', 1, 24*366, 5000)

    # Main page
    st.header('Create Test Plan')
    st.markdown('''Change the test plan parameters on the sidebar.
                Click on the `Create` button if you want to create a test
                plan with the current parameters''')
    text = st.text_input('Test Plan ID', 'TestA')
    params = {'ID': text, 'Alpha': alpha, 'Beta': beta,
              'Disc. Ratio': d, 'Specified MTBF': m0}
    pdf = pd.DataFrame(params, index=['Value'])
    st.write('''*The test preview below will be updated whenever the parameter
             is changed*''', pdf)

    # Manage input states
    @st.cache(allow_output_mutation=True)
    def get_state():
        return []

    state = get_state()

    create = st.button('Create')
    if create:
        if test_inputs(state, params) == 'iderror':
            st.error('ID exists. Please choose another ID')
        elif test_inputs(state, params) == 'paramerror':
            st.error('Test plan with these parameters already exists')
        else:
            state.append(list(params.values()))
            st.info('Create successful')

    st.subheader('Current Test Plans')
    st.write(pd.DataFrame(state, columns=params.keys()))

    st.header('Test')
    st.markdown('Select one of the test IDs')
    tid = st.selectbox('Test ID', [x[0] for x in state])
    if tid:
        st.subheader('Test Properties')
        get_properties(state, tid, noc, oh)

    st.subheader('Upload')
    st.markdown('''Upload test data with format as specified in the Fitter
                page. In the page, you can also generate and download the toy
                data. You can upload the toy data here.''')
    file_csv = st.file_uploader('''Upload Test Data in CSV format''',
                                type=['csv'])

    correction_factor = (d+1)/(2*d)
    ub = (1-beta)/alpha*correction_factor
    lb = beta/(1-alpha)
    # Once uploaded
    if file_csv:
        encoded = file_csv.read().encode('utf8')
        df = pd.read_csv(io.BytesIO(encoded))
        sequential_test(df, (lb, ub, d, m0, oh, noc))
