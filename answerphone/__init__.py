from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify, url_for
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

@app.route("/")
def index():
    return render_template("index.html.j2", recordings=recordings)


@app.route("/answer", methods=["POST"])
def answer():
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
    if request.json.get('status') == 'answered':
        calls.insert(request.json)

    return ""
