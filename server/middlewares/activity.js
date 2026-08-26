
const activity = (action, entityType) => {

    return (req, res, next) => {
        
        console.log('activity fxn working::::::::::::')
        // adds a filed activity to the request
        req.activity = { action, entityType };
        console.log(req.activity)
        next();
    };
};

module.exports = activity;