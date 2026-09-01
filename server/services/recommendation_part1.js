const { PRODUCTS } = require('../models/products.js');


// --------------------------------------------------
// PHASE 4
// Ranking helpers
// --------------------------------------------------

function calculate_vector_similarity(distance) {
    if (distance === undefined || distance === null) {
        return 0;
    }
    return 1 / (1 + Number(distance));
}


function calculate_price_score(anchor, candidate) {
    if (!anchor?.price || anchor.price <= 0) {
        return 0;
    }
    if (!candidate?.price || candidate.price < 0) {
        return 0;
    }
    const ratio = candidate.price / anchor.price;

    // Cross-sell products should normally be
    // substantially cheaper than the main product.

    if (ratio <= 0.05) {
        return 1.0;
    }
    if (ratio <= 0.10) {
        return 0.9;
    }
    if (ratio <= 0.20) {
        return 0.75;
    }
    if (ratio <= 0.30) {
        return 0.50;
    }
    if (ratio <= 0.50) {
        return 0.25;
    }
    return 0.05;
}


function calculate_final_score(candidate, anchor) {
    const complementarity = candidate.complementarity;

    const vector_similarity = calculate_vector_similarity(candidate.similarity);
    const price_score = calculate_price_score(anchor, candidate.product);
    const final_score =
          (0.50 * complementarity)
        + (0.30 * vector_similarity)
        + (0.20 * price_score);

    return {
        ...candidate,
        vector_similarity,
        price_score,
        final_score
    };
}

// --------------------------------------------------
// PHASE 2
// Get cross-sell candidates for cart
// --------------------------------------------------

async function get_cross_sell_candidates(cart) {
    try {
        // --------------------------------------------
        // Get product IDs from cart
        // --------------------------------------------

        const cartProductIds = cart.items.map(
            item => item.product_id
        );
        if (cartProductIds.length === 0) {
            return [];
        }

        // --------------------------------------------
        // Get cart products
        // MongoDB = source of truth
        // --------------------------------------------

        const cartProducts = await PRODUCTS.find({
            product_id: {
                $in: cartProductIds
            }
        }).lean();


        // --------------------------------------------
        // Find anchor products
        // --------------------------------------------

        const anchors = cartProducts.filter(
            product =>
                product.metadata?.product_role ===
                "primary_product"
        );

        // --------------------------------------------
        // No anchor → no recommendation
        // --------------------------------------------

        if (anchors.length === 0) {
            return [];
        }

        // --------------------------------------------
        // Get LanceDB similarity function
        // --------------------------------------------

        const { get_similar_products_using_prestored_vector } = await import('../embeddings/model.js');
        const candidates = [];

        // --------------------------------------------
        // Search for each anchor
        // --------------------------------------------

        for (const anchor of anchors) {
            const similarProducts = await get_similar_products_using_prestored_vector(anchor.product_id);


            for (const candidate of similarProducts) {

                // ------------------------------------
                // ❌ Same product as anchor
                // ------------------------------------

                if (
                    candidate.product_id ===
                    anchor.product_id
                ) {
                    continue;
                }


                // ------------------------------------
                // ❌ Already in cart
                // ------------------------------------

                if (
                    cartProductIds.includes(
                        candidate.product_id
                    )
                ) {
                    continue;
                }


                // ------------------------------------
                // ❌ Out of stock
                // ------------------------------------

                // We need MongoDB data for this.
                // Don't rely on LanceDB stock.

                candidates.push({
                    anchor_product_id: anchor.product_id,
                    candidate_product_id: candidate.product_id,
                    similarity: candidate._distance
                });

            }

        }


        // --------------------------------------------
        // Get candidate details from MongoDB
        // --------------------------------------------

        const candidateIds = [
            ...new Set(
                candidates.map(
                    item => item.candidate_product_id
                )
            )
        ];


        if (candidateIds.length === 0) {
            return [];
        }


        const mongoCandidates = await PRODUCTS.find({
                product_id: {
                    $in: candidateIds
                }
            }).lean();


        const candidateMap = new Map(
            mongoCandidates.map(
                product => [
                    product.product_id,
                    product
                ]
            )
        );

        // --------------------------------------------
        // Apply MongoDB-based filters
        // --------------------------------------------

        const filteredCandidates =
            candidates.filter(item => {

                const product =
                    candidateMap.get(
                        item.candidate_product_id
                    );


                if (!product) {
                    return false;
                }

                // ❌ stock <= 0
                if (product.stock <= 0) {
                    return false;
                }
                const anchor = cartProducts.find(
                        p =>
                            p.product_id ===
                            item.anchor_product_id
                    );


                // ❌ same product_type
                if (
                    product.metadata?.product_type ===
                    anchor?.metadata?.product_type
                ) {
                    return false;
                }

                return true;
            });
        

        // --------------------------------------------------
        // PHASE 3
        // Classify candidate relationships
        // --------------------------------------------------

        const {classify_complementarity} = await import('../structured_ai/product_classifier.js');

        const complementaryCandidates = [];

        for (const item of filteredCandidates) {

            const anchor = cartProducts.find(
                product =>
                    product.product_id ===
                    item.anchor_product_id
            );

            const candidate = candidateMap.get(
                item.candidate_product_id
            );

            if (!anchor || !candidate) {
                continue;
            }

            const classification = await classify_complementarity(anchor, candidate);

            console.log(`${anchor.name} → ${candidate.name}`, classification);

            // Keep only genuine complementary products
            if (
                classification.classification ===
                    "COMPLEMENTARY" &&
                classification.confidence >= 0.80
            ) {

                complementaryCandidates.push({
                    anchor_product_id: anchor.product_id,
                    product: candidate,
                    similarity: item.similarity,
                    complementarity: classification.confidence
                });
            }
        }

        // --------------------------------------------------
        // PHASE 4
        // Rank complementary candidates
        // --------------------------------------------------

        const rankedCandidates = complementaryCandidates.map(
            candidate => {
                const anchor = cartProducts.find(
                    product =>
                        product.product_id ===
                        candidate.anchor_product_id
                );

                return calculate_final_score(
                    candidate,
                    anchor
                );
            }
        );


        // --------------------------------------------------
        // Sort highest score first
        // --------------------------------------------------

        rankedCandidates.sort(
            (a, b) =>
                b.final_score - a.final_score
        );


        // --------------------------------------------------
        // MVP: return top 2
        // --------------------------------------------------

        return rankedCandidates.slice(0, 2);


    } catch (error) {

        console.error(
            "CROSS SELL CANDIDATE ERROR:",
            error
        );

        throw error;
    }
}


module.exports = {
    get_cross_sell_candidates
};