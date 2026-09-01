<h1 align="center">🤖 AI-Powered Agentic Commerce Platform</h1>

<p align="center">
  <b>AI-driven commerce platform enabling autonomous product discovery, recommendations, cart management, checkout, and payments.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-Agentic%20Commerce-blue" alt="AI Agentic Commerce">
  <img src="https://img.shields.io/badge/Node.js-Backend-green" alt="Node.js">
  <img src="https://img.shields.io/badge/Streamlit-Frontend-red" alt="Streamlit">
  <img src="https://img.shields.io/badge/MongoDB-Database-darkgreen" alt="MongoDB">
  <img src="https://img.shields.io/badge/Razorpay-Payments-528FF0" alt="Razorpay">
  <img src="https://img.shields.io/badge/LangChain-Agent%20Framework-orange" alt="LangChain">
</p>

<hr>

<h2>📌 Overview</h2>

<p>
This project is an <b>AI-powered agentic commerce platform</b> designed to automate and enhance the online shopping experience using intelligent AI agents.
</p>

<p>
Instead of relying entirely on traditional search, product pages, and manually driven purchasing flows, the platform allows an AI agent to understand a buyer's intent, discover relevant products, recommend complementary products, manage the shopping cart, and initiate a complete payment workflow.
</p>

<p>
The platform also provides merchants with AI-assisted product management and revenue insights, creating a two-sided ecosystem connecting <b>AI buyers, merchants, products, recommendations, and payments</b>.
</p>

<h3>🎯 Core Objective</h3>

<p>
The primary objective is to demonstrate how <b>agentic AI can participate in commerce end-to-end</b> — from understanding what a customer wants to actually completing a transaction.
</p>

<hr>

<h2>✨ Key Features</h2>

<table>
  <tr>
    <th>Feature</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>🤖 AI Shopping Agent</td>
    <td>Conversational AI agent that understands buyer requirements and searches the product catalog.</td>
  </tr>
  <tr>
    <td>🏪 Merchant Agent</td>
    <td>AI-assisted merchant operations including product discovery, product creation and sales analysis.</td>
  </tr>
  <tr>
    <td>🔍 Semantic Product Search</td>
    <td>Vector-based product discovery using product embeddings rather than relying only on keyword matching.</td>
  </tr>
  <tr>
    <td>🛒 Shopping Cart</td>
    <td>Buyers can add products, modify quantities, remove items and clear their cart.</td>
  </tr>
  <tr>
    <td>💡 AI Cross-Selling</td>
    <td>AI identifies complementary products and recommends additional purchases based on the current shopping context.</td>
  </tr>
  <tr>
    <td>💳 Razorpay Checkout</td>
    <td>Integrated payment flow using Razorpay Orders and Checkout APIs.</td>
  </tr>
  <tr>
    <td>🔐 Payment Verification</td>
    <td>Server-side Razorpay payment signature verification protects the transaction flow.</td>
  </tr>
  <tr>
    <td>📦 Order Management</td>
    <td>Orders and payment status are stored and tracked through the backend.</td>
  </tr>
  <tr>
    <td>📊 AI Revenue Analytics</td>
    <td>Tracks purchases and revenue generated through AI recommendations.</td>
  </tr>
  <tr>
    <td>📝 Activity Tracking</td>
    <td>Records important buyer, merchant and AI-agent actions for observability.</td>
  </tr>
</table>

<hr>

<h2>🏗️ System Architecture</h2>

<p>The platform consists of three major layers:</p>

<ul>
  <li><b>Streamlit Client:</b> Provides the buyer and merchant interfaces.</li>
  <li><b>Node.js / Express Backend:</b> Handles authentication, products, carts, orders, recommendations and payment operations.</li>
  <li><b>AI Layer:</b> Provides conversational agents, structured product metadata generation, semantic search and recommendation intelligence.</li>
</ul>

