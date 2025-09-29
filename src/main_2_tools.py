"""Simple Hello World entry point module."""


import asyncio
import sys
from datetime import datetime
from pathlib import Path

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from prettyprinter import pprint

from src.helpers import get_chat_kargs


def agora() -> datetime:
    """Obtém o dia e hora atuais."""
    return datetime.now()


async def main() -> None:
    """Entry point of the program. Obtains an OAuth token and runs a sample chat."""

    tools = [agora]

    chat_kwargs = await get_chat_kargs()
    chat = ChatOpenAI(**chat_kwargs)
    chat = chat.bind_tools(tools)

    message = await chat.ainvoke(
        [
            HumanMessage(content="que dia é hoje exatamente?"),
        ]
    )

    pprint(message.additional_kwargs.get("tool_calls", []))


if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    asyncio.run(main())
