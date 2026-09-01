<h1 align="center">🤖 AI-Powered Agentic Commerce</h1>

<p align="center">
  <b>An AI-native commerce platform where intelligent agents can discover products, manage carts, drive cross-sell recommendations, and complete real payments through Razorpay.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-Agentic%20Commerce-blue" alt="AI Agentic Commerce">
  <img src="https://img.shields.io/badge/Backend-Node.js%20%7C%20Express-green" alt="Backend">
  <img src="https://img.shields.io/badge/Frontend-Streamlit-red" alt="Streamlit">
  <img src="https://img.shields.io/badge/Database-MongoDB-darkgreen" alt="MongoDB">
  <img src="https://img.shields.io/badge/Vector%20DB-LanceDB-purple" alt="LanceDB">
  <img src="https://img.shields.io/badge/Payments-Razorpay-528FF0" alt="Razorpay">
</p>

<hr>

<h2>📌 Overview</h2>

<p>
This project explores <b>agentic commerce</b>: instead of limiting AI to a conversational interface, the AI agent is connected to real commerce operations through backend tools.
</p>

<p>
A buyer can describe what they need in natural language, receive semantically relevant products, add products to a cart, receive AI-driven complementary-product recommendations, and proceed through a Razorpay payment flow.
</p>

<p>
The platform also provides merchant-side product and sales functionality, while backend activity logging makes it possible to distinguish actions performed directly by users from actions performed by an AI agent.
</p>

<h2>✨ What the platform does</h2>

<table>
<tr><th>Capability</th><th>What it provides</th></tr>
<tr><td>🤖 AI Buyer</td><td>Conversational product discovery and purchase assistance.</td></tr>
<tr><td>🏪 Merchant Tools</td><td>Product management and sales/inventory views.</td></tr>
<tr><td>🔎 Semantic Search</td><td>Vector-based product retrieval instead of keyword-only matching.</td></tr>
<tr><td>🛒 Cart</td><td>Add, fetch, update, remove and clear cart items with stock validation.</td></tr>
<tr><td>💡 AI Cross-Sell</td><td>Finds complementary products using product intelligence, vector retrieval and classification.</td></tr>
<tr><td>💳 Payments</td><td>Razorpay order creation, Checkout integration and server-side signature verification.</td></tr>
<tr><td>📦 Orders</td><td>Confirmed purchases are persisted as order records.</td></tr>
<tr><td>📊 Merchant Analytics</td><td>Sales and inventory views, including best-selling products.</td></tr>
<tr><td>📝 Activity Tracking</td><td>Records important USER and AGENT actions.</td></tr>
</table>

<h2>🧠 Core Idea</h2>

<p>
The important design choice is that the conversational agent is <b>not the commerce system itself</b>. The agent calls application tools and backend services that perform the actual operations.
</p>

<pre>
Buyer
  │
  ▼
AI Buyer Agent
  │
  ├── Search Products
  ├── Add / Buy Product
  ├── Read Previous Orders
  └── Interact with Cart / Checkout
          │
          ▼
Node.js / Express API
          │
     ┌────┼───────────────┐
     ▼    ▼               ▼
 MongoDB LanceDB       Razorpay
     │    │               │
     └────┴───────┬───────┘
                  ▼
             Commerce Flow
</pre>

<h2>🔎 Product Discovery</h2>

<p>
Product search uses embeddings and LanceDB to retrieve products by semantic similarity. This allows a buyer to describe an intent rather than having to know the exact product name or wording used by a merchant.
</p>

<p>
Products can also be enriched with structured AI-generated metadata. That metadata is useful for recommendation filtering and for distinguishing products that complement one another from products that are merely alternatives.
</p>

<h2>💡 AI Cross-Sell Engine</h2>

<p>
The recommendation architecture separates <b>recommendation logic</b> from the conversational agent.
</p>

<pre>
Product Added to Cart
        │
        ▼
Generate Candidate Products
        │
        ├── Vector similarity
        ├── Compatibility metadata
        └── Usage/context signals
        │
        ▼
Apply hard filters
        │
        ├── In stock
        ├── Not already in cart
        ├── Different product type
        └── Valid complementary role
        │
        ▼
LLM relationship classification
        │
        ├── complementary
        ├── alternative
        ├── upsell
        └── unrelated
        │
        ▼
