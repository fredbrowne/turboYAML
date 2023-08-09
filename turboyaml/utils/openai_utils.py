import os

import openai


def is_valid_api_key(api_key):
    if api_key is None or not api_key.startswith("sk-"):
        return False
    return True


def get_api_key(api_key_arg):
    if api_key_arg and is_valid_api_key(api_key_arg):
        return api_key_arg

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key and is_valid_api_key(api_key):
        return api_key
    return None


async def send_to_openai(messages, api_key, model):
    # Set up OpenAI API credentials
    openai.api_key = api_key

    # Send the prompt to the OpenAI API to retrieve the YAML output
    response = await openai.ChatCompletion.acreate(
        model=model, messages=messages, temperature=0.6
    )
    return response
