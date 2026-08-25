import requests
import streamlit as st


def add_product_page(user):
    draft = {}

    st.title("Add Product")
    st.write("Add a new product to your store.")

    with st.form("add_product_form", clear_on_submit=True):
        name = st.text_input("Product Name", value=draft.get("name", ""))

        description = st.text_area("Description", value=draft.get("description", ""))

        price = st.number_input(
            "Price", min_value=0.0, step=1.0, value=float(draft.get("price", 0))
        )

        stock = st.number_input(
            "Stock", min_value=0, step=1, value=int(draft.get("stock", 0))
        )

        category = st.text_input("Category", value=draft.get("category", ""))

        images_text = st.text_area(
            "Product Images",
            value="\n".join(draft.get("images_text", [])),
            placeholder="Enter one image URL per line",
        )

        submitted = st.form_submit_button(
            "Add Product",
            # use_container_width=True
            width="stretch",
        )

        if submitted:
            images = [url.strip() for url in images_text.splitlines() if url.strip()]

            # calling add_products api
            response = requests.post(
                "http://localhost:8009/merchants/add_product",
                json={
                    "name": name,
                    "merchant_id": user["user_id"],
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "category": category,
                    "images": images,
                },
            )

            if response.status_code == 201:
                st.session_state.product_draft = None
                st.toast("Product added successfully!", icon="✅")
            else:
                st.error("Failed to add product!")
