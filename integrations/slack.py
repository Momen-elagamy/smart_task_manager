from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

def send_slack_message(channel, message):
    client = WebClient(token=SLACK_BOT_TOKEN)
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        return response
    except SlackApiError as e:
        return {"error": str(e)}
