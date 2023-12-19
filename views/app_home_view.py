def get_app_home_view(event, HOME_BUTTON_NAME):
    return {
            "type": "home",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Welcome home, <@" + event.get("user") + "> :house:*"
                    }
                },
                {
                    "type": "section",
                    "block_id": "sectionBlockWithButton",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Get a summary of a channel here!"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Click Me",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": HOME_BUTTON_NAME
                    }
                }
            ]
        }