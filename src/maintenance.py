import numpy as np
import pandas as pd
from scipy.optimize import minimize
import streamlit as st

from utils import calculate, draw_distribution, floor_magnitude,\
    img_to_bytes


def maintenance(dist):
    banner = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes("./static/banner-maintenance.png")
    )
    st.markdown(banner, unsafe_allow_html=True)
    # Draw distribution
    st.header('Distribution')
    draw_distribution(dist)

    mag = floor_magnitude(dist.ppf(0.99))

    # Input
    st.markdown('___')
    st.header('Input')
    noc = st.number_input('Number of Components', 1, 1000, 10)
    oh = st.number_input('Operational Hours (Yearly)', 1, 24*366, 5000)
    oh = oh*noc
    st.info('Costs are for single failure occurrence/maintenance activity')
    sfcost = st.number_input('Failure Cost', 0, 100000, 20000)
    mcost = st.number_input('Maintenance Cost', 0, 100000, 3000)

    inputs = {'oh': oh, 'sfcost': sfcost, 'mcost': mcost}

    # Maintenance interval
    cutoff = st.slider('Maintenance Interval', int(mag*0.2),
                       min([int(mag*10), 1000000]), int(mag*0.8), 100)

    st.markdown('___')
    st.header('Cost')

    # Yearly statistics
    st.subheader('Comparison of With/Without Maintenance')
    out = calculate(dist, cutoff, **inputs)

    # Add two fields, interval and cost
    out['interval'] = {'maintenance': cutoff, 'no_maintenance': None}
    out['mcost'] = {'maintenance': out['mcount']['maintenance']*mcost,
                    'no_maintenance': 0}

    # Optimize by cost
    opt = minimize(lambda x: calculate(dist, x, cost=True, **inputs),
                   cutoff)['x'][0]

    # Produce dataframe
    df = pd.DataFrame(out).T
    df.columns = ['Maintenance', 'No Maintenance']
    # Rearrange
    df = df.loc[['interval', 'failures', 'mcount', 'fcost', 'mcost',
                 'cost', 'mtbf'], :]

    # Add cost-optimized values
    co = pd.DataFrame(calculate(dist, opt, **inputs)).T['maintenance']
    co['interval'] = opt
    co['mcost'] = co['mcount']*mcost
    df['Cost-Optimized'] = co[['interval', 'failures', 'mcount', 'fcost',
                               'mcost', 'cost', 'mtbf']].values

    df.index = ['Interval', '# Failure', '# Maintenance', 'Failure Cost',
                'Maintenance Cost', 'Cost', 'MTBF']
    df = df.loc[:, ['No Maintenance', 'Maintenance', 'Cost-Optimized']]
    st.write(np.round(df, 2))
    st.write('*Note: Shown are expected yearly figures*')
