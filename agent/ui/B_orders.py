import streamlit as st
import pandas as pd

from api import get_orders_by_buyer, get_product_details


def orders_page(user):

    # =========================================================
    # FETCH ORDERS
    # =========================================================

    orders = get_orders_by_buyer(user["user_id"])
    orders = orders or []

    st.title("📦 My Orders")

    if not orders:
        st.info("You haven't placed any orders yet.")
        return

    # =========================================================
    # FETCH PRODUCT DETAILS
    # =========================================================

    product_ids = list(
        {order.get("product_id") for order in orders if order.get("product_id")}
    )

    products = get_product_details(product_ids)
    products = products or []

    # product_id -> product
    product_map = {product["product_id"]: product for product in products}

    # =========================================================
    # METRICS
    # =========================================================

    total_orders = len(orders)

    total_spent = sum(
        float(order.get("total_price", 0))
        for order in orders
        if order.get("status") != "CANCELLED"
    )

    active_orders = sum(1 for order in orders if order.get("status") == "CONFIRMED")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Orders", total_orders)

    with col2:
        st.metric("Total Spent", f"₹{total_spent:,.0f}")

    with col3:
        st.metric("Active Orders", active_orders)

    st.divider()

    # =========================================================
    # FILTERS
    # =========================================================

    col1, col2 = st.columns(2)

    with col1:
        status_filter = st.selectbox(
            "Status", ["All", "CONFIRMED", "COMPLETED", "CANCELLED"]
        )

    with col2:
        sort_order = st.selectbox("Sort", ["Newest first", "Oldest first"])

    # =========================================================
    # FILTER ORDERS
    # =========================================================

    filtered_orders = orders.copy()

    if status_filter != "All":

        filtered_orders = [
            order for order in filtered_orders if order.get("status") == status_filter
        ]

    filtered_orders.sort(
        key=lambda x: x.get("createdAt", ""), reverse=(sort_order == "Newest first")
    )

    if not filtered_orders:
        st.info("No orders match your filter.")
        return

    # =========================================================
    # ORDER CARDS
    # =========================================================

    for order in filtered_orders:

        product = product_map.get(order.get("product_id"), {})

        product_name = product.get("name", "Unknown Product")

        product_category = product.get("category", "")

        quantity = int(order.get("quantity", 0))

        price_per_unit = float(order.get("price_per_unit", 0))

        total_price = float(order.get("total_price", 0))

        status = order.get("status", "UNKNOWN")

        # =====================================================
        # DATE & TIME
        # =====================================================

        created_at = order.get("createdAt")

        if created_at:

            try:

                order_datetime = pd.to_datetime(created_at)

                formatted_datetime = order_datetime.strftime("%d %b %Y, %I:%M %p")

            except Exception:

                formatted_datetime = str(created_at)

        else:

            formatted_datetime = "Unknown date"

        # =====================================================
        # STATUS
        # =====================================================

        status_icons = {"CONFIRMED": "🟢", "COMPLETED": "🟡", "CANCELLED": "🔴"}

        status_icon = status_icons.get(status, "⚪")

        # =====================================================
        # CARD
        # =====================================================

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.subheader(product_name)

                if product_category:
                    st.caption(product_category)

                st.write(f"Order ID: `{order.get('order_id', '—')}`")

                st.write(f"🕒 {formatted_datetime}")

            with col2:

                st.markdown(f"### {status_icon} {status}")

            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:

                st.caption("Quantity")

                st.write(quantity)

            with col2:

                st.caption("Price / unit")

                st.write(f"₹{price_per_unit:,.2f}")

            with col3:

                st.caption("Total")

                st.write(f"₹{total_price:,.2f}")
