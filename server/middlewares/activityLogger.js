

const { ACTIVITY } = require("../models/activity");

const activityLogger = (req, res, next) => {

    res.on("finish", async () => {

        try {

            console.log(
                "ACTIVITY LOGGER:",
                req.method,
                req.originalUrl
            );

            // No activity declared for this route
            if (!req.activity) {
                console.log("no activity found:::::::::::::::");
                return;
            }

            // Only record successful operations
            if (res.statusCode < 200 || res.statusCode >= 300) {
                return;
            }

            // Login & register
            if (req.log_or_reg == true) {

                console.log("login or register detected ::::::::::::::");

                const entry = await ACTIVITY.create({
                    IP: req.ip,
                    actor_type: req.actorType,
                    action: req.activity.action,
                    user_id: req.activity.userId
                });
                
                console.log("Activity logged : ",entry);
                return;
            }

            // Normal authenticated activity
            const entry = await ACTIVITY.create({
                user_id: req.userId,
                actor_type: req.actorType,
                action: req.activity.action,
                entity_type: req.activity.entityType,
                entity_id: req.activity.entityId
            });

            console.log("Activity logged : ", entry);

        } catch (error) {

            console.error(
                "Activity logging failed:",
                error
            );
        }
    });

    next();
};

module.exports = activityLogger;