import streamlit as st

from ai.agent import ask_agent

def ai_assisstant_page(user):
    st.title("AI Assisstant")
    st.subheader("One AI assistant for all your needs!")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ---------------- Example prompts ----------------
    if not st.session_state.chat_history:
        
        st.markdown("""
            <style>
            div.stButton > button {
                color: #888888;
                background-color: transparent;
                border: 1px solid #444444;
            }

            div.stButton > button:hover {
                color: #aaaaaa;
                border-color: #666666;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown(
            "<h3 style='text-align: center;'>Try asking...</h3>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            example_1 = st.button(
                "➕ Add a product named Nike Blue Running Shoe",
                width="stretch"
            )
            example_2 = st.button(
                "📊 What's my sales in the last month?",
                width="stretch"
            )

        with col2:
            example_3 = st.button(
                "💰 What's my total sales?",
                width="stretch"
            )
            example_4 = st.button(
                "📦 Which products are running low on stock?",
                width="stretch"
            )

        if example_1:
            question = "Add a product named Nike Blue Running Shoe, desc ..."
        elif example_2:
            question = "What's my sales in the previous 30 days?"
        elif example_3:
            question = "What's my total sales?"
        elif example_4:
            question = "Which products are running low on stock?"
        else:
            question = None

    else:
        question = None

    # ---------------- Display previous messages ----------------
    for chat_msg in st.session_state.chat_history:
        st.chat_message(chat_msg["role"]).markdown(chat_msg["content"])

    # ---------------- Chat input ----------------
    chat_question = st.chat_input("Ask anything about your business")

    if chat_question:
        question = chat_question

    # ---------------- Ask Agent ----------------
    if question:
        with st.chat_message("user"):
            st.write(question)

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("assistant"):
            answer, products = ask_agent(
                question,
                user["user_id"]
            )

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer
            })

            st.write(answer)

        st.rerun()