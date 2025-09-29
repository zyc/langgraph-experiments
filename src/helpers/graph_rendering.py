"""Helpers to render LangGraph diagrams without relying on mermaid.ink."""

from __future__ import annotations

from typing import Any


def render_graph(compiled_graph: Any) -> None:
    """Renderiza o grafo compilado em ASCII e imprime no terminal."""
    if hasattr(compiled_graph, "draw_ascii"):
        ascii_graph = compiled_graph.draw_ascii()
    else:
        ascii_graph = compiled_graph.draw_mermaid()

    print(ascii_graph)
