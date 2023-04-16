const { google } = require("googleapis");
const CLIENT = require("../client_secret.json");
const Org = require("../db/organisations");
const User = require("../db/users");
const Booking = require("../db/bookings");
const axios = require("axios");

async function login(req, res) {
  const existingUser = await User.findOne({ uids: [req.body.platform, `${req.body.uid}`] });
  if (existingUser) {
    return res.json({ loggedIn: true });
  }

  const oauth2Client = new google.auth.OAuth2(
    CLIENT.web.client_id,
    CLIENT.web.client_secret,
    new URL("/user/post-login", process.env.HOST).toString()
  );

  const scopes = [
    // "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/directory.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
  ];

  // Generate a url that asks permissions
  const authorizationUrl = oauth2Client.generateAuthUrl({
    // 'online' (default) or 'offline' (gets refresh_token)
    access_type: "offline",
    scope: scopes,
    include_granted_scopes: true,
    state: `${req.body.platform}|${req.body.uid}`,
  });

  return res.json({ authorizationUrl });
}

// called by google postauth
async function postLogin(req, res) {
  if (!req.query.code) {
    return res.status(500).send("<h1>Login Failed:(</h1>");
  }

  const oauth2Client = new google.auth.OAuth2(
    CLIENT.web.client_id,
    CLIENT.web.client_secret,
    new URL("/user/post-login", process.env.HOST).toString()
  );

  let { tokens } = await oauth2Client.getToken(req.query.code);
  oauth2Client.setCredentials(tokens);

  const userInfo = await google.oauth2("v2").userinfo.get({ auth: oauth2Client });

  const platform = req.query.state.split("|").map((k) => `${k}`);

  const domain = userInfo.data.hd;

  //if org already exists
  const existingOrg = await Org.findOne({ domain });
  if (!existingOrg) {
    // Call the people.connections.list method with the resourceName parameter set to 'people/me'
    const peopleRes = await google.people("v1").people.listDirectoryPeople({
      auth: oauth2Client,
      // pageToken: null,
      sources: ["DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE", "DIRECTORY_SOURCE_TYPE_DOMAIN_CONTACT"],
      pageSize: 20,
      readMask: "emailAddresses,names,locations",
    });

    const directoryPeople = peopleRes.data.people.map((user) => ({
      name: user.names?.[0].displayName,
      email: user.emailAddresses?.[0].value,
      location: user.locations?.[0].value,
    }));
    console.log(directoryPeople);
    await new Org({ domain, members: directoryPeople }).save();
  }

  let user = await User.findOne({ email: userInfo.data.email });

  if (!user) {
    user = new User({ name: userInfo.data.name, email: userInfo.data.email, org: domain, uids: platform });
  } else {
    user.uids = [...user.uids, platform];
  }

  await user.save();

  return res.send("<h1>Login Successful:)</h1><p>You may close this page.</p>");
}

async function onNaturalMessage(req, res) {
  const platform = [req.body.platform, `${req.body.uid}`];
  const user = await User.findOne({ uids: platform });

  const orgMembers = (await Org.findOne({ domain: user.org })).members;

  try {
    const respon = await axios.post(new URL("/parse", process.env.ML_BACKEND).toString(), {
      message: req.body.message,
      contact_list: orgMembers,
    });
    return res.json(respon.data);
  } catch (err) {
    console.log("Joel: " + err.message);
    return res.status(500).json({ message: err.message });
  }
}

async function onParsedMessage(req, res) {
  const { attendees, start_date: startDate, end_date: endDate, location } = req.body;

  // check for location time clash
  let overlap = await Booking.find({ location, startDate: { $lt: endDate }, endDate: { $gt: startDate } });
  if (overlap.length) {
    return res.status(401).json({ message: "location-clash" });
  }

  // check for user time clash
  // check for location time clash
  for (const atten of attendees) {
    let overlap = await Booking.find({
      attendees: atten.email,
      startDate: { $lt: endDate },
      endDate: { $gt: startDate },
    });
    if (overlap.length) {
      return res.status(401).json({ message: "user-clash" });
    }
  }

  await new Booking({
    startDate: new Date(startDate),
    endDate: new Date(endDate),
    location,
    attendees: attendees.map(({ email }) => email),
  }).save();

  const author = await User.findOne({ uids: [req.body.platform, `${req.body.uid}`] });

  // await axios.post(new URL("/mail", process.env.MAIL_SERVER), {
  //   ...req.body,
  //   author: author.name,
  //   platform: undefined,
  //   uid: undefined,
  // });
  return res.json({ ok: true });
}

module.exports = { login, postLogin, onNaturalMessage, onParsedMessage };
