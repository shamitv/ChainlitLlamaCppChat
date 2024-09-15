from openai import AsyncOpenAI
import chainlit as cl


settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

llama_cpp_host: str = 'localhost'
llama_cpp_port: int = 8400

openai_url: str = "http://{host}:{port}/v1".format(host=llama_cpp_host, port=llama_cpp_port)

client = AsyncOpenAI(api_key="...",base_url=openai_url)



@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    print("Step 1")
    msg = cl.Message(content="")
    #await msg.send()
    print("Step 2")
    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            print("stream")
            await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})
    print("Step 4")
    await msg.update()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)