from flask import Flask, request, make_response, Response
import os
import json

from slackclient import SlackClient


# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ.get("SLACK_ROBO_TOKEN")
SLACK_VERIFICATION_TOKEN = os.environ.get("SLACK_ROBO_VERIFICATION_TOKEN")

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)

# your attachment
attachments_json = [
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "color": "#258ab5",
        "attachment_type": "default",
        "callback_id": "the_greatest_war",
        "actions": [
            {
                "name": "choco1",
                "text": "きのこ",
                "value": "kinoko",
                "type": "button"
            },
            {
                "name": "choco2",
                "text": "たけのこ",
                "value": "takenoko",
                "type": "button"
            }
        ]
    }
]

@app.route("/", methods=["GET"])
def index():
    slack_client.api_call(
        "chat.postMessage",
        channel="#general",
        text="あなたはどっち派？",
        attachments=attachments_json
    )
#redirect from button
@app.route("/slack/json_html", methods=["POST"])
def json_html():

    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    val = form_json["actions"][0]["value"]
    if val == "kinoko":
        response_text = "よろしい、ならば戦争だ"
    else:
        response_text = "よろしい、ならば盟友だ"
    response = slack_client.api_call(
        "chat.postMessage",
        channel="#ext-scratch",
        text=response_text,
        attachments=[]
    )


