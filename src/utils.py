import altair as alt
import base64
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.integrate import quad
from scipy.special import gamma, gammainc
import streamlit as st


def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def truncated_ev(dist, cutoff):
    '''
    Helper function to calculate truncated (conditional) expected value.
    '''
    return quad(lambda x: x*dist.pdf(x), 0, cutoff)[0]


def log_likelihood(df, dist, params):
    durations = df['duration'].values
    status = df['status'].values
    d = dist(a=1, loc=0, c=params[0], scale=params[1])
    # Hazard function
    hf = d.pdf(durations)/d.sf(durations)
    sf = d.sf(durations)
    return sum(np.log(np.power(hf, status)*sf))


def numerical_mtbf(dist, cutoff):
    integral = truncated_ev(dist, cutoff)
    return integral/dist.cdf(cutoff) - cutoff*(1-1/dist.cdf(cutoff))


def analytical_mtbf(dist, cutoff, **kwargs):
    c = kwargs.get('c')
    scale = kwargs.get('scale')
    return scale/c*gammainc(1/c, (cutoff/scale)**c)*gamma(1/c)/dist.cdf(cutoff)


def floor_magnitude(x):
    return np.power(10, int(np.log10(x)))


def draw_distribution(dist):
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


def calculate(dist, cutoff, cost=False, **kwargs):
    oh = kwargs.get('oh')
    sfcost = kwargs.get('sfcost')
    mcost = kwargs.get('mcost')

    if cost:
        mtbf = numerical_mtbf(dist, cutoff)
        mc = (mtbf-truncated_ev(dist, cutoff))
        mc = mc/(mtbf*cutoff)*oh
        return oh/mtbf*sfcost + mc*mcost
    else:
        mtbf = {'maintenance': numerical_mtbf(dist, cutoff),
                'no_maintenance': dist.mean()}
        # Maintenance count
        mc = (mtbf['maintenance']-truncated_ev(dist, cutoff))
        mc = mc/(mtbf['maintenance']*cutoff)*oh
        mcount = {'maintenance': mc, 'no_maintenance': 0}
        # Initialize
        failures = {}
        fcost = {}
        cost = {}
        failures['maintenance'] = oh/mtbf['maintenance']
        failures['no_maintenance'] = oh/mtbf['no_maintenance']
        fcost['maintenance'] = failures['maintenance']*sfcost
        fcost['no_maintenance'] = failures['no_maintenance']*sfcost
        cost['maintenance'] = fcost['maintenance'] + mc*mcost
        cost['no_maintenance'] = fcost['no_maintenance']

        out = {'failures': failures, 'fcost': fcost, 'cost': cost,
               'mtbf': mtbf, 'mcount': mcount}

    return out


def cost_section(inputs):
    st.header('Costs')
    st.info('Costs are for single failure occurrence/maintenance activity')
    sfcost = st.number_input('Failure Cost', 0, 100000, 20000)
    mcost = st.number_input('Maintenance Cost', 0, 100000, 3000)

    inputs['sfcost'] = sfcost
    inputs['mcost'] = mcost


def simulate_fleetwide(dist, cutoff):
    timenow = 0
    durations = []
    sim = dist.rvs()
    while sim < cutoff-timenow:
        durations.append([sim, 1])
        timenow += sim
        sim = dist.rvs()
    durations.append([cutoff-timenow, 0])

    return durations


def get_durations_fleetwide(tlen, cutoff, dist):
    durations = []
    for _ in range(int(tlen/cutoff)):
        durations.extend(simulate_fleetwide(dist, cutoff))

    remainder = tlen % cutoff
    if remainder > 0:
        rem = simulate_fleetwide(dist, remainder)
        rem = [x for x in rem if x[1] == 1]
        durations.extend(rem)

    return durations


def uncertainty_chart(df):
    fig = alt.Chart(
        df, height=150, width=180
    ).mark_bar(opacity=0.7).encode(
        alt.X('count', bin=alt.Bin(maxbins=20)), y='count()'
    )
    return fig


def test_inputs(state, params):
    id_ = params['ID']
    params_ = tuple([params['Alpha'], params['Beta'],
                     params['Disc. Ratio'],
                     params['Specified MTBF']])
    if id_ in [x[0] for x in state]:
        return 'iderror'
    if params_ in [tuple(x[1:]) for x in state]:
        return 'paramerror'
    return 'pass'


def get_test_properties(alpha, beta, d, m0, noc):
    correction_factor = (d+1)/(2*d)
    ub = (1-beta)/alpha*correction_factor  # A
    lb = beta/(1-alpha)  # B
    hspace = np.linspace(-2, 2, 50)
    m = {h: m0*(np.power(d, h)-1)/(h*(d-1)) for h in hspace}
    pa = {h: (np.power(ub, h)-1)/(np.power(ub, h) - np.power(lb, h))
          for h in hspace}
    er = {h: m0*(pa[h]*(np.log(ub)-np.log(lb)) - np.log(ub)) /
          (m[h]*(d-1) - m0*np.log(d)) for h in hspace}
    et = {h: m[h]/noc*er[h] for h in hspace}
    df = pd.DataFrame([m, pa, et], index=['m', 'Pa', 'Et'], columns=hspace).T
    df.reset_index(inplace=True)

    return df
