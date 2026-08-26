const express = require('express')
const router = express.Router();

const activity = require('../middlewares/activity');

const {ORDERS} = require('../models/orders')
const {PRODUCTS} = require('../models/products')

const { nanoid } = require('nanoid');



router.post('/create_order',activity('ORDER_CREATED', 'ORDER'), async (req, res) => {
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

        // adding product_id for the middleware (activity logging)
        req.activity.entityId = product.product_id;

        if (product.stock < quantity) {
            return res.status(400).json({
                msg: "Insufficient stock"
            });
        }
        const price_per_unit = product.price;
        const total_price = quantity * price_per_unit;

        const order = await ORDERS.create({

            order_id: nanoid(12),
            buyer_id,
            product_id,
            merchant_id: product.merchant_id,
            quantity,
            price_per_unit,
            total_price,
            status: "CONFIRMED"
        });
        
        // decrease the stock by quantity and save it
        product.stock -= quantity;
        await product.save();

        return res.status(201).json({
            msg: "Order created successfully",
            order
        });

    } catch (err) {
        console.error(err);
        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});

module.exports = router;