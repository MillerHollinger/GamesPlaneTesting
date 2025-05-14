import streamlit as st
import base64

st.set_page_config(page_title="Home - GamesPlane")

# Read the SVG file content
with open("ExtraFiles\GamesPlane Logo\GamesPlane Logo.svg", "r", encoding="utf-8") as f:
    svg_code = f.read()

# Encode to base64
b64 = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")

# Center the image using a div
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/svg+xml;base64,{b64}" width="300"/>
    </div>
    """,
    unsafe_allow_html=True,
)
""
""
"""
Welcome to **GamesPlane**! GamesPlane is GamesCrafters' augmented reality board game app. With GamesPlane, you can
create, edit, and play games supported by GamesmanUni with AR move hints.
"""
""
"##### Where to next?"
# TODO Make these link directly to the destination pages.
"""
**I want to play an existing game!** ➡️ Click **Launch Game** in the sidebar.  
**I want to learn the basics!** ➡️ Click **Starter Guide** in the sidebar.  
**I want to see the docs!** ➡️ Click **Docs** in the sidebar.  
**I want to add a new game!** ➡️ Click **Craftsman** in the sidebar. Be sure to read the **Docs** first to learn how to use Craftsman.  
"""

"*made with ❤️ by Miller Hollinger, MS 2025*"