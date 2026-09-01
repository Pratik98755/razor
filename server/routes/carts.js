const express = require('express')
const router = express.Router()


const crypto = require("crypto");
const { ORDERS } = require("../models/orders");
const { nanoid } = require("nanoid");
const { CARTS } = require("../models/carts");
const { PRODUCTS } = require("../models/products");


const activity = require('../middlewares/activity')

const { CHECKOUTS } = require("../models/checkouts");
const Razorpay = require("razorpay");
const razorpay = new Razorpay({
    key_id: process.env.RAZORPAY_KEY_ID,
    key_secret: process.env.RAZORPAY_KEY_SECRET
});



router.post("/add",activity('ADDED_ITEMS_IN_CART', 'ITEM'), async (req, res) => {
    try {
        const { buyer_id, product_id, quantity } = req.body;

        if (!buyer_id || !product_id || !quantity) {
            return res.status(400).json({
                msg: "buyer_id, product_id and quantity are required"
            });
        }

        if (quantity < 1) {
            return res.status(400).json({
                msg: "quantity must be at least 1"
            });
        }

        // Check product
        const product = await PRODUCTS.findOne({ product_id });

        if (!product) {
            return res.status(404).json({
                msg: "Product not found"
            });
        }

        // Check stock
        if (product.stock < quantity) {
            return res.status(400).json({
                msg: "Insufficient stock"
            });
        }

        // Find buyer's cart
        let cart = await CARTS.findOne({ buyer_id });

        // Create cart if it doesn't exist
        if (!cart) {
            cart = await CARTS.create({
                cart_id: `C-${buyer_id}`,
                buyer_id,
                items: [
                    {
                        product_id,
                        quantity
                    }
                ]
            });

            return res.status(201).json({
                msg: "Product added to cart",
                cart
            });
        }

        // Check whether product is already in cart
        const existing_item = cart.items.find(
            item => item.product_id === product_id
        );

        if (existing_item) {

            const new_quantity =
                existing_item.quantity + quantity;

            if (new_quantity > product.stock) {
                return res.status(400).json({
                    msg: `Cannot add ${quantity}. Only ${product.stock} available`
                });
            }

            existing_item.quantity = new_quantity;

        } else {
            cart.items.push({
                product_id,
                quantity
            });
        }

        await cart.save();

        /// for activity logging
        req.activity.entityId = product_id

        return res.status(200).json({
            msg: "Product added to cart",
            cart
        });

    } catch (error) {
        console.error("Add to cart error:", error);

        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});


router.get("/cart", async (req, res) => {
    try {
        const { buyer_id } = req.query;

        if (!buyer_id) {
            return res.status(400).json({
                msg: "buyer_id is required"
            });
        }

        const cart = await CARTS.findOne({ buyer_id });

        // Buyer doesn't have a cart yet
        if (!cart) {
            return res.status(200).json({
                cart: {
                    cart_id: null,
                    buyer_id,
                    items: []
                }
            });
        }

        const items = [];

        for (const item of cart.items) {

            const product = await PRODUCTS.findOne({
                product_id: item.product_id
            });

            // Product may have been deleted
            if (!product) {
                continue;
            }

            items.push({
                product_id: product.product_id,
                name: product.name,
                description: product.description,
                price: product.price,
                stock: product.stock,
                merchant_id: product.merchant_id,
                images: product.images,
                quantity: item.quantity
            });
        }

        /// for activity logging
        // req.activity.entityId = `C-${buyer_id}`

        return res.status(200).json({
            cart: {
                cart_id: cart.cart_id,
                buyer_id: cart.buyer_id,
                items
            }
        });

    } catch (error) {
        console.error("Get cart error:", error);

        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});



router.patch("/update",activity('CART_MODIFIED', 'ITEM'), async (req, res) => {
    try {
        const { buyer_id, product_id, quantity } = req.body;

        if (!buyer_id || !product_id || quantity === undefined) {
            return res.status(400).json({
                msg: "buyer_id, product_id and quantity are required"
            });
        }

        if (quantity < 1) {
            return res.status(400).json({
                msg: "quantity must be at least 1"
            });
        }

        // Find cart
        const cart = await CARTS.findOne({ buyer_id });

        if (!cart) {
            return res.status(404).json({
                msg: "Cart not found"
            });
        }

        // Find item in cart
        const item = cart.items.find(
            item => item.product_id === product_id
        );

        if (!item) {
            return res.status(404).json({
                msg: "Product not found in cart"
            });
        }

        // Get current product
        const product = await PRODUCTS.findOne({ product_id });

        if (!product) {
            return res.status(404).json({
                msg: "Product no longer exists"
            });
        }

        // Check stock
        if (quantity > product.stock) {
            return res.status(400).json({
                msg: `Only ${product.stock} units available`
            });
        }

        // Update quantity
        item.quantity = quantity;

        await cart.save();

        /// for activity logging
        req.activity.entityId = product_id

        return res.status(200).json({
            msg: "Cart updated successfully",
            cart
        });

    } catch (error) {
        console.error("Update cart error:", error);

        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});


router.delete("/remove",activity('ITEMS_REMOVED_FROM_CART', 'ITEM'), async (req, res) => {
    try {
        const { buyer_id, product_id } = req.body;

        if (!buyer_id || !product_id) {
            return res.status(400).json({
                msg: "buyer_id and product_id are required"
            });
        }

        const cart = await CARTS.findOne({ buyer_id });

        if (!cart) {
            return res.status(404).json({
                msg: "Cart not found"
            });
        }

        const item_exists = cart.items.some(
            item => item.product_id === product_id
        );

        if (!item_exists) {
            return res.status(404).json({
                msg: "Product not found in cart"
            });
        }

        cart.items = cart.items.filter(
            item => item.product_id !== product_id
        );

        await cart.save();

        /// for activity logging
        req.activity.entityId = product_id

        return res.status(200).json({
            msg: "Product removed from cart",
            cart
        });

    } catch (error) {
        console.error("Remove from cart error:", error);

        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});

router.delete("/clear",activity('CART_CLEARED', 'CART'), async (req, res) => {
    try {
        const { buyer_id } = req.body;

        if (!buyer_id) {
            return res.status(400).json({
                msg: "buyer_id is required"
            });
        }

        const cart = await CARTS.findOne({ buyer_id });

        if (!cart) {
            return res.status(404).json({
                msg: "Cart not found"
            });
        }

        cart.items = [];

        await cart.save();

        /// for activity logging
        req.activity.entityId = cart.cart_id

        return res.status(200).json({
            msg: "Cart cleared successfully",
            cart
        });

    } catch (error) {
        console.error("Clear cart error:", error);

        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});


// ###########################################################################
// ############################ CART PAYMENTS ################################
router.get("/check_checkout_status", async (req, res) => {
    try {
        console.log("/check checkout status called");

        const { razorpay_order_id } = req.query;

        if (!razorpay_order_id) {
            return res.status(400).json({
                msg: "razorpay_order_id is required"
            });
        }

        const checkout = await CHECKOUTS.findOne({
            razorpay_order_id
        });

        console.log("checkout found:", checkout);

        if (!checkout) {
            return res.status(404).json({
                msg: "checkout not found"
            });
        }

        return res.status(200).json({
            status: checkout.status
        });

    } catch (err) {
        console.error("CHECK CHECKOUT STATUS ERROR:", err);

        return res.status(500).json({
            err: "failed to check checkout status"
        });
    }
});


router.post("/checkout",activity('CART_CHECKOUT_INITIATED', 'CART'), async (req, res) => {
    try {

        const { buyer_id } = req.body;

        if (!buyer_id) {
            return res.status(400).json({
                msg: "buyer_id is required"
            });
        }

        // -----------------------------------
        // 1. Find buyer's cart
        // -----------------------------------

        const cart = await CARTS.findOne({ buyer_id });

        if (!cart || cart.items.length === 0) {
            return res.status(400).json({
                msg: "Cart is empty"
            });
        }


        // -----------------------------------
        // 2. Build checkout snapshot
        // -----------------------------------

        const checkout_items = [];

        let total_price = 0;


        for (const item of cart.items) {

            const product = await PRODUCTS.findOne({
                product_id: item.product_id
            });

            // Product deleted
            if (!product) {
                return res.status(400).json({
                    msg: `Product ${item.product_id} no longer exists`
                });
            }

            // Stock check
            if (product.stock < item.quantity) {
                return res.status(400).json({
                    msg: `Insufficient stock for ${product.name}`
                });
            }

            // Current server-side price
            const price_per_unit = product.price;

            const item_total =
                price_per_unit * item.quantity;

            checkout_items.push({
                product_id: product.product_id,
                merchant_id: product.merchant_id,
                name: product.name,
                quantity: item.quantity,
                price_per_unit,
                total_price: item_total
            });

            total_price += item_total;
        }


        // -----------------------------------
        // 3. Generate checkout ID
        // -----------------------------------
        const generated_checkout_id = nanoid(12);
        const checkout_id = generated_checkout_id


        // -----------------------------------
        // 4. Create Razorpay order
        // -----------------------------------

        const razorpay_order = await razorpay.orders.create({
            amount: total_price * 100,
            currency: "INR",
            receipt: `checkout_${checkout_id}`
        });


        console.log(
            "Cart Razorpay order created:",
            razorpay_order
        );


        // -----------------------------------
        // 5. Create CHECKOUT document
        // -----------------------------------

        const checkout = await CHECKOUTS.create({

            checkout_id,

            buyer_id,

            items: checkout_items,

            total_price,

            razorpay_order_id: razorpay_order.id,

            razorpay_status: razorpay_order.status,

            status: "PENDING_PAYMENT"

        });


        console.log(
            "CHECKOUT CREATED:",
            checkout
        );


        // -----------------------------------
        // 6. Return payment information
        // -----------------------------------

        /// for activity logging
        req.activity.entityId = `C-${buyer_id}`

        return res.status(201).json({

            msg: "Cart checkout created successfully",
            checkout_id: checkout.checkout_id,
            razorpay_order_id: razorpay_order.id,
            amount: razorpay_order.amount,
            currency: razorpay_order.currency,
            key_id: process.env.RAZORPAY_KEY_ID

        });


    } catch (err) {

        console.error(
            "CART CHECKOUT ERROR:",
            err
        );

        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});


router.post("/verify_payment",activity('CART_PAYMENT_CONFIRMED', 'CART'), async (req, res) => {
    try {
        const {
            razorpay_payment_id,
            razorpay_order_id,
            razorpay_signature
        } = req.body;

        // -----------------------------------
        // 1. Validate payment data
        // -----------------------------------

        if (
            !razorpay_payment_id ||
            !razorpay_order_id ||
            !razorpay_signature
        ) {
            return res.status(400).json({
                msg: "Missing payment verification details"
            });
        }

        // -----------------------------------
        // 2. Verify Razorpay signature
        // -----------------------------------

        const generated_signature = crypto
            .createHmac(
                "sha256",
                process.env.RAZORPAY_KEY_SECRET
            )
            .update(
                razorpay_order_id +
                "|" +
                razorpay_payment_id
            )
            .digest("hex");

        if (generated_signature !== razorpay_signature) {
            return res.status(400).json({
                msg: "Payment verification failed"
            });
        }

        // -----------------------------------
        // 3. Find checkout
        // -----------------------------------

        const checkout = await CHECKOUTS.findOne({
            razorpay_order_id
        });

        if (!checkout) {
            return res.status(404).json({
                msg: "Checkout not found"
            });
        }

        // -----------------------------------
        // 4. Prevent duplicate verification
        // -----------------------------------

        if (checkout.status === "CONFIRMED") {
            return res.status(400).json({
                msg: "Checkout is already confirmed"
            });
        }

        // -----------------------------------
        // 5. Pre-check ALL products
        // -----------------------------------

        const products = [];

        for (const item of checkout.items) {

            const product = await PRODUCTS.findOne({
                product_id: item.product_id
            });

            if (!product) {
                return res.status(400).json({
                    msg: `Product ${item.product_id} no longer exists`
                });
            }

            if (product.stock < item.quantity) {
                return res.status(400).json({
                    msg: `Insufficient stock for ${product.name}`
                });
            }

            products.push({
                product,
                item
            });
        }

        // -----------------------------------
        // 6. Atomically decrease stock
        // -----------------------------------

        const updated_products = [];

        for (const { product, item } of products) {

            const updated_product =
                await PRODUCTS.findOneAndUpdate(
                    {
                        product_id: item.product_id,
                        stock: {
                            $gte: item.quantity
                        }
                    },
                    {
                        $inc: {
                            stock: -item.quantity
                        }
                    },
                    {
                        new: true
                    }
                );

            if (!updated_product) {

                // Something changed between
                // pre-check and atomic update.

                // Restore previously updated stocks
                for (const updated of updated_products) {

                    await PRODUCTS.updateOne(
                        {
                            product_id: updated.product_id
                        },
                        {
                            $inc: {
                                stock: updated.quantity
                            }
                        }
                    );

                }

                return res.status(409).json({
                    msg: `Stock changed while processing ${item.product_id}. Please retry checkout.`
                });
            }

            updated_products.push({
                product_id: item.product_id,
                quantity: item.quantity
            });
        }

        // -----------------------------------
        // 7. Create ORDERS
        // -----------------------------------

        const created_orders = [];

        try {

            for (const { item } of products) {

                const generated_order_id = nanoid(12);

                const order = await ORDERS.create({

                    order_id: generated_order_id,

                    buyer_id: checkout.buyer_id,

                    product_id: item.product_id,

                    merchant_id: item.merchant_id,

                    quantity: item.quantity,

                    price_per_unit: item.price_per_unit,

                    total_price: item.total_price,

                    razorpay_order_id:
                        checkout.razorpay_order_id,

                    razorpay_payment_id:
                        razorpay_payment_id,

                    razorpay_signature:
                        razorpay_signature,

                    razorpay_status: "paid",

                    status: "CONFIRMED"

                });

                created_orders.push(order);
            }

        } catch (order_error) {

            console.error(
                "ORDER CREATION FAILED:",
                order_error
            );

            // Restore stock
            for (const updated of updated_products) {

                await PRODUCTS.updateOne(
                    {
                        product_id:
                            updated.product_id
                    },
                    {
                        $inc: {
                            stock: updated.quantity
                        }
                    }
                );
            }

            return res.status(500).json({
                msg: "Order creation failed. Stock restored."
            });
        }

        // -----------------------------------
        // 8. Mark checkout confirmed
        // -----------------------------------

        checkout.razorpay_payment_id =
            razorpay_payment_id;

        checkout.razorpay_signature =
            razorpay_signature;

        checkout.razorpay_status =
            "paid";

        checkout.status =
            "CONFIRMED";

        await checkout.save();

        // -----------------------------------
        // 9. Clear cart
        // -----------------------------------

        await CARTS.updateOne(
            {
                buyer_id: checkout.buyer_id
            },
            {
                $set: {
                    items: []
                }
            }
        );

        // -----------------------------------
        // 10. Response
        // -----------------------------------

        /// for activity logging
        req.activity.entityId = `C-${checkout.buyer_id}`

        return res.status(200).json({

            msg: "Cart payment verified successfully",

            checkout_id:
                checkout.checkout_id,

            orders: created_orders.map(order => ({
                order_id: order.order_id,
                product_id: order.product_id,
                merchant_id: order.merchant_id,
                quantity: order.quantity,
                total_price: order.total_price,
                status: order.status
            }))

        });

    } catch (err) {

        console.error(
            "CART PAYMENT VERIFICATION ERROR:",
            err
        );

        return res.status(500).json({
            msg: "Internal server error"
        });
    }
});

router.post("/cancel_checkout", activity("CHECKOUT_CANCELLED", "RAZORPAY_ORDER_ID"), async (req, res) => {
        try {
            console.log("/cancel_checkout called");
            const { razorpay_order_id } = req.body;
            if (!razorpay_order_id) {
                return res.status(400).json({
                    msg: "razorpay_order_id is required"
                });
            }

            const checkout = await CHECKOUTS.findOneAndUpdate(
                {
                    razorpay_order_id,
                    status: "PENDING_PAYMENT"
                },
                {
                    $set: {
                        status: "CANCELLED"
                    }
                },
                {
                    new: true
                }
            );

            if (!checkout) {
                return res.status(400).json({
                    msg: "Checkout not found or already completed"
                });
            }

            /// for activity logging
            req.activity.entityId = razorpay_order_id

            console.log("CHECKOUT CANCELLED:",razorpay_order_id);
            return res.status(200).json({
                status: "done",
                checkout_id: checkout.checkout_id
            });

        } catch (error) {
            console.error(
                "CANCEL CHECKOUT ERROR:",
                error
            );
            return res.status(500).json({
                status: "err"
            });
        }
    }
);


router.post("/checkout_payment_failure", activity("CHECKOUT_PAYMENT_FAILURE", "RAZORPAY_ORDER_ID"), async (req, res) => {
        try {
            console.log("/checkout_payment_failure called");
            const { razorpay_order_id } = req.body;
            if (!razorpay_order_id) {
                return res.status(400).json({
                    msg: "razorpay_order_id is required"
                });
            }

            const checkout = await CHECKOUTS.findOneAndUpdate(
                {
                    razorpay_order_id,
                    status: "PENDING_PAYMENT"
                },
                {
                    $set: {
                        status: "FAILED"
                    }
                },
                {
                    new: true
                }
            );

            if (!checkout) {
                return res.status(400).json({
                    msg: "Checkout not found or already completed"
                });
            }

            /// for activity logging
            req.activity.entityId = razorpay_order_id

            console.log("CHECKOUT PAYMENT FAILURE:",razorpay_order_id);
            return res.status(200).json({
                status: "done",
                checkout_id: checkout.checkout_id
            });

        } catch (error) {
            console.error(
                "/checkout_payment_failure API error:",
                error
            );
            return res.status(500).json({
                status: "err"
            });
        }
    }
);




module.exports = router;