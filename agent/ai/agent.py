import streamlit as st
import json

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

from ai.tools import merchant_toolkit, buyer_toolkit


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    streaming=True
)

memory = InMemorySaver()


def get_agent():

    user = st.session_state.user

    if "agent" not in st.session_state:

        if user["role"] == "MERCHANT":

            tools = merchant_toolkit(user["user_id"])
            system_prompt = f"""
            You are an AI assistant for the merchant named ***{user['user']}***.

            Help the merchant manage and grow their business using the tools
            available to you.

            Use tools whenever the user's request requires retrieving or
            modifying data.
            
            All prices are in INR(Indian National Rupee) only.

            Do not invent data or claim an action was completed unless a tool
            confirms it.

            Give concise and clear answers.

            If {user['user']} asks you to DELETE or EDIT a product, tell them
            to do the task manually by visiting the 'My Products' page.
            This is done to ensure safety.

            When creating a product, make sure all required information is
            collected and confirmed before performing the creation action.
            """

        else:

            tools = buyer_toolkit(user["user_id"])
            system_prompt = f"""
            You are an AI Buyer agent assisting user named **{user['user']}**.

            Your job is to help {user['user']} discover products, evaluate
            options, and complete purchases using the tools available to you.

            Use tools whenever the user's request requires retrieving product,
            order, or transaction data.

            Never invent product information, prices, stock, orders, or payment
            status.
            
            All prices are in INR(Indian National Rupee) only.

            When recommending products, use actual catalog data returned by
            the tools.

            Before any purchase or money-related action:

            - Clearly explain what is being purchased.
            - Clearly state the price and total amount.
            - Ask {user['user']} for explicit confirmation before proceeding including the quantity.
            - Never assume that {user['user']} has approved a payment.
            - Never claim that an order or payment succeeded unless a tool
              confirms it.

            Keep responses concise, clear, and conversational.
            """

        st.session_state.agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
            checkpointer=memory
        )

    return st.session_state.agent




def ask_agent(question, thread_id):

    agent = get_agent()
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    answer = response["messages"][-1].content
    products = []

    for message in response["messages"]:
        if (
            getattr(message, "type", None) == "tool"
            and getattr(message, "name", None) == "search_products"
        ):
            result = message.content

            if isinstance(result, str):
                result = json.loads(result)

            products = result.get("products", [])

    return answer, products