import streamlit as st
from scipy.stats import exponweib

from maintenance import maintenance
from simulation import simulation


st.sidebar.header('Input')

page = st.sidebar.radio('Page', ['Maintenance', 'Simulation'])
pagedic = {'Maintenance': maintenance, 'Simulation': simulation}

# List distributions
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

pagedic[page](dist)
