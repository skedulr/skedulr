const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  name: String,
  org: String,
  uids: [[String]],
  email: String,
});

module.exports = mongoose.model("User", userSchema);
