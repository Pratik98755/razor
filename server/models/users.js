const mongoose = require('mongoose')

const user_schema = mongoose.Schema({
    name: {
        type : String,
        required : true
    },
    user_id:{                      // generated using nano id
        type : String,
        required : true,
        unique : true
    },
    email: {
        type : String,
        unique : true,
        required : true
    },
    password: {
        type : String,
        required : true
    },
    role: {
        type: String,
        enum: ['BUYER', 'MERCHANT'],
        required: true
    }
}, {collection : 'users_collection', timestamps : true})

const USERS = mongoose.model('users', user_schema);

module.exports = {USERS}