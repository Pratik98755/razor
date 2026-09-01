
require('dotenv').config();

const express = require('express')
const router = express.Router();

const activity = require('../middlewares/activity');

const {ORDERS} = require('../models/orders')
const {PRODUCTS} = require('../models/products')
const { CHECKOUTS } = require("../models/checkouts");

const { nanoid } = require('nanoid');
const crypto = require("crypto");

const Razorpay = require('razorpay');
// const { error } = require('console');

const razorpay = new Razorpay({
    key_id: process.env.RAZORPAY_KEY_ID,
    key_secret: process.env.RAZORPAY_KEY_SECRET
});




router.post('/create_order', activity('ORDER_CREATED', 'ITEM'), async (req, res) => {

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




router.post("/verify_payment", activity("ORDER_CONFIRMED", "ITEM"), async (req, res) => {
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

        // -----------------------------------------
        // Normal order
        // -----------------------------------------

        const order = await ORDERS.findOne({
            razorpay_order_id
        });

        if (order) {
            console.log("ORDER FOUND !!! : ", order);
            if (
                order.razorpay_status === "paid" &&
                order.status === "CONFIRMED"
            ) {
                return res.status(200).json({
                    status: "CONFIRMED",
                    paid: true,
                    msg: "order paid"
                });
            }

            return res.status(200).json({
                status: order.status,
                paid: false,
                msg: "order not paid yet"
            });
        }

        // -----------------------------------------
        // Cart checkout
        // -----------------------------------------

        const checkout = await CHECKOUTS.findOne({
            razorpay_order_id
        });

        if (checkout) {
            console.log(
                "CHECKOUT FOUND !!! : ",
                checkout
            );

            return res.status(200).json({
                status: checkout.status,
                paid: checkout.status === "CONFIRMED",
                msg:
                    checkout.status === "CONFIRMED"
                        ? "checkout paid"
                        : checkout.status === "CANCELLED"
                            ? "checkout cancelled"
                            : "checkout payment pending"
            });
        }

        // -----------------------------------------
        // Nothing found
        // -----------------------------------------

        return res.status(404).json({
            msg: "order/checkout not found"
        });

    } catch (err) {
        console.error(
            "CHECK ORDER STATUS ERROR:",
            err
        );
        return res.status(500).json({
            err: "failed to check order status"
        });
    }
});



router.post("/cancel_order", activity("ORDER_CANCELLED", "RAZORPAY_ORDER_ID"), async (req, res) => {
        try {
            console.log("/cancel_order called");

            const { razorpay_order_id } = req.body;

            if (!razorpay_order_id) {
                return res.status(400).json({
                    msg: "razorpay_order_id is required"
                });
            }

            const order = await ORDERS.findOneAndUpdate(
                {
                    razorpay_order_id,
                    status: "PENDING_PAYMENT"
                },
                {
                    $set: {
                        status: "CANCELLED"
                    }
                },
                {
                    new: true
                }
            );

            console.log('order found ::::', order)

            if (!order) {
                return res.status(400).json({
                    msg: "Order not found or already completed"
                });
            }

            // For activity logging
            req.activity.entityId = razorpay_order_id;

            console.log("ORDER CANCELLED:", razorpay_order_id);
            return res.status(200).json({
                status: "done",
                order_id: order.order_id
            });

        } catch (error) {

            console.error(
                "CANCEL ORDER ERROR:",
                error
            );

            return res.status(500).json({
                status: "err"
            });
        }
    }
);

router.post("/order_payment_failure",activity("ORDER_PAYMENT_FAILURE", "RAZORPAY_ORDER_ID"), async (req, res) => {
        try {
            console.log("/order_payment_failure called");
            const { razorpay_order_id } = req.body;

            if (!razorpay_order_id) {
                return res.status(400).json({
                    msg: "razorpay_order_id is required"
                });
            }

            const order = await ORDERS.findOneAndUpdate(
                {
                    razorpay_order_id,
                    status: "PENDING_PAYMENT"
                },
                {
                    $set: {
                        status: "FAILED"
                    }
                },
                {
                    new: true
                }
            );

            if (!order) {
                return res.status(400).json({
                    msg: "Order not found or already completed"
                });
            }

            // For activity logging
            req.activity.entityId = razorpay_order_id;

            console.log(
                "ORDER PAYMENT FAILURE:",
                razorpay_order_id
            );

            return res.status(200).json({
                status: "done",
                order_id: order.order_id
            });

        } catch (error) {

            console.error(
                "/order_payment_failure API error:",
                error
            );

            return res.status(500).json({
                status: "err"
            });
        }
    }
);




module.exports = router;