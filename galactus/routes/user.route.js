const express = require("express");
const router = express.Router();
const userController = require("../controllers/user.controller");

// returns null if logged in, or auth url otherwise
router.post("/login", userController.login);

// arguments: message, returns: parsed time, place, attendees, title,
router.post("/message", userController.onNaturalMessage);

// receive: message details, schedule a meeting, returns ok
router.post("/message-parsed", userController.onParsedMessage);

// callback from google
router.get("/post-login", userController.postLogin);

module.exports = router;
