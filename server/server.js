const express = require('express')
const app = express();

const mongoose = require('mongoose')



///////////////////////////////////////////////////////////////////
/// EDIT THIS AS PER YOUR REQUIREMENTS
const port = 8009;
const MONGO_DB_URL = 'mongodb://127.0.0.1:27017/razor_DB';
///////////////////////////////////////////////////////////////////




const acc_router = require('./routes/accounts');
const merchant_router = require('./routes/merchants')
const buyer_router = require('./routes/buyers')
const order_router = require('./routes/orders')

// connection to DATABASE
mongoose
    .connect(MONGO_DB_URL)
    .then(() => {
        console.log("mongodb connected !");
    })
    .catch((error) => {
        console.log("db connection error :", error);
    })
    .finally(() => {
        console.log("finally block executed");
    });


// middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: false }))


app.use('/accounts', acc_router)
app.use('/merchants', merchant_router)
app.use('/buyers', buyer_router)
app.use('/orders', order_router)


app.listen(port, () => {
    console.log(`server running at port : ${port}`)
})