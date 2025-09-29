
"""Simple Hello World entry point module."""

import asyncio
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from prettyprinter import pprint

from src.chat_kargs import get_chat_kargs


async def main() -> None:
    """Entry point of the program. Obtains an OAuth token and runs a sample chat."""

    chat_kwargs = await get_chat_kargs()
    chat = ChatOpenAI(**chat_kwargs)

    prompt = SystemMessage(
        content=(
            "Você é um assistente que responde apenas 'sim' ou 'não', "
            "mas sempre explica utilizando o contexto fornecido."
        )
    )

    message = await chat.ainvoke(
        [
            prompt,
            HumanMessage(content="que dia é hoje exatamente?"),
        ]
    )

    pprint(message.content)


if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    asyncio.run(main())
