<h1>🏗️ System Architecture</h1>

<h2>1. High-Level Architecture</h2>

<pre>
┌─────────────────────────────────────────────┐
│              Streamlit Application         │
│                                             │
│   Buyer UI                  Merchant UI    │
│   ├─ Scout AI               ├─ Products    │
│   ├─ Search results         ├─ Sales       │
│   ├─ Cart                   └─ Inventory   │
│   └─ Payments                              │
└───────────────────┬─────────────────────────┘
                    │
                    │ HTTP / REST
                    ▼
┌─────────────────────────────────────────────┐
│             Node.js + Express               │
│                                             │
│ Users / Products / Cart / Checkout / Orders│
│ Recommendations / Activity / Payments      │
└───────┬───────────────────┬─────────────────┘
        │                   │
        ▼                   ▼
┌───────────────┐     ┌──────────────────────┐
│   MongoDB     │     │     Razorpay         │
│               │     │                      │
│ Users         │     │ Orders               │
│ Products      │     │ Checkout             │
│ Carts         │     │ Payments             │
│ Checkouts     │     └──────────────────────┘
│ Orders        │
│ Activities    │
└───────────────┘
        ▲
        │
┌───────┴─────────────────────────────────────┐
│                AI Layer                    │
│                                             │
│ LangChain / LangGraph                       │
│ Gemini / Groq                               │
│ Product metadata generation                 │
│ Semantic search                             │
│ Recommendation classification              │
│ LanceDB                                     │
└─────────────────────────────────────────────┘
</pre>

<h2>2. Buyer Flow</h2>

<pre>
Buyer message
      ↓
Streamlit
      ↓
ask_agent(...)
      ↓
AI Buyer Agent
      ↓
Tool invocation
      ↓
Node backend
      ↓
MongoDB / LanceDB
      ↓
Result
      ↓
Agent response + UI state
</pre>

<h2>3. Product Search Flow</h2>

<pre>
Natural-language query
        ↓
Embedding / semantic representation
        ↓
LanceDB vector search
        ↓
Relevant product candidates
        ↓
Product metadata + availability
        ↓
Streamlit product results
</pre>

<h2>4. Cart Flow</h2>

<pre>
Add product
    ↓
Check product exists
    ↓
Check stock
    ↓
Find buyer cart
    ↓
Create cart OR update existing item
    ↓
Persist CART
</pre>

<p>
The backend checks stock when products are added and prevents a quantity from exceeding available inventory.
</p>

<h2>5. Cart Checkout Flow</h2>

<pre>
CART
 ↓
Validate every product
 ↓
Validate stock
 ↓
Use current server-side price
 ↓
Build checkout snapshot
 ↓
Create Razorpay order
 ↓
Create CHECKOUT document
 ↓
Return Razorpay order information
</pre>

<h2>6. Payment Verification Flow</h2>

<pre>
Razorpay Checkout
       ↓
payment_id
order_id
signature
       ↓
Backend
       ↓
HMAC SHA-256 verification
       ↓
Find CHECKOUT
       ↓
Prevent duplicate confirmation
       ↓
Re-check all products / stock
       ↓
Create ORDER records
       ↓
Mark CHECKOUT CONFIRMED
       ↓
Clear CART
</pre>

<h2>7. Failure Handling</h2>

<p>
The cart-payment implementation attempts to keep inventory consistent. If order creation fails after stock has been decremented, the updated quantities are restored before returning an error.
</p>

<h2>8. Activity Architecture</h2>

<p>
Activity middleware attaches the action and entity information to requests. A request context identifies the user and actor type, while the activity logger persists the resulting event.
</p>

<pre>
HTTP Request
     ↓
requestContext
     ↓
activity(...)
     ↓
Route handler
     ↓
Response finishes
     ↓
activityLogger
     ↓
ACTIVITY collection
</pre>

<h2>9. Design Principle</h2>

<p>
The platform keeps the AI reasoning layer separate from transaction-critical backend operations. The LLM can decide which tool should be used, but the backend remains responsible for validating products, stock, checkout state and payment signatures.
</p>
