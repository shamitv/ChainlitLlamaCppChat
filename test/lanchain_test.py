from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="...",
    base_url="http://i3tiny1:9750/v1"
)

messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence to French.",
    ),
    ("human", "Translate following text to French : My brother is an Idiot."),
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)