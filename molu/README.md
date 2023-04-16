# molu 👧

The mail provider in the Skedulr stack. It is currently built to work with Google Mail. But, by implementing the required communication APIs, more providers can be added into the `molu` group.

## Running It

1. Install the requirements by running

   ```bash
   pip install -r requirements.txt
   ```

2. Generate a web client o-auth client using the google cloud console.

3. Using the client_id and client_secret from previous step, go to the [OAuth Playground](https://developers.google.com/oauthplayground) and run through an oauth flow to get the access token and refresh token.

4. Create a credentials.json in the following format

   ```json
   {
     "client_id": "[CLIENT_ID]",
     "client_secret": "[CLIENT_SECRET]",
     "access_token": "[ACCESS TOKEN]",
     "refresh_token": "[REFRESH TOKEN]"
   }
   ```

   - todo check when refresh token expires

5. Run main.py
