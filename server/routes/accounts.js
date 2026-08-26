const express = require('express')
const router = express.Router();

const activity = require('../middlewares/activity')

const { USERS } = require('../models/users')
const {nanoid} = require('nanoid')

router.post('/register', activity('USER_REGISTERED', 'USER'), async (req, res) => {
    const data = req.body;
    // console.log(data)
    const random_id = nanoid(8);
    const entry = await USERS.create({
        name: data.name,
        user_id : random_id,
        email: data.email,
        password: data.password,
        role: data.role
    })

    // for the activity logging
    req.activity.userId = random_id
    req.log_or_reg = true

    console.log(`user registered : ${entry}`)

    return res.status(201).json({
        'msg': 'registration successful !'
    })
})

router.post('/login',activity('USER_LOGIN', 'USER'), async (req, res) => {
    const data = req.body;
    // console.log(data)
    const user = await USERS.findOne({
        email: data.email,
        password: data.password
    })

    if (!user) {
        res.status(401).json({
            'msg': "invalid credentials !"
        })
    } else {

        // for the activity logging
        req.activity.userId =  user.user_id;
        req.log_or_reg = true
        
        return res.status(200).json({
            'msg': 'login successful !',
            'user': user.name,
            'user_id' : user.user_id,
            'role': user.role
        })
    }
})

module.exports = router