import streamlit as st
import requests


def register():
    st.subheader("Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["BUYER", "MERCHANT"])

    if st.button("Register"):
        response = requests.post(
            "http://localhost:8009/accounts/register",
            json={"name": name, "email": email, "password": password, "role": role},
        )

        if response.content:
            try:
                st.write(response.json())
            except ValueError:
                pass


def login():
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            "http://localhost:8009/accounts/login",
            json={"email": email, "password": password},
        )

        if response.status_code == 200:
            try:
                st.session_state.user = response.json()
                st.rerun()
            except ValueError:
                pass
