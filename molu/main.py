from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from icalendar import Calendar, Event, vCalAddress, vText

from datetime import datetime
from pathlib import Path
from flask import Flask, request
import string
import secrets

import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from requests import HTTPError

app = Flask(__name__)



def makeICS(summary, dtstart, dtend, cn, location, attendees):
    organizermail = 'jmrnitctest@gmail.com'

    cal = Calendar()
    cal['method'] = 'REQUEST'

    event = Event()
    event.add('summary', summary)
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    event.add('dtstamp', datetime.today())

    # Organizer details
    organizer = vCalAddress('MAILTO:' + organizermail)
    organizer.params['cn'] = vText(cn)
    event['organizer'] = organizer
    event['location'] = vText(location)

    uid = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(26))
    event['uid'] = uid + '@google.com'

    for a in attendees:
        attendee = vCalAddress('MAILTO:' + a['email'])
        attendee.params['cutype'] = vText('INDIVIDUAL')
        attendee.params['role'] = vText('REQ-PARTICIPANT')
        attendee.params['partstat'] = vText('NEEDS-ACTION')
        attendee.params['rsvp'] = vText('TRUE')
        attendee.params['name'] = vText(a['name'])
        event.add('attendee', attendee, encode=0)

    # Adding events to calendar
    cal.add_component(event)

    return cal.to_ical()


def mailICS(subject, receiver_emails, ical):
    message = MIMEMultipart('mixed')

    message['to'] = ", ".join(receiver_emails)
    message['subject'] = subject
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    msg = MIMEBase('application', 'octet-stream')
    msg.set_payload(ical)
    msg.add_header('Content-Disposition', 'attachment', filename='invite.ics')
    message.attach(msg)

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
    ]
    creds = Credentials.from_authorized_user_file('credentials.json', ['https://www.googleapis.com/auth/gmail.compose'])
    service = build('gmail', 'v1', credentials=creds)

    try:
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        sent_message = (service.users().messages().send(userId="me", body=create_message).execute())
    except HTTPError as error:
        print(F'An error occurred: {error}')
        sent_message = None

    return sent_message

@app.route('/mail', methods=['POST'])
def makeAndMailICS():
    ical = makeICS(request.json["summary"],
                   datetime.fromisoformat(request.json["start_date"]),
                   datetime.fromisoformat(request.json["end_date"]), request.json["author"],
                   request.json["location"], request.json["attendees"])

    mailICS(request.json["summary"], list(map(lambda x: x['email'], request.json["attendees"])), ical)

    return {"ok": True}


if __name__ == '__main__':
    app.run()