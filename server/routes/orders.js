
require('dotenv').config();

const express = require('express')
const router = express.Router();

const activity = require('../middlewares/activity');

const {ORDERS} = require('../models/orders')
const {PRODUCTS} = require('../models/products')

const { nanoid } = require('nanoid');
const crypto = require("crypto");

const Razorpay = require('razorpay');
const { error } = require('console');

const razorpay = new Razorpay({
    key_id: process.env.RAZORPAY_KEY_ID,
    key_secret: process.env.RAZORPAY_KEY_SECRET
});




router.post('/create_order', activity('ORDER_CREATED', 'ORDER'), async (req, res) => {

    try {

        const { buyer_id, product_id, quantity } = req.body;

        const product = await PRODUCTS.findOne({
            product_id
        });

        if (!product) {
            return res.status(404).json({
                msg: "Product not found"
            });
        }


        if (product.stock < quantity) {
            return res.status(400).json({
                msg: "Insufficient stock"
            });
        }

        // Calculate price on SERVER
        const price_per_unit = product.price;
        const total_price = quantity * price_per_unit;
        const generated_order_id = nanoid(12);


        console.log("quantity:", quantity);
        console.log("product price:", product.price);
        console.log("total price:", total_price);
        console.log("Razorpay amount:", total_price * 100);

        // Razorpay expects amount in paise
        const razorpay_order = await razorpay.orders.create({

            amount: total_price * 100,

            currency: "INR",

            receipt: `receipt_${generated_order_id}`

        });

        console.log("Razorpay order created:", razorpay_order);

        // Create YOUR order only after Razorpay order succeeds
        const order = await ORDERS.create({

            order_id: generated_order_id,

            buyer_id,

            product_id,

            merchant_id: product.merchant_id,

            quantity,

            price_per_unit,

            total_price,

            razorpay_order_id: razorpay_order.id,

            razorpay_status: razorpay_order.status,

            status: "PENDING_PAYMENT"

        });

        // adding product_id for activity logging
        req.activity.entityId = generated_order_id;

        console.log('ORDERS_CREATED_LOCALLY : ', order)

        return res.status(201).json({

            msg: "Order created successfully",

            order_id: order.order_id,

            razorpay_order_id: razorpay_order.id,

            amount: razorpay_order.amount,

            currency: razorpay_order.currency,

            key_id: process.env.RAZORPAY_KEY_ID

        });

    } catch (err) {

        console.error(err);

        return res.status(500).json({
            msg: "Internal server error"
        });

    }

});




router.post("/verify_payment", activity("ORDER_CONGFIRMED", "ORDER"), async (req, res) => {
        console.log("/verify payment called ::::::::::::::::::::::::::")
        try {
            const {razorpay_payment_id, razorpay_order_id, razorpay_signature} = req.body;

            if (
                !razorpay_payment_id ||
                !razorpay_order_id ||
                !razorpay_signature
            ) {
                return res.status(400).json({
                    msg: "Missing payment verification details"
                });
            }

            // Find our local order
            const order = await ORDERS.findOne({
                razorpay_order_id
            });

            if (!order) {
                return res.status(404).json({
                    msg: "Order not found"
                });
            }

            // Prevent re-verification of an already paid order
            if (order.status === "CONFIRMED") {
                return res.status(400).json({
                    msg: "Order is already confirmed"
                });
            }

            // Create expected signature
            const generated_signature = crypto.createHmac("sha256", process.env.RAZORPAY_KEY_SECRET)
                .update(
                    razorpay_order_id + "|" + razorpay_payment_id
                )
                .digest("hex");

            // Compare signatures
            if (generated_signature !== razorpay_signature) {
                return res.status(400).json({
                    msg: "Payment verification failed"
                });
            }

            // Signature is valid
            order.razorpay_payment_id = razorpay_payment_id;
            order.razorpay_signature = razorpay_signature;
            order.razorpay_status = "paid";
            order.status = "CONFIRMED";

            await order.save();

            // NOW decrease stock
            const product = await PRODUCTS.findOne({
                product_id: order.product_id
            });

            if (!product) {
                return res.status(404).json({
                    msg: "Product not found"
                });
            }

            if (product.stock < order.quantity) {
                return res.status(400).json({
                    msg: "Insufficient stock"
                });
            }

            product.stock -= order.quantity;
            await product.save();

            req.activity.entityId = order.order_id;

            return res.status(200).json({
                msg: "Payment verified successfully",
                order: order
            });

        } catch (err) {
            console.error(err);
            return res.status(500).json({
                msg: "Internal server error"
            });
        }
    }
);





// router.get("/check_order_status",activity("ORDER_CONFIRMED", "ORDER") ,async (req, res) => {
router.get("/check_order_status", async (req, res) => {
    try {
        console.log("/check order status called");

        const { razorpay_order_id } = req.query;

        if (!razorpay_order_id) {
            return res.status(400).json({
                msg: "razorpay_order_id is required"
            });
        }

        const order = await ORDERS.findOne({
            razorpay_order_id
        });

        console.log("order_found !!! : ", order);

        if (!order) {
            return res.status(404).json({
                msg: "order not found!"
            });
        }

        // req.activity.entityId = order.order_id;

        if (
            order.razorpay_status === "paid" &&
            order.status === "CONFIRMED"
        ) {


            return res.status(200).json({
                paid: true,
                msg: "order paid"
            });
        }

        return res.status(200).json({
            paid: false,
            msg: "order not paid yet"
        });

    } catch (err) {
        console.error("CHECK ORDER STATUS ERROR:", err);

        return res.status(500).json({
            err: "failed to check order status"
        });
    }
});


module.exports = router;