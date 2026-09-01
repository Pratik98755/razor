const express = require('express')
const router = express.Router();

const activity = require('../middlewares/activity.js');

const { nanoid } = require('nanoid');
const { PRODUCTS } = require('../models/products');
const {ORDERS} = require('../models/orders.js')
const {USERS} = require('../models/users.js')
const {ACTIVITY} = require('../models/activity.js')
const RECOMMENDATION_STATS =require('../models/recommendation_stats.js')


// import { add_product_embedding, edit_product_embedding, delete_product_embedding } from '../embeddings/model.js'



router.post('/add_product',activity('PRODUCT_ADDED', 'PRODUCT'), async (req, res) => {

        try {
            const data = req.body;
            const random_id = nanoid(10);

            // ----------------------------------------
            // Generate AI product metadata
            // ----------------------------------------

            const { generate_product_metadata } = await import('../structured_ai/product_metadata.js');
            const metadata = await generate_product_metadata({
                    name: data.name,
                    description: data.description,
                    category: data.category
                });

            // ----------------------------------------
            // Save product + metadata in MongoDB
            // ----------------------------------------

            const product = await PRODUCTS.create({
                product_id: random_id,
                merchant_id: data.merchant_id,
                name: data.name,
                price: data.price,
                stock: data.stock,
                description: data.description,
                category: data.category,
                images: data.images,
                metadata
            });


            // ----------------------------------------
            // Activity logging
            // ----------------------------------------

            req.activity.entityId = random_id;


            // ----------------------------------------
            // Generate / store embedding
            // ----------------------------------------

            const {add_product_embedding} = await import('../embeddings/model.js');

            await add_product_embedding(product);
            console.log(`product_created : ${product}`);

            return res.status(201).json({
                msg: 'product added!'
            });

        } catch (error) {

            console.error(
                "ADD PRODUCT ERROR:",
                error
            );
            return res.status(500).json({
                msg: "failed to add product",
                error: error.message
            });
        }
    }
);






