import streamlit as st
import pandas as pd

from api import get_products, sales_by_merchant


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
