import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.special import gamma, gammainc
import streamlit as st


def analytical_mtbf(dist, cutoff, **kwargs):
    '''
    Analytically compute MTBF assuming Weibull distribution, to be deprecated
    in favor of the more flexible function `numerical_mtbf`
    '''
    c = kwargs.get('c')
    scale = kwargs.get('scale')
    return scale/c*gammainc(1/c, (cutoff/scale)**c)*gamma(1/c)/dist.cdf(cutoff)


def calculate(dist, cutoff, cost=False, **kwargs):
    '''
    Calculate the cost of maintenance plan given parameters
    '''
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
    '''
    Template for cost section of the page
    '''
    st.header('Costs')
    st.info('Costs are for single failure occurrence/maintenance activity')
    sfcost = st.number_input('Failure Cost', 0, 100000, 20000)
    mcost = st.number_input('Maintenance Cost', 0, 100000, 3000)

    inputs['sfcost'] = sfcost
    inputs['mcost'] = mcost


def floor_magnitude(x):
    '''
    Helper function to compute floor of the magnitude in base 10
    '''
    return np.power(10, int(np.log10(x)))


def get_test_properties(alpha, beta, d, m0, noc):
    '''
    Get test properties of a given test plan
    '''
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


def log_likelihood(df, dist, params):
    '''
    Calculate the log-likelihood of data given censoring
    '''
    durations = df['duration'].values
    status = df['status'].values
    d = dist(a=1, loc=0, c=params[0], scale=params[1])
    # Hazard function
    hf = d.pdf(durations)/d.sf(durations)
    sf = d.sf(durations)
    return sum(np.log(np.power(hf, status)*sf))


def numerical_mtbf(dist, cutoff):
    '''
    Numerically compute the MTBF
    '''
    integral = truncated_ev(dist, cutoff)
    return integral/dist.cdf(cutoff) - cutoff*(1-1/dist.cdf(cutoff))


def test_inputs(state, params):
    '''
    Check if test plan inputs fulfil criteria
    '''
    id_ = params['ID']
    params_ = tuple([params['Alpha'], params['Beta'],
                     params['Disc. Ratio'],
                     params['Specified MTBF']])
    if id_ in [x[0] for x in state]:
        return 'iderror'
    if params_ in [tuple(x[1:]) for x in state]:
        return 'paramerror'
    return 'pass'


def truncated_ev(dist, cutoff):
    '''
    Helper function to calculate truncated (conditional) expected value.
    '''
    return quad(lambda x: x*dist.pdf(x), 0, cutoff)[0]
