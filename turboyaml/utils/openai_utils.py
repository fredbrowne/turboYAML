import os

from openai import OpenAI, AsyncOpenAI

def get_client(api_key):
    try:
        client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        client.models.list()
        return client
    except Exception as e:
        raise ValueError(f"Failed to initialize OpenAI client: {e}")

async def send_to_openai(messages, api_key, model):
    # Set up OpenAI API credentials
    client = AsyncOpenAI(api_key=api_key)

    # Send the prompt to the OpenAI API to retrieve the YAML output
    response = await client.chat.completions.create(
        model=model, messages=messages, temperature=0.6
    )
    return response
