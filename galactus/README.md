# Galactus

This repo hosts the code for **Galactus**, the centralised backend for Skedulr. Galactus interfaces with all the other micro-services in the Skedulr stack.

The following files are present.

```
.
├── controllers
│   └── user.controller.js
├── db
│   ├── bookings.js
│   ├── organisations.js
│   └── users.js
├── routes
│   └── user.route.js
├── client_secret.json
├── .env.example
├── .gitignore
├── index.js
├── package.json
├── package-lock.json
├── .prettierrc
└── README.md
```

## Running It 🏃

1. Either install mongodb or [setup the mongodb docker container](https://hevodata.com/learn/docker-postgresql/) or set up an Atlas instance.

2. Create a DB by accessing the `mongosh` shell.

3. Replicate the `.env.example` file as `.env`. Edit the environment variables with the DB details and microservice URLs.

4. Then the usual drill. `npm install` and then `npm run dev` to start a dev instance

5. Generate a `client-secret.json` from the Google Cloud console.

## Botty Endpoints

A program that is part of `Botty` is expected to use the following endpoints.

### POST /login

**Body**

```json
{
  "platform": "discord", //or something else
  "uid": "unique identifier for platform"
}
```

**Response**

```json
//if user is already logged in
{"loggedIn": true}

//otherwise
{"authorizationUrl": "url"}
```

### POST /message

to parse a natural language message using `mle`.

**Body**

```json
{
  "platform": "discord", //or something else
  "uid": "unique identifier for platform",
  "message": "some natural message"
}
```

**Response**

```json
{
  "attendees": [{ "name": "arun kumar", "email": "arun@nitc.ac.in" }],
  "start_date": "ISO String with time",
  "end_date": "ISO String with time",
  "location": "office conference room",
  "operation": "create",
  "summary": "sales cadence meeting"
}
```

### POST /message-parsed

once the user confirms the parsed message, this function can invoke the invitation emails from `molu`.

**Body**

```json
{
  "attendees": [{ "name": "arun kumar", "email": "arun@nitc.ac.in" }],
  "start_date": "ISO String with time",
  "end_date": "ISO String with time",
  "location": "office conference room",
  "operation": "create",
  "summary": "sales cadence meeting"
}
```

**Response**

```json
{ "ok": true }
```

## MLE endpoints

An app that is to be part of `MLE` is expected to implement the following endpoint.

### POST /parse

parse a natural language string for its components.

**Body**

```json
{
  "message": "do something for me",
  "contact_list": [{ "name": "JOEL", "email": "joel@nitc.ac.in" }]
}
```

## Molu endpoints

### POST /mail

to send an email

**Body**

```json
{
  "attendees": [{ "name": "arun kumar", "email": "arun@nitc.ac.in" }],
  "start_date": "ISO String with time",
  "end_date": "ISO String with time",
  "location": "office conference room",
  "operation": "create",
  "summary": "sales cadence meeting",
  "author": "cliford"
}
```
