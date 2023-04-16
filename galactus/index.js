require("dotenv").config();
const express = require("express");
const logger = require("morgan");
const app = express();
const PORT = process.env.PORT || 3001;
const mongoose = require("mongoose");

app.use(logger("dev"));
app.use(express.json());

app.get("/", (req, res) => {
  res.send("<h1>Who lives in a pineapple under the sea?</h1>");
});

app.use("/user", require("./routes/user.route"));

/* Error handler middleware */
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  console.error(err.message, err.stack);
  return res.status(statusCode).json({ message: err.message });
});

const init = async () => {
  console.log("init");
  const connectionString = process.env.MONGO_URI || "";

  await mongoose.connect(connectionString, {
    dbName: process.env.DB_NAME,
  });

  // start the Express server
  app.listen(PORT, "0.0.0.0", 511, () => {
    console.log(`Server is running on port: ${PORT}`);
  });
};

init();
