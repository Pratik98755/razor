import streamlit as st
from ai.agent import ask_agent

st.set_page_config(initial_sidebar_state=600)

from ui.payments.payment import payment_dialog
from ui.payments.cart_checkout_payment import cart_checkout_payment_dialog

from api import check_order_status,add_to_cart


def ai_scout_page(user):

    # Initialize session state
    if "buyer_chat_history" not in st.session_state:
        st.session_state.buyer_chat_history = []

    if "product_search_results" not in st.session_state:
        st.session_state.product_search_results = []

    if "buy_now_prompt" not in st.session_state:
        st.session_state.buy_now_prompt = None

    # razorpay payment
    if "pending_payment" not in st.session_state:
        st.session_state.pending_payment = None
    # razorpay payment for cart checkout
    if "pending_cart_checkout" not in st.session_state:
        st.session_state.pending_cart_checkout = None

    if st.session_state.pending_payment:
        order_id = st.session_state.pending_payment["razorpay_order_id"]
        print("pending payment : ", order_id)
        status = check_order_status(order_id)
        if status == True:
            st.session_state.pending_payment = None
            st.rerun()
    # payment dialog
    if st.session_state.pending_payment:
        payment_dialog(st.session_state.pending_payment, user["user_id"])

    if st.session_state.pending_cart_checkout:
        order_id = st.session_state.pending_cart_checkout["razorpay_order_id"]
        print("pending cart checkout : ", order_id)
        status = check_order_status(order_id)
        if status == True:
            print('pending cart PAID')
            st.session_state.pending_cart_checkout = None
            st.rerun()
    # payment dialog for cart
    if st.session_state.pending_cart_checkout:
        cart_checkout_payment_dialog(
            st.session_state.pending_cart_checkout, user["user_id"]
        )

    has_results = bool(st.session_state.product_search_results)

    # ---------------- PRODUCTS SIDEBAR ----------------

    if has_results:

        st.sidebar.title("🔎 Products Found")

        for product in st.session_state.product_search_results:

            with st.sidebar.container(border=True):

                col1, col2 = st.columns([1, 1.5], vertical_alignment="top")

                # ---------------- IMAGE ----------------

                with col1:

                    images = product.get("images", [])

                    if images:
                        st.image(images[0], width="stretch")

                # ---------------- DETAILS ----------------

                with col2:

                    st.markdown(
                        f"**Product :**  " f"{product.get('name', 'Unnamed Product')}"
                    )

                    st.markdown(f"**Price :**  " f"💰 ₹{product.get('price', 'N/A')}")

                    st.markdown(f"**Desc :**  " f"{product.get('description', 'N/A')}")

                    st.markdown(
                        f"**Available Stock :**  " f"{product.get('stock', 'N/A')}"
                    )

                    if product.get("match_percentage"):

                        st.markdown(
                            f"**Match :**  " f"🎯 {product['match_percentage']}"
                        )

                    st.space("stretch")
                    
                    
                    
                    
                    # ---------------- CART CONTROLS ----------------

                    product_id = product["product_id"]
                    available_stock = product.get("stock", 0)

                    quantity_key = f"cart_qty_{product_id}"

                    if quantity_key not in st.session_state:
                        st.session_state[quantity_key] = 1


                    # ---------------- QUANTITY + ADD TO CART ----------------

                    if available_stock > 0:

                        # One row:  -  quantity  +  |  Add to Cart
                        qty_col1, qty_col2, qty_col3, cart_col = st.columns(
                            [0.7, 0.8, 0.7, 2.5]
                        )

                        with qty_col1:
                            if st.button(
                                "−",
                                key=f"minus_{product_id}",
                                use_container_width=True,
                            ):
                                if st.session_state[quantity_key] > 1:
                                    st.session_state[quantity_key] -= 1
                                st.rerun()

                        with qty_col2:
                            st.markdown(
                                f"""
                                <div style="
                                    text-align: center;
                                    padding-top: 6px;
                                    font-weight: bold;
                                ">
                                    {st.session_state[quantity_key]}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        with qty_col3:
                            if st.button(
                                "+",
                                key=f"plus_{product_id}",
                                use_container_width=True,
                            ):
                                if st.session_state[quantity_key] < available_stock:
                                    st.session_state[quantity_key] += 1
                                else:
                                    st.toast("Maximum available stock reached.")

                                st.rerun()

                        with cart_col:
                            if st.button(
                                "🛒 Add to Cart",
                                key=f"add_cart_{product_id}",
                                type="secondary",
                                use_container_width=True,
                            ):
                                quantity = st.session_state[quantity_key]

                                result = add_to_cart(
                                    buyer_id=user["user_id"],
                                    product_id=product_id,
                                    quantity=quantity,
                                )

                                if result:
                                    st.toast(
                                        f"Added {quantity} × "
                                        f"{product.get('name', 'product')} to cart!"
                                    )

                                    st.session_state[quantity_key] = 1

                    else:
                        st.error("Out of stock")





                    # ---------------- BUY NOW ----------------

                    if st.button(
                        "🛒 Buy Now",
                        key=f"buy_{product['product_id']}",
                        type="primary",
                        use_container_width=True,
                    ):

                        st.session_state.buy_now_prompt = (
                            f"I want to buy the product with product_id "
                            f"{product['product_id']}. "
                            f"Please help me proceed with the purchase."
                        )

                        st.rerun()

    # ---------------- SCOUT ----------------

    st.title(f"Welcome to the Market, {user['user']}")

    st.header("🛍️ SCOUT")

    st.subheader("The AI Buyer for you!")

    print("PENDING PAYMENT:", st.session_state.get("pending_payment"))

    # ---------------- CHAT HISTORY ----------------

    for chat_msg in st.session_state.buyer_chat_history:

        with st.chat_message(chat_msg["role"]):

            st.markdown(chat_msg["content"])

    # ---------------- BUY NOW PROMPT ----------------

    if st.session_state.buy_now_prompt:

        question = st.session_state.buy_now_prompt

        # Clear it immediately so it is processed only once
        st.session_state.buy_now_prompt = None

        # Add user message to chat history
        st.session_state.buyer_chat_history.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.write(question)

        # Agent
        # answer, products, payment = ask_agent(question, user["user_id"])
        with st.spinner("🤖 Scout is working with your order..."):
            answer, products, payment, cart_checkout_details = ask_agent(
                question, user["user_id"]
            )

        # Save assistant response
        st.session_state.buyer_chat_history.append(
            {"role": "assistant", "content": answer}
        )

        with st.chat_message("assistant"):
            st.write(answer)

        # Save products if returned
        if products:
            st.session_state.product_search_results = products

        # razorpay payment details
        if payment:
            print("payment_details:", payment)
            st.session_state.pending_payment = payment

        if cart_checkout_details:
            print("checkout_details : ", cart_checkout_details)
            st.session_state.pending_cart_checkout = cart_checkout_details

        if products or payment or cart_checkout_details:
            st.rerun()

    # ---------------- NORMAL CHAT INPUT ----------------

    question = st.chat_input("What are you looking for?")

    if question:

        # User message
        with st.chat_message("user"):
            st.write(question)

        st.session_state.buyer_chat_history.append(
            {"role": "user", "content": question}
        )

        # Agent
        # answer, products, payment = ask_agent(question, user["user_id"])
        with st.spinner("🤖 Scout is finding the best option for you..."):
            answer, products, payment, cart_checkout_details = ask_agent(
                question, user["user_id"]
            )

        # Save assistant response
        st.session_state.buyer_chat_history.append(
            {"role": "assistant", "content": answer}
        )

        # Save products
        if products:
            st.session_state.product_search_results = products

        with st.chat_message("assistant"):
            st.write(answer)

        # razorpay payment details
        if payment:
            print("payment_details:", payment)
            st.session_state.pending_payment = payment

        if cart_checkout_details:
            print("checkout_details : ", cart_checkout_details)
            st.session_state.pending_cart_checkout = cart_checkout_details

        if products or payment or cart_checkout_details:
            st.rerun()
