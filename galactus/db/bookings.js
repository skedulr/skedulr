const mongoose = require("mongoose");

const bookingSchema = new mongoose.Schema({
  startDate: Date,
  endDate: Date,
  location: String,
  attendees: [String],
});

module.exports = mongoose.model("Booking", bookingSchema);
