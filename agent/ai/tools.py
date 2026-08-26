import requests

import streamlit as st
from langchain_community.tools import tool

from ai.structured_agent import structured_prepare_products_llm


#### MERCHANT_TOOLS:
def merchant_toolkit(merchant_id):

    headers = {
        "X-User-ID": merchant_id,
        "X-Actor-Type": "AGENT",
    }

    @tool
    def get_products():
        """
        Fetch all products belonging to the specified merchant.
        This tool can be used to fetch all the products listed by the merchant in the market
        output = json of all products or an empty list if no products available
        """

        response = requests.get(
            "http://localhost:8009/merchants/get_products",
            params={"merchant_id": merchant_id},
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()["products"]
        else:
            return []

    @tool
    def add_product(dsc):
        """
        ***  if u dont know what to input, input whaterver the merchant asked u ***
        *** input = string only : even if u have a dict etc make it a string before inputing here ***
        ***CALL THE TOOL ONLY AFTER 'DSC' description IS CONFIRMED BY THE USER***
           Add the confirmed product to the merchant's inventory. Input is the description that you will first make sure after getting confirmation from the user and then and then only call this tool. Once tool is called, no returning back.
        """

        response = structured_prepare_products_llm.invoke(dsc)
        product_data = response.model_dump()
        print("response from structured_llm : ", product_data)

        response = requests.post(
            "http://localhost:8009/merchants/add_product",
            json={
                "merchant_id": merchant_id,
                "name": product_data["name"],
                "price": product_data["price"],
                "stock": product_data["stock"],
                "description": product_data["description"],
                "category": product_data["category"],
                "images": product_data["images"],
            },
            headers=headers,
        )
        print("STATUS:", response.status_code)
        print("TEXT:", response.text)
        return response.json()

    @tool
    def sales_by_merchant():
        """
        Retrieve all orders placed belonging to the current merchant.
        Returns all orders associated with the current merchant,
        including order ID, buyer ID, product ID, quantity,
        price, total price, status, and creation time.

        Do not use this tool to create, modify, or cancel orders.
        """

        response = requests.get(
            "http://localhost:8009/merchants/sales_by_merchant",
            params={"merchant_id": merchant_id},
            headers=headers,
        )

        data = response.json()

        return {"status_code": response.status_code, "orders": data.get("orders", [])}

    return [get_products, add_product, sales_by_merchant]


#### BUYER TOOLS:


def buyer_toolkit(user_id):

    headers = {
        "X-User-ID": user_id,
        "X-Actor-Type": "AGENT",
    }

    @tool
    def search_products(query, price=None, quantity=None):
        """
        Search for products using semantic similarity while respecting price and stock constraints.

        Use this tool when the buyer wants to find products.

        Args:
            query: What the buyer is looking for, expressed in natural language.
            price: Optional maximum price the buyer is willing to pay. All prices are in INR(Indian National Rupee) only.
            quantity: Optional minimum quantity of the product that must be in stock.

        IMPORTANT:
        - If the buyer asks to "show more", "see more", "next", or similar,
        call this tool again with the SAME query, price, and quantity.
        Do not change or invent the cursor; pagination is handled automatically.
        - If the buyer starts a new product search or changes any search constraint,
        use the new query/constraints.
        - Do not use this tool to add, edit, or delete products.
        """

        current_search = st.session_state.get("product_search")
        # New search if query or filters changed
        if (
            current_search is None
            or current_search["query"] != query
            or current_search["price"] != price
            or current_search["quantity"] != quantity
        ):
            cursor = None

        # Same search → continue from previous cursor
        else:
            cursor = current_search["cursor"]

        response = requests.get(
            "http://localhost:8009/buyers/search_product",
            params={
                "query": query,
                "price": price,
                "quantity": quantity,
                "cursor": cursor,
            },
            headers=headers,
        )

        result = response.json()
        # Save current search state + new cursor
        st.session_state.product_search = {
            "query": query,
            "price": price,
            "quantity": quantity,
            "cursor": result.get("next_cursor"),
        }

        # Save products for UI
        new_products = result.get("products", [])
        print("buyer tool found result : \n", result)
        print("buyer tool found product : \n", new_products)
        if cursor is None:
            # New search
            st.session_state.product_search_results = new_products
        else:
            # for "Show more"
            st.session_state.product_search_results.extend(new_products)

        return result

    @tool
    def buy_product(product_id, quantity):
        """
        Purchase a product.

        IMPORTANT:
        Only call this tool after the buyer has explicitly confirmed
        the purchase, including the quantity.
        """
        response = requests.post(
            "http://localhost:8009/orders/create_order",
            json={"buyer_id": user_id, "product_id": product_id, "quantity": quantity},
            headers=headers,
        )

        return {"status_code": response.status_code, "data": response.json()}

    @tool
    def previous_orders():
        """
        Retrieve the buyer's previous orders.
        Returns the buyer's previous orders, including order details such as
        order ID, product ID, quantity, price, and order status.
        Do not use this tool to create, cancel, or modify orders.
        """
        response = requests.get(
            "http://localhost:8009/buyers/get_previous_orders",
            params={"user_id": user_id},
            headers=headers,
        )
        data = response.json()
        return {
            "status_code": response.status_code,
            "previous_orders": data.get("previous_orders", []),
        }

    return [search_products, buy_product, previous_orders]
