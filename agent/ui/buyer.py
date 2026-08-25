import streamlit as st

from ui.B_orders import orders_page
from ui.B_ai_scout import ai_scout_page

st.set_page_config(initial_sidebar_state=600)


def buyer_ui():

    user = st.session_state.user

    # ---------------- NAVIGATION ----------------

    page = st.radio(
        "Navigation",
        ["🛍️ Scout AI", "📦 Orders", "🔍 Activity"],
        horizontal=True,
        label_visibility="collapsed",
    )

    # ---------------- PAGES ----------------

    if page == "🛍️ Scout AI":
        ai_scout_page(user)

    elif page == "📦 Orders":
        orders_page(user)

    elif page == "🔍 Activity":
        st.header("🔍 Activity")
        st.info("Agent activity and audit trail will appear here.")