<pre>
                    ┌──────────────────────────┐
                    │       Streamlit UI       │
                    │                          │
                    │  Buyer     │   Merchant  │
                    └────────────┬─────────────┘
                                 │
                                 │ REST APIs
                                 ▼
                    ┌──────────────────────────┐
                    │    Node.js / Express     │
                    │                          │
                    │ Auth                     │
                    │ Products                 │
                    │ Cart                     │
                    │ Checkout                 │
                    │ Orders                   │
                    │ Recommendations         │
                    │ Activity Logging         │
                    └───────┬─────────┬────────┘
                            │         │
                  ┌─────────┘         └──────────┐
                  ▼                              ▼
        ┌───────────────────┐          ┌──────────────────┐
        │     MongoDB       │          │   Razorpay APIs  │
        │                   │          │                  │
        │ Users             │          │ Orders           │
        │ Products          │          │ Checkout         │
        │ Cart              │          │ Payments         │
        │ Orders            │          │ Verification     │
        │ Activities        │          └──────────────────┘
        └───────────────────┘

                            │
                            ▼
                    ┌──────────────────┐
                    │    AI Layer      │
                    │                  │
                    │ LangChain        │
                    │ LangGraph        │
                    │ Gemini           │
                    │ Vector Search    │
                    └────────┬─────────┘
                             │
                             ▼
                       ┌────────────┐
                       │  LanceDB   │
                       │  Vectors   │
                       └────────────┘
</pre>

<hr>

<h2>🧠 AI Architecture</h2>

<h3>1. Buyer Agent</h3>

<p>
The buyer-facing agent acts as an intelligent shopping assistant. It can understand natural-language requirements and use backend tools to perform commerce-related operations.
</p>

<p>Typical capabilities include:</p>

<ul>
  <li>Searching for products</li>
  <li>Understanding product requirements</li>
  <li>Finding relevant products through semantic search</li>
  <li>Checking previous orders</li>
  <li>Adding products to the shopping workflow</li>
  <li>Providing product recommendations</li>
  <li>Initiating purchase workflows</li>
</ul>

<h3>2. Merchant Agent</h3>

<p>
The merchant agent provides AI-assisted functionality for sellers operating on the platform.
</p>

<p>Merchant-side capabilities include:</p>

<ul>
  <li>Viewing merchant products</li>
  <li>Adding products</li>
  <li>Managing product information</li>
  <li>Analyzing sales</li>
  <li>Accessing AI-generated insights</li>
</ul>

<h3>3. Agent Tools</h3>

<p>The agents interact with the backend through specialized tools.</p>

<table>
  <tr>
    <th>Agent</th>
    <th>Tool</th>
    <th>Purpose</th>
  </tr>
  <tr>
    <td>Buyer</td>
    <td><code>search_products</code></td>
    <td>Find products matching buyer requirements.</td>
  </tr>
  <tr>
    <td>Buyer</td>
    <td><code>buy_product</code></td>
    <td>Initiate product purchase workflow.</td>
  </tr>
  <tr>
    <td>Buyer</td>
    <td><code>previous_orders</code></td>
    <td>Retrieve the buyer's previous orders.</td>
  </tr>
  <tr>
    <td>Merchant</td>
    <td><code>get_products</code></td>
    <td>Retrieve merchant products.</td>
  </tr>
  <tr>
    <td>Merchant</td>
    <td><code>add_product</code></td>
    <td>Add a new product.</td>
  </tr>
  <tr>
    <td>Merchant</td>
    <td><code>sales_by_merchant</code></td>
    <td>Retrieve merchant sales information.</td>
  </tr>
</table>

<hr>

<h2>🔎 Semantic Product Search</h2>

<p>
Traditional keyword search can fail when a buyer describes what they need using different terminology from the product listing.
</p>

<p>
To solve this, product information is converted into vector embeddings and stored in a vector database. Buyer queries are also embedded and compared against product vectors.
</p>

<p>
The system therefore searches based on <b>semantic similarity</b> rather than exact keyword matching.
</p>

<h3>Product Vector Data</h3>

<pre>
Product
   │
   ├── Name
   ├── Description
   ├── Category
   └── Product Metadata
            │
            ▼
      Embedding Model
            │
            ▼
         Vector
            │
            ▼
         LanceDB
</pre>

