"""Helpers to render LangGraph diagrams without relying on mermaid.ink."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from IPython.core.getipython import get_ipython
from IPython.display import Image, display
from langchain_core.runnables.graph_mermaid import \
    _render_mermaid_using_pyppeteer


async def render_graph(
    compiled_graph: Any,
    *,
    output_path: Path | str = Path("react_graph.png"),
) -> Path:
    """Render ``compiled_graph`` to PNG using Pyppeteer and handle presentation.

    The PNG is saved to ``output_path`` and:
    - displayed inline when running under IPython/Jupyter;
    - otherwise the absolute file path is printed to stdout.

    Returns the path to the generated PNG.
    """

    path = Path(output_path)
    png_bytes = await _render_mermaid_using_pyppeteer(
        compiled_graph.draw_mermaid(),
        output_file_path=str(path),
    )

    if get_ipython() is not None:
        display(Image(png_bytes))
    else:
        print(f"Mermaid graph rendered to {path.resolve()}")

    return path
