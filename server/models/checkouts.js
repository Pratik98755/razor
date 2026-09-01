const mongoose = require("mongoose");

const checkout_item_schema = new mongoose.Schema(
    {
        product_id: {
            type: String,
            required: true
        },

        merchant_id: {
            type: String,
            required: true
        },

        name: {
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
        }
    },
    {
        _id: false
    }
);


const checkout_schema = new mongoose.Schema(
    {
        checkout_id: {
            type: String,
            unique: true,
            required: true
        },

        buyer_id: {
            type: String,
            required: true
        },

        items: {
            type: [checkout_item_schema],
            required: true,
            validate: {
                validator: items => items.length > 0,
                message: "Checkout must contain at least one item"
            }
        },

        total_price: {
            type: Number,
            required: true,
            min: 0
        },

        // -----------------------------
        // Razorpay
        // -----------------------------

        razorpay_order_id: {
            type: String,
            unique: true,
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
            ],
            default: "created"
        },

        // -----------------------------
        // Our checkout status
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
    },
    {
        collection: "checkouts_collection",
        timestamps: true
    }
);


const CHECKOUTS = mongoose.model(
    "checkouts_collection",
    checkout_schema
);

module.exports = { CHECKOUTS };