<p>
Product embeddings and metadata are regenerated when important product information such as the product name, description, or category changes.
</p>

<hr>

<h2>💡 AI-Powered Cross-Selling</h2>

<p>
The platform includes an AI-driven recommendation system designed to increase the value of a customer's purchase.
</p>

<p>
Instead of recommending random popular products, the system attempts to identify products that are <b>contextually complementary</b> to the product already being considered.
</p>

<h3>Recommendation Pipeline</h3>

<pre>
              Anchor Product
                    │
                    ▼
             Vector Search
                    │
                    ▼
          Top Candidate Products
                    │
                    ▼
        Remove Invalid Candidates
                    │
        ┌───────────┼────────────┐
        │           │            │
     Out of       Already       Same
      Stock       in Cart      Product
        │           │            │
        └───────────┴────────────┘
                    │
                    ▼
          AI Complementarity Check
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
    COMPLEMENTARY ALTERNATIVE UNRELATED
          │
          ▼
     Final Recommendations
</pre>

<p>
The recommendation layer considers product metadata, semantic similarity and product relationships to determine whether a candidate is genuinely useful as an additional purchase.
</p>

<h3>Product Metadata</h3>

<p>
The AI also generates structured product metadata such as:
</p>

<ul>
  <li><code>product_type</code></li>
  <li><code>product_role</code></li>
  <li><code>attributes</code></li>
</ul>

<p>
Supported product roles include primary products, accessories, replacements, consumables, components, services and bundles.
</p>

<hr>

<h2>🛒 Cart & Checkout</h2>

<p>
The platform supports a complete shopping-cart workflow.
</p>

<table>
  <tr>
    <th>Operation</th>
    <th>Purpose</th>
  </tr>
  <tr>
    <td>Add</td>
    <td>Add a product to the buyer's cart.</td>
  </tr>
  <tr>
    <td>Get Cart</td>
    <td>Retrieve the current cart.</td>
  </tr>
  <tr>
    <td>Update</td>
    <td>Change product quantity.</td>
  </tr>
  <tr>
    <td>Remove</td>
    <td>Remove a specific product.</td>
  </tr>
  <tr>
    <td>Clear</td>
    <td>Remove all products from the cart.</td>
  </tr>
</table>

<p>
Before adding or updating products, the backend performs stock validation to prevent purchasing quantities that are not available.
</p>

<h3>Cart Checkout Flow</h3>

<pre>
Buyer
 │
 ▼
Add Products
 │
 ▼
Shopping Cart
 │
 ▼
Create Checkout
 │
 ▼
Create Razorpay Order
 │
 ▼
Razorpay Checkout
 │
 ▼
Payment
 │
 ▼
Payment Verification
 │
 ▼
Order Confirmation
</pre>

<hr>

<h2>💳 Razorpay Payment Integration</h2>

<p>
Razorpay is integrated to make the AI-driven shopping experience transactable from end to end.
</p>

<h3>Payment Flow</h3>

<ol>
  <li>The backend creates a Razorpay order.</li>
  <li>The generated <code>razorpay_order_id</code> is returned to the frontend.</li>
  <li>The frontend opens Razorpay Checkout.</li>
  <li>The customer completes the payment.</li>
  <li>Razorpay returns payment information.</li>
  <li>The backend verifies the payment signature.</li>
  <li>The order status is updated.</li>
</ol>

<h3>Important Razorpay Data</h3>

<ul>
  <li><code>razorpay_order_id</code></li>
  <li><code>razorpay_payment_id</code></li>
  <li><code>razorpay_signature</code></li>
</ul>

<p>
Payment verification is performed server-side using an HMAC SHA-256 signature check before treating the transaction as successfully verified.
</p>

<hr>

<h2>📊 AI Revenue Analytics</h2>

<p>
The platform tracks the commercial impact of AI recommendations.
</p>

<p>
Important metrics include:
</p>

<ul>
  <li><b>Revenue generated through AI recommendations</b></li>
  <li><b>Additional purchases</b></li>
  <li>Recommendation-driven conversions</li>
</ul>

