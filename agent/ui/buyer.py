

import streamlit as st

from ui.B_orders import orders_page
from ui.B_ai_scout import ai_scout_page
from ui.B_activity import activity_page
from ui.B_cart import cart_page

st.set_page_config(initial_sidebar_state=600)


def buyer_ui():

    user = st.session_state.user

    # ---------------- NAVIGATION STYLE ----------------

    st.html("""
    <style>

    .st-key-nav_radio [role="radiogroup"] {
        gap: 10px;
    }

    .st-key-nav_radio label {
        font-size: 17px !important;
        font-weight: 600 !important;
        padding: 0px 16px 0px 0px !important;
        border-radius: 10px !important;
    }

    .st-key-nav_radio label p {
        font-size: 20px !important;
        font-weight: 600 !important;
        padding: 0px 16px 0px 16px !important;
        
        border-radius : 2rem;
        border : 2px solid cyan;
    }

    </style>
    """)

    # ---------------- NAVIGATION ----------------

    page = st.radio(
        "Navigation",
        ["🛍️ Scout AI", "🛒 Cart", "📦 Orders", "🔍 Activity"],
        horizontal=True,
        label_visibility="collapsed",
        key="nav_radio",
    )

    # ---------------- PAGES ----------------

    if page == "🛍️ Scout AI":
        ai_scout_page(user)

    elif page == "📦 Orders":
        orders_page(user)

    elif page == "🔍 Activity":
        activity_page(user)
    
    elif page == "🛒 Cart":
        cart_page(user)
