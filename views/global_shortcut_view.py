def get_global_shortcut_view(callback_id, earliest_date_field, latest_date_field, selected_channel_field):
    return {
        "type": "modal",
        "callback_id": callback_id,
        "title": {
            "type": "plain_text",
            "text": "My Demo App",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "input",
                "label": {
                    "type": "plain_text",
                    "text": "Please select the earliest date for summary."
                },
                "element": {
                    "type": "datepicker",
                    "action_id": earliest_date_field
                }
            },
            {
                "type": "input",
                "label": {
                    "type": "plain_text",
                    "text": "Please select the latest date for summary."
                },
                "element": {
                    "type": "datepicker",
                    "action_id": latest_date_field
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick a channel from the dropdown list"
                },
                "accessory": {
                    "action_id": selected_channel_field,
                    "type": "channels_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item"
                    }
                }
            }
        ]
    }