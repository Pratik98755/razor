import "dotenv/config";

import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { z } from "zod";


// --------------------------------------------------
// LLM
// --------------------------------------------------

const llm = new ChatGoogleGenerativeAI({
    model: "gemini-3.5-flash-lite",
    temperature: 0
});


// --------------------------------------------------
// STRUCTURED OUTPUT SCHEMA
// --------------------------------------------------

const product_metadata_schema = z.object({

    product_type: z
        .string()
        .describe(
            "Specific type of product, such as laptop, wireless_mouse, laptop_bag, phone_case."
        ),

    product_role: z
        .enum([
            "primary_product",
            "accessory",
            "replacement",
            "consumable",
            "component",
            "service",
            "bundle"
        ])
        .describe(
            "The role this product normally plays in a purchase."
        ),

    use_contexts: z
        .array(z.string())
        .describe(
            "Products, activities, environments, or use cases this product is commonly associated with."
        ),

    attributes: z
        .array(
            z.object({
                key: z
                    .string()
                    .describe("Name of the product attribute."),

                value: z
                    .string()
                    .describe("Factual value of the attribute.")
            })
        )
        .describe(
            "Useful factual attributes explicitly available from the product information. Do not invent values."
        )

});


// --------------------------------------------------
// STRUCTURED LLM
// --------------------------------------------------

const structured_llm = llm.withStructuredOutput(
    product_metadata_schema
);


// --------------------------------------------------
// GENERATE PRODUCT METADATA
// --------------------------------------------------

async function generate_product_metadata(product) {

    try {
        const prompt = `
            You are a product understanding system for an e-commerce platform.

            Analyze the following product and generate structured semantic metadata.

            PRODUCT:

            Name:
            ${product.name || ""}

            Description:
            ${product.description || ""}

            Category:
            ${product.category || ""}


            RULES:

            1. Determine the most specific reasonable product_type.

            2. Determine the product_role using ONLY one of:
            - primary_product
            - accessory
            - replacement
            - consumable
            - component
            - service
            - bundle

            3. use_contexts should describe what products, activities,
            environments, or use cases this product is associated with.

            4. attributes should contain useful factual information that
            can help understand or compare the product.

            5. NEVER invent specifications or facts that are not present
            in the provided product information.

            6. Do not use marketing terms such as:
            "best", "premium", "high-quality", "affordable", etc.

            7. Keep the metadata concise and useful for semantic product
            retrieval and future cross-selling.

            8. Do not explain your answer. Return only the structured output.
            `;

        const metadata = await structured_llm.invoke(prompt);

        return metadata;

    } catch (error) {

        console.error(
            "PRODUCT METADATA GENERATION ERROR:",
            error
        );

        throw error;
    }
}


export {
    generate_product_metadata
};