"""Simple Hello World entry point module."""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import cast

from IPython.display import Image, display
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.chat_kargs import get_chat_kargs

# from prettyprinter import pprint


def agora() -> datetime:
    """Abtém o dia e hora atuais."""
    return datetime.now()


async def main() -> None:
    """Entry point of the program. Obtains an OAuth token and runs a sample chat."""

    # tools = []
    tools = [agora]

    chat_kwargs = await get_chat_kargs()
    chat = ChatOpenAI(**chat_kwargs)
    chat_with_tools = chat.bind_tools(tools)

    # def assistant(state: MessagesState):
    #     return {"messages": [chat.invoke(state["messages"])]}

    # prompt = SystemMessage(
    #     content=(
    #         "Você é um assistente que responde apenas 'sim' ou 'não', "
    #         "mas sempre explica utilizando o contexto fornecido."
    #     )
    # )

    async def call_model(state: MessagesState) -> MessagesState:
        response = cast(AnyMessage, await chat_with_tools.ainvoke(state["messages"]))
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("chat", call_model)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "chat")
    graph.add_conditional_edges(
        "chat",
        tools_condition,
    )
    graph.add_edge("tools", "chat")

    memory = MemorySaver()
    react_graph = graph.compile(checkpointer=memory)
    display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))

    messages: list[AnyMessage] = [
        # prompt,
        HumanMessage(content="que horas são e que dia é hoje?"),
    ]

    state = MessagesState(messages=messages)
    config = RunnableConfig(configurable={"thread_id": "1"})
    result = await react_graph.ainvoke(state, config=config)

    for m in result["messages"]:
        m.pretty_print()


if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    asyncio.run(main())
