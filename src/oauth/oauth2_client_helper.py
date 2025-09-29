"""Utilitários para cliente OAuth2 assíncrono.

Fornece um gerenciador de contexto para criar e fechar um
``AsyncOAuth2Client`` e uma camada simples de cache/renovação de
tokens baseada em expiração.
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from authlib.integrations.httpx_client import AsyncOAuth2Client

from .oauth2_client_config import OAuth2ClientConfig


@asynccontextmanager
async def get_oauth2_http_client(
    config: OAuth2ClientConfig,
    on_new_token: Callable[[], None] | None = None,
) -> AsyncGenerator[AsyncOAuth2Client, None]:
    """Cria e gerencia um ``AsyncOAuth2Client`` autenticado.

    Obtém e configura automaticamente um token OAuth2 (com cache e
    renovação) antes de entregar o cliente ao chamador e garante o
    fechamento do cliente ao final do contexto.

    Args:
        config: Configurações do cliente OAuth2 (URLs e credenciais).
        on_new_token: Callback opcional chamado quando um novo token é
            obtido e aplicado ao cliente.

    Yields:
        AsyncOAuth2Client: Cliente HTTP autenticado via OAuth2.
    """
    client: AsyncOAuth2Client | None = None

    try:
        client_kwargs = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "verify": False,
            "timeout": config.auth_timeout,
        }
        if config.base_url:
            client_kwargs["base_url"] = config.base_url

        client = AsyncOAuth2Client(**client_kwargs)

        await _ensure_token(client, config, on_new_token)
        yield client

    finally:
        if client is not None:
            await client.aclose()


_TOKENS: dict[str, dict] = {}
_TOKEN_EXPS: dict[str, float] = {}


async def get_oauth2_token(
    config: OAuth2ClientConfig,
    on_new_token: Callable[[], None] | None = None,
) -> str:
    """Obtém e retorna um token OAuth2 válido para a configuração fornecida."""
    async with get_oauth2_http_client(config, on_new_token) as client:
        token_data: dict[str, str] | None = getattr(client, "token", None)
        if not token_data:
            msg = "OAuth2 client did not return a token payload."
            raise RuntimeError(msg)

        access_token = token_data.get("access_token")
        if not access_token:
            msg = "Token payload is missing the 'access_token' field."
            raise RuntimeError(msg)

        return access_token


async def _ensure_token(
    client: AsyncOAuth2Client,
    config: OAuth2ClientConfig,
    on_new_token: Callable[[], None] | None = None,
) -> None:
    """Garante que o cliente possua um token OAuth2 válido e em cache."""
    key = f"{config.auth_url}:{config.client_id}"
    token = _TOKENS.get(key)
    exp = _TOKEN_EXPS.get(key, 0)

    if token is None or time.time() >= exp:
        token_response = await client.fetch_token(config.auth_url)
        _TOKENS[key] = token_response
        _TOKEN_EXPS[key] = time.time() + token_response["expires_in"] - 60

        client.token_auth.set_token(token_response)

        if on_new_token is not None:
            on_new_token()
    else:
        client.token_auth.set_token(token)
