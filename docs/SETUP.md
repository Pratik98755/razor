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

<h2>🍃 MongoDB</h2>

<p>
The backend uses MongoDB through Mongoose. Configure the MongoDB connection string through an environment variable rather than hard-coding credentials in source code.
</p>

<h2>🔐 Environment Variables</h2>

<p>
Create a local <code>.env</code> file containing the credentials required by the backend and AI integrations. The exact variable names should match the names read by the source code.
</p>

<pre>
MONGO_URI=...

RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...

GOOGLE_API_KEY=...
GROQ_API_KEY=...
</pre>

<p>
Do <b>not</b> commit <code>.env</code> or API credentials to the repository.
</p>

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

<h3>Backend cannot connect to MongoDB</h3>
<p>Check that MongoDB is running and that the configured connection string points to the correct database.</p>

<h3>Razorpay initialization fails</h3>
<p>Verify that both the Razorpay key ID and secret are available to the Node.js process.</p>

<h3>AI calls fail</h3>
<p>Check the relevant Google/Groq credentials and confirm that the configured model is available to the account.</p>

<h3>Payment verification fails</h3>
<p>Make sure the exact Razorpay order ID, payment ID and signature returned by Checkout are sent to the backend. The server independently computes the expected HMAC signature.</p>
