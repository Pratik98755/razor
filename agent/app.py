# import streamlit as st
# from auth import register, login

# st.title("Agent")

# option = st.radio("Choose", ["Login", "Register"])

# if option == "Login":
#     login()
# else:
#     register()


import streamlit as st
from auth import register, login

# ui pages
from ui.merchant import merchant_ui
from ui.buyer import buyer_ui

if "user" not in (st.session_state):
    st.title("Agent")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", use_container_width=True):
            st.session_state["auth_page"] = "login"

    with col2:
        if st.button("Register", use_container_width=True):
            st.session_state["auth_page"] = "register"

    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    if st.session_state["auth_page"] == "login":
        login()
    else:
        register()


else:
    # user is logged in , show ui
    user = st.session_state.user
    if user["role"] == "MERCHANT":
        st.set_page_config(initial_sidebar_state=200)
        merchant_ui()
    else:
        st.set_page_config(initial_sidebar_state=600)
        buyer_ui()
