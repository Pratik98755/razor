import "dotenv/config";

import { GoogleGenerativeAIEmbeddings } from "@langchain/google-genai";
import * as lancedb from "@lancedb/lancedb";


const embeddings = new GoogleGenerativeAIEmbeddings({
    model: "gemini-embedding-2"
});

const db = await lancedb.connect("../VECTOR_DBS/product_DB");


// SUPPORTING FXNS

// adding product embeddings for new products
async function add_product_embedding(product) {

    const vector = await embeddings.embedQuery(`
        ${product.name}.
        ${product.description}.
        Category: ${product.category}
    `);

    const data = {
        product_id: product.product_id,
        name: product.name,
        merchant_id: product.merchant_id,
        description: product.description,
        images: product.images || [],
        price: product.price,
        stock: product.stock,
        category: product.category,
        vector
    };

    const tables = await db.tableNames();

    if (!tables.includes("products")) {

        // First product → LanceDB creates the schema automatically
        await db.createTable("products", [data]);

    } else {

        const table = await db.openTable("products");
        await table.add([data]);

    }

    console.log("product embedding added to db");
}






// delete product embedding
async function delete_product_embedding(product_id) {
    const products_table = await db.openTable("products");
    await products_table.delete(
        `product_id = '${product_id}'`
    );
}


// edit product embedding
async function edit_product_embedding(product) {

    const products_table = await db.openTable("products");
    const vector = await embeddings.embedQuery(`
        ${product.name}.
        ${product.description}.
        Category: ${product.category}
    `);

    await products_table.update({
        where: `product_id = '${product.product_id}'`,

        values: {
            name: product.name,
            merchant_id: product.merchant_id,
            description: product.description,
            images: product.images || [],
            price: product.price,
            stock: product.stock,
            category: product.category,
            vector
        }
    });
}




// similarity search for products
async function similarity_search_products(query, price, quantity, cursor) {
    const { PRODUCTS } = await import('../models/products.js');

    try {
        const table = await db.openTable("products");

        const query_vector = await embeddings.embedQuery(query);

        const offset = cursor ? parseInt(cursor) : 0;

        // LanceDB semantic search only
        const results = await table
            .search(query_vector)
            .limit(10)
            .offset(offset)
            .toArray();

        if (results.length === 0) {
            return {
                products: [],
                next_cursor: null
            };
        }

        const productIds = results.map(
            product => product.product_id
        );

        console.log("PRODUCT IDS:", productIds);

        // MongoDB = source of truth
        const mongoProducts = await PRODUCTS.find({
            product_id: { $in: productIds }
        }).lean();

        console.log("MONGO PRODUCTS:", mongoProducts);

        const productMap = new Map(
            mongoProducts.map(product => [
                product.product_id,
                product
            ])
        );

        let products = results
            .map(match => {
                const product = productMap.get(match.product_id);

                if (!product) {
                    return null;
                }

                return {
                    ...product,
                    _distance: match._distance
                };
            })
            .filter(Boolean);

        if (price !== undefined) {
            products = products.filter(
                product => product.price <= Number(price)
            );
        }

        if (quantity !== undefined) {
            products = products.filter(
                product => product.stock >= Number(quantity)
            );
        }

        const next_cursor =
            results.length === 10
                ? String(offset + 10)
                : null;

        return {
            products,
            next_cursor
        };

    } catch (err) {
        console.error(
            "SIMILARITY SEARCH ERROR:",
            err
        );

        throw err;
    }
}


// async function similarity_search_products(query, price, quantity, cursor) {
//     const {PRODUCTS} = await import('../models/products.js')
//     try {

//         const table = await db.openTable("products");

//         const query_vector = await embeddings.embedQuery(query);

//         const offset = cursor ? parseInt(cursor) : 0;

//         // LanceDB semantic search only
//         const results = await table
//             .search(query_vector)
//             .limit(10)
//             .offset(offset)
//             .toArray();

//         // console.log("LANCE RESULTS:", results);

//         if (results.length === 0) {
//             return {
//                 products: [],
//                 next_cursor: null
//             };
//         }

//         const productIds = results.map(
//             product => product.product_id
//         );

//         console.log("PRODUCT IDS:", productIds);

//         // MongoDB = source of truth
//         const mongoProducts = await PRODUCTS.find({
//             product_id: { $in: productIds }
//         }).lean();

//         console.log("MONGO PRODUCTS:", mongoProducts);

//         const productMap = new Map(
//             mongoProducts.map(product => [
//                 product.product_id,
//                 product
//             ])
//         );


//         let products = results
//             .map(match => {

//                 const product = productMap.get(match.product_id);

//                 if (!product) {
//                     return null;
//                 }

//                 const match_percentage = Math.max(
//                     0,
//                     Math.min(
//                         100,
//                         (1 - match._distance) * 100
//                     )
//                 );

//                 return {
//                     ...product,
//                     match_percentage: `${Math.round(match_percentage)}%`
//                 };
//             })
//             .filter(Boolean);

//         if (price !== undefined) {
//             products = products.filter(
//                 product => product.price <= Number(price)
//             );
//         }

//         if (quantity !== undefined) {
//             products = products.filter(
//                 product => product.stock >= Number(quantity)
//             );
//         }

//         const next_cursor =
//             results.length === 10
//                 ? String(offset + 10)
//                 : null;

//         return {
//             products,
//             next_cursor
//         };

//     } catch (err) {

//         console.error(
//             "SIMILARITY SEARCH ERROR:",
//             err
//         );

//         throw err;
//     }
// }






export {
    add_product_embedding,
    edit_product_embedding,
    delete_product_embedding,
    similarity_search_products
};
