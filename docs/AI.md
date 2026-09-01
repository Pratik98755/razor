<h1>🧠 AI & Recommendation Architecture</h1>

<h2>1. AI Buyer Agent</h2>

<p>
The buyer experience is centered around a conversational AI agent exposed through the Streamlit Scout interface.
</p>

<p>
The Streamlit page sends the buyer's question and user ID to the agent. The agent returns a natural-language answer plus structured information that the UI can use for product results and payment / checkout flows.
</p>

<pre>
ask_agent(
    question,
    user_id
)
        ↓
answer
products
payment
cart_checkout_details
</pre>

<h2>2. Agent Tools</h2>

<table>
<tr><th>Agent</th><th>Tool</th><th>Purpose</th></tr>
<tr><td>Buyer</td><td><code>search_products</code></td><td>Find products matching buyer intent.</td></tr>
<tr><td>Buyer</td><td><code>buy_product</code></td><td>Initiate a purchase workflow.</td></tr>
<tr><td>Buyer</td><td><code>previous_orders</code></td><td>Retrieve order history.</td></tr>
<tr><td>Merchant</td><td><code>get_products</code></td><td>Retrieve merchant products.</td></tr>
<tr><td>Merchant</td><td><code>add_product</code></td><td>Create a product.</td></tr>
<tr><td>Merchant</td><td><code>sales_by_merchant</code></td><td>Retrieve merchant sales information.</td></tr>
</table>

<h2>3. Structured Product Intelligence</h2>

<p>
Product information can be enriched by an LLM into structured metadata rather than relying only on merchant-entered category labels.
</p>

<table>
<tr><th>Field</th><th>Purpose</th></tr>
<tr><td><code>product_type</code></td><td>Normalized product type.</td></tr>
<tr><td><code>product_role</code></td><td>Primary product, accessory, replacement, consumable, component, service, bundle, etc.</td></tr>
<tr><td><code>use_contexts</code></td><td>Contexts in which the product is used.</td></tr>
<tr><td><code>compatible_with</code></td><td>Product types that this item complements or works with.</td></tr>
<tr><td><code>complementary_search_queries</code></td><td>Natural-language queries describing useful complementary products.</td></tr>
<tr><td><code>attributes</code></td><td>Important structured product characteristics.</td></tr>
</table>

<h2>4. Embeddings</h2>

<p>
The product-search layer uses embeddings and LanceDB. Product information can be represented as enriched searchable text so that semantic similarity captures intent beyond exact keyword matches.
</p>

<p>
For cross-sell recommendations, the architecture uses an anchor product's complementary-product intent to retrieve candidate products.
</p>

<h2>5. Candidate Generation</h2>

<pre>
Anchor product
      ↓
Vector candidate retrieval
      +
Compatibility / metadata retrieval
      +
Context overlap
      ↓
Union + deduplicate
      ↓
Hard filters
      ↓
Candidate pool
</pre>

<h2>6. Complementary vs Alternative vs Unrelated</h2>

<p>
A critical requirement is avoiding recommendations that are merely alternatives to the product the buyer already selected.
</p>

<table>
<tr><th>Relationship</th><th>Example</th></tr>
<tr><td>Complementary</td><td>Laptop → Laptop Bag</td></tr>
<tr><td>Alternative</td><td>Laptop → Another Laptop</td></tr>
<tr><td>Upsell</td><td>Laptop → Higher-end Laptop</td></tr>
<tr><td>Unrelated</td><td>Laptop → Water Bottle</td></tr>
</table>

<p>
The recommendation design uses inexpensive deterministic filtering before LLM pair classification. The classifier can label candidates as <code>complementary</code>, <code>alternative</code>, <code>upsell</code> or <code>unrelated</code>.
</p>

<h2>7. Recommendation Ranking</h2>

<p>
Complementary candidates can be ranked using a combination of signals such as LLM confidence, price relationship, vector similarity and metadata compatibility.
</p>

<pre>
Final recommendation score
        =
LLM complementarity confidence
+ price-band signal
+ vector similarity
+ metadata compatibility
+ optional quality / popularity signal
</pre>

<h2>8. Recommendation Guardrails</h2>

<ul>
<li>Candidate must be in stock.</li>
<li>Candidate must not already be in the cart.</li>
<li>Candidate should have a different product type from the anchor.</li>
<li>Candidate should have an appropriate complementary role.</li>
<li>Unrelated candidates should be rejected.</li>
<li>Only a small number of recommendations should be shown at a time.</li>
</ul>

<h2>9. Agent vs Recommendation Engine</h2>

<table>
<tr><th>Component</th><th>Responsibility</th></tr>
<tr><td>Recommendation Engine</td><td>Candidate generation, filtering, relationship classification and ranking.</td></tr>
<tr><td>AI Agent</td><td>Conversation, tool selection, presenting recommendations and handling buyer interaction.</td></tr>
<tr><td>Backend</td><td>Transactions, stock validation, cart state, checkout, orders and payment verification.</td></tr>
</table>

<p>
This separation is important because the LLM should not be trusted to directly enforce transaction-critical business rules.
</p>

<h2>10. End-to-End AI Commerce Flow</h2>

<pre>
Merchant creates product
        ↓
AI product enrichment
        ↓
Embeddings / vector storage
        ↓
Buyer asks Scout for a product
        ↓
Semantic product search
        ↓
Buyer adds a product
        ↓
Cross-sell candidate generation
        ↓
Filtering + AI relationship classification
        ↓
Top complementary recommendation
        ↓
Buyer accepts / rejects
        ↓
Cart update
        ↓
Razorpay checkout
        ↓
Payment verification
        ↓
Confirmed order
        ↓
Activity logging
</pre>
