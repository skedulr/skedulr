# Skedulr

This is our project for the Hackverse 4.0 hackathon. It is a platform agnostic chatbot that is (currently) used to schedule meetings. You can chat with the bot using natural language. There are 4 micro-services to this system

- Galactus: The centralized backend where all the information goes through.
- Botty: Our bot protocol. The current implementation is for a discord bot, but it can theoretically be extended to any chat platform.
- Molu: Our mailing services. The current implementation is using the GMail API, but it can be extended to work with any email provider.
- ML Engine: The part of the system that implements natural language parsing and returns the parsed data to Galactus.

More details can be found in the respective folder READMEs.
