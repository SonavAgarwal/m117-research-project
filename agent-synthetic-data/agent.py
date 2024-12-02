# Import relevant functionality
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from gitsim_tools import all_tools

import dotenv
dotenv.load_dotenv()

# # Create the agent
# memory = MemorySaver()
# model = ChatOpenAI(model="gpt-4")
# tools = all_tools
# agent_executor = create_react_agent(model, tools, checkpointer=memory)


def create_datagen_agent():
    memory = MemorySaver()
    model = ChatOpenAI(model="gpt-4")
    tools = all_tools
    agent_executor = create_react_agent(model, tools, checkpointer=memory)
    return agent_executor

# # Use the agent
# config = {"configurable": {"thread_id": "abc123"}}
# for chunk in agent_executor.stream(
#     {"messages": [HumanMessage(content="hi im bob! and i live in sf")]}, config
# ):
#     print(chunk)
#     print("----")

# for chunk in agent_executor.stream(
#     {"messages": [HumanMessage(
#         content="whats the weather where I live?")]}, config
# ):
#     print(chunk)
#     print("----")
