import numpy as np
import pandas as pd
from scipy.optimize import minimize
import streamlit as st

from utils import (
    calculate,
    cost_section,
    draw_distribution,
    img_to_bytes
)


def maintenance(dist, inputs):
    cutoff = inputs.get('cutoff')
    inputs.pop('cutoff')

    banner = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes("./static/banner-maintenance.png")
    )
    st.markdown(banner, unsafe_allow_html=True)
    st.markdown('''Given costs and maintenance interval length, see how the
                total cost changes''')
    st.markdown('*Assumption: Maintenance is done component by component*')
    # Draw distribution
    st.header('Distribution')
    draw_distribution(dist)

    # Input
    st.markdown('---')
    cost_section(inputs)

    st.markdown('---')
    st.header('Comparison')

    # Yearly statistics
    out = calculate(dist, cutoff, **inputs)

    # Add two fields, interval and cost
    out['interval'] = {'maintenance': cutoff, 'no_maintenance': None}
    out['mcost'] = {'maintenance':
                    out['mcount']['maintenance']*inputs['mcost'],
                    'no_maintenance': 0}

    # Optimize by cost
    with st.spinner('Running optimization...'):
        opt = minimize(lambda x: calculate(dist, x, cost=True, **inputs),
                       cutoff, options={'maxiter': 30})
        nit = opt['nit']
        success = opt['success']
        opt = opt['x'][0]

    if success:
        st.write('Optimized in {} iterations'.format(nit))
    else:
        st.write('Failed to converge under 30 iterations allowed.')
    # Produce dataframe
    df = pd.DataFrame(out).T
    df.columns = ['Maintenance', 'No Maintenance']
    # Rearrange
    df = df.loc[['interval', 'failures', 'mcount', 'fcost', 'mcost',
                 'cost', 'mtbf'], :]

    # Add cost-optimized values
    co = pd.DataFrame(calculate(dist, opt, **inputs)).T['maintenance']
    co['interval'] = opt
    co['mcost'] = co['mcount']*inputs['mcost']
    df['Cost-Optimized'] = co[['interval', 'failures', 'mcount', 'fcost',
                               'mcost', 'cost', 'mtbf']].values

    df.index = ['Interval', '# Failure', '# Maintenance', 'Failure Cost',
                'Maintenance Cost', 'Cost', 'MTBF']
    df = df.loc[:, ['No Maintenance', 'Maintenance', 'Cost-Optimized']]
    st.write(np.round(df, 2))
    st.write('*Note: Shown are expected yearly figures*')
