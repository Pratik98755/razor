const express = require('express');
const router = express.Router();

const {CHECKOUTS} = require('../models/checkouts')
const RECOMMENDATION_STATS = require('../models/recommendation_stats')

router.post("/recommendation_stats", async (req, res) => {
    try {
        console.log("/recommendation_stats called");

        const {
            buyer_id,
            razorpay_order_id,
            recommendations,
            skipped
        } = req.body;

        // --------------------------------------------------
        // VALIDATION
        // --------------------------------------------------

        if (
            !buyer_id ||
            !razorpay_order_id ||
            !Array.isArray(recommendations)
        ) {
            return res.status(400).json({
                msg: "buyer_id, razorpay_order_id and recommendations are required"
            });
        }

        // --------------------------------------------------
        // FIND CHECKOUT
        // --------------------------------------------------

        const checkout = await CHECKOUTS.findOne({
            buyer_id,
            razorpay_order_id
        });

        if (!checkout) {
            return res.status(404).json({
                msg: "Checkout not found"
            });
        }

        console.log("CHECKOUT FOUND:", checkout._id);

        // --------------------------------------------------
        // PAYMENT TRUTH
        // --------------------------------------------------

        const payment_confirmed =
            checkout.razorpay_status === "paid" &&
            checkout.status === "CONFIRMED";

        console.log("PAYMENT CONFIRMED:", payment_confirmed);

        const checkout_items = checkout.items || [];

        // --------------------------------------------------
        // CREATE ONE STATS DOCUMENT PER RECOMMENDATION
        // --------------------------------------------------

        const created_stats = [];

        for (const recommendation of recommendations) {

            const product_id = recommendation.product_id;
            const merchant_id = recommendation.merchant_id;

            if (!product_id || !merchant_id) {
                continue;
            }

            // --------------------------------------------------
            // CHECK WHETHER RECOMMENDED PRODUCT WAS PURCHASED
            // --------------------------------------------------

            let purchased_item = null;

            if (payment_confirmed) {
                purchased_item = checkout_items.find(
                    item => item.product_id === product_id
                );
            }

            const purchased = !!purchased_item;

            const purchased_quantity = purchased_item
                ? purchased_item.quantity || 0
                : 0;

            // --------------------------------------------------
            // ACTUAL PURCHASE VALUE
            // Use price stored in checkout, NOT recommendation
            // price.
            // --------------------------------------------------

            const cross_sell_revenue = purchased_item
                ? (purchased_item.price_per_unit || 0) * purchased_quantity
                : 0;

            // --------------------------------------------------
            // CREATE STATS DOCUMENT
            // --------------------------------------------------

            const stat = await RECOMMENDATION_STATS.create({
                buyer_id,
                merchant_id,
                product_id,
                razorpay_order_id,

                shown: true,

                added_to_cart:
                    recommendation.added_to_cart === true,

                skipped: skipped === true,

                purchased,

                purchased_quantity,

                payment_confirmed,

                cross_sell_revenue
            });

            created_stats.push(stat);
        }

        // --------------------------------------------------
        // RESPONSE
        // --------------------------------------------------

        return res.status(201).json({
            msg: "Recommendation statistics recorded",
            count: created_stats.length,
            recommendation_stats: created_stats
        });

    } catch (error) {
        console.error(
            "RECOMMENDATION STATS ERROR:",
            error
        );

        return res.status(500).json({
            msg: "Failed to record recommendation statistics",
            error: error.message
        });
    }
});



module.exports = router;