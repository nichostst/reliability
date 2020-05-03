import base64
import pandas as pd
import streamlit as st

from sim import Simulation
from utils import floor_magnitude


def simulation(dist):
    st.title('Simulation')
    st.header('Input')
    size = st.number_input('Number of trials', 1000, 100000, 2000)
    mag = floor_magnitude(dist.ppf(0.99))
    cutoff = st.slider('Maintenance Interval', int(mag*0.2),
                       min([int(mag*10), 1000000]), int(mag*0.8), 100)
    sim = Simulation(dist, cutoff, size)
    sim.simulate()
    df = pd.DataFrame({'time': sim.trials})
    csv = df.to_csv(index=False)

    # Strings <-> bytes conversion
    b64 = base64.b64encode(csv.encode()).decode()
    href = '<a href="data:file/csv;base64,{}" download="{}">Download CSV</a>'
    filename = st.text_input('Filename (e.g. data.csv)', 'data.csv')

    st.markdown(href.format(b64, filename), unsafe_allow_html=True)
    st.write('Development in progress...')
