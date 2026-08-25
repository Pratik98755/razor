import streamlit as st

from ai.agent import ask_agent
st.set_page_config(initial_sidebar_state=600)


def ai_scout_page(user):

    # Initialize session state
    if "buyer_chat_history" not in st.session_state:
        st.session_state.buyer_chat_history = []

    if "product_search_results" not in st.session_state:
        st.session_state.product_search_results = []

    has_results = bool(st.session_state.product_search_results)

    # ---------------- PRODUCTS SIDEBAR ----------------

    if has_results:

        st.sidebar.title("🔎 Products Found")

        for product in st.session_state.product_search_results:

            with st.sidebar.container(border=True):
                col1, col2 = st.columns([1, 1.5], vertical_alignment="top")

                # ---------------- IMAGE ----------------
                with col1:
                    images = product.get("images", [])
                    if images:
                        st.image(images[0], width="stretch")

                # ---------------- DETAILS ----------------
                with col2:
                    # Top section: text details
                    st.markdown(
                        f"**Product :**  " f"{product.get('name', 'Unnamed Product')}"
                    )
                    st.markdown(f"**Price :**  " f"💰 ₹{product.get('price', 'N/A')}")
                    st.markdown(f"**Desc :**  " f"{product.get('description', 'N/A')}")
                    if product.get("match_percentage"):
                        st.markdown(
                            f"**Match :**  " f"🎯 {product['match_percentage']}"
                        )

                    # Spacer that stretches to fill remaining space
                    st.space("stretch")

                    # Buy Now button pinned to bottom
                    if st.button(
                        "🛒 Buy Now",
                        key=f"buy_{product['product_id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        st.session_state.selected_product = product
                        st.rerun()

    # ---------------- SCOUT ----------------

    st.title(f"Welcome to the Market, {user['user']}")

    st.header("🛍️ SCOUT")
    st.subheader("The AI Buyer for you!")

    # ---------------- CHAT ----------------

    for chat_msg in st.session_state.buyer_chat_history:

        with st.chat_message(chat_msg["role"]):
            st.markdown(chat_msg["content"])

    question = st.chat_input("What are you looking for?")

    if question:

        # User message
        with st.chat_message("user"):
            st.write(question)

        st.session_state.buyer_chat_history.append(
            {"role": "user", "content": question}
        )

        # Agent
        answer, products = ask_agent(question, user["user_id"])

        # Save assistant response
        st.session_state.buyer_chat_history.append(
            {"role": "assistant", "content": answer}
        )

        # Save products
        if products:
            st.session_state.product_search_results = products

        # Display response
        with st.chat_message("assistant"):
            st.write(answer)

        # Rerun so sidebar updates
        if products:
            st.rerun()
