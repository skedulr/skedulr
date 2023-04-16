const mongoose = require("mongoose");

const orgSchema = new mongoose.Schema({
  domain: String,
  members: [
    {
      name: String,
      email: String,
    },
  ],
});

module.exports = mongoose.model("Organisation", orgSchema);
