const mongoose = require('mongoose');

const order_schema = mongoose.Schema({

    order_id: {
        type: String,
        unique: true,
        required: true
    },

    buyer_id: {
        type: String,
        required: true
    },

    product_id: {
        type: String,
        required: true
    },

    merchant_id: {
        type: String,
        required: true
    },

    quantity: {
        type: Number,
        required: true,
        min: 1
    },

    price_per_unit: {
        type: Number,
        required: true
    },

    total_price: {
        type: Number,
        required: true
    },

    // -----------------------------
    // Razorpay fields
    // -----------------------------

    razorpay_order_id: {
        type: String,
        // unique: true,
        sparse: true
    },

    razorpay_payment_id: {
        type: String,
        sparse: true
    },

    razorpay_signature: {
        type: String,
        sparse: true
    },

    razorpay_status: {
        type: String,
        enum: [
            "created",
            "attempted",
            "paid",
            "failed"
        ]
    },

    // -----------------------------
    // Our internal order status
    // -----------------------------

    status: {
        type: String,
        enum: [
            "PENDING_PAYMENT",
            "CONFIRMED",
            "CANCELLED",
            "FAILED"
        ],
        default: "PENDING_PAYMENT"
    }

}, {
    collection: "orders_collection",
    timestamps: true
})

const ORDERS = new mongoose.model('orders_collection', order_schema);

module.exports = {ORDERS}