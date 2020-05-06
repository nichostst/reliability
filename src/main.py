import streamlit as st
from scipy.stats import exponweib

from home import home
from fitter import fitter
from maintenance import maintenance
from simulation import simulation
from utils import floor_magnitude


st.sidebar.title('Reliability')

page = st.sidebar.radio('Page',
                        ['Home', 'Fitter', 'Maintenance', 'Simulation'])
pagedic = {'Home': home, 'Fitter': fitter, 'Maintenance': maintenance,
           'Simulation': simulation}

if page in ['Home']:
    pagedic[page]()
elif page in ['Fitter']:
    dlist = {'weibull': exponweib}
    d = st.sidebar.selectbox('Distribution', ['weibull'],
                             0, lambda x: x.capitalize())
    pagedic[page](dlist[d])
elif page in ['Maintenance', 'Simulation']:
    # List distributions
    st.sidebar.subheader('Failure Process')
    dlist = {'weibull': exponweib}
    d = st.sidebar.selectbox('Distribution', ['weibull'],
                             0, lambda x: x.capitalize())

    # Trial parameters
    scale = st.sidebar.number_input('Scale', 100, 1000000, 20000, 100)
    shape = st.sidebar.slider('Shape', 0.2, 5.0, 1.5, 0.01)

    # List sets of their respective parameters
    params = {'weibull': {'c': shape, 'scale': scale}}

    # Freeze distribution
    dist = dlist[d](a=1, loc=0, **params[d])
    st.sidebar.info(f'Characteristic Life is {int(dist.mean())} hours')

    # Maintenance interval
    st.sidebar.subheader('System')
    mag = floor_magnitude(dist.ppf(0.99))
    cutoff = st.sidebar.slider('Maintenance Interval', int(mag*0.2),
                               min([int(mag*10), 1000000]), int(mag*0.9), 100)

    noc = st.sidebar.number_input('Number of Components', 1, 1000, 10)
    oh = st.sidebar.number_input('Operational Hours (Yearly)', 1, 24*366, 5000)
    oh = oh*noc

    inputs = {'oh': oh, 'cutoff': cutoff, 'noc': noc}

    pagedic[page](dist, inputs)
