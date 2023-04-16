# Skedulr ML Engine

This is the ML engine for extraction of events from conversational queries by users. This is a micro-service of the larger Skedulr project. The base structure is built on pretrained BERT. SpaCy's parts of speech labeler and Named entity recognizer, used along with fuzzywuzzy is used to achieve the conversational capabilities. Additionally, the engine exposes a flask api to accept inputs and return outputs. The folder contents are as follows (pycache can be ignored).
```
.
├── README.md
├── __pycache__
│   ├── bert.cpython-310.pyc
│   ├── bert.cpython-38.pyc
│   ├── event_parser.cpython-310.pyc
│   ├── event_parser.cpython-38.pyc
│   ├── handler.cpython-310.pyc
│   ├── handler.cpython-38.pyc
│   ├── main.cpython-310.pyc
│   └── main.cpython-38.pyc
├── bert.py
├── event_parser.py
├── handler.py
└── main.py
```

The API spec is as follows

**Endpoint:**/parse

**Description:** Endpoint to call the ML engine and return extracted features

**Body:**
```
{
    message: "users meeting query string",
    "contact_list": [{"name":"Users name","email":"your@email.com"},{...}]
}
```

**Response:**
```
{
  "attendees": [
    {
      "name": "Users name",
      "email":"your@email.com"
    },
    {...}
  ],
  "end_date": "end time ISO string",
  "location": "location of meeting",
  "operation": "create",
  "start_date": "start time ISO string",
  "summary": "summary of meet"
}
```