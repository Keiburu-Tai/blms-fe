import streamlit as st
import pandas as pd
import numpy as np
from st_pages import Page, Section, show_pages, add_page_title

#side bar part refer https://github.com/blackary/st_pages
# add_page_title()

st.title('''BLMS''')


# Display the image, which should be centered with the CSS above
show_pages(
    [
        Page("streamlit.py", "Main Introduce", "💡"),
        Page("play.py", "Ready for Playing!", "🎸"),
        Page("session.py", "Session", "🎸"),
        # Unless you explicitly say in_section=False
    ]
)