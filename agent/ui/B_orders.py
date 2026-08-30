
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
        {
            order.get("product_id")
            for order in orders
            if order.get("product_id")
        }
    )

    products = get_product_details(product_ids)
    products = products or []

    # product_id -> product
    product_map = {
        product["product_id"]: product
        for product in products
    }

    # =========================================================
    # GROUP ORDERS BY RAZORPAY ORDER ID
    # =========================================================
    # Same Razorpay order ID = same checkout/payment.
    #
    # Direct purchase:
    #   razorpay_order_id -> 1 order
    #
    # Cart purchase:
    #   razorpay_order_id -> multiple orders
    #
    grouped_orders = {}

    for order in orders:

        razorpay_order_id = order.get("razorpay_order_id")

        # Fallback in case an old order doesn't have
        # razorpay_order_id.
        group_key = razorpay_order_id or order.get("order_id")

        if group_key not in grouped_orders:
            grouped_orders[group_key] = []

        grouped_orders[group_key].append(order)

    grouped_orders = list(grouped_orders.values())

    # =========================================================
    # METRICS
    # =========================================================
    total_orders = len(grouped_orders)

    total_spent = sum(
        sum(
            float(order.get("total_price", 0))
            for order in order_group
            if order.get("status") != "CANCELLED"
        )
        for order_group in grouped_orders
    )

    active_orders = sum(
        1
        for order_group in grouped_orders
        if any(
            order.get("status") == "CONFIRMED"
            for order in order_group
        )
    )

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
            "Status",
            ["All", "CONFIRMED", "COMPLETED", "CANCELLED"]
        )

    with col2:
        sort_order = st.selectbox(
            "Sort",
            ["Newest first", "Oldest first"]
        )

    # =========================================================
    # FILTER ORDER GROUPS
    # =========================================================
    filtered_order_groups = []

    for order_group in grouped_orders:

        if status_filter != "All":

            # Keep the checkout if at least one order
            # has the selected status.
            if not any(
                order.get("status") == status_filter
                for order in order_group
            ):
                continue

        filtered_order_groups.append(order_group)

    # =========================================================
    # SORT GROUPS
    # =========================================================
    def get_group_date(order_group):

        dates = [
            order.get("createdAt", "")
            for order in order_group
            if order.get("createdAt")
        ]

        return min(dates) if dates else ""

    filtered_order_groups.sort(
        key=get_group_date,
        reverse=(sort_order == "Newest first")
    )

    if not filtered_order_groups:
        st.info("No orders match your filter.")
        return

    # =========================================================
    # ORDER CARDS
    # =========================================================
    for order_group in filtered_order_groups:

        # -----------------------------------------------------
        # GROUP INFORMATION
        # -----------------------------------------------------
        first_order = order_group[0]

        razorpay_order_id = first_order.get(
            "razorpay_order_id",
            "—"
        )

        created_at = first_order.get("createdAt")

        if created_at:
            try:
                order_datetime = pd.to_datetime(created_at)
                formatted_datetime = order_datetime.strftime(
                    "%d %b %Y, %I:%M %p"
                )
            except Exception:
                formatted_datetime = str(created_at)
        else:
            formatted_datetime = "Unknown date"

        # -----------------------------------------------------
        # GROUP STATUS
        # -----------------------------------------------------
        statuses = {
            order.get("status")
            for order in order_group
        }

        if statuses == {"CANCELLED"}:
            group_status = "CANCELLED"

        elif statuses == {"COMPLETED"}:
            group_status = "COMPLETED"

        elif "CONFIRMED" in statuses:
            group_status = "CONFIRMED"

        else:
            group_status = first_order.get(
                "status",
                "UNKNOWN"
            )

        status_icons = {
            "CONFIRMED": "🟢",
            "COMPLETED": "🟡",
            "CANCELLED": "🔴"
        }

        status_icon = status_icons.get(
            group_status,
            "⚪"
        )

        # -----------------------------------------------------
        # GROUP TOTAL
        # -----------------------------------------------------
        group_total = sum(
            float(order.get("total_price", 0))
            for order in order_group
        )

        # =====================================================
        # CARD
        # =====================================================
        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                # For a single-product purchase
                if len(order_group) == 1:

                    order = order_group[0]

                    product = product_map.get(
                        order.get("product_id"),
                        {}
                    )

                    product_name = product.get(
                        "name",
                        "Unknown Product"
                    )

                    product_category = product.get(
                        "category",
                        ""
                    )

                    st.subheader(product_name)

                    if product_category:
                        st.caption(product_category)

                # For cart checkout
                else:

                    st.subheader(
                        f"🛒 Cart Purchase ({len(order_group)} items)"
                    )

                st.write(
                    f"Payment ID: `{razorpay_order_id}`"
                )

                st.write(
                    f"🕒 {formatted_datetime}"
                )

            with col2:

                st.markdown(
                    f"### {status_icon} {group_status}"
                )

            st.divider()

            # =================================================
            # PRODUCTS INSIDE THIS CHECKOUT
            # =================================================
            for order in order_group:

                product = product_map.get(
                    order.get("product_id"),
                    {}
                )

                product_name = product.get(
                    "name",
                    "Unknown Product"
                )

                quantity = int(
                    order.get("quantity", 0)
                )

                price_per_unit = float(
                    order.get("price_per_unit", 0)
                )

                total_price = float(
                    order.get("total_price", 0)
                )

                # Keep the existing 3-column style
                col1, col2, col3 = st.columns(3)

                with col1:

                    st.caption("Product")

                    st.write(product_name)

                with col2:

                    st.caption("Quantity")

                    st.write(quantity)

                with col3:

                    st.caption("Total")

                    st.write(
                        f"₹{total_price:,.2f}"
                    )

                # Show price/unit without changing
                # the overall visual structure.
                st.caption(
                    f"Price / unit: ₹{price_per_unit:,.2f}"
                )

                if order != order_group[-1]:
                    st.divider()

            # =================================================
            # CHECKOUT TOTAL
            # =================================================
            if len(order_group) > 1:

                st.divider()

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.caption("Items")
                    st.write(len(order_group))

                with col2:
                    st.caption("Payment")
                    st.write("Razorpay")

                with col3:
                    st.caption("Total")
                    st.write(
                        f"₹{group_total:,.2f}"
                    )