router.get('/sales_by_merchant',activity('SALES_FETCHED', 'PRODUCT'), async (req, res) => {
    try {
        const { merchant_id } = req.query;
        if (!merchant_id) {
            return res.status(400).json({
                msg: "merchant_id is required"
            });
        }

        const orders = await ORDERS.find({
            merchant_id: merchant_id
        }).sort({
            createdAt: -1
        });
        return res.status(200).json({
            orders: orders
        });

    }catch(err){
        console.error(err);
        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});





router.get("/stats", async (req, res) => {
    try {
        const { merchant_id } = req.query;

        const stats = await RECOMMENDATION_STATS.find({
            merchant_id
        }).sort({ createdAt: -1 });

        // =========================================================
        // AGGREGATE METRICS
        // =========================================================

        const shown = stats.length;

        const added_to_cart = stats.filter(
            stat => stat.added_to_cart
        ).length;

        const purchased = stats.filter(
            stat => stat.purchased
        ).length;

        const dismissed = stats.filter(
            stat => stat.skipped
        ).length;

        const payment_confirmed = stats.filter(
            stat => stat.payment_confirmed
        ).length;

        const cross_sell_revenue = stats.reduce(
            (total, stat) =>
                total + (stat.cross_sell_revenue || 0),
            0
        );

        const purchased_units = stats.reduce(
            (total, stat) =>
                total + (stat.purchased_quantity || 0),
            0
        );

        // =========================================================
        // PRODUCT-LEVEL AI CROSS-SELL ANALYTICS
        // =========================================================

        const productStats = {};

        for (const stat of stats) {

            const product_id = stat.product_id;

            if (!product_id) {
                continue;
            }

            if (!productStats[product_id]) {
                productStats[product_id] = {
                    product_id,
                    shown: 0,
                    added_to_cart: 0,
                    purchased: 0,
                    skipped: 0,
                    purchased_units: 0,
                    revenue: 0
                };
            }

            const product = productStats[product_id];

            // Recommendation was shown
            product.shown += 1;

            // Added to cart
            if (stat.added_to_cart) {
                product.added_to_cart += 1;
            }

            // Purchased
            if (stat.purchased) {
                product.purchased += 1;
            }

            // Skipped / dismissed
            if (stat.skipped) {
                product.skipped += 1;
            }

            // Units purchased
            product.purchased_units +=
                stat.purchased_quantity || 0;

            // Actual cross-sell revenue
            product.revenue +=
                stat.cross_sell_revenue || 0;
        }

        // =========================================================
        // CALCULATE PRODUCT-LEVEL RATES
        // =========================================================

        const top_ai_cross_sells = Object.values(productStats)
            .map(product => ({
                product_id: product.product_id,

                shown: product.shown,

                added_to_cart: product.added_to_cart,

                add_to_cart_rate:
                    product.shown > 0
                        ? product.added_to_cart / product.shown
                        : 0,

                purchased: product.purchased,

                purchase_rate:
                    product.shown > 0
                        ? product.purchased / product.shown
                        : 0,

                skipped: product.skipped,

                skip_rate:
                    product.shown > 0
                        ? product.skipped / product.shown
                        : 0,

                purchased_units: product.purchased_units,

                revenue: product.revenue
            }))
            .sort((a, b) => b.revenue - a.revenue);

        // =========================================================
        // RESPONSE
        // =========================================================

        return res.status(200).json({

            // -----------------------------------------------------
            // EXISTING AGGREGATE METRICS
            // -----------------------------------------------------

            shown,
            added_to_cart,
            purchased,
            dismissed,
            payment_confirmed,
            purchased_units,
            cross_sell_revenue,

            add_to_cart_rate:
                shown > 0
                    ? added_to_cart / shown
                    : 0,

            purchase_rate:
                shown > 0
                    ? purchased / shown
                    : 0,

            recommendation_conversion_rate:
                added_to_cart > 0
                    ? purchased / added_to_cart
                    : 0,

            revenue_per_recommendation:
                shown > 0
                    ? cross_sell_revenue / shown
                    : 0,

            // -----------------------------------------------------
            // PRODUCT-LEVEL ANALYTICS
            // -----------------------------------------------------

            top_ai_cross_sells

        });

    } catch (error) {

        console.error(
            "MERCHANT RECOMMENDATION STATS ERROR:",
            error
        );

        return res.status(500).json({
            msg: "Failed to fetch recommendation statistics",
            error: error.message
        });
    }
});





router.get('/get_products', async (req, res) => {
    // console.log("GET PRODUCTS CALLED :::::::::::::::::::::")
    const merchant_id = req.query.merchant_id;
    const products = await PRODUCTS.find({
        merchant_id: merchant_id
    })

    if (products.length == 0) {
        return res.status(200).json({
            'msg': 'no products found !',
            products: products
        })
    } else {
        return res.status(200).json({
            'msg': 'products found !',
            products: products
        })
    }
})

router.delete('/delete_product',activity('PRODUCT_DELETED', 'PRODUCT'), async(req, res) => {
    const pro_id = req.query.product_id;
    const product = await PRODUCTS.findOne({
        product_id : pro_id
    })
    if(product){

        // adding product_id for the middleware (activity logging)
        req.activity.entityId = pro_id;

        await PRODUCTS.deleteOne({
            product_id : pro_id
        })
        // delete product from vector db
        const { delete_product_embedding} = await import('../embeddings/model.js');
        await delete_product_embedding(pro_id)

        console.log(`product_deleted : ${product}`)
        res.status(200).json({
            'msg' : 'product deleted'
        })
    }else{
        res.sendStatus(204)
    }
})



router.patch('/edit_product', activity('PRODUCT_EDITED', 'PRODUCT'), async (req, res) => {

        try {
            const product_id = req.query.product_id;

            // ----------------------------------------
            // Find existing product
            // ----------------------------------------

            const product = await PRODUCTS.findOne({
                product_id: product_id
            });
            if (!product) {
                return res.sendStatus(204);
            }

            // ----------------------------------------
            // Activity logging
            // ----------------------------------------

            req.activity.entityId = product_id;

            // ----------------------------------------
            // Check whether semantic fields changed
            // ----------------------------------------
            // These fields affect product meaning,
            // so metadata + embedding must be regenerated.

            const semanticFieldsChanged =
                req.body.name !== undefined ||
                req.body.description !== undefined ||
                req.body.category !== undefined;

            // ----------------------------------------
            // Build allowed update fields
            // metadata is NOT allowed from client
            // ----------------------------------------

            const updateData = {};
            if (req.body.name !== undefined) {
                updateData.name = req.body.name;
            }
            if (req.body.description !== undefined) {
                updateData.description = req.body.description;
            }
            if (req.body.price !== undefined) {
                updateData.price = req.body.price;
            }
            if (req.body.stock !== undefined) {
                updateData.stock = req.body.stock;
            }
            if (req.body.category !== undefined) {
                updateData.category = req.body.category;
            }
            if (req.body.images !== undefined) {
                updateData.images = req.body.images;
            }

            // ----------------------------------------
            // Update basic product information
            // ----------------------------------------

            const updated = await PRODUCTS.findOneAndUpdate(
                {
                    product_id: product_id
                },
                {
                    $set: updateData
                },
                {
                    new: true
                }
            );


            // ----------------------------------------
            // Regenerate metadata + embedding
            // ONLY when semantic fields changed
            // ----------------------------------------

            if (semanticFieldsChanged) {
                // ------------------------------------
                // Generate NEW AI metadata
                // ------------------------------------
                const {generate_product_metadata} = await import('../ai/product_metadata.js');

                const metadata = await generate_product_metadata({
                        name: updated.name,
                        description: updated.description,
                        category: updated.category
                    });


                // ------------------------------------
                // Save AI metadata
                // ------------------------------------

                updated.metadata = metadata;
                await updated.save();

                // ------------------------------------
                // Regenerate product embedding
                // ------------------------------------

                const {edit_product_embedding} = await import('../embeddings/model.js');
                await edit_product_embedding(updated);
            }

            // ----------------------------------------

            console.log(`product_updated : ${updated}`);
            return res.status(200).json({
                msg: 'product updated'
            });


        } catch (error) {
            console.error(
                "EDIT PRODUCT ERROR:",
                error
            );
            return res.status(500).json({
                msg: "failed to update product",
                error: error.message
            });

        }

    }
);



router.get('/activities', async(req, res) => {
    console.log('/merchant activities api called')
    const {user_id} = req.query;
    const user = await USERS.findOne({
        user_id : user_id
    })
    if(!user){
        return res.status(404).json({
            'msg' : 'user not found !'
        })
    }
    const activities = await ACTIVITY.find({
        user_id : user_id
    }).sort({
        createdAt: -1
    });
    console.log('activities found !!!', activities)
    return res.status(200).json({
        'user_id' : user_id,
        'activities' : activities
    })
})


module.exports = router