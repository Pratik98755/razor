import streamlit as st

from api import get_products, delete_product, edit_product




def my_products_page(user):

    st.title("My Products")
    
    # for editing products ::::
    if "editing_product_id" not in st.session_state:
        st.session_state.editing_product_id = None
        
    # for fetching products ::::
    products = get_products(user["user_id"])

    if not products:
        st.info("You haven't added any products yet.")
        return
    
    
    
    #### editing products form
    editing_id = st.session_state.editing_product_id
    if editing_id:

        product = next(
            p for p in products
            if p["product_id"] == editing_id
        )

        st.divider()
        st.subheader(f"Edit Product — {product['name']}")

        with st.form("edit_product_form"):

            name = st.text_input(
                "Product Name",
                value=product["name"]
            )

            description = st.text_area(
                "Description",
                value=product["description"]
            )

            price = st.number_input(
                "Price",
                min_value=0.0,
                value=float(product["price"]),
                step=1.0
            )

            stock = st.number_input(
                "Stock",
                min_value=0,
                value=int(product["stock"]),
                step=1
            )

            category = st.text_input(
                "Category",
                value=product["category"]
            )

            images_text = st.text_area(
                "Product Images",
                value="\n".join(product["images"]),
                help="One image URL per line"
            )

            col1, col2 = st.columns(2)

            with col1:
                submitted = st.form_submit_button(
                    "Save Changes",
                    type="primary"
                )

            with col2:
                cancelled = st.form_submit_button(
                    "Cancel"
                )

            if submitted:

                images = [
                    url.strip()
                    for url in images_text.splitlines()
                    if url.strip()
                ]

                updates = {
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "category": category,
                    "images": images
                }

                msg = edit_product(
                    editing_id,
                    updates
                )

                st.session_state.editing_product_id = None

                st.success(msg)
                st.rerun()

            if cancelled:
                st.session_state.editing_product_id = None
                st.rerun()
        
    
    
    
    
    

    for product in products:

        with st.container(border=True):

            col1, col2, col3 = st.columns([1, 4, 0.5])

            # Product image
            with col1:
                if product["images"]:
                    st.image(
                        product["images"][0],
                        width="stretch"
                    )

            # Product details
            with col2:
                st.subheader(product["name"])

                st.caption(f"Product ID: {product['product_id']}")

                st.write(product["description"])

                st.write(
                    f"**Category:** {product['category']}  |  "
                    f"**Price:** ₹{product['price']}  |  "
                    f"**Stock:** {product['stock']}"
                )

            # Delete button
            with col3:
                if st.button(
                    "✏️",
                    key=f"edit_{product['product_id']}",
                    help="Edit product",
                    type="secondary"
                ):
                    st.session_state.editing_product_id = product["product_id"]
                    st.rerun()
                if st.button(
                    "🗑️",
                    key=f"delete_{product['product_id']}",
                    help="Delete product",
                    type= "primary"
                ):
                    msg = delete_product(product["product_id"])
                    st.success(msg)
                    st.toast("Product Deleted, Kindly refresh the page!")