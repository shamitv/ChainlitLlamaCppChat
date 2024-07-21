import chainlit as cl
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAI
from langchain.chains import LLMMathChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents.agent_types import AgentType
from langchain.agents import Tool, initialize_agent

llama_cpp_host: str = 'i3tiny1'
llama_cpp_port: int = 9820

openai_url: str = "http://{host}:{port}/v1".format(host=llama_cpp_host, port=llama_cpp_port)


@cl.on_chat_start
def math_chatbot():
    model = ChatOpenAI(streaming=True,
                       api_key="...",
                       base_url=openai_url,
                       temperature=0)

    word_problem_template = """You are a reasoning agent tasked with solving the user's logic-based questions.
    Logically arrive at the solution, and be factual. In your answers, clearly detail the steps involved and give
    the final answer. Provide the response in bullet points. Question  {question} Answer"""

    math_assistant_prompt = PromptTemplate(
        input_variables=["question"],
        template=word_problem_template
    )

    word_problem_chain = LLMChain(llm=model,
                                  prompt=math_assistant_prompt)
    word_problem_tool = Tool.from_function(name="Reasoning Tool",
                                           func=word_problem_chain.run,
                                           description="Useful for when you need to answer logic-based/reasoning  "
                                                       "questions.",
                                           )

    problem_chain = LLMMathChain.from_llm(llm=model)
    math_tool = Tool.from_function(name="Calculator",
                                   func=problem_chain.run,
                                   description="Useful for when you need to answer numeric questions. This tool is "
                                               "only for math questions and nothing else. Only input math "
                                               "expressions, without text",
                                   )

    agent = initialize_agent(
        tools=[math_tool, word_problem_tool],
        llm=model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )
    cl.user_session.set("agent", agent)


@cl.on_message
async def process_user_query(message: cl.Message):
    agent = cl.user_session.get("agent")

    response = await agent.acall(message.content,
                                 callbacks=[cl.AsyncLangchainCallbackHandler()])

    await cl.Message(response["output"]).send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)