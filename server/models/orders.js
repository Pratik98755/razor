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

    status: {
        type: String,
        enum: [
            "CONFIRMED",
            "CANCELLED",
            "COMPLETED"
        ],
        default: "CONFIRMED"
    }

}, {
    collection: "orders_collection",
    timestamps: true
})

const ORDERS = new mongoose.model('orders_collection', order_schema);

module.exports = {ORDERS}