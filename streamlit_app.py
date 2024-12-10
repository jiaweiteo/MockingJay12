from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Meeting Management",
    page_icon=":calendar:",  # This is an emoji shortcode. Could be a URL too.
)

pages = {
    'Home': [
        st.Page('pages/home.py', title='Home', icon='🏠'), #Overview of all meetings, create meeting
    ],
    'Pre-Meeting': [
        st.Page('pages/agenda.py', title='Agenda', icon='📜'),
    ],
    'Meeting': [
        st.Page('pages/minutes.py', title='Note-Taking', icon='📝'),
    ],
    'Admin': [
        st.Page('pages/dependencies.py', title='Dependencies'),
        st.Page('pages/cdh.py', title='CDH'),
    ]
}

nav = st.navigation(pages)
nav.run()