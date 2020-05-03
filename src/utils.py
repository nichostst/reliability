import altair as alt
import base64
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.integrate import quad
from scipy.special import gamma, gammainc
import streamlit as st


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def truncated_ev(dist, cutoff):
    '''
    Helper function to calculate truncated (conditional) expected value.
    '''
    return quad(lambda x: x*dist.pdf(x), 0, cutoff)[0]


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
