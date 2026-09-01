import requests
import streamlit as st


def get_headers():
    user = st.session_state.user
    return {
        "X-User-ID": user["user_id"],
        "X-Actor-Type": "USER",
    }


def get_products(merchant_id):
    response = requests.get(
        "http://localhost:8009/merchants/get_products",
        params={"merchant_id": merchant_id},
        headers=get_headers(),
    )
    if response.status_code == 200:
        return response.json()["products"]
    else:
        return []


def delete_product(product_id):
    response = requests.delete(
        "http://localhost:8009/merchants/delete_product",
        params={"product_id": product_id},
        headers=get_headers(),
    )
    if response.status_code == 200:
        return response.json()["msg"]
    elif response.status_code == 204:
        return "Product not found"


def edit_product(product_id, updates):
    response = requests.patch(
        "http://localhost:8009/merchants/edit_product",
        params={"product_id": product_id},
        json=updates,
        headers=get_headers(),
    )
    if response.status_code == 200:
        return response.json()["msg"]
    elif response.status_code == 204:
        return "Product not found"


def sales_by_merchant(merchant_id):
    headers = {
        "X-User-ID": merchant_id,
        "X-Actor-Type": "USER",
    }
    try:
        response = requests.get(
            "http://localhost:8009/merchants/sales_by_merchant",
            params={"merchant_id": merchant_id},
            timeout=10,
            headers=get_headers(),
        )
        response.raise_for_status()
        data = response.json()
        return data.get("orders", [])

    except requests.exceptions.RequestException as e:
        print(f"Sales API error: {e}")
        return []
    except ValueError:
        print("Sales API returned invalid JSON.")
        return []
    
    
def get_recommendation_stats(merchant_id):
    try:
        response = requests.get(
            "http://localhost:8009/merchants/stats",
            params = {'merchant_id' : merchant_id}
        )
        if response.status_code == 200:
            return response.json()
        print(
            "GET RECOMMENDATION STATS ERROR:",
            response.status_code,
            response.text,
        )
        return None

    except Exception as e:
        print("GET RECOMMENDATION STATS EXCEPTION:", e)
        return None




def get_merchant_activities(user_id):
    response = requests.get(
        "http://localhost:8009/merchants/activities",
        params={"user_id": user_id},
        headers=get_headers(),
    )

    if response.status_code != 200:
        return []

    return response.json().get("activities", [])


# //###################################### BUYERS


def get_orders_by_buyer(user_id):
    try:
        response = requests.get(
            "http://localhost:8009/buyers/get_previous_orders",
            params={"user_id": user_id},
            timeout=10,
            headers=get_headers(),
        )

        response.raise_for_status()

        data = response.json()

        return data.get("previous_orders", [])

    except requests.exceptions.RequestException as e:
        print(f"Orders API error: {e}")
        return []

    except ValueError:
        print("Orders API returned invalid JSON.")
        return []


def get_product_details(product_ids):
    try:
        response = requests.get(
            "http://localhost:8009/buyers/product_details",
            params={"product_ids": product_ids},
            timeout=10,
            headers=get_headers(),
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


def get_activities(user_id):
    response = requests.get(
        "http://localhost:8009/buyers/activities",
        params={"user_id": user_id},
        headers=get_headers(),
    )

    if response.status_code != 200:
        return []

    return response.json().get("activities", [])


def get_recommendations(cart_id):
    response = requests.get(
        "http://localhost:8009/buyers/recommendation", params={"cart_id": cart_id}
    )
    if response.status_code == 200:
        return response.json()
    return None


def send_recommendation_stats(stats):
    try:
        response = requests.post(
            "http://localhost:8009/stats/recommendation_stats",
            json=stats,
            timeout=10,
        )

        print("SEND RECOMMENDATION STATS:", response.status_code,response.text)
        if response.status_code == 200:
            return response.json()
        return None

    except requests.RequestException as e:
        print(
            "RECOMMENDATION STATS API ERROR:",e)
        return None





############ ORDERS ###########


def check_order_status(razorpay_order_id):
    try:
        response = requests.get(
            "http://localhost:8009/orders/check_order_status",
            params={
                "razorpay_order_id": razorpay_order_id,
            },
            headers=get_headers(),
            timeout=10,
        )
        print(
            "CHECK ORDER STATUS RESPONSE:",
            response.status_code,
            response.text,
        )
        if response.status_code == 200:
            return response.json()
        return None

    except requests.RequestException as e:
        print("CHECK ORDER STATUS ERROR:", e)
        return None


def cancel_order(razorpay_order_id):
    try:
        response = requests.post(
            "http://localhost:8009/orders/cancel_order",
            json={
                "razorpay_order_id": razorpay_order_id,
            },
            headers=get_headers(),
            timeout=10,
        )
        print(
            "CANCEL ORDER STATUS RESPONSE:",
            response.status_code,
            response.text,
        )
        if response.status_code == 200:
            return response.json()
        return None

    except requests.RequestException as e:
        print("CHECK ORDER STATUS ERROR:", e)
        return None


################### CARTS ##################


def check_checkout_status(razorpay_order_id):

    response = requests.get(
        "http://localhost:8009/carts/check_checkout_status",
        params={
            "razorpay_order_id": razorpay_order_id,
        },
        headers=get_headers(),
    )
    if response.status_code == 200:
        return response.json().get("status")

    return None


BASE_URL = "http://localhost:8009"


def cancel_checkout(razorpay_order_id):
    try:
        response = requests.post(
            f"{BASE_URL}/carts/cancel_checkout",
            headers=get_headers(),
            json={"razorpay_order_id": razorpay_order_id},
        )
        if response.status_code == 200:
            return response.json()
        print("CANCEL CHECKOUT ERROR:", response.text)
        return None

    except requests.RequestException as e:
        print("CANCEL CHECKOUT REQUEST ERROR:", e)
        return None


def get_cart(buyer_id):

    response = requests.get(
        f"{BASE_URL}/carts/cart", params={"buyer_id": buyer_id}, headers=get_headers()
    )
    if response.status_code == 200:
        return response.json().get("cart")
    return None


def add_to_cart(buyer_id, product_id, quantity=1):
    response = requests.post(
        f"{BASE_URL}/carts/add",
        json={"buyer_id": buyer_id, "product_id": product_id, "quantity": quantity},
        headers=get_headers(),
    )
    if response.status_code in [200, 201]:
        return response.json()
    print("Add to cart failed:", response.text)
    return None


def update_cart_item(buyer_id, product_id, quantity):

    response = requests.patch(
        f"{BASE_URL}/carts/update",
        json={"buyer_id": buyer_id, "product_id": product_id, "quantity": quantity},
        headers=get_headers(),
    )
    return response.status_code == 200


def remove_cart_item(buyer_id, product_id):

    response = requests.delete(
        f"{BASE_URL}/carts/remove",
        json={"buyer_id": buyer_id, "product_id": product_id},
        headers=get_headers(),
    )
    return response.status_code == 200


def clear_cart(buyer_id):
    response = requests.delete(
        f"{BASE_URL}/carts/clear", json={"buyer_id": buyer_id}, headers=get_headers()
    )
    return response.status_code == 200


def create_cart_checkout(buyer_id):
    response = requests.post(
        f"{BASE_URL}/carts/checkout", json={"buyer_id": buyer_id}, headers=get_headers()
    )
    if response.status_code == 201:
        return response.json()

    print("Cart checkout failed:", response.text)
    return None
