import altair as alt
import io
import numpy as np
import pandas as pd
import streamlit as st

from utils import img_to_bytes


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
                engineering literature called Sequential Test Plan, covered in
                IEC 61124 standard.''')

    st.header('Upload')
    st.markdown('''Upload test data with format as specified in the Fitter
                page. In the page, you can also generate and download the toy
                data.''')
    file_csv = st.file_uploader('''Upload Test Data in CSV format''',
                                type=['csv'])

    st.sidebar.header('Parameters')
    m0 = st.sidebar.number_input('Specified MTBF', 1000, 100000, 20000)
    d = st.sidebar.number_input('Discrimination Ratio', 1.01, 5.0,
                                1.5, 0.01)
    alpha = st.sidebar.slider("Producer's Risk (alpha)", 0.01, 0.3, 0.05, 0.01)
    beta = st.sidebar.slider("Consumer's Risk (beta)", 0.01, 0.3, 0.05, 0.01)
    noc = st.sidebar.number_input('Number of Components Tested', 1, 100, 10)
    oh = st.sidebar.number_input('Operational Hours (Yearly)', 1, 24*366, 5000)

    correction_factor = (d+1)/(2*d)
    prob_upperbound = (1-beta)/alpha*correction_factor
    prob_lowerbound = beta/(1-alpha)
    # Once uploaded
    if file_csv:
        encoded = file_csv.read().encode('utf8')
        df = pd.read_csv(io.BytesIO(encoded))
        df.columns = [x.lower() for x in df.columns]
        # Get cumulative failures/maintenances time
        cumul = df.cumsum()
        pr_exponent = cumul['duration']*(1-d)/m0
        cumul['p_ratio'] = np.power(d, cumul['status'])*np.exp(pr_exponent)
        cumul['accept'] = cumul['p_ratio'] < prob_lowerbound
        cumul['reject'] = cumul['p_ratio'] > prob_upperbound
        ac = cumul['accept']
        rj = cumul['reject']
        ac = ac[ac == 1]
        rj = rj[rj == 1]
        # Look for index where it is accepted/rejected
        success = False
        if len(ac) == 0 and len(rj) == 0:
            st.warning('Test time not enough')
        elif len(rj) == 0:
            success = True
            idx = ac.idxmax()
            st.info('Specification accepted')
        elif len(ac) == 0:
            success = True
            idx = rj.idxmax()
            st.error('Specification rejected')
        else:
            success = True
            idx = min(ac.idxmax(), rj.idxmax())

        if success:
            showr = st.checkbox('Show sequential test results?')
            showc = st.checkbox('Show sequential test chart?')

            row = cumul.iloc[idx, :][['duration', 'status']]
            st.write('Test cumulative duration:', int(row['duration']),
                     'hours (', round(row['duration']/oh/noc, 2),
                     'years over', noc, 'components)')
            st.write('Test cumulative failures:', row['status'])

            if showr:
                st.write(cumul.iloc[:idx+1, :])

            if showc:
                cml = cumul.loc[:idx+1, ['duration', 'status']]
                cml = cml.append(pd.DataFrame({'duration': 0, 'status': 0},
                                 index=[0]))
                cml = cml.sort_values('duration').reset_index(drop=True)
                a = np.log(prob_lowerbound)/np.log(d)
                c = np.log(prob_upperbound)/np.log(d)
                b = (d-1)/(m0*np.log(d))
                cml['accept'] = a + b*cml['duration']
                cml['reject'] = c + b*cml['duration']
                cml = pd.melt(cml, id_vars=['duration'],
                              value_vars=['status', 'accept', 'reject'],
                              var_name='type')
                accept = cml[cml['type'] == 'accept']
                reject = cml[cml['type'] == 'reject']
                status = cml[cml['type'] == 'status'].head(-1)
                reject['y2'] = row['status']+1
                fstatus = alt.Chart(
                    status
                    ).mark_line(clip=True, color='black',
                                interpolate='step-after').encode(
                    x=alt.X('duration:Q',
                            scale=alt.Scale(domain=(0, row['duration']))),
                    y=alt.Y('value:Q',
                            scale=alt.Scale(domain=(0, row['status'])))
                        )
                faccept = alt.Chart(
                    accept).mark_area(clip=True, color='green',
                                      opacity=0.5,).encode(
                    x=alt.X('duration:Q',
                            scale=alt.Scale(domain=(0, row['duration'])),
                            axis=alt.Axis(title='Cumulative Time')),
                    y=alt.Y('value:Q',
                            scale=alt.Scale(domain=(0, row['status'])),
                            axis=alt.Axis(title='Cumulative Failures'))
                        )
                freject = alt.Chart(
                    reject).mark_area(clip=True, color='red',
                                      opacity=0.5, orient='vertical').encode(
                    x=alt.X('duration:Q',
                            scale=alt.Scale(domain=(0, row['duration']))),
                    y=alt.Y('value:Q',
                            scale=alt.Scale(domain=(0, row['status']))),
                    y2='y2'
                        )
                st.altair_chart(fstatus + faccept + freject)
