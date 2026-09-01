import streamlit as st

from ai.agent import ask_agent

st.set_page_config(initial_sidebar_state=600)

from ui.payments.payment import payment_dialog
from ui.payments.cart_checkout_payment import cart_checkout_payment_dialog

from api import (
    check_order_status,
    check_checkout_status,
    cancel_order,
    cancel_checkout,
    add_to_cart,
)


def ai_scout_page(user):

    # ============================================================
    # INITIALIZE SESSION STATE
    # ============================================================

    if "buyer_chat_history" not in st.session_state:
        st.session_state.buyer_chat_history = []

    if "product_search_results" not in st.session_state:
        st.session_state.product_search_results = []

    if "buy_now_prompt" not in st.session_state:
        st.session_state.buy_now_prompt = None

    # ============================================================
    # NORMAL PAYMENT STATE
    # ============================================================

    if "pending_payment" not in st.session_state:
        st.session_state.pending_payment = None

    # Stores the Razorpay order ID whose normal payment
    # dialog has already been displayed once.
    if "shown_payment_order_id" not in st.session_state:
        st.session_state.shown_payment_order_id = None

    # ============================================================
    # CART CHECKOUT STATE
    # ============================================================

    if "pending_cart_checkout" not in st.session_state:
        st.session_state.pending_cart_checkout = None

    # Stores the Razorpay order ID whose cart checkout
    # dialog has already been displayed once.
    if "shown_cart_checkout_order_id" not in st.session_state:
        st.session_state.shown_cart_checkout_order_id = None

    # ============================================================
    # CHECK NORMAL PAYMENT
    # ============================================================

    if st.session_state.pending_payment:

        payment = st.session_state.pending_payment

        order_id = payment["razorpay_order_id"]

        print("PENDING PAYMENT:", order_id)

        result = check_order_status(order_id)

        print("CHECK ORDER RESULT:", result)

        if result:

            status = result.get("status")
            paid = result.get("paid", False)

            print("STATUS:", status)
            print("PAID:", paid)

            # ----------------------------------------------------
            # CASE A: PAYMENT SUCCESSFUL
            # ----------------------------------------------------

            if paid is True:

                print("PAYMENT CONFIRMED")

                st.session_state.pending_payment = None
                st.session_state.shown_payment_order_id = None

                st.rerun()

            # ----------------------------------------------------
            # CASE B: PAYMENT FAILED / CANCELLED
            # ----------------------------------------------------

            elif status in ["FAILED", "CANCELLED"]:

                print("PAYMENT FAILED/CANCELLED")

                st.session_state.pending_payment = None
                st.session_state.shown_payment_order_id = None

                st.rerun()

            # ----------------------------------------------------
            # CASE C: STILL PENDING
            #
            # If the same pending order is encountered again,
            # its payment dialog has already been shown once.
            #
            # Therefore cancel the order.
            # ----------------------------------------------------

            elif status == "PENDING_PAYMENT":

                if (
                    st.session_state.shown_payment_order_id
                    == order_id
                ):

                    print(
                        "SAME PENDING PAYMENT DETECTED AGAIN"
                    )

                    print(
                        "CANCELLING NORMAL PAYMENT:",
                        order_id
                    )

                    cancel_result = cancel_order(order_id)

                    print(
                        "CANCEL ORDER RESULT:",
                        cancel_result
                    )

                    # Clear local state regardless of whether
                    # cancellation request succeeded.
                    st.session_state.pending_payment = None
                    st.session_state.shown_payment_order_id = None

                    st.rerun()

                else:

                    # ------------------------------------------------
                    # FIRST TIME SHOWING THIS PAYMENT
                    # ------------------------------------------------

                    print(
                        "FIRST TIME SHOWING PAYMENT:",
                        order_id
                    )

                    st.session_state.shown_payment_order_id = order_id

    # ============================================================
    # NORMAL PAYMENT DIALOG
    # ============================================================

    if st.session_state.pending_payment:

        payment_dialog(
            st.session_state.pending_payment,
            user["user_id"]
        )

    # ============================================================
    # CHECK CART CHECKOUT
    # ============================================================

    if st.session_state.pending_cart_checkout:

        checkout = st.session_state.pending_cart_checkout

        order_id = checkout["razorpay_order_id"]

        print("PENDING CART CHECKOUT:", order_id)

        status = check_checkout_status(order_id)

        print("CART CHECKOUT STATUS:", status)

        # --------------------------------------------------------
        # CASE A: PAYMENT SUCCESSFUL
        # --------------------------------------------------------

        if status == "CONFIRMED":

            print("CART CHECKOUT CONFIRMED")

            st.session_state.pending_cart_checkout = None
            st.session_state.shown_cart_checkout_order_id = None

            st.rerun()

        # --------------------------------------------------------
        # CASE B: CHECKOUT FAILED / CANCELLED
        # --------------------------------------------------------

        elif status in ["FAILED", "CANCELLED"]:

            print(
                "CART CHECKOUT FAILED/CANCELLED"
            )

            st.session_state.pending_cart_checkout = None
            st.session_state.shown_cart_checkout_order_id = None

            st.rerun()

        # --------------------------------------------------------
        # CASE C: STILL PENDING
        #
        # If this exact order ID has already been shown once,
        # this is another Streamlit execution.
        #
        # Therefore cancel the checkout.
        # --------------------------------------------------------

        elif status == "PENDING_PAYMENT":

            if (
                st.session_state.shown_cart_checkout_order_id
                == order_id
            ):

                print(
                    "SAME PENDING CART CHECKOUT DETECTED AGAIN"
                )

                print(
                    "CANCELLING CART CHECKOUT:",
                    order_id
                )

                cancel_result = cancel_checkout(order_id)

                print(
                    "CANCEL CHECKOUT RESULT:",
                    cancel_result
                )

                # Clear local state regardless of whether
                # cancellation request succeeded.
                st.session_state.pending_cart_checkout = None
                st.session_state.shown_cart_checkout_order_id = None

                st.rerun()

            else:

                # ------------------------------------------------
                # FIRST TIME SHOWING THIS CART CHECKOUT
                # ------------------------------------------------

                print(
                    "FIRST TIME SHOWING CART CHECKOUT:",
                    order_id
                )

                st.session_state.shown_cart_checkout_order_id = order_id

    # ============================================================
    # CART PAYMENT DIALOG
    # ============================================================

    if st.session_state.pending_cart_checkout:

        cart_checkout_payment_dialog(
            st.session_state.pending_cart_checkout,
            user["user_id"]
        )

    # ============================================================
    # PRODUCTS SIDEBAR
    # ============================================================

    has_results = bool(
        st.session_state.product_search_results
    )

    if has_results:

        st.sidebar.title("🔎 Products Found")

        for product in st.session_state.product_search_results:

            with st.sidebar.container(border=True):

                col1, col2 = st.columns(
                    [1, 1.5],
                    vertical_alignment="top"
                )

                # ------------------------------------------------
                # IMAGE
                # ------------------------------------------------

                with col1:

                    images = product.get("images", [])

                    if images:

                        st.image(
                            images[0],
                            width="stretch"
                        )

                # ------------------------------------------------
                # DETAILS
                # ------------------------------------------------

                with col2:

                    st.markdown(
                        f"**Product :** "
                        f"{product.get('name', 'Unnamed Product')}"
                    )

                    st.markdown(
                        f"**Price :** "
                        f"💰 ₹{product.get('price', 'N/A')}"
                    )

                    st.markdown(
                        f"**Desc :** "
                        f"{product.get('description', 'N/A')}"
                    )

                    st.markdown(
                        f"**Available Stock :** "
                        f"{product.get('stock', 'N/A')}"
                    )

                    if product.get("match_percentage"):

                        st.markdown(
                            f"**Match :** "
                            f"🎯 {product['match_percentage']}"
                        )

                    st.space("stretch")

                    # ------------------------------------------------
                    # CART CONTROLS
                    # ------------------------------------------------

                    product_id = product["product_id"]

                    available_stock = product.get(
                        "stock",
                        0
                    )

                    quantity_key = (
                        f"cart_qty_{product_id}"
                    )

                    if quantity_key not in st.session_state:

                        st.session_state[
                            quantity_key
                        ] = 1

                    # ------------------------------------------------
                    # QUANTITY + ADD TO CART
                    # ------------------------------------------------

                    if available_stock > 0:

                        qty_col1, qty_col2, qty_col3, cart_col = st.columns(
                            [0.7, 0.8, 0.7, 2.5]
                        )

                        with qty_col1:

                            if st.button(
                                "−",
                                key=f"minus_{product_id}",
                                use_container_width=True,
                            ):

                                if (
                                    st.session_state[
                                        quantity_key
                                    ] > 1
                                ):

                                    st.session_state[
                                        quantity_key
                                    ] -= 1

                                st.rerun()

                        with qty_col2:

                            st.markdown(
                                f"""
                                <div style="
                                    text-align: center;
                                    padding-top: 6px;
                                    font-weight: bold;
                                ">
                                    {
                                        st.session_state[
                                            quantity_key
                                        ]
                                    }
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

                                if (
                                    st.session_state[
                                        quantity_key
                                    ]
                                    < available_stock
                                ):

                                    st.session_state[
                                        quantity_key
                                    ] += 1

                                else:

                                    st.toast(
                                        "Maximum available stock reached."
                                    )

                                st.rerun()

                        with cart_col:

                            if st.button(
                                "🛒 Add to Cart",
                                key=f"add_cart_{product_id}",
                                type="secondary",
                                use_container_width=True,
                            ):

                                quantity = (
                                    st.session_state[
                                        quantity_key
                                    ]
                                )

                                result = add_to_cart(
                                    buyer_id=user["user_id"],
                                    product_id=product_id,
                                    quantity=quantity,
                                )

                                if result:

                                    st.toast(
                                        f"Added {quantity} × "
                                        f"{product.get('name', 'product')} "
                                        f"to cart!"
                                    )

                                    st.session_state[
                                        quantity_key
                                    ] = 1

                    else:

                        st.error("Out of stock")

                    # ------------------------------------------------
                    # BUY NOW
                    # ------------------------------------------------

                    if st.button(
                        "🛒 Buy Now",
                        key=f"buy_{product['product_id']}",
                        type="primary",
                        use_container_width=True,
                    ):

                        st.session_state.buy_now_prompt = (
                            f"I want to buy the product with "
                            f"product_id {product['product_id']}. "
                            f"Quantity = "
                            f"{st.session_state[quantity_key]}. "
                            f"Please help me proceed with the purchase."
                        )

                        st.rerun()

    # ============================================================
    # SCOUT
    # ============================================================

    st.title(
        f"Welcome to the Market, {user['user']}"
    )

    st.header("🛍️ SCOUT")

    st.subheader("The AI Buyer for you!")

    print(
        "PENDING PAYMENT:",
        st.session_state.get("pending_payment")
    )

    print(
        "PENDING CART CHECKOUT:",
        st.session_state.get(
            "pending_cart_checkout"
        )
    )

    # ============================================================
    # CHAT HISTORY
    # ============================================================

    for chat_msg in st.session_state.buyer_chat_history:

        with st.chat_message(chat_msg["role"]):

            st.markdown(
                chat_msg["content"]
            )

    # ============================================================
    # BUY NOW PROMPT
    # ============================================================

    if st.session_state.buy_now_prompt:

        question = st.session_state.buy_now_prompt

        st.session_state.buy_now_prompt = None

        st.session_state.buyer_chat_history.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):

            st.write(question)

        with st.spinner(
            "🤖 Scout is working with your order..."
        ):

            answer, products, payment, cart_checkout_details = (
                ask_agent(
                    question,
                    user["user_id"]
                )
            )

        st.session_state.buyer_chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):

            st.write(answer)

        if products:

            st.session_state.product_search_results = products

        if payment:

            print(
                "payment_details:",
                payment
            )

            st.session_state.pending_payment = payment

            # IMPORTANT:
            # Brand-new payment must be considered
            # not-yet-shown.
            st.session_state.shown_payment_order_id = None

        if cart_checkout_details:

            print(
                "checkout_details:",
                cart_checkout_details
            )

            st.session_state.pending_cart_checkout = (
                cart_checkout_details
            )

            # IMPORTANT:
            # Brand-new checkout must be considered
            # not-yet-shown.
            st.session_state.shown_cart_checkout_order_id = None

        if (
            products
            or payment
            or cart_checkout_details
        ):

            st.rerun()

    # ============================================================
    # NORMAL CHAT INPUT
    # ============================================================

    question = st.chat_input(
        "What are you looking for?"
    )

    if question:

        with st.chat_message("user"):

            st.write(question)

        st.session_state.buyer_chat_history.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.spinner(
            "🤖 Scout is finding the best option for you..."
        ):

            answer, products, payment, cart_checkout_details = (
                ask_agent(
                    question,
                    user["user_id"]
                )
            )

        st.session_state.buyer_chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        if products:

            st.session_state.product_search_results = products

        with st.chat_message("assistant"):

            st.write(answer)

        if payment:

            print(
                "payment_details:",
                payment
            )

            st.session_state.pending_payment = payment

            # Brand-new normal payment
            st.session_state.shown_payment_order_id = None

        if cart_checkout_details:

            print(
                "checkout_details:",
                cart_checkout_details
            )

            st.session_state.pending_cart_checkout = (
                cart_checkout_details
            )

            # Brand-new cart checkout
            st.session_state.shown_cart_checkout_order_id = None

        if (
            products
            or payment
            or cart_checkout_details
        ):

            st.rerun()







# import streamlit as st

# from ai.agent import ask_agent

# st.set_page_config(initial_sidebar_state=600)

# from ui.payments.payment import payment_dialog
# from ui.payments.cart_checkout_payment import cart_checkout_payment_dialog

# from api import (
#     check_order_status,
#     check_checkout_status,
#     cancel_order,
#     cancel_checkout,
#     add_to_cart,
#     get_recommendations,
#     get_cart,
#     create_cart_checkout,
# )

# # ============================================================
# # RECOMMENDATION MODAL
# # ============================================================


# @st.dialog("✨ Complete Your Checkout", width="large")
# def recommendation_dialog(buyer_id, cart_id):

#     # ========================================================
#     # INITIALIZE RECOMMENDATION STATE
#     # ========================================================

#     if "checkout_recommendations" not in st.session_state:
#         st.session_state.checkout_recommendations = None

#     # ========================================================
#     # FETCH RECOMMENDATIONS ONLY ONCE
#     # ========================================================

#     if st.session_state.checkout_recommendations is None:

#         with st.spinner("Finding something useful for your order..."):

#             result = get_recommendations(cart_id)

#         print("RECOMMENDATION RESULT:", result)

#         if result:
#             recommendations = result.get("candidates", [])
#         else:
#             recommendations = []

#         st.session_state.checkout_recommendations = recommendations

#         # ----------------------------------------------------
#         # IMPORTANT
#         #
#         # DO NOT call st.rerun() here.
#         #
#         # The dialog is already executing. Streamlit will
#         # continue rendering using the newly stored state.
#         # ----------------------------------------------------

#     recommendations = st.session_state.checkout_recommendations

#     # ========================================================
#     # NO RECOMMENDATIONS
#     # ========================================================

#     if not recommendations:

#         print("NO RECOMMENDATIONS -> CONTINUING TO PAYMENT")

#         # ----------------------------------------------------
#         # Automatically finish recommendation phase.
#         # ----------------------------------------------------

#         finish_recommendation_step(buyer_id)

#         return

#     # ========================================================
#     # RECOMMENDATIONS FOUND
#     # ========================================================

#     st.write("You might also want to add:")

#     for recommendation in recommendations:

#         product = recommendation["product"]

#         with st.container(border=True):

#             col1, col2, col3 = st.columns([1, 3, 1], vertical_alignment="center")

#             # ------------------------------------------------
#             # IMAGE
#             # ------------------------------------------------

#             with col1:

#                 images = product.get("images", [])

#                 if images:

#                     st.image(images[0], width=100)

#             # ------------------------------------------------
#             # DETAILS
#             # ------------------------------------------------

#             with col2:

#                 st.markdown(f"### {product['name']}")

#                 st.write(f"₹{product['price']}")

#                 complementarity = recommendation.get("complementarity", 0)

#                 st.caption(f"{complementarity:.0%} complementary match")

#             # ------------------------------------------------
#             # ADD
#             # ------------------------------------------------

#             with col3:

#                 if st.button(
#                     "Add",
#                     key=("recommendation_add_" f"{product['product_id']}"),
#                     use_container_width=True,
#                 ):

#                     response = add_to_cart(buyer_id, product["product_id"], 1)

#                     if response:

#                         st.success(f"{product['name']} added to cart!")

#                         # ------------------------------------
#                         # Recommendation phase finished.
#                         # ------------------------------------

#                         finish_recommendation_step(buyer_id)

#                         return

#     # ========================================================
#     # SKIP
#     # ========================================================

#     st.divider()

#     if st.button("Skip & Continue to Payment", use_container_width=True):

#         print("USER SKIPPED RECOMMENDATIONS")

#         finish_recommendation_step(buyer_id)

#         return


# # ============================================================
# # FINISH RECOMMENDATION STEP
# # ============================================================


# def finish_recommendation_step(buyer_id):

#     print("FINISHING RECOMMENDATION STEP")

#     # ========================================================
#     # MARK RECOMMENDATION PHASE AS COMPLETE
#     # ========================================================

#     st.session_state.checkout_recommendation_checked = True

#     # ========================================================
#     # CLOSE RECOMMENDATION MODAL
#     # ========================================================

#     st.session_state.show_recommendation_dialog = False

#     # ========================================================
#     # CLEAR OLD RECOMMENDATIONS
#     #
#     # They must not be reused during the next checkout.
#     # ========================================================

#     st.session_state.checkout_recommendations = None

#     # ========================================================
#     # GET LATEST CART
#     #
#     # VERY IMPORTANT:
#     #
#     # If the user added a recommendation, the cart total has
#     # changed.
#     #
#     # Therefore we create Razorpay order AFTER getting the
#     # updated cart.
#     # ========================================================

#     cart = get_cart(buyer_id)

#     if not cart:

#         st.warning("Unable to load your cart.")

#         return

#     items = cart.get("items", [])

#     if not items:

#         st.warning("Your cart is empty.")

#         return

#     # ========================================================
#     # CREATE RAZORPAY ORDER
#     # ========================================================

#     with st.spinner("Preparing your payment..."):

#         payment = create_cart_checkout(buyer_id)

#     if not payment:

#         st.error("Unable to create checkout.")

#         return

#     order_id = payment["razorpay_order_id"]

#     print("NEW CART CHECKOUT CREATED:", order_id)

#     # ========================================================
#     # SAVE PAYMENT
#     # ========================================================

#     st.session_state.pending_cart_checkout = payment

#     # --------------------------------------------------------
#     # Brand-new checkout.
#     # Payment dialog has NOT been displayed yet.
#     # --------------------------------------------------------

#     st.session_state.shown_cart_checkout_order_id = None

#     # ========================================================
#     # RESET RECOMMENDATION STATE
#     #
#     # This allows the NEXT checkout to get a fresh
#     # recommendation.
#     # ========================================================

#     st.session_state.checkout_recommendation_checked = False

#     st.session_state.checkout_recommendations = None

#     # ========================================================
#     # RERUN
#     #
#     # Recommendation dialog is now closed and payment dialog
#     # will be opened by cart checkout state.
#     # ========================================================

#     st.rerun()


# # ============================================================
# # AI SCOUT PAGE
# # ============================================================


# def ai_scout_page(user):

#     buyer_id = user["user_id"]

#     # ========================================================
#     # INITIALIZE SESSION STATE
#     # ========================================================

#     if "buyer_chat_history" not in st.session_state:

#         st.session_state.buyer_chat_history = []

#     if "product_search_results" not in st.session_state:

#         st.session_state.product_search_results = []

#     if "buy_now_prompt" not in st.session_state:

#         st.session_state.buy_now_prompt = None

#     # ========================================================
#     # NORMAL PAYMENT STATE
#     # ========================================================

#     if "pending_payment" not in st.session_state:

#         st.session_state.pending_payment = None

#     if "shown_payment_order_id" not in st.session_state:

#         st.session_state.shown_payment_order_id = None

#     # ========================================================
#     # CART CHECKOUT STATE
#     # ========================================================

#     if "pending_cart_checkout" not in st.session_state:

#         st.session_state.pending_cart_checkout = None

#     if "shown_cart_checkout_order_id" not in st.session_state:

#         st.session_state.shown_cart_checkout_order_id = None

#     # ========================================================
#     # RECOMMENDATION STATE
#     # ========================================================

#     if "show_recommendation_dialog" not in st.session_state:

#         st.session_state.show_recommendation_dialog = False

#     if "checkout_recommendation_checked" not in st.session_state:

#         st.session_state.checkout_recommendation_checked = False

#     if "checkout_recommendations" not in st.session_state:

#         st.session_state.checkout_recommendations = None

#     if "recommendation_cart_id" not in st.session_state:

#         st.session_state.recommendation_cart_id = None

#     # ========================================================
#     # CHECK NORMAL PAYMENT
#     # ========================================================

#     if st.session_state.pending_payment:

#         payment = st.session_state.pending_payment

#         order_id = payment["razorpay_order_id"]

#         print("PENDING PAYMENT:", order_id)

#         result = check_order_status(order_id)

#         print("CHECK ORDER RESULT:", result)

#         if result:

#             status = result.get("status")

#             paid = result.get("paid", False)

#             print("STATUS:", status)

#             print("PAID:", paid)

#             # ------------------------------------------------
#             # PAYMENT SUCCESSFUL
#             # ------------------------------------------------

#             if paid is True:

#                 print("PAYMENT CONFIRMED")

#                 st.session_state.pending_payment = None

#                 st.session_state.shown_payment_order_id = None

#                 st.rerun()

#             # ------------------------------------------------
#             # PAYMENT FAILED / CANCELLED
#             # ------------------------------------------------

#             elif status in ["FAILED", "CANCELLED"]:

#                 print("PAYMENT FAILED/CANCELLED")

#                 st.session_state.pending_payment = None

#                 st.session_state.shown_payment_order_id = None

#                 st.rerun()

#             # ------------------------------------------------
#             # STILL PENDING
#             # ------------------------------------------------

#             elif status == "PENDING_PAYMENT":

#                 if st.session_state.shown_payment_order_id == order_id:

#                     print("SAME PENDING PAYMENT DETECTED AGAIN")

#                     print("CANCELLING NORMAL PAYMENT:", order_id)

#                     cancel_result = cancel_order(order_id)

#                     print("CANCEL ORDER RESULT:", cancel_result)

#                     st.session_state.pending_payment = None

#                     st.session_state.shown_payment_order_id = None

#                     st.rerun()

#                 else:

#                     print("FIRST TIME SHOWING PAYMENT:", order_id)

#                     st.session_state.shown_payment_order_id = order_id

#     # ========================================================
#     # NORMAL PAYMENT DIALOG
#     # ========================================================

#     if st.session_state.pending_payment:

#         payment_dialog(st.session_state.pending_payment, buyer_id)

#     # ========================================================
#     # CHECK CART CHECKOUT
#     # ========================================================

#     if st.session_state.pending_cart_checkout:

#         checkout = st.session_state.pending_cart_checkout

#         order_id = checkout["razorpay_order_id"]

#         print("PENDING CART CHECKOUT:", order_id)

#         status = check_checkout_status(order_id)

#         print("CART CHECKOUT STATUS:", status)

#         # ----------------------------------------------------
#         # PAYMENT SUCCESSFUL
#         # ----------------------------------------------------

#         if status == "CONFIRMED":

#             print("CART CHECKOUT CONFIRMED")

#             st.session_state.pending_cart_checkout = None

#             st.session_state.shown_cart_checkout_order_id = None

#             st.rerun()

#         # ----------------------------------------------------
#         # FAILED / CANCELLED
#         # ----------------------------------------------------

#         elif status in ["FAILED", "CANCELLED"]:

#             print("CART CHECKOUT FAILED/CANCELLED")

#             st.session_state.pending_cart_checkout = None

#             st.session_state.shown_cart_checkout_order_id = None

#             st.rerun()

#         # ----------------------------------------------------
#         # STILL PENDING
#         # ----------------------------------------------------

#         elif status == "PENDING_PAYMENT":

#             if st.session_state.shown_cart_checkout_order_id == order_id:

#                 print("SAME PENDING CART CHECKOUT DETECTED AGAIN")

#                 print("CANCELLING CART CHECKOUT:", order_id)

#                 cancel_result = cancel_checkout(order_id)

#                 print("CANCEL CHECKOUT RESULT:", cancel_result)

#                 st.session_state.pending_cart_checkout = None

#                 st.session_state.shown_cart_checkout_order_id = None

#                 st.rerun()

#             else:

#                 print("FIRST TIME SHOWING CART CHECKOUT:", order_id)

#                 st.session_state.shown_cart_checkout_order_id = order_id

#     # ========================================================
#     # CART PAYMENT DIALOG
#     # ========================================================

#     if st.session_state.pending_cart_checkout:

#         cart_checkout_payment_dialog(st.session_state.pending_cart_checkout, buyer_id)

#     # ========================================================
#     # RECOMMENDATION DIALOG
#     #
#     # IMPORTANT:
#     #
#     # This is controlled by session state.
#     #
#     # Therefore st.rerun() will NOT make the dialog disappear.
#     # ========================================================

#     if (
#         st.session_state.show_recommendation_dialog
#         and not st.session_state.pending_cart_checkout
#     ):

#         recommendation_dialog(buyer_id, st.session_state.recommendation_cart_id)

#     # ========================================================
#     # PRODUCTS SIDEBAR
#     # ========================================================

#     has_results = bool(st.session_state.product_search_results)

#     if has_results:

#         st.sidebar.title("🔎 Products Found")

#         for product in st.session_state.product_search_results:

#             with st.sidebar.container(border=True):

#                 col1, col2 = st.columns([1, 1.5], vertical_alignment="top")

#                 # ------------------------------------------------
#                 # IMAGE
#                 # ------------------------------------------------

#                 with col1:

#                     images = product.get("images", [])

#                     if images:

#                         st.image(images[0], width="stretch")

#                 # ------------------------------------------------
#                 # DETAILS
#                 # ------------------------------------------------

#                 with col2:

#                     st.markdown(
#                         f"**Product :** " f"{product.get('name', 'Unnamed Product')}"
#                     )

#                     st.markdown(f"**Price :** " f"💰 ₹{product.get('price', 'N/A')}")

#                     st.markdown(f"**Desc :** " f"{product.get('description', 'N/A')}")

#                     st.markdown(
#                         f"**Available Stock :** " f"{product.get('stock', 'N/A')}"
#                     )

#                     if product.get("match_percentage"):

#                         st.markdown(f"**Match :** " f"🎯 {product['match_percentage']}")

#                     st.space("stretch")

#                     # ------------------------------------------------
#                     # CART CONTROLS
#                     # ------------------------------------------------

#                     product_id = product["product_id"]

#                     available_stock = product.get("stock", 0)

#                     quantity_key = f"cart_qty_{product_id}"

#                     if quantity_key not in st.session_state:

#                         st.session_state[quantity_key] = 1

#                     # ------------------------------------------------
#                     # QUANTITY + ADD TO CART
#                     # ------------------------------------------------

#                     if available_stock > 0:

#                         qty_col1, qty_col2, qty_col3, cart_col = st.columns(
#                             [0.7, 0.8, 0.7, 2.5]
#                         )

#                         with qty_col1:

#                             if st.button(
#                                 "−",
#                                 key=f"minus_{product_id}",
#                                 use_container_width=True,
#                             ):

#                                 if st.session_state[quantity_key] > 1:

#                                     st.session_state[quantity_key] -= 1

#                                 st.rerun()

#                         with qty_col2:

#                             st.markdown(
#                                 f"""
#                                 <div style="
#                                     text-align: center;
#                                     padding-top: 6px;
#                                     font-weight: bold;
#                                 ">
#                                     {
#                                         st.session_state[
#                                             quantity_key
#                                         ]
#                                     }
#                                 </div>
#                                 """,
#                                 unsafe_allow_html=True,
#                             )

#                         with qty_col3:

#                             if st.button(
#                                 "+",
#                                 key=f"plus_{product_id}",
#                                 use_container_width=True,
#                             ):

#                                 if st.session_state[quantity_key] < available_stock:

#                                     st.session_state[quantity_key] += 1

#                                 else:

#                                     st.toast("Maximum available stock reached.")

#                                 st.rerun()

#                         with cart_col:

#                             if st.button(
#                                 "🛒 Add to Cart",
#                                 key=f"add_cart_{product_id}",
#                                 type="secondary",
#                                 use_container_width=True,
#                             ):

#                                 quantity = st.session_state[quantity_key]

#                                 result = add_to_cart(
#                                     buyer_id=buyer_id,
#                                     product_id=product_id,
#                                     quantity=quantity,
#                                 )

#                                 if result:

#                                     st.toast(
#                                         f"Added {quantity} × "
#                                         f"{product.get('name', 'product')} "
#                                         f"to cart!"
#                                     )

#                                     st.session_state[quantity_key] = 1

#                     else:

#                         st.error("Out of stock")

#                     # ------------------------------------------------
#                     # BUY NOW
#                     # ------------------------------------------------

#                     if st.button(
#                         "🛒 Buy Now",
#                         key=f"buy_{product['product_id']}",
#                         type="primary",
#                         use_container_width=True,
#                     ):

#                         st.session_state.buy_now_prompt = (
#                             f"I want to buy the product with "
#                             f"product_id {product['product_id']}. "
#                             f"Quantity = "
#                             f"{st.session_state[quantity_key]}. "
#                             f"Please help me proceed with the purchase."
#                         )

#                         st.rerun()

#     # ============================================================
#     # SCOUT
#     # ============================================================

#     st.title(f"Welcome to the Market, {user['user']}")

#     st.header("🛍️ SCOUT")

#     st.subheader("The AI Buyer for you!")

#     # ============================================================
#     # CHAT HISTORY
#     # ============================================================

#     for chat_msg in st.session_state.buyer_chat_history:

#         with st.chat_message(chat_msg["role"]):

#             st.markdown(chat_msg["content"])

#     # ============================================================
#     # BUY NOW PROMPT
#     # ============================================================

#     if st.session_state.buy_now_prompt:

#         question = st.session_state.buy_now_prompt

#         st.session_state.buy_now_prompt = None

#         st.session_state.buyer_chat_history.append(
#             {"role": "user", "content": question}
#         )

#         with st.chat_message("user"):

#             st.write(question)

#         with st.spinner("🤖 Scout is working with your order..."):

#             answer, products, payment, cart_checkout_details = ask_agent(
#                 question, buyer_id
#             )

#         st.session_state.buyer_chat_history.append(
#             {"role": "assistant", "content": answer}
#         )

#         with st.chat_message("assistant"):

#             st.write(answer)

#         if products:

#             st.session_state.product_search_results = products

#         if payment:

#             print("payment_details:", payment)

#             st.session_state.pending_payment = payment

#             st.session_state.shown_payment_order_id = None

#         if cart_checkout_details:

#             print("checkout_details:", cart_checkout_details)

#             st.session_state.pending_cart_checkout = cart_checkout_details

#             st.session_state.shown_cart_checkout_order_id = None

#         if products or payment or cart_checkout_details:

#             st.rerun()

#     # ============================================================
#     # NORMAL CHAT INPUT
#     # ============================================================

#     question = st.chat_input("What are you looking for?")

#     if question:

#         with st.chat_message("user"):

#             st.write(question)

#         st.session_state.buyer_chat_history.append(
#             {"role": "user", "content": question}
#         )

#         with st.spinner("🤖 Scout is finding the best option for you..."):

#             answer, products, payment, cart_checkout_details = ask_agent(
#                 question, buyer_id
#             )

#         st.session_state.buyer_chat_history.append(
#             {"role": "assistant", "content": answer}
#         )

#         with st.chat_message("assistant"):

#             st.write(answer)

#         if products:

#             st.session_state.product_search_results = products

#         if payment:

#             print("payment_details:", payment)

#             st.session_state.pending_payment = payment

#             st.session_state.shown_payment_order_id = None

#         if cart_checkout_details:

#             print("checkout_details:", cart_checkout_details)

#             st.session_state.pending_cart_checkout = cart_checkout_details

#             st.session_state.shown_cart_checkout_order_id = None

#         if products or payment or cart_checkout_details:

#             st.rerun()
