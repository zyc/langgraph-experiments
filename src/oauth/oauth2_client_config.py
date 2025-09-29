"""Configurações do cliente OAuth2.

Define uma dataclass imutável com os parâmetros necessários para
autenticação via OAuth2, incluindo URLs, credenciais do cliente e
tempo limite para requisições.
"""

import os
from dataclasses import dataclass

from src.envvar import get_env

DEFAULT_AUTH_TIMEOUT = 300


@dataclass(frozen=True, kw_only=True)
class OAuth2ClientConfig:  # pylint: disable=too-few-public-methods
    """
    Classe de configuração para as definições do cliente OAuth2.

    Atributos:
        base_url (str | None): URL base do provedor OAuth2.
        auth_url (str): URL do endpoint de autorização.
        client_id (str): Identificador do cliente fornecido pelo provedor OAuth2.
        client_secret (str): Segredo do cliente fornecido pelo provedor OAuth2.
    auth_timeout (int, opcional): Tempo limite em segundos para obtenção do token OAuth2. Padrão é 300.
    """
    base_url: str | None = None
    auth_url: str
    client_id: str
    client_secret: str
    auth_timeout: int = DEFAULT_AUTH_TIMEOUT

    @staticmethod
    def from_env(
        base_url_var: str | None = "SERVICE_BASE_URL",
        auth_url_var: str = "OAUTH2_TOKEN_URL",
        client_id_var: str = "OAUTH2_CLIENT_ID",
        client_secret_var: str = "OAUTH2_CLIENT_SECRET",
        auth_timeout_var: str = "OAUTH2_AUTH_TIMEOUT",
    ) -> "OAuth2ClientConfig":
        """Cria uma instância usando variáveis de ambiente obrigatórias."""

        base_url_value = None
        if base_url_var:
            base_url_value = os.getenv(base_url_var, "").strip() or None

        # Busca o timeout da envvar, se existir, senão usa o padrão da dataclass
        env_timeout = os.getenv(auth_timeout_var)

        try:
            auth_timeout_value = int(
                env_timeout) if env_timeout is not None else DEFAULT_AUTH_TIMEOUT
        except ValueError:
            auth_timeout_value = DEFAULT_AUTH_TIMEOUT

        return OAuth2ClientConfig(
            base_url=base_url_value,
            auth_url=get_env(auth_url_var),
            client_id=get_env(client_id_var),
            client_secret=get_env(client_secret_var),
            auth_timeout=auth_timeout_value,
        )
