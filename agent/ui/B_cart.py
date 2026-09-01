


import streamlit as st

from api import (
    get_cart,
    update_cart_item,
    remove_cart_item,
    clear_cart,
    create_cart_checkout,
    check_checkout_status,
    cancel_checkout,
    get_recommendations,
    add_to_cart,
    send_recommendation_stats,
)

from ui.payments.cart_checkout_payment import cart_checkout_payment_dialog

# ============================================================
# RECOMMENDATION MODAL
# ============================================================


@st.dialog("✨ Complete Your Checkout", width="large")
def recommendation_dialog(buyer_id, cart_id):

    # ========================================================
    # FETCH RECOMMENDATIONS ONCE
    # ========================================================

    if st.session_state.checkout_recommendations is None:

        with st.spinner("Finding something useful for your order..."):
            result = get_recommendations(cart_id)

        if result:
            recommendations = result.get("candidates", [])
        else:
            recommendations = []

        st.session_state.checkout_recommendations = recommendations

        # ====================================================
        # CREATE RECOMMENDATION STATS
        # ====================================================

        st.session_state.recommendation_stats = {
            "buyer_id": buyer_id,
            "cart_id": cart_id,
            "razorpay_order_id": None,
            "skipped": False,
            "recommendations": [],
        }

        # ====================================================
        # STORE EVERY SHOWN RECOMMENDATION
        # ====================================================

        for recommendation in recommendations:

            product = recommendation["product"]

            st.session_state.recommendation_stats["recommendations"].append(
                {
                    "product_id": product["product_id"],
                    "merchant_id": product["merchant_id"],
                    "price_at_recommendation": product["price"],
                    "complementarity": recommendation.get("complementarity", 0),
                    "added_to_cart": False,
                    "purchased": False,
                }
            )

        # ====================================================
        # RERUN TO RENDER RECOMMENDATIONS
        # ====================================================

        st.rerun()

    recommendations = st.session_state.checkout_recommendations

    # ========================================================
    # NO RECOMMENDATIONS
    # ========================================================

    if not recommendations:

        if not st.session_state.recommendation_auto_continued:

            st.session_state.recommendation_auto_continued = True

            finish_recommendation_step(buyer_id)

        return

    # ========================================================
    # RECOMMENDATIONS FOUND
    # ========================================================

    st.write("You might also want:")

    for recommendation in recommendations:

        product = recommendation["product"]

        with st.container(border=True):

            col1, col2, col3 = st.columns([1, 3, 1], vertical_alignment="center")

            # ------------------------------------------------
            # IMAGE
            # ------------------------------------------------

            with col1:

                images = product.get("images", [])

                if images:

                    st.image(images[0], width=100)

            # ------------------------------------------------
            # DETAILS
            # ------------------------------------------------

            with col2:

                st.markdown(f"### {product['name']}")

                st.write(f"₹{product['price']}")

                st.caption(
                    f"{recommendation['complementarity']:.0%} " "complementary match"
                )

            # ------------------------------------------------
            # ADD TO CART
            # ------------------------------------------------

            with col3:

                if st.button(
                    "Add",
                    key=("recommendation_add_" f"{product['product_id']}"),
                    use_container_width=True,
                ):

                    response = add_to_cart(buyer_id, product["product_id"], 1)

                    if response:

                        # ====================================
                        # RECORD RECOMMENDATION ADDED
                        # ====================================

                        for rec in st.session_state["recommendation_stats"][
                            "recommendations"
                        ]:

                            if rec["product_id"] == product["product_id"]:

                                rec["added_to_cart"] = True

                                break

                        st.success(f"{product['name']} added to cart!")

                        # ====================================
                        # IMPORTANT:
                        #
                        # DO NOT finish recommendation step.
                        #
                        # User can add more recommendations.
                        # ====================================

                        st.rerun()

    # ========================================================
    # CONTINUE / SKIP
    # ========================================================

    st.divider()

    col1, col2 = st.columns([1, 1])

    # ========================================================
    # SKIP
    # ========================================================

    with col1:

        if st.button("Skip", use_container_width=True):

            # ================================================
            # RECORD THAT USER DISMISSED RECOMMENDATIONS
            # ================================================

            st.session_state.recommendation_stats["skipped"] = True

            finish_recommendation_step(buyer_id)

    # ========================================================
    # CONTINUE TO PAYMENT
    # ========================================================

    with col2:

        if st.button("Continue to Payment", type="primary", use_container_width=True):

            finish_recommendation_step(buyer_id)


# ============================================================
# FINISH RECOMMENDATION STEP
# ============================================================


