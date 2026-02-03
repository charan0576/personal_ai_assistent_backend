from langgraph.prebuilt import create_react_agent
from config import llm
from tools import read_file, write_file





tools = [read_file, write_file]

agent = create_react_agent(llm, tools=tools)