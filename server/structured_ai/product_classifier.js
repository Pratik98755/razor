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

const complementarity_schema = z.object({

    classification: z
        .enum([
            "COMPLEMENTARY",
            "ALTERNATIVE",
            "UNRELATED"
        ])
        .describe(
            "Relationship between the anchor product and candidate product."
        ),

    confidence: z
        .number()
        .min(0)
        .max(1)
        .describe(
            "Confidence in the classification, from 0 to 1."
        )

});


// --------------------------------------------------
// STRUCTURED LLM
// --------------------------------------------------

const structured_llm = llm.withStructuredOutput(
        complementarity_schema
    );


// --------------------------------------------------
// CLASSIFY PRODUCT RELATIONSHIP
// --------------------------------------------------

async function classify_complementarity(anchor, candidate){
    try {
        const prompt = `
            You are a product relationship classifier
            for an e-commerce recommendation system.

            Determine the relationship between the ANCHOR
            product and the CANDIDATE product.

            ANCHOR PRODUCT:

            Name:
            ${anchor.name || ""}

            Description:
            ${anchor.description || ""}

            Category:
            ${anchor.category || ""}

            Product type:
            ${anchor.metadata?.product_type || ""}

            Product role:
            ${anchor.metadata?.product_role || ""}

            Use contexts:
            ${JSON.stringify(anchor.metadata?.use_contexts || [])}

            Attributes:
            ${JSON.stringify(anchor.metadata?.attributes || [])}


            CANDIDATE PRODUCT:

            Name:
            ${candidate.name || ""}

            Description:
            ${candidate.description || ""}

            Category:
            ${candidate.category || ""}

            Product type:
            ${candidate.metadata?.product_type || ""}

            Product role:
            ${candidate.metadata?.product_role || ""}

            Use contexts:
            ${JSON.stringify(candidate.metadata?.use_contexts || [])}

            Attributes:
            ${JSON.stringify(candidate.metadata?.attributes || [])}


            CLASSIFICATION RULES:

            1. COMPLEMENTARY:
            The candidate is normally purchased or used
            together with the anchor and adds functionality,
            convenience, protection, maintenance, or support.

            Example:
            Laptop → Laptop Bag
            Laptop → Mouse
            Camera → Memory Card


            2. ALTERNATIVE:
            The candidate serves essentially the same
            primary purpose as the anchor and could replace
            or substitute for it.

            Example:
            MacBook Air → Dell Laptop
            iPhone → Samsung Phone


            3. UNRELATED:
            The candidate has no meaningful purchasing or
            usage relationship with the anchor.

            Example:
            Laptop → Flower Bouquet


            IMPORTANT:

            - Do not classify something as complementary merely
            because the products are semantically similar.
            - Focus on whether they are naturally used or
            purchased together.
            - Do not invent compatibility or product facts.
            - Return only the structured classification and confidence.

            `;

        const result =
            await structured_llm.invoke(prompt);

        return result;

    } catch (error) {

        console.error(
            "COMPLEMENTARITY CLASSIFICATION ERROR:",
            error
        );

        throw error;
    }
}


export {
    classify_complementarity
};