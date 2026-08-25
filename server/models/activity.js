const mongoose = require("mongoose");

const activitySchema = new mongoose.Schema(
    {
        user_id: {
            type: String,
            required: true
        },

        role: {
            type: String,
            enum: ["BUYER", "MERCHANT"]
        },

        actor_type: {
            type: String,
            enum: ["USER", "AGENT"],
            default: "USER"
        },

        action: {
            type: String,
            required: true
        },

        entity_type: {
            type: String
        },

        entity_id: {
            type: String
        },

        metadata: {
            type: mongoose.Schema.Types.Mixed
        }
    },
    {
        collection : 'activity_collection',
        timestamps: true
    }
);

module.exports = mongoose.model("Activity", activitySchema);