<p>
This allows merchants to evaluate whether AI recommendations are actually producing additional revenue instead of merely generating suggestions.
</p>

<hr>

<h2>📝 Activity Tracking</h2>

<p>
Important actions performed by users and AI agents are recorded in an activity collection.
</p>

<h3>Tracked Information</h3>

<ul>
  <li>User ID</li>
  <li>User role</li>
  <li>Actor type</li>
  <li>Action</li>
  <li>Entity type</li>
  <li>Entity ID</li>
  <li>Metadata</li>
  <li>IP address</li>
</ul>

<p>
The system distinguishes between actions performed by a normal <code>USER</code> and actions performed through an <code>AGENT</code>.
</p>

<p>
This provides a foundation for understanding agent behavior and creating an auditable agentic-commerce workflow.
</p>

<hr>

<h2>🧰 Technology Stack</h2>

<table>
  <tr>
    <th>Layer</th>
    <th>Technology</th>
  </tr>
  <tr>
    <td>Frontend</td>
    <td>Python, Streamlit</td>
  </tr>
  <tr>
    <td>Backend</td>
    <td>Node.js, Express.js</td>
  </tr>
  <tr>
    <td>Database</td>
    <td>MongoDB, Mongoose</td>
  </tr>
  <tr>
    <td>AI Framework</td>
    <td>LangChain, LangGraph</td>
  </tr>
  <tr>
    <td>LLM</td>
    <td>Google Gemini / Groq</td>
  </tr>
  <tr>
    <td>Embeddings</td>
    <td>Google Generative AI Embeddings</td>
  </tr>
  <tr>
    <td>Vector Database</td>
    <td>LanceDB</td>
  </tr>
  <tr>
    <td>Payments</td>
    <td>Razorpay</td>
  </tr>
  <tr>
    <td>Product IDs</td>
    <td>Nanoid</td>
  </tr>
</table>

<hr>

<h2>📁 Project Structure</h2>

<pre>
razor/
│
├── agent/
│   ├── ai/
│   │   ├── agent.py
│   │   └── product_metadata.js
│   │
│   ├── ui/
│   │   ├── B_cart.py
│   │   ├── buyer.py
│   │   ├── merchant.py
│   │   └── payments/
│   │       ├── payment.py
│   │       └── cart_checkout_payment.py
│   │
│   └── api.py
│
├── server/
│   ├── models/
│   │   ├── users.js
│   │   ├── products.js
│   │   ├── carts.js
│   │   ├── checkouts.js
│   │   ├── orders.js
│   │   └── activities.js
│   │
│   ├── routes/
│   │   ├── merchants.js
│   │   ├── carts.js
│   │   ├── orders.js
│   │   └── recommendations.js
│   │
│   ├── middleware/
│   │   ├── activity.js
│   │   ├── activityLogger.js
│   │   └── requestContext.js
│   │
│   └── server.js
│
├── app.py
├── auth.py
├── requirements.txt
├── package.json
└── README.md
</pre>

<p>
The exact structure may evolve as additional modules and features are added.
</p>

<hr>

<h2>🔌 Backend API Modules</h2>

<h3>Merchant APIs</h3>

<ul>
  <li><code>POST /merchants/add_product</code></li>
  <li><code>GET /merchants/get_products</code></li>
  <li><code>DELETE /merchants/delete_product</code></li>
  <li><code>PUT /merchants/edit_product</code></li>
</ul>

<h3>Cart APIs</h3>

<ul>
  <li><code>POST /add</code></li>
  <li><code>GET /cart</code></li>
  <li><code>PATCH /update</code></li>
  <li><code>DELETE /remove</code></li>
  <li><code>DELETE /clear</code></li>
</ul>

<h3>Order & Payment APIs</h3>

<ul>
  <li>Create checkout</li>
  <li>Create Razorpay order</li>
  <li>Verify payment</li>
  <li>Check order status</li>
  <li>Cancel order</li>
</ul>

<h3>Activity APIs</h3>

<ul>
  <li>Retrieve user activity history</li>
  <li>Track buyer actions</li>
  <li>Track merchant actions</li>
  <li>Track agent-generated actions</li>
