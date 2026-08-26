const express = require('express');
const router = express.Router();

const activity = require('../middlewares/activity')

const { ORDERS } = require('../models/orders.js');
const {USERS} = require('../models/users.js');
const { PRODUCTS } = require('../models/products.js');
const {ACTIVITY} = require('../models/activity.js')

router.get('/search_product', activity('PRODUCT_SEARCHED', 'PRODUCT'), async (req, res) => {
    try {
        const {query, price, quantity, cursor} = req.query;
        if (!query) {
            return res.status(400).json({
                error: "query is required"
            });
        }
        console.log('PERFORMING SIMILARITY SEARCH ::::::::::::')
        const { similarity_search_products} = await import('../embeddings/model.js');
        const result = await similarity_search_products(query, price, quantity, cursor);
        const products = result.products.map(
            ({ vector, _distance, ...product }) => ({
                ...product,
                match_percentage: `${Math.max(
                    0,
                    Math.min(100, (1 - _distance) * 100)
                ).toFixed(0)}%`
            })
        );

        console.log('similar products : ', products)

        return res.status(200).json({
            products,
            next_cursor: result.next_cursor
        });

    } catch (error) {
        console.error("product search error:", error);
        return res.status(500).json({
            error: "failed to search products"
        });
    }
});



router.get('/get_previous_orders',activity('ORDER_HISTORY_FETCHED', 'ORDER'), async (req, res) => {

    try {
        const { user_id } = req.query;
        if (!user_id) {
            return res.status(400).json({
                msg: "user_id is required"
            });
        }
        const user_orders = await ORDERS.find({
            buyer_id: user_id
        }).sort({
            createdAt: -1
        });
        return res.status(200).json({
            previous_orders: user_orders
        });

    } catch (err) {
        console.error(err);
        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});



// either give a product_id or a list containing product_ids
router.get('/product_details', async (req, res) => {

    try {
        let { product_ids } = req.query;
        if (!product_ids) {
            return res.status(400).json({
                msg: "product_ids is required"
            });
        }

        // If only one ID is sent, Express gives a string.
        // If multiple IDs are sent, Express gives an array.
        if (!Array.isArray(product_ids)) {
            product_ids = [product_ids];
        }
        const products = await PRODUCTS.find({
            product_id: { $in: product_ids }
        });
        return res.status(200).json({
            product_details: products
        });

    } catch (err) {
        console.error(err);
        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});


router.get('/activities', async(req, res) => {
    console.log('/activities api called')
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


module.exports = router;