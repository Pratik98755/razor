import streamlit as st
import pandas as pd

from api import get_products, sales_by_merchant, get_recommendation_stats


def dashboard_page(user):

    # =========================================================
    # FETCH DATA
    # =========================================================

    products = get_products(user["user_id"])
    orders = sales_by_merchant(user["user_id"])

    # Convert None -> []
    products = products or []
    orders = orders or []

    # =========================================================
    # PRODUCT LOOKUP
    # =========================================================

    product_map = {product["product_id"]: product for product in products}

    # =========================================================
    # BASIC METRICS
    # =========================================================

    # Only count successful sales
    valid_orders = [
        order for order in orders if order.get("status") in ["CONFIRMED", "COMPLETED"]
    ]

    total_sales = sum(float(order.get("total_price", 0)) for order in valid_orders)

    total_orders = len(valid_orders)

    total_units_sold = sum(int(order.get("quantity", 0)) for order in valid_orders)

    low_stock_products = [
        product for product in products if int(product.get("stock", 0)) <= 5
    ]

    # =========================================================
    # HEADER
    # =========================================================

    st.title("Merchant Dashboard")
    st.subheader(f"Hello {user['user']}!")
    st.caption("Here's what's happening with your store.")

    # =========================================================
    # METRICS
    # =========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sales", f"₹{total_sales:,.0f}")

    with col2:
        st.metric("Orders", total_orders)

    with col3:
        st.metric("Units Sold", total_units_sold)

    with col4:
        st.metric("Low Stock", len(low_stock_products))

    st.divider()

    # =========================================================
    # SALES OVER TIME
    # =========================================================

    st.subheader("📈 Sales Overview")

    if valid_orders:

        sales_data = []

        for order in valid_orders:

            created_at = order.get("createdAt")

            if not created_at:
                continue

            sales_data.append(
                {
                    "date": pd.to_datetime(created_at).date(),
                    "sales": float(order.get("total_price", 0)),
                }
            )

        if sales_data:

            sales_df = pd.DataFrame(sales_data)

            daily_sales = sales_df.groupby("date")["sales"].sum().sort_index()

            st.bar_chart(daily_sales, height=350)

        else:
            st.info("No sales data available.")

    else:
        st.info("No sales yet.")

    # =========================================================
    # BEST SELLERS + INVENTORY
    # =========================================================

    col1, col2 = st.columns(2)

    # =========================================================
    # BEST SELLERS
    # =========================================================

    with col1:

        st.subheader("🏆 Best Sellers")

        if valid_orders:

            product_sales = {}

            for order in valid_orders:

                product_id = order.get("product_id")

                if not product_id:
                    continue

                quantity = int(order.get("quantity", 0))

                product_sales[product_id] = product_sales.get(product_id, 0) + quantity

            best_sellers = []

            for product_id, units in product_sales.items():

                product = product_map.get(product_id)

                product_name = product["name"] if product else product_id

                best_sellers.append({"Product": product_name, "Units Sold": units})

            if best_sellers:

                best_sellers_df = (
                    pd.DataFrame(best_sellers)
                    .sort_values("Units Sold", ascending=False)
                    .head(5)
                )

                st.bar_chart(best_sellers_df.set_index("Product"), height=300)

            else:
                st.info("No product sales available.")

        else:
            st.info("No sales yet.")

    # =========================================================
    # INVENTORY
    # =========================================================

    with col2:

        st.subheader("📦 Inventory")

        if products:

            stock_data = []

            for product in products:

                stock_data.append(
                    {
                        "Product": product.get("name", "Unknown"),
                        "Stock": int(product.get("stock", 0)),
                    }
                )

            stock_df = pd.DataFrame(stock_data)

            # Lowest stock first
            stock_df = stock_df.sort_values("Stock", ascending=True)

            st.bar_chart(stock_df.set_index("Product"), height=300)

        else:
            st.info("No products found.")

    # # =========================================================
    # # AI RECOMMENDATION ANALYTICS
    # # =========================================================

    # recommendation_stats = get_recommendation_stats(user["user_id"])

    # st.divider()
    # st.subheader("🤖 AI Recommendation Performance")

    # if recommendation_stats:

    #     shown = int(recommendation_stats.get("shown", 0))
    #     added = int(recommendation_stats.get("added_to_cart", 0))
    #     purchased = int(recommendation_stats.get("purchased", 0))
    #     dismissed = int(recommendation_stats.get("dismissed", 0))
    #     purchased_units = int(recommendation_stats.get("purchased_units", 0))

    #     cross_sell_revenue = float(recommendation_stats.get("cross_sell_revenue", 0))

    #     add_rate = float(recommendation_stats.get("add_to_cart_rate", 0))

    #     purchase_rate = float(recommendation_stats.get("purchase_rate", 0))

    #     conversion_rate = float(
    #         recommendation_stats.get("recommendation_conversion_rate", 0)
    #     )

    #     revenue_per_recommendation = float(
    #         recommendation_stats.get("revenue_per_recommendation", 0)
    #     )

    #     # ---------------------------------------------------------
    #     # MAIN RECOMMENDATION METRICS
    #     # ---------------------------------------------------------

    #     col1, col2, col3, col4 = st.columns(4)

    #     with col1:
    #         st.metric("Recommendations Shown", shown)

    #     with col2:
    #         st.metric("Added to Cart", added, delta=f"{add_rate:.1%}")

    #     with col3:
    #         st.metric("Purchased", purchased, delta=f"{purchase_rate:.1%}")

    #     with col4:
    #         st.metric("Dismissed", dismissed)

    #     # ---------------------------------------------------------
    #     # REVENUE + CONVERSION
    #     # ---------------------------------------------------------

    #     col1, col2, col3, col4 = st.columns(4)

    #     with col1:
    #         st.metric("Cross-Sell Revenue", f"₹{cross_sell_revenue:,.0f}")

    #     with col2:
    #         st.metric("Purchase Conversion", f"{conversion_rate:.1%}")

    #     with col3:
    #         st.metric("Recommended Units Sold", purchased_units)

    #     with col4:
    #         st.metric("Revenue / Recommendation", f"₹{revenue_per_recommendation:,.2f}")

    # else:

    #     st.info("No recommendation analytics available yet.")

    # =========================================================
    # AI GROWTH / RECOMMENDATION ANALYTICS
    # =========================================================

    recommendation_stats = get_recommendation_stats(user["user_id"])

    st.divider()

    if recommendation_stats:

        shown = int(recommendation_stats.get("shown", 0))
        added = int(recommendation_stats.get("added_to_cart", 0))
        purchased = int(recommendation_stats.get("purchased", 0))
        dismissed = int(recommendation_stats.get("dismissed", 0))

        purchased_units = int(recommendation_stats.get("purchased_units", 0))

        cross_sell_revenue = float(recommendation_stats.get("cross_sell_revenue", 0))

        add_rate = float(recommendation_stats.get("add_to_cart_rate", 0))

        purchase_rate = float(recommendation_stats.get("purchase_rate", 0))

        conversion_rate = float(
            recommendation_stats.get("recommendation_conversion_rate", 0)
        )

        revenue_per_recommendation = float(
            recommendation_stats.get("revenue_per_recommendation", 0)
        )

        st.subheader("🤖 AI Growth")

        # =====================================================
        # AI-GENERATED REVENUE — HERO METRIC
        # =====================================================

        st.markdown("### 💰 AI-Generated Revenue")

        revenue_col1, revenue_col2 = st.columns([2, 1])

        with revenue_col1:
            with st.container(border=True):
                st.metric(
                    "Revenue generated through AI recommendations",
                    f"₹{cross_sell_revenue:,.0f}",
                )

        with revenue_col2:
            with st.container(border=True):
                st.metric("Additional Purchases", purchased)

        # =====================================================
        # RECOMMENDATION FUNNEL
        # =====================================================

        st.markdown("### 📊 Recommendation Funnel")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Recommendations Shown", shown)

        with col2:
            st.metric("Added to Cart", added, delta=f"{add_rate:.1%}")

        with col3:
            st.metric("Purchased", purchased, delta=f"{conversion_rate:.1%}")

        with col4:
            st.metric("Dismissed", dismissed)

        # =====================================================
        # SECONDARY METRICS
        # =====================================================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Add-to-Cart Rate", f"{add_rate:.1%}")

        with col2:
            st.metric("Recommendation Conversion", f"{conversion_rate:.1%}")

        with col3:
            st.metric("Revenue / Recommendation", f"₹{revenue_per_recommendation:,.2f}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Recommended Units Sold", purchased_units)

        with col2:
            st.metric("Purchase After Add-to-Cart", f"{purchase_rate:.1%}")

    else:

        st.info(
            "No AI recommendation activity yet. "
            "Your AI cross-sell analytics will appear here."
        )

    # =====================================================
    # TOP AI CROSS-SELLS
    # =====================================================

    st.markdown("### 🛍️ Top AI Cross-Sells")

    top_ai_cross_sells = recommendation_stats.get("top_ai_cross_sells", [])

    if top_ai_cross_sells:

        cross_sell_rows = []

        for item in top_ai_cross_sells:

            product = product_map.get(item.get("product_id"))

            product_name = (
                product["name"] if product else item.get("product_id", "Unknown")
            )

            cross_sell_rows.append(
                {
                    "Product": product_name,
                    "Shown": item.get("shown", 0),
                    "Added": item.get("added_to_cart", 0),
                    "Add Rate": (f"{float(item.get('add_to_cart_rate', 0)):.1%}"),
                    "Purchased": item.get("purchased", 0),
                    "Purchase Rate": (f"{float(item.get('purchase_rate', 0)):.1%}"),
                    "Skipped": item.get("skipped", 0),
                    "Skip Rate": (f"{float(item.get('skip_rate', 0)):.1%}"),
                    "Units Sold": item.get("purchased_units", 0),
                    "Revenue": (f"₹{float(item.get('revenue', 0)):,.0f}"),
                }
            )

        cross_sell_df = pd.DataFrame(cross_sell_rows)

        st.dataframe(cross_sell_df, width="stretch", hide_index=True)

    else:

        st.info("No AI cross-sell recommendations yet.")

    # =========================================================
    # LOW STOCK
    # =========================================================

    st.subheader("⚠️ Stock Overview")

    if products:

        # Show minimum 3 products, or all if there are fewer than 3.
        stock_overview = sorted(products, key=lambda x: int(x.get("stock", 0)))[:3]

        stock_data = []

        for product in stock_overview:
            stock_data.append(
                {
                    "Product": product.get("name", "Unknown"),
                    "Category": product.get("category", "—"),
                    "Stock": int(product.get("stock", 0)),
                }
            )

        st.dataframe(stock_data, width="stretch", hide_index=True)

    else:
        st.info("No products found.")

    # =========================================================
    # RECENT ORDERS
    # =========================================================

    st.subheader("🧾 Recent Orders")

    if valid_orders:

        recent_orders = []

        for order in valid_orders[:10]:

            product = product_map.get(order.get("product_id"))

            product_name = (
                product["name"] if product else order.get("product_id", "Unknown")
            )

            created_at = order.get("createdAt")

            if created_at:
                order_datetime = pd.to_datetime(created_at)
                formatted_datetime = order_datetime.strftime("%d %b %Y, %I:%M %p")
            else:
                formatted_datetime = "—"

            recent_orders.append(
                {
                    "Order ID": order.get("order_id", "—"),
                    "Product": product_name,
                    "Quantity": order.get("quantity", 0),
                    "Amount": f"₹{float(
                        order.get("total_price", 0)
                    ):,.2f}",
                    "Status": order.get("status", "—"),
                    "Date & Time": formatted_datetime,
                }
            )

        st.dataframe(recent_orders, width="stretch", hide_index=True)

    else:
        st.info("No orders yet.")
