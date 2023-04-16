from flask import Flask, request
from event_parser import meeting_details_parse

app = Flask(__name__)


@app.route('/parse', methods=['POST'])
def parse():
    try:
        res = meeting_details_parse(request.json["message"], request.json["contact_list"])
    except Exception as e:
        print(e)
        return {
            "operation": None,
            "location": None,
            "attendees": None,
            "summary": None,
            "start_date": None,
            "end_date": None,
        }
    return res


if __name__ == "__main__":
    app.run(port=5002, debug=True)
