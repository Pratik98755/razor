import streamlit as st
import requests


# from ai.agent import ask_agent

from ui.M_my_products import my_products_page
from ui.M_ai_assisstant import ai_assisstant_page
from ui.M_add_product import add_product_page
from ui.M_dashboard import dashboard_page


def merchant_ui():

    # user details contains name, user_id, role
    user = st.session_state.user

    # ---------------- Sidebar ----------------
    st.sidebar.title("Merchant")
    st.sidebar.title(user["user"])

    #
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    page = st.sidebar.radio(
        "Menu",
        ["Dashboard", "AI Assisstant", "Add Product", "My Products"],
        key="current_page",
    )

    if page == "Dashboard":
        dashboard_page(user)

    elif page == "Add Product":
        add_product_page(user)

    elif page == "My Products":
        my_products_page(user)

    elif page == "AI Assisstant":
        ai_assisstant_page(user)
