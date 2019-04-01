"""
A Flask application to demonstrate recording audio from a Nexmo Voice call.
"""

from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify, url_for, make_response
from tinydb import TinyDB, Query
import nexmo

import os
from pprint import pprint

load_dotenv()

client = nexmo.Client(
    application_id=os.environ["NEXMO_APPLICATION_ID"],
    private_key=os.environ["NEXMO_PRIVATE_KEY"],
)

app = Flask(__name__)
db = TinyDB(os.environ["DATABASE_PATH"])
calls = db.table('calls')
recordings = db.table('recordings')


class Recording:
    """
    A view object representing a combination of a `recording` and a `call` record.
    
    TinyDB has no concept of relationships, so this object does a query on the `calls` table and adds the related data to this object as `related_call`.
    """
    def __init__(self, data):
        self.uuid = data['recording_uuid']
        related_calls = calls.search(Query().conversation_uuid == data['conversation_uuid'])
        if related_calls:
            self.related_call = related_calls[0]
        else:
            self.related_call = None


@app.route("/")
def index():
    """
    A view which lists all stored recordings.
    """
    return render_template("index.html.j2", recordings=[Recording(r) for r in recordings])


@app.route("/recordings/<uuid>")
def recording(uuid):
    """
    A view which provides a recording's MP3 data so it can be played in
    the browser.
    """
    b = open(f'recordings/{uuid}.mp3', 'rb').read()
    response = make_response(b)
    response.headers['Content-Type'] = 'audio/mpeg'
    return response


@app.route("/answer", methods=["POST"])
def answer():
    """
    An NCCO webhook, providing actions that tell Nexmo to read a statement
    to the user and then record a message.
    """
    return jsonify(
        [
            {
                "action": "talk",
                "text": "<speak>You have reached <phoneme alphabet='ipa' ph='əʊlɛgz'>Oleg's</phoneme> pizza. Please leave a message after the beep.</speak>",
                "voiceName": "Brian",
            },
            {
                "action": "record",
                "beepStart": True,
                "eventUrl": [url_for("new_recording", _external=True)],
                "endOnSilence": 3,
            },
        ]
    )


@app.route("/new-recording", methods=["POST"])
def new_recording():
    """
    A Nexmo event webhook, only called when a recording is made available.

    This webhook downloads the MP3 to the `recordings` directory and adds
    metadata to the `recordings` table in the db.
    """
    # Ideally this would be done as a background process.
    # Try using Celery, or using Sanic instead of Flask!
    recording_bytes = client.get_recording(request.json['recording_url'])
    recording_id = request.json['recording_uuid']
    with open(f"recordings/{recording_id}.mp3", 'wb') as mp3_file:
        mp3_file.write(recording_bytes)
    recordings.insert(request.json)
    return ""


@app.route("/event", methods=["POST"])
def event():
    """
    A Nexmo event webhook.

    If the event is an `answered` event, the event data is stored in the `calls` table.
    Any other event types are currently ignored.
    """
    if request.json.get('status') == 'answered':
        calls.insert(request.json)

    return ""
