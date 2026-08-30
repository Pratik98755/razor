const mongoose = require("mongoose");

const cart_item_schema = new mongoose.Schema(
    {
        product_id: {
            type: String,
            required: true
        },

        quantity: {
            type: Number,
            required: true,
            min: 1
        }
    },
    {
        _id: false
    }
);

const cart_schema = new mongoose.Schema(
    {
        cart_id: {
            type: String,
            unique: true,
            required: true
        },

        buyer_id: {
            type: String,
            unique: true,
            required: true
        },

        items: {
            type: [cart_item_schema],
            default: []
        }
    },
    {
        collection: "carts_collection",
        timestamps: true
    }
);

const CARTS = mongoose.model("carts_collection", cart_schema);

module.exports = { CARTS };