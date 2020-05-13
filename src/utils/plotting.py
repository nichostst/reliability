import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from .utils import (
    floor_magnitude,
    get_test_properties
)


def plot_distribution(dist):
    # Get CDF and PDF
    # For time from 0 to the 99% percentile with steps of its magnitude - 2
    p99 = dist.ppf(0.99)
    mag = floor_magnitude(p99)
    df = pd.DataFrame({'Hours': [x for x in
                                 range(0, int(p99),
                                       int(mag/100))]})
    df['CDF'] = dist.cdf(df['Hours'])
    df['PDF'] = dist.pdf(df['Hours'])

    base = alt.Chart(
        df, height=300, width=650).mark_area(line=True).transform_fold(
            ['CDF', 'PDF'],
            as_=['Measure', 'Value']
        ).encode(alt.Color('Measure:N', scale=alt.Scale(scheme='tableau20')),
                 x='Hours')

    cdf = base.transform_filter(
        alt.datum.Measure == 'CDF'
    ).encode(alt.Y('Value:Q', axis=alt.Axis(title='CDF')))
    pdf = base.transform_filter(
        alt.datum.Measure == 'PDF'
    ).encode(alt.Y('Value:Q', axis=alt.Axis(title='PDF')))
    fig = alt.layer(cdf, pdf).resolve_scale(y='independent')
    st.altair_chart(fig)


def plot_properties(state, tid, noc, oh):
    # Get parameters for the test ID
    params_ = [x[1:] for x in state if x[0] == tid][0]
    et = get_test_properties(noc=noc, *params_)
    # Plot the properties
    oc = alt.Chart(et, height=250, width=300).mark_area(line=True).encode(
        x=alt.X('m', title='Actual MTBF'),
        y=alt.Y('Pa', title='Probability of Acceptance')
        ).properties(title='Operating Characteristic Curve')
    exp_time = alt.Chart(et, height=250,
                         width=300).mark_area(line=True).encode(
        x=alt.X('m', title='Actual MTBF'),
        y=alt.Y('Et', title='Expected Time to Decision')
        ).properties(title='Actual MTBF vs Et')
    st.altair_chart(oc | exp_time)
    a_ = np.log(params_[1]/(1-params_[0]))/np.log(params_[2])
    b_ = (params_[2]-1)/(params_[3]*np.log(params_[2]))
    mtt = -a_/b_/noc
    st.write('Minimum test time (years) is', round(mtt/oh, 2), 'with',
             noc, 'components.')


def plot_seq_chart(cumul, idx, bounds, d, m0):
    (lb, ub) = bounds
    cml = cumul.loc[:idx+1, ['duration', 'status']]
    # Maximum duration
    maxd = cml.tail(1)['duration'].values[0]
    # Maximum number of failure
    maxf = cml.tail(1)['status'].values[0]
    cml = cml.append(pd.DataFrame({'duration': 0, 'status': 0},
                     index=[0]))
    cml = cml.sort_values('duration').reset_index(drop=True)
    a = np.log(lb)/np.log(d)
    c = np.log(ub)/np.log(d)
    b = (d-1)/(m0*np.log(d))
    cml['accept'] = a + b*cml['duration']
    cml['reject'] = c + b*cml['duration']
    cml = pd.melt(cml, id_vars=['duration'],
                  value_vars=['status', 'accept', 'reject'],
                  var_name='type')
    accept = cml[cml['type'] == 'accept']
    reject = cml[cml['type'] == 'reject']
    status = cml[cml['type'] == 'status'].head(-1)
    reject['y2'] = maxf+10
    fstatus = alt.Chart(
        status
        ).mark_line(clip=True, color='black',
                    interpolate='step-after').encode(
        x=alt.X('duration:Q',
                scale=alt.Scale(domain=(0, maxd))),
        y=alt.Y('value:Q',
                scale=alt.Scale(domain=(0, maxf)))
            )
    faccept = alt.Chart(
        accept).mark_area(clip=True, color='green',
                          opacity=0.5,).encode(
        x=alt.X('duration:Q',
                scale=alt.Scale(domain=(0, maxd)),
                axis=alt.Axis(title='Cumulative Time')),
        y=alt.Y('value:Q',
                scale=alt.Scale(domain=(0, maxf)),
                axis=alt.Axis(title='Cumulative Failures'))
            )
    freject = alt.Chart(
        reject).mark_area(clip=True, color='red',
                          opacity=0.5, orient='vertical').encode(
        x=alt.X('duration:Q',
                scale=alt.Scale(domain=(0, maxd))),
        y=alt.Y('value:Q',
                scale=alt.Scale(domain=(0, maxf))),
        y2='y2'
            )
    st.altair_chart(fstatus + faccept + freject)


def plot_uncertainty_chart(df):
    fig = alt.Chart(
        df, height=150, width=180
    ).mark_bar(opacity=0.7).encode(
        alt.X('count', bin=alt.Bin(maxbins=20)), y='count()'
    )
    return fig


def plot_sequential_test(df, params):
    '''
    Implement test plan on given data
    '''
    (lb, ub, d, m0, oh, noc) = params
    df.columns = [x.lower() for x in df.columns]
    # Get cumulative failures/maintenances time
    cumul = df.cumsum()
    pr_exponent = cumul['duration']*(1-d)/m0
    cumul['p_ratio'] = np.power(d, cumul['status'])*np.exp(pr_exponent)
    cumul['accept'] = cumul['p_ratio'] < lb
    cumul['reject'] = cumul['p_ratio'] > ub
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
        row = cumul.iloc[idx, :][['duration', 'status']]
        st.write('Test cumulative duration:', int(row['duration']),
                 'hours (', round(row['duration']/oh/noc, 2),
                 'years over', noc, 'components)')
        st.write('Test cumulative failures:', row['status'])

        showr = st.checkbox('Show sequential test results?')
        if showr:
            st.write(cumul.iloc[:idx+1, :])

        showc = st.checkbox('Show sequential test chart?')
        if showc:
            plot_seq_chart(cumul, idx, (lb, ub), d, m0)
