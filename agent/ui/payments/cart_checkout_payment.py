
import streamlit as st
import streamlit.components.v1 as components

@st.dialog("Complete Cart Payment", width="large")

def cart_checkout_payment_dialog(payment, user_id):

    checkout_html = f"""
    <html>

        <body style="
            margin: 0;
            padding: 10px;
            font-family: sans-serif;
        ">

            <div id="status"
                 style="
                    text-align: center;
                    margin: 10px;
                    font-size: 16px;
                 ">
                Connecting to payment gateway...
            </div>


            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>


            <script>

                async function startPayment() {{

                    const statusDiv =
                        document.getElementById("status");

                    try {{

                        const options = {{

                            "key": "{payment["key_id"]}",

                            "amount": {payment["amount"]},

                            "currency": "{payment["currency"]}",

                            "name": "AI Marketplace",

                            "description": "Cart Purchase",

                            "order_id":
                                "{payment["razorpay_order_id"]}",


                            "handler": async function(resp) {{

                                try {{

                                    statusDiv.innerHTML =
                                        "<p>Verifying cart payment...</p>";


                                    const response = await fetch(

                                        "http://localhost:8009/carts/verify_payment",

                                        {{

                                            method: "POST",

                                            headers: {{

                                                "Content-Type":
                                                    "application/json",

                                                "X-User-ID":
                                                    "{user_id}",

                                                "X-Actor-Type":
                                                    "USER"

                                            }},

                                            body: JSON.stringify({{

                                                razorpay_payment_id:
                                                    resp.razorpay_payment_id,

                                                razorpay_order_id:
                                                    resp.razorpay_order_id,

                                                razorpay_signature:
                                                    resp.razorpay_signature

                                            }})

                                        }}

                                    );


                                    const result =
                                        await response.json();


                                    if (response.ok) {{

                                        statusDiv.innerHTML =

                                            '<div style="text-align:center;">' +

                                            '<h2 style="color:#00d084;">' +

                                            '✅ Payment Successful' +

                                            '</h2>' +

                                            '<p style="color:aqua;">' +

                                            'Your cart order has been confirmed.' +

                                            '</p>' +

                                            '<p style="color:aqua;">' +

                                            'Checkout ID: ' +

                                            result.checkout_id +

                                            '</p>' +

                                            '</div>';


                                        console.log(
                                            "Cart verification response:",
                                            result
                                        );

                                    }}

                                    else {{

                                        statusDiv.innerHTML =

                                            '<h4 style="color:red;">' +

                                            '❌ Payment verification failed' +

                                            '</h4>';

                                        console.error(
                                            "Verification error:",
                                            result
                                        );

                                    }}

                                }}

                                catch (error) {{

                                    statusDiv.innerHTML =

                                        '<h4 style="color:red;">' +

                                        '❌ Verification request failed' +

                                        '</h4>';

                                    console.error(
                                        "Verification request error:",
                                        error
                                    );

                                }}

                            }},


                            "prefill": {{

                                "name": "Test User",

                                "email": "test@example.com",

                                "contact": "9999999999"

                            }},


                            "theme": {{

                                "color": "#3399cc"

                            }}

                        }};


                        const rzp =
                            new Razorpay(options);


                        rzp.on(

                            "payment.failed",

                            function(resp) {{

                                statusDiv.innerHTML =

                                    '<h4 style="color:red;">' +

                                    '❌ Payment Failed' +

                                    '</h4>';

                                console.error(
                                    "Payment failed:",
                                    resp
                                );

                            }}

                        );


                        rzp.open();


                        statusDiv.innerText =
                            "Proceeding with cart checkout...";

                    }}

                    catch (err) {{

                        statusDiv.innerHTML =

                            '<h4 style="color:red;">' +

                            '❌ Error initiating payment: ' +

                            err.message +

                            '</h4>';

                        console.error(err);

                    }}

                }}


                startPayment();

            </script>

        </body>

    </html>
    """

    components.html(checkout_html, height=500, scrolling=False)
