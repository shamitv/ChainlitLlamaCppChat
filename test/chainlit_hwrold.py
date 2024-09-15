import chainlit as cl


@cl.on_chat_start
async def main():
    resp = cl.Message(content="")
    data_list = "How are you doing today. I am an assistant.".split(" ")
    for token in data_list:
        await resp.stream_token(token)
        await resp.stream_token(" ")

    await resp.send()


@cl.on_message
async def on_message(message: cl.Message):
    data_list = "This is a sample response.".split(" ")
    resp = cl.Message(content="")
    for token in data_list:
        await resp.stream_token(token)
        await resp.stream_token(" ")

    message.streaming = False
    await message.send()



if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
