import chainlit as cl


@cl.on_message
async def main(message: cl.Message):
    msg_str: str = message.content
    data_list = "This is a sample response.".split(" ")
    resp = cl.Message(content="")
    for token in data_list:
        await resp.stream_token(token)
        await resp.stream_token(" ")

    resp_str = f"This was in response to : {msg_str}"
    await resp.send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
