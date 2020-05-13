import base64
import pandas as pd
import streamlit as st
from utils.io import img_to_bytes
from utils.plotting import plot_uncertainty_chart
from utils.sim import (
    get_durations_fleetwide,
    simulate_bycomponent
)
from utils.utils import cost_section


def simulation(dist, inputs):
    noc = inputs.get('noc')
    oh = inputs.get('oh')
    cutoff = inputs.get('cutoff')
    banner = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes("./static/banner-simulation.png")
    )
    st.markdown(banner, unsafe_allow_html=True)
    st.markdown('')
    st.markdown('')
    st.markdown('''For shorter analysis periods, simulation is preferred
                in order to obtain uncertainty estimates''')

    cost_section(inputs)

    st.markdown('---')
    st.header('Trials')
    mtype = st.radio('Maintenance Type', ['Component-wise', 'Fleetwide'])

    st.markdown('---')
    st.header('Trials')
    tl = st.slider('Length of Trials (in years)', 0.5, 10.0, 3.0, 0.1)
    rept = st.number_input('Repeat', 100, 10000, 2500)
    # Convert trial length to hours per component
    tlen = tl*oh/noc

    btn = st.button('Simulate')
    if btn:
        p = st.progress(0)
        trials = []
        ms = []
        fs = []
        for i in range(rept):
            if mtype == 'Component-wise':
                [trial, m, f] = simulate_bycomponent(dist, cutoff, noc, tlen)
                trials.append(trial)
                ms.append(m)
                fs.append(f)
            elif mtype == 'Fleetwide':
                f = []
                m = []
                tr = []
                for _ in range(noc):
                    durations = get_durations_fleetwide(tlen, cutoff, dist)
                    tr.append(durations)
                    f.append(len([x[0] for x in durations if x[1] == 1]))
                    m.append(len([x[0] for x in durations if x[1] == 0]))
                trials.append(tr)
                fs.append(f)
                ms.append(m)
            p.progress(int((i+1)*100/rept))
        df = pd.DataFrame(trials).rename_axis('trial_id')
        df.columns = ['component_'+str(x+1) for x in df.columns]
        csv = df.to_csv()

        maintenances = pd.DataFrame([sum(x) for x in ms],
                                    columns=['count'])
        failures = pd.DataFrame([sum(x) for x in fs], columns=['count'])

        # Strings <-> bytes conversion
        b64 = base64.b64encode(csv.encode()).decode()
        href = '''<a href="data:file/csv;base64,{}"
            download="{}">Download trials</a>'''
        filename = st.text_input('Filename (e.g. data.csv)', 'data.csv')

        st.markdown(href.format(b64, filename), unsafe_allow_html=True)

        st.markdown('---')
        st.header('Uncertainty')

        mfig = plot_uncertainty_chart(maintenances).properties(
            title='Maintenance Count Distribution'
            )
        ffig = plot_uncertainty_chart(failures).properties(
            title='Failure Count Distribution'
            )
        st.markdown(f'Over {noc} components and trial length of {tl} years:')

        cost = inputs['mcost']*maintenances + inputs['sfcost']*failures
        cfig = plot_uncertainty_chart(cost).properties(
            title='Cost Distribution'
            )
        st.altair_chart(mfig | ffig | cfig)
