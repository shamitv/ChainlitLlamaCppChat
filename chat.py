from openai import AsyncOpenAI
import chainlit as cl

client = AsyncOpenAI(base_url='http://i3tiny1:9750/v1',
                     api_key="dummy")

# Instrument the OpenAI client
cl.instrument_openai()

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    # ... more settings
}


@cl.on_message
async def on_message(message: cl.Message):
    response = await client.chat.completions.create(
        messages=[
            {
                "content": "You are a helpful bot, you always reply with chain of thought.",
                "role": "system"
            },
            {
                "content": message.content,
                "role": "user"
            }
        ],
        **settings
    )
    await cl.Message(content=response.choices[0].message.content).send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)