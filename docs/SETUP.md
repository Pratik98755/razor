<h1>⚙️ Setup & Installation</h1>

<p>
This document contains the detailed local-development setup for the AI-powered agentic commerce platform.
</p>

<h2>📋 Prerequisites</h2>

<ul>
<li>Node.js and npm</li>
<li>Python 3.x</li>
<li>MongoDB</li>
<li>Razorpay test-mode credentials</li>
<li>Google/Gemini API credentials used by the AI layer</li>
<li>Groq API credentials if the configured agent model requires them</li>
</ul>

<h2>📥 Clone the project</h2>

<pre>
git clone &lt;repository-url&gt;
cd razor
</pre>

<h2>🐍 Python environment</h2>

<pre>
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
</pre>

<h2>🟢 Node.js backend</h2>

<pre>
npm install
</pre>

<p>
Start the Express server using the project's configured development command.
</p>

<pre>
npm run dev
</pre>
Or if you have nodemon run (while being in server/)
<pre>
nodemon server.js
</pre>

<h2>🍃 MongoDB</h2>

<p>
The backend uses MongoDB through Mongoose. Configure the MongoDB connection string through an environment variable rather than hard-coding credentials in source code.
</p>

<h2>🔐 Environment Variables</h2>

<p>
Create a local <code>.env</code> file containing the credentials required by the backend and AI integrations. The exact variable names should match the names read by the source code. We have <code>.env.example</code> for your help in the agent and server directory.
</p>

<pre>
MONGO_URI=...

RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...

GOOGLE_API_KEY=...
GROQ_API_KEY=...
</pre>

<h2>🖥️ Start Streamlit</h2>

<pre>
streamlit run app.py
</pre>

<h2>💳 Razorpay Test Mode</h2>

<p>
The project uses Razorpay for order creation and payment processing. Use Razorpay test-mode credentials during development.
</p>

<p>
The backend creates Razorpay orders and returns the order information required by the Streamlit payment UI. Successful payments are verified server-side using the Razorpay signature.
</p>

<h2>🔍 Vector Search</h2>

<p>
The AI product-search layer uses embeddings and LanceDB. Make sure the embedding credentials required by the configured implementation are available before using semantic search or AI recommendation functionality.
</p>

<h2>🧪 Development Notes</h2>

<ul>
<li>Never trust payment success information supplied only by the client.</li>
<li>Keep Razorpay secrets on the backend.</li>
<li>Keep AI API keys out of source control.</li>
<li>Run MongoDB before starting the backend.</li>
<li>Use test-mode payment credentials while developing.</li>
</ul>

<h2>🛠️ Troubleshooting</h2>

<h3>⚠️ IMPORTANT — Model & Resource Limitations</h3>

<ul>
<li>
<b>Groq free-tier token limit:</b>
The free Groq API model has a token limit of approximately <b>8,000 tokens</b> per request. If an agent tool returns a large amount of data, such as an entire MongoDB collection or a large list of products, the resulting context can quickly exceed the model's token limit and cause an API error. Keep tool responses small and return only the data required by the agent.
</li>

<li>
<b>Google Embeddings request limits:</b>
The Google embedding model can also hit request or rate limits when a large number of embeddings are generated simultaneously. Avoid triggering many embedding requests concurrently, especially while generating or updating embeddings for a large product collection.
</li>

<li>
<b>Changing the AI models:</b>
Client-side AI models can be configured in:
<br>
<code>agent/agent.py</code> and <code>agent/structured_agent.py</code>
<br><br>
Server-side AI models can be configured in:
<br>
<code>server/embeddings/model.js</code> and the server-side structured AI module.
</li>

<li>
<b>Changing MongoDB / server configuration:</b>
The MongoDB connection URL, backend port and other server-level configuration can be modified in:
<br>
<code>server/server.js</code>
</li>

<li>
<b>Vector database location:</b>
Product vector embeddings are managed using <b>LanceDB</b>. The generated vector database files are stored in the <code>VECTOR_DBS</code> directory, located at the project root alongside the <code>server/</code> and <code>agent/</code> directories.
</li>
</ul>

<h3>Backend cannot connect to MongoDB</h3>

<p>
Check that MongoDB is running and that the configured MongoDB connection URL in <code>server/server.js</code> is correct.
</p>

<h3>Razorpay initialization fails</h3>

<p>
Verify that both the Razorpay key ID and secret are available to the Node.js process and that the credentials correspond to the intended Razorpay environment.
</p>

<h3>AI calls fail because of token limits</h3>

<p>
Check whether an agent tool is returning excessive data. Returning an entire collection, a large product list, or unnecessarily large documents can consume the model's context very quickly. Reduce the amount of data returned by the tool or limit the number of records.
</p>

<h3>Google Embeddings request limit error</h3>

<p>
If embedding requests fail intermittently or return rate-limit/request-limit errors, check whether multiple products are being embedded simultaneously. Reduce concurrency or process embeddings in smaller batches.
</p>

<h3>Payment verification fails</h3>

<p>
Make sure the exact Razorpay order ID, payment ID and signature returned by Checkout are sent to the backend. The server independently computes the expected HMAC signature before confirming the payment.
</p>

<h3>Vector search is not working</h3>

<p>
Make sure the <code>VECTOR_DBS</code> directory exists at the project root and that the required LanceDB vector data has been generated. If embeddings have not yet been created for the products, semantic search and recommendation functionality may not return results.
</p>

<h3>AI model configuration</h3>

<p>
If you want to change the model used by the application, check the corresponding client-side or server-side AI configuration files rather than changing the model in the UI.
</p>

<ul>
<li><code>agent/agent.py</code> — client-side agent model</li>
<li><code>agent/structured_agent.py</code> — client-side structured AI model</li>
<li><code>server/embeddings/model.js</code> — server-side embedding/model configuration</li>
<li><code>server/structured_ai</code> — server-side structured AI configuration</li>
</ul>

<h3>AI calls fail</h3>
<p>Check the relevant Google/Groq credentials and confirm that the configured model is available to the account.</p>

<h3>Payment verification fails</h3>
<p>Make sure the exact Razorpay order ID, payment ID and signature returned by Checkout are sent to the backend. The server independently computes the expected HMAC signature.</p>
