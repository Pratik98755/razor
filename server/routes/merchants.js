const express = require('express')
const router = express.Router();

const activity = require('../middlewares/activity.js');

const { nanoid } = require('nanoid');
const { PRODUCTS } = require('../models/products');
const {ORDERS} = require('../models/orders.js')
const {USERS} = require('../models/users.js')
const {ACTIVITY} = require('../models/activity.js')


// import { add_product_embedding, edit_product_embedding, delete_product_embedding } from '../embeddings/model.js'



router.post('/add_product',activity('PRODUCT_ADDED', 'PRODUCT'), async (req, res) => {
    try {
        const data = req.body;

        const random_id = nanoid(10);

        const product = await PRODUCTS.create({
            product_id: random_id,
            merchant_id: data.merchant_id,
            name: data.name,
            price: data.price,
            stock: data.stock,
            description: data.description,
            category: data.category,
            images: data.images
        });

        // adding product_id for the middleware (activity logging)
        req.activity.entityId = random_id;

        const { add_product_embedding } = await import('../embeddings/model.js');
        await add_product_embedding(product);
        console.log(`product_created : ${product}`);

        return res.status(201).json({
            msg: 'product added!'
        });

    } catch (error) {

        console.error("ADD PRODUCT ERROR:", error);

        return res.status(500).json({
            msg: "failed to add product",
            error: error.message
        });
    }
});


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


router.patch('/edit_product',activity('PRODUCT_EDITED', 'PRODUCT'), async (req, res) => {
    const product_id = req.query.product_id;
    const product = await PRODUCTS.findOne({
        product_id: product_id
    });

    if (!product) {
        return res.sendStatus(204)
    }

     // adding product_id for the middleware (activity logging)
    req.activity.entityId = product_id;

    const updated = await PRODUCTS.findOneAndUpdate(
        { product_id: product_id },
        { $set: req.body },
        { new: true }
    );
    // edit the product embeddings
    const { edit_product_embedding} = await import('../embeddings/model.js');
    await edit_product_embedding(updated)

    console.log(`product_updated : ${updated}`)
    res.status(200).json({
        msg: 'product updated'
    });
});



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