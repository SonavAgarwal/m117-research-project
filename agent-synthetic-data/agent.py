# Import relevant functionality
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from gitsim_tools import all_tools

import dotenv
dotenv.load_dotenv()

# Create the agent
memory = MemorySaver()
# 3.5 turbo
model = ChatOpenAI(model="gpt-3.5-turbo")
tools = all_tools
agent_executor = create_react_agent(model, tools, checkpointer=memory)
