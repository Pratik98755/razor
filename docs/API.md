<h1>🔌 Backend API Reference</h1>

<p>
The backend is implemented using Node.js and Express. Endpoint prefixes depend on how the routers are mounted in the application.
</p>

<h2>🛍️ Product / Merchant APIs</h2>

<table>
<tr><th>Method</th><th>Endpoint</th><th>Purpose</th></tr>
<tr><td>POST</td><td><code>/merchants/add_product</code></td><td>Create a merchant product.</td></tr>
<tr><td>GET</td><td><code>/merchants/get_products</code></td><td>Retrieve merchant products.</td></tr>
<tr><td>DELETE</td><td><code>/merchants/delete_product</code></td><td>Delete a product.</td></tr>
<tr><td>PUT</td><td><code>/merchants/edit_product</code></td><td>Edit an existing product.</td></tr>
</table>

<h2>🛒 Cart APIs</h2>

<table>
<tr><th>Method</th><th>Endpoint</th><th>Purpose</th></tr>
<tr><td>POST</td><td><code>/add</code></td><td>Add a product or increase its cart quantity.</td></tr>
<tr><td>GET</td><td><code>/cart</code></td><td>Fetch a buyer's cart.</td></tr>
<tr><td>PATCH</td><td><code>/update</code></td><td>Update cart quantity.</td></tr>
<tr><td>DELETE</td><td><code>/remove</code></td><td>Remove an item.</td></tr>
<tr><td>DELETE</td><td><code>/clear</code></td><td>Clear cart items.</td></tr>
<tr><td>POST</td><td><code>/checkout</code></td><td>Create a checkout snapshot and Razorpay order.</td></tr>
<tr><td>POST</td><td><code>/verify_payment</code></td><td>Verify cart payment and create confirmed orders.</td></tr>
</table>

<h3>POST /add</h3>

<p>Expected request fields:</p>

<pre>
{
  "buyer_id": "...",
  "product_id": "...",
  "quantity": 1
}
</pre>

<p>
The route validates the required fields, checks that the product exists, checks stock, creates the buyer cart when necessary, and updates an existing cart item when the product is already present.
</p>

<h3>POST /checkout</h3>

<p>
The checkout route receives a <code>buyer_id</code>. It rejects an empty cart, verifies that each product still exists and has sufficient stock, calculates the total using the current server-side product price, creates a checkout snapshot, creates a Razorpay order and persists the checkout.
</p>

<h3>POST /verify_payment</h3>

<p>
The request contains:</p>

<pre>
{
  "razorpay_payment_id": "...",
  "razorpay_order_id": "...",
  "razorpay_signature": "..."
}
</pre>

<p>
The server computes an HMAC SHA-256 signature using the Razorpay secret and the order/payment IDs. Only a matching signature proceeds to checkout confirmation.
</p>

<h2>📦 Order APIs</h2>

<table>
<tr><th>Purpose</th><th>Behavior</th></tr>
<tr><td>Create / verify payment</td><td>Persist confirmed order information after successful payment verification.</td></tr>
<tr><td>Check order status</td><td>Used by the Streamlit UI to determine whether a pending payment has completed or been cancelled.</td></tr>
<tr><td>Order history</td><td>Retrieves a buyer's previous orders.</td></tr>
<tr><td>Cancel order</td><td>Handles cancellation of eligible orders / pending payment workflows.</td></tr>
</table>

<h2>📝 Activity API</h2>

<table>
<tr><th>Method</th><th>Endpoint</th><th>Purpose</th></tr>
<tr><td>GET</td><td><code>/activities</code></td><td>Retrieve activity records for a user.</td></tr>
</table>

<p>
Activity events include actions such as product search, cart additions, order-history access, login and payment verification. Events can be associated with either a <code>USER</code> or <code>AGENT</code>.
</p>

<h2>🤖 AI-facing operations</h2>

<p>
The AI agent uses application tools rather than directly manipulating MongoDB or Razorpay. The currently implemented buyer-side tool set includes product search, purchase-related operations and previous-order retrieval; merchant-side tools include product retrieval, product creation and sales information.
</p>

<h2>⚠️ API Contract Note</h2>

<p>
The exact mounted URL prefix is determined by the Express router registration in the server entry point. Keep the endpoint paths in this document synchronized with the router mounting configuration when the backend structure changes.
</p>
