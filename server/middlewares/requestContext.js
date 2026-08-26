
const requestContext = (req, res, next) => {

    // adds ids to unquely identify each activity 
    req.userId = req.headers["x-user-id"];  
    req.actorType = req.headers["x-actor-type"] || "USER";

    console.log('request_Context working ::: adding hedders to req')
    console.log(req.userId, req.actorType)
    next();
};

module.exports = requestContext;