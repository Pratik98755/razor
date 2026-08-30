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
        Initiate the purchase of a product.

        IMPORTANT:
        Only call this tool after the buyer has explicitly confirmed
        the purchase, including the quantity.

        This tool creates the marketplace order and initiates the
        Razorpay payment process.

        IMPORTANT:
        A successful response means the order was created and payment
        is required. It does NOT mean that the payment was completed.
        """

        response = requests.post(
            "http://localhost:8009/orders/create_order",
            json={"buyer_id": user_id, "product_id": product_id, "quantity": quantity},
            headers=headers,
        )
        data = response.json()
        print("BUY PRODUCT TOOL RESPONSE:", data)
        return {"status_code": response.status_code, "data": data}

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

    @tool
    def get_product_details(product_ids):
        """takes in array of product_ids and returns details about the products. use this tool to find
        information about any product given you have the product id"""
        try:
            response = requests.get(
                "http://localhost:8009/buyers/product_details",
                params={"product_ids": product_ids},
                timeout=10,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("product_details", [])

        except requests.exceptions.RequestException as e:
            print(f"Products API error: {e}")
            return []

        except ValueError:
            print("Products API returned invalid JSON.")
            return []

    ########################## CARTS ############################
    @tool
    def add_to_cart(product_id, quantity):
        """
        Add a product to the buyer's permanent shopping cart.

        Use this when the buyer explicitly asks to add a product
        to their cart.

        IMPORTANT:
        - Do NOT use this when the buyer only asks to view a product.
        - Do NOT use this for Buy Now purchases.
        - quantity must be explicitly known.
        - This does NOT make a payment.
        """

        response = requests.post(
            "http://localhost:8009/carts/add",
            json={"buyer_id": user_id, "product_id": product_id, "quantity": quantity},
            headers=headers,
        )
        data = response.json()
        print("ADD TO CART TOOL RESPONSE:", data)
        return {"status_code": response.status_code, "data": data}

    @tool
    def get_cart():
        """
        Retrieve the buyer's current shopping cart.

        Use this when the buyer asks:
        - what's in my cart
        - show my cart
        - what have I added
        - how much is my cart
        - review my cart

        This tool does NOT modify the cart.
        """
        response = requests.get(
            "http://localhost:8009/carts/cart",
            params={"buyer_id": user_id},
            headers=headers,
        )

        data = response.json()
        print("GET CART TOOL RESPONSE:", data)
        return {"status_code": response.status_code, "cart": data.get("cart", {})}

    @tool
    def update_cart(product_id, quantity):
        """
        Change the quantity of a product already in the buyer's cart.

        Use this when the buyer explicitly asks to change
        the quantity of a cart item.

        Example:
        "Change the keyboard quantity to 3."

        quantity must be at least 1.
        This does NOT make a payment.
        """
        response = requests.patch(
            "http://localhost:8009/carts/update",
            json={"buyer_id": user_id, "product_id": product_id, "quantity": quantity},
            headers=headers,
        )

        data = response.json()
        print("UPDATE CART TOOL RESPONSE:", data)
        return {"status_code": response.status_code, "data": data}

    @tool
    def remove_from_cart(product_id):
        """
        Remove a specific product from the buyer's cart.

        Use only when the buyer explicitly asks to remove
        a product from their cart.

        This does NOT make a payment.
        """
        response = requests.delete(
            "http://localhost:8009/carts/remove",
            json={"buyer_id": user_id, "product_id": product_id},
            headers=headers,
        )

        data = response.json()
        print("REMOVE FROM CART TOOL RESPONSE:", data)
        return {"status_code": response.status_code, "data": data}

    @tool
    def clear_cart():
        """
        Remove ALL products from the buyer's cart.

        IMPORTANT:
        Only use this when the buyer explicitly asks
        to empty or clear their entire cart.

        Do not use this when the buyer asks to remove
        only one product.
        """
        response = requests.delete(
            "http://localhost:8009/carts/clear",
            json={"buyer_id": user_id},
            headers=headers,
        )
        data = response.json()
        print("CLEAR CART TOOL RESPONSE:", data)
        return {"status_code": response.status_code, "data": data}

    @tool
    def cart_checkout(user_id):
        """
        this tool is used for cart checkout, this only begins the payment process for the products available in the cart of the buyer.
        once you call this tool, payment process is automatic, once tool called just say the user to continue with payment, that's all.
        once called, you do not control the cart checkout.
        """
        response = requests.post(
            "http://localhost:8009/carts/checkout",
            json={"buyer_id": user_id},
            headers=headers,
        )
        data = response.json()
        print("CART CHECKOUT TOOL RESPONSE:", data)
        return {"status_code": response.status_code, "data": data}

    return [
        search_products,
        buy_product,
        previous_orders,
        get_product_details,
        add_to_cart,
        get_cart,
        update_cart,
        remove_from_cart,
        clear_cart,
        cart_checkout,
    ]
