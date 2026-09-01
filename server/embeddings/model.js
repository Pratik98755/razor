import "dotenv/config";

import { GoogleGenerativeAIEmbeddings } from "@langchain/google-genai";
import * as lancedb from "@lancedb/lancedb";


const embeddings = new GoogleGenerativeAIEmbeddings({
    model: "gemini-embedding-2"
});

const db = await lancedb.connect("../VECTOR_DBS/product_DB");


// --------------------------------------------------
// SUPPORTING FUNCTION
// Build the text that represents a product
// --------------------------------------------------

function build_product_embedding_text(product) {

    const metadata = product.metadata || {};

    const attributes = metadata.attributes || {};

    return `
        Product Name: ${product.name || ""}
        Description: ${product.description || ""}
        Category: ${product.category || ""}
        Product Type: ${metadata.product_type || ""}
        Product Role: ${metadata.product_role || ""}
        Use Contexts: ${(metadata.use_contexts || []).join(", ")}

        Attributes:
        ${Object.entries(attributes)
            .map(([key, value]) => `${key}: ${value}`)
            .join(", ")}
    `.trim();
}


// --------------------------------------------------
// ADD PRODUCT EMBEDDING
// --------------------------------------------------

async function add_product_embedding(product) {

    const embedding_text = build_product_embedding_text(product);

    const vector = await embeddings.embedQuery(
        embedding_text
    );

    const data = {
        product_id: product.product_id,
        name: product.name,
        merchant_id: product.merchant_id,
        category: product.category,
        vector
    };

    const tables = await db.tableNames();

    if (!tables.includes("products")) {

        // First product → LanceDB creates schema automatically
        await db.createTable("products", [data]);

    } else {

        const table = await db.openTable("products");

        await table.add([data]);
    }

    console.log("product embedding added to db");
}


// --------------------------------------------------
// DELETE PRODUCT EMBEDDING
// --------------------------------------------------

async function delete_product_embedding(product_id) {

    const products_table = await db.openTable("products");

    await products_table.delete(
        `product_id = '${product_id}'`
    );

    console.log("product embedding deleted from db");
}


// --------------------------------------------------
// EDIT PRODUCT EMBEDDING
// --------------------------------------------------

async function edit_product_embedding(product) {

    const products_table = await db.openTable("products");

    const embedding_text = build_product_embedding_text(product);

    const vector = await embeddings.embedQuery(
        embedding_text
    );

    await products_table.update({

        where: `product_id = '${product.product_id}'`,

        values: {
            name: product.name,
            merchant_id: product.merchant_id,
            category: product.category,
            vector
        }
    });

    console.log("product embedding updated in db");
}


// --------------------------------------------------
// SIMILARITY SEARCH FOR PRODUCTS
// --------------------------------------------------

async function similarity_search_products(
    query,
    price,
    quantity,
    cursor
) {

    const { PRODUCTS } = await import("../models/products.js");

    try {

        const table = await db.openTable("products");

        const query_vector = await embeddings.embedQuery(query);

        const offset = cursor
            ? parseInt(cursor)
            : 0;


        // LanceDB semantic search
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


        // Extract product IDs
        const productIds = results.map(
            product => product.product_id
        );

        console.log(
            "PRODUCT IDS:",
            productIds
        );


        // MongoDB = source of truth
        const mongoProducts = await PRODUCTS.find({

            product_id: {
                $in: productIds
            }

        }).lean();


        console.log(
            "MONGO PRODUCTS:",
            mongoProducts
        );


        // Map MongoDB products by product_id
        const productMap = new Map(

            mongoProducts.map(product => [
                product.product_id,
                product
            ])

        );


        // Preserve LanceDB similarity ordering
        let products = results

            .map(match => {

                const product = productMap.get(
                    match.product_id
                );

                if (!product) {
                    return null;
                }

                return {
                    ...product,
                    _distance: match._distance
                };

            })

            .filter(Boolean);


        // Price filter
        if (price !== undefined) {

            products = products.filter(

                product =>
                    product.price <= Number(price)

            );
        }


        // Quantity / stock filter
        if (quantity !== undefined) {

            products = products.filter(

                product =>
                    product.stock >= Number(quantity)

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



async function get_similar_products_using_prestored_vector(product_id) {

    try {
        const table = await db.openTable("products");

        // Get the actual stored vector of the anchor
        const anchor = await table
            .query()
            .where(`product_id = '${product_id}'`)
            .limit(1)
            .toArray();

        if (anchor.length === 0) {
            return [];
        }

        const anchor_vector = anchor[0].vector;

        // Search LanceDB using the anchor's actual vector
        const results = await table
            .search(anchor_vector)
            .limit(20)
            .toArray();

        return results;

    } catch (error) {

        console.error(
            "GET SIMILAR PRODUCTS ERROR:",
            error
        );

        throw error;
    }
}



export {
    add_product_embedding,
    edit_product_embedding,
    delete_product_embedding,
    similarity_search_products,
    get_similar_products_using_prestored_vector
};