from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

import chainlit as cl

llama_cpp_host: str = 'localhost'
llama_cpp_port: int = 8000

openai_url: str = "http://{host}:{port}/v1".format(host=llama_cpp_host, port=llama_cpp_port)

# This Dictionary will store chat history in memory.
# Key for each history object is a unique session ID

history_store = {}


def get_history(session_id: str) -> ChatMessageHistory:
    if session_id in history_store:
        return history_store[session_id]
    else:
        history = ChatMessageHistory()
        history_store[session_id] = history
        return history


@cl.on_chat_start
async def on_chat_start():
    session_id = cl.user_session.get("id")
    model = ChatOpenAI(streaming=True,
                       api_key="...",
                       base_url=openai_url)
    session_history = get_history(session_id)
    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    with_message_history = RunnableWithMessageHistory(
        runnable,
        get_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    cl.user_session.set("history", session_history)
    cl.user_session.set("runnable", with_message_history)


@cl.on_message
async def on_message(message: cl.Message):
    inp = message.content
    session_id = cl.user_session.get("id")
    with_message_history = cl.user_session.get("runnable")
    config = {"configurable": {"session_id": session_id,
                               'callbacks': [cl.LangchainCallbackHandler()]}, 'session_id': session_id}
    async for chunk in with_message_history.astream(
            {"input": inp},
            config,
    ):
        await message.stream_token(chunk)

    await message.send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
