import os
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
import chat_gpt_interface
from command_input import CommandInput
from helpers import get_input_dates, execute_get_summary, get_modal_inputs, get_input_dates_from_mention
from views.app_home_view import get_app_home_view
from views.global_shortcut_view import get_global_shortcut_view

load_dotenv()

app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

HOME_BUTTON_NAME = "button_click"
MODAL_EARLIEST_DATE_FIELD_NAME = "earliest-date"
MODAL_LATEST_DATE_FIELD_NAME = "latest-date"
MODAL_SELECTED_CHANNEL_FIELD_NAME = "selected-channel"
MODAL_CALLBACK_ID = "execute_global_shortcut"

# INJECTED ARGS: https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/async_args.html


# --- HELLO WORLD ---
# https://api.slack.com/events/message
@app.message("hello")
async def hello(message, say):
    await say(f"Hi <@{message['user']}>!")


# --- BOT MENTION ---
# https://api.slack.com/events/app_mention
@app.event("app_mention")
async def handle_mention(say, event, client):
    message: str = event.get("text", "")
    if "summarize" in message:
        oldest, newest = get_input_dates_from_mention(event)
        command_input = CommandInput(oldest, newest, event.get("channel"), event.get("team"))
        response = await execute_get_summary(command_input, client)
    else:
        help_message = "Get a summary by saying 'summarize' and optionally follow it up with start and end dates (mm-dd-yyyy)."
        response = help_message
    await say(response)


# --- SLASH COMMAND ---
@app.command("/summarize")
async def handle_slash(ack, command, respond, client):
    await ack()
    await respond("Loading...")
    oldest, newest = get_input_dates(command)
    channel_id = command.get("channel_id")
    team_id = command.get("team_id")
    command_input = CommandInput(oldest, newest, channel_id, team_id)
    response = await execute_get_summary(command_input, client)
    await respond(response)


# --- MESSAGE SHORTCUT ---
@app.message_shortcut('summarize_message_shortcut')
async def handle_message_shortcut(ack, shortcut, respond):
    await ack()
    message = shortcut.get("message").get("text")
    response = await chat_gpt_interface.get_summary(message)
    await respond(response)


# --- GLOBAL SHORTCUT ---
@app.global_shortcut('summarize_global_shortcut')
async def start_global_shortcut(ack, shortcut, client):
    await ack()
    view = get_global_shortcut_view(MODAL_CALLBACK_ID, MODAL_EARLIEST_DATE_FIELD_NAME, MODAL_LATEST_DATE_FIELD_NAME, MODAL_SELECTED_CHANNEL_FIELD_NAME)
    # https://api.slack.com/methods/views.open
    await client.views_open(user_id=shortcut.get("user", {}).get('id'), trigger_id=shortcut.get("trigger_id"),
                            view=view)


@app.view(MODAL_CALLBACK_ID)
async def execute_global_shortcut(ack, body, client):
    await ack()
    # https://api.slack.com/methods/chat.postMessage
    await client.chat_postMessage(channel=body["user"]["id"],
                                  text="Hi! I've received your request and I'm working on it!")
    oldest_ts, newest_ts, channel = get_modal_inputs(body, MODAL_EARLIEST_DATE_FIELD_NAME, MODAL_LATEST_DATE_FIELD_NAME, MODAL_SELECTED_CHANNEL_FIELD_NAME)
    command_input = CommandInput(oldest=oldest_ts, newest=newest_ts, team_id=body['team']['id'], channel_id=channel)
    response = await execute_get_summary(command_input, client)
    await client.chat_postMessage(channel=body["user"]["id"], text=response)


# --- APP HOME ---
# https://api.slack.com/events/app_home_opened
@app.event("app_home_opened")
async def update_home_tab(event, client):
    # https://api.slack.com/methods/views.publish
    await client.views_publish(
        user_id=event["user"],
        view=get_app_home_view(event, HOME_BUTTON_NAME)
    )


@app.action(HOME_BUTTON_NAME)
async def action_button_click(body, ack, client):
    # Acknowledge the action
    await ack()
    shortcut = {
        "user": {
            "id": body["user"]["id"]
        },
        "trigger_id": body["trigger_id"]
    }
    await start_global_shortcut(ack=ack, shortcut=shortcut, client=client)


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 8000)))
