import os

from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.environ.get('CHAT_GPT_KEY')
openai.organization = 'org-rATfTP97mV7pPHGVIfOBa5x6'


async def get_summary(message):
    try:
        response = await openai.ChatCompletion.acreate(
            # model="gpt-3.5-turbo",
            model="gpt-4",
            messages=[
                {"role": "user",
                 "content": "Can you summarize the following message or conversation and highlight the important parts?"},
                {"role": "user", "content": message}
            ],
            temperature=0,
        )

        return response['choices'][0]['message']['content']

    except Exception as e:
        print(e)
        return "Couldn't get response from ChatGPT."