Rank complementary candidates
        │
        ▼
Return best recommendation(s)
        │
        ▼
AI Agent presents recommendation
</pre>

<p>
This prevents the conversational model from freely inventing recommendations. The recommendation layer determines what should be recommended; the agent is responsible for communicating it to the buyer and handling the interaction.
</p>

<h2>🛒 Cart → Checkout → Payment</h2>

<p>
The cart checkout flow creates a server-side checkout snapshot containing the products, quantities, merchant IDs and prices used for the checkout.
</p>

<pre>
Cart
 │
 ▼
Validate products + stock
 │
 ▼
Build checkout snapshot
 │
 ▼
Create Razorpay Order
 │
 ▼
Persist CHECKOUT
 │
 ▼
Razorpay Checkout
 │
 ▼
Payment
 │
 ▼
Verify Razorpay Signature
 │
 ▼
Validate stock again
 │
 ▼
Create confirmed ORDER records
 │
 ▼
Update checkout
 │
 ▼
Clear cart
</pre>

<p>
For cart payments, the backend verifies the signature using the Razorpay order ID and payment ID before confirming the checkout. The implementation also protects against duplicate checkout verification and restores stock if order creation fails after stock has been decremented.
</p>

<h2>📊 Merchant Side</h2>

<p>
The merchant interface provides product management and business visibility. The dashboard includes sales information and inventory views, including a best-seller chart and stock-level visualization.
</p>

<h2>📝 Activity & Agent Observability</h2>

<p>
Commerce actions are logged with an actor type so the application can distinguish between actions performed by a normal user and actions performed through an AI agent.
</p>

<pre>
USER
  └── PRODUCT_SEARCHED
  └── ADDED_ITEMS_IN_CART
  └── ORDER_HISTORY_FETCHED
  └── ORDER_PAYMENT_VERIFIED

AGENT
  └── PRODUCT_SEARCHED
  └── ADDED_ITEMS_IN_CART
  └── ORDER_HISTORY_FETCHED
  └── ...
</pre>

<p>
This provides an audit trail for agentic actions and creates a foundation for measuring the commercial effect of AI-driven interactions.
</p>

<h2>🧰 Technology Stack</h2>

<table>
<tr><th>Layer</th><th>Technology</th></tr>
<tr><td>UI</td><td>Python + Streamlit</td></tr>
<tr><td>Backend</td><td>Node.js + Express</td></tr>
<tr><td>Database</td><td>MongoDB + Mongoose</td></tr>
<tr><td>Agent Framework</td><td>LangChain / LangGraph</td></tr>
<tr><td>LLMs</td><td>Google Gemini and Groq-based models</td></tr>
<tr><td>Embeddings</td><td>Google Generative AI Embeddings</td></tr>
<tr><td>Vector Database</td><td>LanceDB</td></tr>
<tr><td>Payments</td><td>Razorpay</td></tr>
</table>

<h2>📁 Documentation</h2>

<table>
<tr><th>Document</th><th>Purpose</th></tr>
<tr><td><a href="docs/SETUP.md">SETUP.md</a></td><td>Installation, environment configuration and running the application.</td></tr>
<tr><td><a href="docs/ARCHITECTURE.md">ARCHITECTURE.md</a></td><td>System architecture and end-to-end data flows.</td></tr>
<tr><td><a href="docs/API.md">API.md</a></td><td>Backend endpoint reference and request/response behavior.</td></tr>
<tr><td><a href="docs/AI.md">AI.md</a></td><td>AI agent, semantic search, product enrichment and cross-sell architecture.</td></tr>
</table>

<h2>⚡ Quick Start</h2>

<pre>
# Backend
npm install
npm run dev

# Python environment
pip install -r requirements.txt

# Streamlit
streamlit run app.py
</pre>

<p>
For the complete configuration and environment-variable setup, see <a href="docs/SETUP.md">docs/SETUP.md</a>.
</p>

<h2>🎯 Project Direction</h2>

<p>
The project is built around a simple idea: <b>AI should be able to participate in commerce, not merely talk about commerce.</b>
</p>

<p>
The current architecture combines agentic interaction, semantic product discovery, recommendation intelligence, cart operations and real payment infrastructure into one workflow.
</p>

<hr>

<p align="center"><b>AI + Commerce + Recommendations + Payments + Agentic Workflows</b></p>