def finish_recommendation_step(buyer_id):

    print("FINISHING RECOMMENDATION STEP")

    # ========================================================
    # CLOSE RECOMMENDATION PHASE
    # ========================================================

    st.session_state.show_recommendation_dialog = False

    # ========================================================
    # CLEAR OLD RECOMMENDATIONS
    # ========================================================

    st.session_state.checkout_recommendations = None

    # ========================================================
    # GET LATEST CART
    #
    # Important because recommendations may have been added.
    # ========================================================

    cart = get_cart(buyer_id)

    if not cart:

        st.warning("Unable to load your cart.")

        return

    items = cart.get("items", [])

    if not items:

        st.warning("Your cart is empty.")

        return

    # ========================================================
    # CREATE RAZORPAY CHECKOUT
    # ========================================================

    with st.spinner("Preparing your payment..."):

        payment = create_cart_checkout(buyer_id)

    if not payment:

        st.error("Unable to create checkout.")

        return

    order_id = payment["razorpay_order_id"]

    print("NEW CART CHECKOUT CREATED:", order_id)

    # ========================================================
    # ATTACH RAZORPAY ORDER ID TO RECOMMENDATION STATS
    # ========================================================

    if "recommendation_stats" in st.session_state:

        st.session_state.recommendation_stats["razorpay_order_id"] = order_id

    # ========================================================
    # STORE PAYMENT
    # ========================================================

    st.session_state.pending_cart_payment = payment

    st.session_state.shown_cart_payment_order_id = None

    # ========================================================
    # RESET AUTO CONTINUE
    # ========================================================

    st.session_state.recommendation_auto_continued = False

    # ========================================================
    # RERUN
    #
    # Recommendation dialog closes.
    # Payment dialog opens.
    # ========================================================

    st.rerun()


# ============================================================
# SEND RECOMMENDATION STATS
# ============================================================


def submit_recommendation_stats():
    stats = st.session_state.get("recommendation_stats")

    if not stats:
        print("NO RECOMMENDATION STATS TO SUBMIT")
        return

    print("SUBMITTING RECOMMENDATION STATS:", stats)

    try:
        response = send_recommendation_stats(stats)
        print("RECOMMENDATION STATS RESPONSE:", response)

    except Exception as e:
        print("RECOMMENDATION STATS ERROR:", e)

    # Prevent duplicate submission
    st.session_state.recommendation_stats = None


# ============================================================
# CART PAGE
# ============================================================


