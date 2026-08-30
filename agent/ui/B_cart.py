import streamlit as st

from api import (
    get_cart,
    update_cart_item,
    remove_cart_item,
    clear_cart,
    create_cart_checkout,
    check_order_status,
)

from ui.payments.cart_checkout_payment import cart_checkout_payment_dialog


def cart_page(user):

    ############## pre checks ###############
    if "pending_cart_payment" not in st.session_state:
        st.session_state.pending_cart_payment = None

    if st.session_state.pending_cart_payment:
        order_id = st.session_state.pending_cart_payment["razorpay_order_id"]
        print("pending cart checkout : ", order_id)
        status = check_order_status(order_id)
        if status == True:
            print("pending cart PAID")
            st.session_state.pending_cart_payment = None
            st.rerun()

    #########################################

    buyer_id = user["user_id"]
    st.title("🛒 Your Cart")

    # -----------------------------------------
    # Get cart
    # -----------------------------------------

    cart = get_cart(buyer_id)

    if not cart:
        st.info("Your cart is empty.")
        return

    items = cart.get("items", [])

    if not items:
        st.info("Your cart is empty.")
        return

    total = 0

    # -----------------------------------------
    # Cart items
    # -----------------------------------------

    for item in items:

        quantity = item["quantity"]
        price = item["price"]

        item_total = price * quantity
        total += item_total

        with st.container(border=True):

            col1, col2, col3 = st.columns([1, 3, 1], vertical_alignment="center")

            # ---------------- IMAGE ----------------

            with col1:

                images = item.get("images", [])

                if images:
                    st.image(images[0], width=120)

            # ---------------- DETAILS ----------------

            with col2:

                st.markdown(f"### {item['name']}")

                st.write(f"₹{price} × {quantity}")

                st.caption(f"Merchant: {item['merchant_id']}")

                st.write(f"**Item total: ₹{item_total}**")

            # ---------------- ACTIONS ----------------

            with col3:

                new_quantity = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=item["stock"],
                    value=quantity,
                    step=1,
                    key=f"cart_qty_{item['product_id']}",
                )

                if new_quantity != quantity:

                    if st.button("Update", key=f"update_{item['product_id']}"):

                        response = update_cart_item(
                            buyer_id, item["product_id"], new_quantity
                        )

                        if response:

                            st.success("Updated")
                            st.rerun()

                if st.button("Remove", key=f"remove_{item['product_id']}"):

                    response = remove_cart_item(buyer_id, item["product_id"])

                    if response:

                        st.rerun()

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    st.divider()

    col1, col2 = st.columns([3, 1])

    with col1:

        st.markdown(f"### Total: ₹{total}")

        st.caption(f"{len(items)} product(s) in cart")

    with col2:

        if st.button("🗑️ Clear Cart", use_container_width=True):

            clear_cart(buyer_id)

            st.rerun()

    # -----------------------------------------
    # Checkout
    # -----------------------------------------

    st.divider()

    if st.button(f"💳 Checkout ₹{total}", type="primary", use_container_width=True):

        with st.spinner("Preparing your checkout..."):

            payment = create_cart_checkout(buyer_id)

        if payment:

            st.session_state.pending_cart_payment = payment

            st.rerun()

    # -----------------------------------------
    # Payment dialog
    # -----------------------------------------

    if st.session_state.get("pending_cart_payment"):

        cart_checkout_payment_dialog(st.session_state.pending_cart_payment, buyer_id)
