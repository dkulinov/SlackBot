from datetime import timedelta, datetime
import time

from slack_sdk.web.async_client import AsyncWebClient

import chat_gpt_interface
from command_input import CommandInput


async def execute_get_summary(command_input: CommandInput, client: AsyncWebClient) -> str:
    try:
        # https://api.slack.com/methods/conversations.history
        # TODO: FILL IN get message history
        messages_res = await client.conversations_history(channel=command_input.channel_id, oldest=command_input.oldest, newest=command_input.newest)
        messages = messages_res.get("messages")
        # https://api.slack.com/methods/users.list
        # TODO: FILL IN get members
        users_res = await client.users_list(team_id=command_input.team_id)
        users = users_res.get("members")
        formatted_messages = format_messages(messages, users)
        response = await chat_gpt_interface.get_summary(formatted_messages)
    except Exception as e:
        print(e)
        response = "Something went wrong. Try again."
    return response


def get_input_dates(command: dict) -> tuple:
    OLDEST_DEFAULT = 14
    DATE_FORMAT = "%Y-%m-%d"
    oldest, newest = extract_inputs(command)
    oldest_date = datetime.strptime(oldest, DATE_FORMAT) if oldest else (
            datetime.now() - timedelta(days=OLDEST_DEFAULT))
    newest_date = datetime.strptime(newest, DATE_FORMAT) if newest else datetime.now()
    oldest_unix_timestamp = time.mktime(oldest_date.timetuple())
    newest_unix_timestamp = time.mktime(newest_date.timetuple())
    return str(int(oldest_unix_timestamp)), str(int(newest_unix_timestamp))


def extract_inputs(command):
    inputs = command.get("text", " ").split(" ")
    if len(inputs) < 2:
        inputs.append("")
    oldest, newest = inputs[0], inputs[1]
    return oldest, newest


def format_messages(messages, users):
    formatted_messages = [f"User {message.get('user')}: {message.get('text')}" for message in messages]
    formatted_messages.reverse()
    formatted_messages_str = ". ".join(formatted_messages)
    id_to_name = get_user_id_to_name_map(users)
    for id, name in id_to_name.items():
        formatted_messages_str = formatted_messages_str.replace(id, name)
    return formatted_messages_str


def get_user_id_to_name_map(users):
    return {user.get("id"): user.get("name") for user in users}



def get_modal_inputs(body, earliest_date_field, latest_date_field, selected_channel_field):
    state: dict = body.get("view").get("state").get("values")
    submissions = state.values()
    earliest_input, latest_input = '', ''
    channel = ''
    for submission in submissions:
        if submission.get(earliest_date_field):
            earliest_input = submission.get(earliest_date_field).get("selected_date")
        elif submission.get(latest_date_field):
            latest_input = submission.get(latest_date_field).get("selected_date")
        else:
            channel = submission.get(selected_channel_field).get("selected_channel")
    oldest_ts, newest_ts = get_input_dates({"text": f"{earliest_input} {latest_input}"})
    return oldest_ts, newest_ts, channel


def get_input_dates_from_mention(event):
    message = event.get("text", "")
    message = message.split(' ', 1)[1]
    message = message.removeprefix('summarize')
    message = message.removeprefix(' ')
    event['text'] = message
    oldest, newest = get_input_dates(event)
    return oldest, newest
