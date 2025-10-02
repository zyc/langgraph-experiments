"""Helpers to render LangGraph diagrams without relying on mermaid.ink."""
from __future__ import annotations

import asyncio
import atexit
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any
from uuid import uuid4
from langchain_core.runnables.graph import MermaidDrawMethod


_PNG_EXECUTOR: ProcessPoolExecutor | None = None


def _get_png_executor() -> ProcessPoolExecutor:
    """Create a process executor lazily so pyppeteer runs in main thread."""
    global _PNG_EXECUTOR
    if _PNG_EXECUTOR is None:
        _PNG_EXECUTOR = ProcessPoolExecutor(max_workers=1)
        atexit.register(_PNG_EXECUTOR.shutdown, wait=False)
    return _PNG_EXECUTOR


def _render_png_via_pyppeteer(
    mermaid_syntax: str,
    background_color: str,
    padding: int,
    output_file_path: Path,
) -> Path:
    """Helper executed in a separate process to avoid nested event loops."""
    from langchain_core.runnables.graph_mermaid import draw_mermaid_png

    draw_mermaid_png(
        mermaid_syntax=mermaid_syntax,
        draw_method=MermaidDrawMethod.PYPPETEER,
        background_color=background_color,
        padding=padding,
        output_file_path=str(output_file_path),
    )
    return output_file_path


async def render_graph(compiled_graph: Any) -> None:
    """Renderiza o grafo compilado."""
    # render_ascii_graph(compiled_graph)
    await render_png_graph(compiled_graph)


def render_mermaid_graph(compiled_graph: Any) -> None:
    """Renderiza o grafo compilado em Mermaid e imprime no terminal."""
    if hasattr(compiled_graph, "draw_mermaid"):
        mermaid_graph = compiled_graph.draw_mermaid()
    else:
        mermaid_graph = compiled_graph.draw_ascii()

    print(mermaid_graph)


async def render_png_graph(compiled_graph: Any) -> Path:
    """Renderiza o grafo compilado em PNG, salva e informa o caminho."""
    loop = asyncio.get_running_loop()
    mermaid_syntax = compiled_graph.draw_mermaid()

    output_dir = Path("artifacts/graphs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"langgraph_{uuid4().hex}.png"

    draw = partial(
        _render_png_via_pyppeteer,
        mermaid_syntax,
        "white",
        10,
        output_path,
    )

    png_path = await loop.run_in_executor(_get_png_executor(), draw)
    print(f"Mermaid graph PNG salvo em: {png_path}")
    return png_path


def render_ascii_graph(compiled_graph: Any) -> None:
    """Renderiza o grafo compilado em ASCII e imprime no terminal."""
    if hasattr(compiled_graph, "draw_ascii"):
        ascii_graph = compiled_graph.draw_ascii()
    else:
        ascii_graph = compiled_graph.draw_mermaid()

    print(ascii_graph)
