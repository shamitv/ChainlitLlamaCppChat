import chainlit as cl


@cl.on_chat_start
async def main():
    msg = cl.Message(content="")
    data_list = "How are you doing today. I am an assistant.".split(" ")
    for token in data_list:
        await msg.stream_token(token)
        await msg.stream_token(" ")

    await msg.send()


@cl.on_message
async def on_message(message: cl.Message):
    data_list = "This is a sample response.".split(" ")
    for token in data_list:
        await message.stream_token(token)
        await message.stream_token(" ")

    await message.send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
