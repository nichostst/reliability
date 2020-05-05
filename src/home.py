import streamlit as st

from utils import img_to_bytes


def home():
    banner = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes("./static/banner-home.png")
    )
    st.markdown(banner, unsafe_allow_html=True)
    st.markdown('')
    st.markdown('')
    st.header('Some Words')
    st.markdown('''Hello and welcome to this web application!
                This interface is completely built on the Python
                project *Streamlit*, check their docs and awesome work
                [here](https://docs.streamlit.io/).''')
    st.markdown('''This app is a one-stop solution to asset maintenance... in
                the making **so** stay tuned for exciting new features. You can
                also help to contribute or make feature requests at the Github
                [repository](https://github.com/nichostst/reliability). Though
                I am not planning to over-engineer this application in terms of
                design and interface for the purpose it serves - goes with
                Streamlit design statement of simplicity - so sorry about that!
                ''')
    st.markdown('''I am just a lone statistician-turned-developer so any
                suggestion or kind words is highly appreciated. Hope it is
                useful and happy exploring ;)''')
    st.info('Navigate using the sidebar on the left side of the page')

    st.markdown('---')
    st.header('Purpose')
    st.markdown('''Allows the user to provide self-collected failure data and
                fit well-known statistical distributions to learn the
                underlying failure process in presence of censoring. This
                allows the user to experiment with time-based maintenance to
                improve system reliability, and save costs by proactively doing
                regular preventive maintenance as opposed to reactively fixing
                failures as they come. It also comes with a simulation platform
                to enable the user to gauge the uncertainty for analysis in
                shorter time periods.''')

    st.markdown('---')
    st.header('Assumptions')
    st.markdown('''   1. Maintenance restores asset to *good-as-new* condition.
    If the assets are replaced every time it fails, it will satisfy this
    assumption, no worries!
    2. Operating hours and operating conditions of the assets are the same
    across the whole system.''')

    st.markdown('---')
    st.header('Workflow')
    st.markdown('''   1. Input failure data at the `Fitter` page to learn the
    distribution of the failure process. If you do not have the data, you may
    skip to the step 2.
    2. On the `Maintenance` page, you will be able to input the learned (if you
    do step 1, else you can still plug and play with the parameters) failure
    process with the parameters on the sidebar. Important to note is the
    maintenance interval length parameter, which is the crux of our analysis.
    **Do take note of the additional assumption.**
    3. Input the estimated/expected costs of a maintenance action on the asset
    and the estimated/expected costs of a failure. A table will show at the
    bottom of the page showing the costs given the maintenance interval set at
    the sidebar. It will also show the cost-optimized length of the maintenance
    interval.
    4. In case the estimate of the uncertainty is needed, users may proceed to
    the `Simulation` page to simulate maintenance within a user-specified time
    period. **Note that the assumption in step 2 is made optional by allowing
    user to choose the maintenance type.** The choice `Component-wise` reflects
    said assumption. The simulation data may be downloaded to allow users to
    conduct their own analysis that is not covered by the application. The
    bottom of the page will show the uncertainty as distributions.''')

    st.markdown('---')
    st.header('Disclaimer')
    st.markdown('''The developer is not responsible of any outcome resulting
    from decision-making based on this application. Understand the assumptions
    that allows the modeling, and decide whether it is suitable for your
    purposes. You may [contact](https://github.com/nichostst) the developer to
    report bugs, or if you have general inquiry related to the application.''')
