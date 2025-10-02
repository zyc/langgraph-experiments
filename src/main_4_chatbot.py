"""Simple Hello World entry point module."""

import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, cast

from langchain.tools import tool
from langchain_core.messages import (AnyMessage, HumanMessage, RemoveMessage,
                                     SystemMessage, ToolMessage)
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel

from src.helpers import get_chat_kargs, render_graph


class CustomState(MessagesState):
    """
    Represents the state of messages with an additional summary.

    Attributes:
        summary (str): A textual summary of the current state.
    """
    summary: str | None


@tool("now")
async def now_tool() -> datetime:
    """Obtém o dia e hora atuais."""
    return datetime.now()


async def main() -> None:
    """Entry point of the program. Obtains an OAuth token and runs a sample chat."""

    db_path = "db/example.db"
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # !mkdir -p db && [ ! -f db/example.db ] && wget -P db https://github.com/langchain-ai/langchain-academy/raw/main/module-2/state_db/example.db

    # tools = []
    tools = [now_tool]
    memory = MemorySaver()

    async with AsyncSqliteSaver.from_conn_string(str(db_file)) as memory2:
        chat_kwargs = await get_chat_kargs()
        chat = ChatOpenAI(**chat_kwargs).bind_tools(tools)

        node_prepare_name = "prepare"
        node_chat_name = "chat"
        node_tool_name = "tools"
        node_summarize_name = "summarize_conversation"

        async def prepare(state: CustomState) -> CustomState:
            """Prepare the state before processing."""
            # Here you can add any preparation logic if needed
            return state

        # def assistant(state: MessagesState):
        #     return {"messages": [chat.invoke(state["messages"])]}

        # prompt = SystemMessage(
        #     content=(
        #         "Você é um assistente que responde apenas 'sim' ou 'não', "
        #         "mas sempre explica utilizando o contexto fornecido."
        #     )
        # )

        async def invoke_chat(state: CustomState) -> CustomState:
            summary = state.get("summary", "")

            # If there is summary, then we add it
            if summary:
                # Add summary to system message
                system_message = f"Summary of conversation earlier: {summary}"

                # Append summary to any newer messages
                messages = [SystemMessage(
                    content=system_message)] + state["messages"]

            else:
                messages = state["messages"]

            response = cast(AnyMessage, await chat.ainvoke(messages))
            return CustomState(messages=[response], summary="")

        async def summarize_conversation(state: CustomState) -> CustomState:
            # return state

            summary = state.get("summary", "")

            # Create our summarization prompt
            if summary:

                # A summary already exists
                summary_message = (
                    f"This is summary of the conversation to date: {summary}\n\n"
                    "Extend the summary by taking into account the new messages above:"
                )

            else:
                summary_message = "Create a summary of the conversation above:"

            # Filtra as mensagens retirando as que são do tipo ToolMessage
            messages = [m for m in state["messages"]
                        if not isinstance(m, ToolMessage)]

            # Filtra as mensagens retirando as que não possuem content
            messages = [m for m in messages if m.content]

            # Add prompt to our history
            messages = messages + \
                [HumanMessage(content=summary_message)]

            response = await chat.ainvoke(messages)

            # Remove todas menos as duas últimas mensagens
            remove_messages = [
                RemoveMessage(id=str(m.id))
                for m in state["messages"][:-4]
                if getattr(m, "id", None) is not None
            ]

            return CustomState(messages=cast(
                list[AnyMessage],
                remove_messages),
                summary=str(response.content))

        # Determine whether to end or summarize the conversation
        async def summarize_condition(state: CustomState) -> Literal["summarize_conversation", "chat"]:
            """Return the next node to execute."""

            messages = state["messages"]

            # If there are more than three messages, then we summarize the conversation
            if len(messages) > 6:
                return node_summarize_name

            # Otherwise we can just end
            return node_chat_name

        graph = StateGraph(CustomState)

        graph.add_node(node_prepare_name, prepare)
        graph.add_node(node_chat_name, invoke_chat)
        graph.add_node(node_tool_name, ToolNode(tools))
        graph.add_node(node_summarize_name, summarize_conversation)

        graph.add_edge(START, node_prepare_name)

        graph.add_conditional_edges(node_prepare_name, summarize_condition)
        graph.add_conditional_edges(node_chat_name, tools_condition)

        graph.add_edge(node_tool_name, node_prepare_name)
        graph.add_edge(node_summarize_name, node_chat_name)
        # graph.add_edge(node_chat_name, END)

        react_graph = graph.compile(checkpointer=memory)
        compiled_graph = react_graph.get_graph(xray=True)
        await render_graph(compiled_graph)

        # state = CustomState(messages=[message], summary="")
        config = RunnableConfig(configurable={"thread_id": "1"})

        print("\n\n---\n")

        input_message = HumanMessage(content="Quem é o presidente?")
        output = await react_graph.ainvoke(CustomState(messages=[input_message], summary=None), config=config)
        for m in output['messages']:
            m.pretty_print()

        print("\n\n---\n")

        message = HumanMessage(content="Eu sou Cleverson")
        output = await react_graph.ainvoke(CustomState(messages=[message], summary=None), config=config)
        for m in output['messages']:
            m.pretty_print()

        print("\n\n---\n")

        message = HumanMessage(
            content="Quero saber quem é o presidente do Brasil")
        output = await react_graph.ainvoke(CustomState(messages=[message], summary=None), config=config)
        for m in output['messages']:
            m.pretty_print()

        print("\n\n---\n")

        message = HumanMessage(content="Quantos anos ele tem?")
        output = await react_graph.ainvoke(CustomState(messages=[message], summary=None), config=config)
        for m in output['messages']:
            m.pretty_print()

        print("\n\n---\n")

        message = HumanMessage(content="Que dia é hoje?")
        output = await react_graph.ainvoke(CustomState(messages=[message], summary=None), config=config)
        for m in output['messages']:
            m.pretty_print()

        print("\n\n---\n")

        message = HumanMessage(content="Qual o sobrenome dele?")
        output = await react_graph.ainvoke(CustomState(messages=[message], summary=None), config=config)
        # for m in output['messages'][-1:]:
        for m in output['messages']:
            m.pretty_print()

        print("\n\n---\n")

        message = HumanMessage(content="Qual o nome real dele?")
        output = await react_graph.ainvoke(CustomState(messages=[message], summary=None), config=config)
        # for m in output['messages'][-1:]:
        for m in output['messages']:
            m.pretty_print()


if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    asyncio.run(main())