</ul>

<hr>

<h2>⚙️ Installation & Setup</h2>

<h3>1. Clone the Repository</h3>

<pre>
git clone &lt;repository-url&gt;
cd razor
</pre>

<h3>2. Backend Setup</h3>

<pre>
cd server
npm install
</pre>

<h3>3. Python Environment</h3>

<pre>
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
</pre>

<h3>4. Environment Variables</h3>

<p>
Create a <code>.env</code> file for the backend and configure the required credentials.
</p>

<pre>
MONGO_URI=your_mongodb_connection_string

RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
</pre>

<p>
Do not commit API keys, secrets, database credentials, or other sensitive configuration values to GitHub.
</p>

<h3>5. Start the Backend</h3>

<pre>
npm run dev
</pre>

<p>
The Express server runs on the configured backend port.
</p>

<h3>6. Start Streamlit</h3>

<pre>
streamlit run app.py
</pre>

<hr>

<h2>🔐 Security Considerations</h2>

<ul>
  <li>Secrets are stored using environment variables.</li>
  <li>Razorpay payments are verified on the backend.</li>
  <li>Stock availability is checked server-side.</li>
  <li>Payment status is not trusted solely from the frontend.</li>
  <li>Agent actions can be distinguished from direct user actions through activity logging.</li>
</ul>

<hr>

<h2>🚀 End-to-End Example</h2>

<p>
A typical AI-assisted purchase can work as follows:
</p>

<pre>
Buyer:
"I need a laptop for programming under ₹60,000."

        │
        ▼

AI Buyer Agent

        │
        ▼

Semantic Product Search

        │
        ▼

Relevant Products

        │
        ▼

Buyer selects a product

        │
        ▼

AI identifies complementary products

        │
        ▼

Cross-Sell Recommendations

        │
        ▼

Buyer adds products to Cart

        │
        ▼

Cart Checkout

        │
        ▼

Razorpay Order Creation

        │
        ▼

Razorpay Checkout

        │
        ▼

Payment Verification

        │
        ▼

Order Confirmed

        │
        ▼

Revenue + Activity Analytics
</pre>

<hr>

<h2>🎯 Why Agentic Commerce?</h2>

<p>
Traditional e-commerce generally requires the customer to manually navigate search, filtering, product pages, cart operations and checkout.
</p>

<p>
An agentic commerce system changes this interaction model by allowing an AI agent to reason about the customer's goal and interact with commerce infrastructure through tools.
</p>

<p>
The goal of this project is not simply to add a chatbot to an e-commerce website. The goal is to demonstrate a system where an AI agent can participate in the <b>actual commerce workflow</b>.
</p>

<hr>

<h2>🔮 Future Improvements</h2>

<ul>
  <li>Persistent conversational memory for buyers.</li>
  <li>More advanced recommendation ranking.</li>
  <li>Learning recommendation quality from conversion data.</li>
  <li>Agent-driven negotiation and personalized offers.</li>
  <li>Improved fraud and payment monitoring.</li>
  <li>Real-time Razorpay webhook processing.</li>
  <li>Merchant-level AI revenue optimization.</li>
  <li>More detailed agent observability and analytics.</li>
  <li>Production-grade authentication and authorization.</li>
  <li>Deployment using separate production services for frontend, backend and AI infrastructure.</li>
</ul>

<hr>

<h2>🏆 Project Focus</h2>

<p align="center">
  <b>AI + Commerce + Payments + Recommendations + Agentic Workflows</b>
</p>

<p align="center">
  The project demonstrates how AI agents can move beyond conversation and interact with real commerce infrastructure to discover products, influence purchases, and complete transactions.
</p>

<hr>

<h2>👨‍💻 Development</h2>

<p>
This project is being developed as an experimental <b>agentic commerce platform</b> combining AI agents with a real transaction pipeline.
</p>

<p>
The architecture is intentionally modular so that the AI layer, commerce backend, recommendation system and payment infrastructure can evolve independently.
</p>

<hr>

<h2>📄 License</h2>

<p>
This project is currently intended for educational, experimental and hackathon purposes.
</p>
