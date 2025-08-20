# tools/llm_agent.py
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
import operator
import os

MAX_TAVILY_RESPONSE_URLS = 10
AGENT_LLM = "llama3.2:latest" # Choose a model that's good for tool calling and basic writing & reasoning ideally.

# Get our Tavily API key
tavily_api_key = os.getenv("TAVILY_API_KEY")

if tavily_api_key is None:
    print("Error: Cannot find Tavily API key for search.")
    exit(1)

os.environ["TAVILY_API_KEY"] = tavily_api_key
web_search_tool = TavilySearchResults(max_results=MAX_TAVILY_RESPONSE_URLS)

tools = [web_search_tool]

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def call_model(state : AgentState) -> dict:
    print("Calling model")
    messages = state["messages"]
    response = model.invoke(messages)
    if response.tool_calls:
        print("Model expects tool calls", response.tool_calls)

    return {"messages": [response]}

def call_tool(state : AgentState) -> dict:
    last_message = state["messages"][-1]

    # Ensure there are tool calls before continuing
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"messages": []}
    
    # Execute tool calls
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]

        # Locate the tool to call
        tool_to_call = next((t for t in tools if t.name == tool_name), None)
        if not tool_to_call:
            raise ValueError(f"Tool '{tool_name}' not found.")

        tool_messages.append(ToolMessage(content=str(tool_to_call.invoke(tool_call["args"])), 
                                         tool_call_id=tool_call["id"]
                                        ))

    return {"messages" : tool_messages}

def should_continue(state : AgentState) -> str:
    last_message = state["messages"][-1]
    
    # If we've called tools, we need to continue
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls: # Continue to agent response
        return "continue"
    else: # Otherwise, we have the agent response
        return "end"

def query(input : str):
    inputs     = {"messages": [HumanMessage(content=input)]}

    for output in app.stream(inputs, {"recursion_limit": 5}):
        for key, value in output.items():
            if key == "agent":
                yield {"agentResponse": value}
            else:
                yield {"toolResponse": value}

# Setup model
model = ChatOllama(model=AGENT_LLM).bind_tools(tools)

# Setup the graph workflow
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue" : "action", "end" : END})
workflow.add_edge("action", "agent") # Add action node that points to agent node so we get Agent -> Tool -> Agent -> ...
app = workflow.compile()

if __name__ == "__main__": # Tests
    inp = "What were the main announcements from Apple's latest keynote event?"
    for output in query(inp):
        print(output)
