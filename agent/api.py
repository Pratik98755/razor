import requests
import streamlit as st

def get_products(merchant_id):
    response = requests.get(
        "http://localhost:8009/merchants/get_products",
        params={"merchant_id": merchant_id},
    )
    if response.status_code == 200:
        return response.json()["products"]
    else:
        return []


def delete_product(product_id):
    response = requests.delete(
        "http://localhost:8009/merchants/delete_product",
        params={"product_id": product_id},
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
    )
    if response.status_code == 200:
        return response.json()["msg"]
    elif response.status_code == 204:
        return "Product not found"


def sales_by_merchant(merchant_id):
    try:
        response = requests.get(
            "http://localhost:8009/merchants/sales_by_merchant",
            params={"merchant_id": merchant_id},
            timeout=10,
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


# // BUYERS


def get_orders_by_buyer(user_id):
    try:
        response = requests.get(
            "http://localhost:8009/buyers/get_previous_orders",
            params={"user_id": user_id},
            timeout=10,
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