def cart_page(user):

    buyer_id = user["user_id"]

    # ========================================================
    # SESSION STATE
    # ========================================================

    if "pending_cart_payment" not in st.session_state:

        st.session_state.pending_cart_payment = None

    if "shown_cart_payment_order_id" not in st.session_state:

        st.session_state.shown_cart_payment_order_id = None

    if "show_recommendation_dialog" not in st.session_state:

        st.session_state.show_recommendation_dialog = False

    if "checkout_recommendations" not in st.session_state:

        st.session_state.checkout_recommendations = None

    if "recommendation_auto_continued" not in st.session_state:

        st.session_state.recommendation_auto_continued = False

    if "recommendation_stats" not in st.session_state:

        st.session_state.recommendation_stats = None

    # ========================================================
    # CHECK PENDING CART PAYMENT
    # ========================================================

    if st.session_state.pending_cart_payment:

        payment = st.session_state.pending_cart_payment

        order_id = payment["razorpay_order_id"]

        print("PENDING CART CHECKOUT:", order_id)

        status = check_checkout_status(order_id)

        print("CHECKOUT STATUS:", status)

        # ====================================================
        # PAYMENT SUCCESSFUL
        # ====================================================

        if status == "CONFIRMED":

            # -----------------------------------------------
            # SUBMIT RECOMMENDATION ANALYTICS
            #
            # NO PAYMENT STATUS IS SENT.
            # Server checks CHECKOUTS.
            # -----------------------------------------------

            submit_recommendation_stats()

            print("CART PAYMENT CONFIRMED")

            # -----------------------------------------------
            # CLEAR PAYMENT STATE
            # -----------------------------------------------

            st.session_state.pending_cart_payment = None

            st.session_state.shown_cart_payment_order_id = None

            st.rerun()

        # ====================================================
        # PAYMENT FAILED
        # ====================================================

        elif status == "FAILED":
            # -----------------------------------------------
            # SUBMIT RECOMMENDATION ANALYTICS
            #
            # Server determines the actual checkout status.
            # -----------------------------------------------

            submit_recommendation_stats()

            print("CART CHECKOUT FAILED")

            # -----------------------------------------------
            # CLEAR PAYMENT STATE
            # -----------------------------------------------

            st.session_state.pending_cart_payment = None

            st.session_state.shown_cart_payment_order_id = None

            st.rerun()

        # ====================================================
        # PAYMENT STILL PENDING
        # ====================================================

        elif status == "PENDING_PAYMENT":

            if st.session_state.shown_cart_payment_order_id == order_id:

                print("SAME PENDING CART PAYMENT " "DETECTED AGAIN")

                print("CANCELLING CHECKOUT:", order_id)

                cancel_result = cancel_checkout(order_id)

                print("CANCEL CHECKOUT RESULT:", cancel_result)

                # -------------------------------------------
                # SUBMIT RECOMMENDATION ANALYTICS
                #
                # Server checks CHECKOUTS after cancellation.
                # -------------------------------------------

                submit_recommendation_stats()

                # -------------------------------------------
                # CLEAR PAYMENT STATE
                # -------------------------------------------

                st.session_state.pending_cart_payment = None

                st.session_state.shown_cart_payment_order_id = None

                st.rerun()

            else:

                print("FIRST TIME SHOWING CART PAYMENT:", order_id)

                st.session_state.shown_cart_payment_order_id = order_id

    # ========================================================
    # PAGE
    # ========================================================

    st.title("🛒 Your Cart")

    # ========================================================
    # GET CART
    # ========================================================

    cart = get_cart(buyer_id)

    if not cart:

        st.info("Your cart is empty.")

        return

    items = cart.get("items", [])

    if not items:

        st.info("Your cart is empty.")

        return

    # ========================================================
    # CART TOTAL
    # ========================================================

    total = 0

    # ========================================================
    # CART ITEMS
    # ========================================================

    for item in items:

        quantity = item["quantity"]

        price = item["price"]

        item_total = price * quantity

        total += item_total

        with st.container(border=True):

            col1, col2, col3 = st.columns([1, 3, 1], vertical_alignment="center")

            # ------------------------------------------------
            # IMAGE
            # ------------------------------------------------

            with col1:

                images = item.get("images", [])

                if images:

                    st.image(images[0], width=120)

            # ------------------------------------------------
            # DETAILS
            # ------------------------------------------------

            with col2:

                st.markdown(f"### {item['name']}")

                st.write(f"₹{price} × {quantity}")

                st.caption(f"Merchant: {item['merchant_id']}")

                st.write(f"**Item total: ₹{item_total}**")

            # ------------------------------------------------
            # ACTIONS
            # ------------------------------------------------

            with col3:

                new_quantity = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=item["stock"],
                    value=quantity,
                    step=1,
                    key=("cart_qty_" f"{item['product_id']}"),
                )

                if new_quantity != quantity:

                    if st.button("Update", key=("update_" f"{item['product_id']}")):

                        response = update_cart_item(
                            buyer_id, item["product_id"], new_quantity
                        )

                        if response:

                            st.success("Updated")

                            st.rerun()

                if st.button("Remove", key=("remove_" f"{item['product_id']}")):

                    response = remove_cart_item(buyer_id, item["product_id"])

                    if response:

                        st.rerun()

    # ========================================================
    # SUMMARY
    # ========================================================

    st.divider()

    col1, col2 = st.columns([3, 1])

    with col1:

        st.markdown(f"### Total: ₹{total}")

        st.caption(f"{len(items)} product(s) in cart")

    with col2:

        if st.button("🗑️ Clear Cart", use_container_width=True):

            clear_cart(buyer_id)

            st.rerun()

    # ========================================================
    # CHECKOUT
    # ========================================================

    st.divider()

    if st.button(f"💳 Checkout ₹{total}", type="primary", use_container_width=True):

        # ----------------------------------------------------
        # Don't start another checkout while payment pending.
        # ----------------------------------------------------

        if st.session_state.pending_cart_payment:

            st.warning("A checkout is already in progress.")

        else:

            # ------------------------------------------------
            # START RECOMMENDATION PHASE
            #
            # No Razorpay order is created yet.
            # ------------------------------------------------

            st.session_state.checkout_recommendations = None

            st.session_state.recommendation_stats = None

            st.session_state.recommendation_auto_continued = False

            st.session_state.show_recommendation_dialog = True

            st.rerun()

    # ========================================================
    # RECOMMENDATION DIALOG
    # ========================================================

    if (
        st.session_state.show_recommendation_dialog
        and not st.session_state.pending_cart_payment
    ):

        recommendation_dialog(buyer_id, cart["cart_id"])

    # ========================================================
    # PAYMENT DIALOG
    # ========================================================

    if st.session_state.get("pending_cart_payment"):

        cart_checkout_payment_dialog(st.session_state.pending_cart_payment, buyer_id)
