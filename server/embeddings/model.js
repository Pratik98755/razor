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

    const table = await db.openTable("products");
    const query_vector = await embeddings.embedQuery(query);
    const offset = cursor ? parseInt(cursor) : 0;

    let search = table
        .search(query_vector)
        .limit(10)
        .offset(offset);

    // Hard constraints
    const filters = [];

    if (price !== undefined) {
        filters.push(`price <= ${Number(price)}`);
    }
    if (quantity !== undefined) {
        filters.push(`stock >= ${Number(quantity)}`);
    }
    if (filters.length > 0) {
        search = search.where(filters.join(" AND "));
    }

    const results = await search.toArray();
    const next_cursor = results.length === 10? String(offset + 10) : null;

    return {
        products: results,
        next_cursor
    };
}


export {
    add_product_embedding,
    edit_product_embedding,
    delete_product_embedding,
    similarity_search_products
};
