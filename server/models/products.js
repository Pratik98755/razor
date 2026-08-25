const mongoose = require('mongoose')

const product_schema = mongoose.Schema({
    product_id : {
        type : String,
        unique : true,
        required : true
    },
    merchant_id : {
        type : String,
        required : true
    },
    name: {
        type: String,
        required: true,
        trim: true
    },
    description: {
        type: String,
        default: ""
    },
    price: {
        type: Number,
        required: true,
        min: 0
    },
    stock: {
        type: Number,
        required: true,
        min: 0,
        default: 0
    },
    category: {
        type: String,
        required: true
    },
    images: [
        {
            type: String
        }
    ],
}, {collection : 'products_collection', timestamps : true})

const PRODUCTS = new mongoose.model('products_collection', product_schema)

module.exports = {PRODUCTS}