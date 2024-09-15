from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

import chainlit as cl

llama_cpp_host: str = 'i3tiny1'
llama_cpp_port: int = 9750

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
    session_history.add_message({"role": "system", "content": "You are a helpful assistant, your name "
                                                              "is CapitalAnalyst. Keep your responses concise."})
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

    resp = cl.Message(content="")
    data_list = "How are you doing today. I am an assistant.".split(" ")
    for token in data_list:
        await resp.stream_token(token)
        await resp.stream_token(" ")

    await resp.send()

def get_file_from_message(message: cl.Message):
    ret = {"name":None,"content":None}
    if len(message.elements) > 0:
        e = message.elements[0]
        name = e.name
        path = e.path
        try:
            # Opening the file in 'read' mode and reading its contents into a variable
            with open(path, 'r') as file:
                content = file.read()
                ret["name"] = name
                ret["content"] = content
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")

    return ret

@cl.on_message
async def on_message(message: cl.Message):
    inp = message.content

    doc = get_file_from_message(message)
    if doc["content"] is not None:
        inp = inp + "\n\n Consider following additional context. \n\n##Context:\n\n" + doc["content"]

    session_id = cl.user_session.get("id")
    with_message_history = cl.user_session.get("runnable")
    config = {"configurable": {"session_id": session_id,
                               'callbacks': [cl.LangchainCallbackHandler()]}, 'session_id': session_id}

    msg = cl.Message(content="")
    async for chunk in with_message_history.astream(
            {"input": inp},
            config,
    ):
        await msg.stream_token(chunk)

    await msg.update()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
