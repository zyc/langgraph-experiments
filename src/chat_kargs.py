"""Helpers para montar kwargs do modelo de chat."""

from src.envvar import get_env
from src.oauth import OAuth2ClientConfig, get_oauth2_token


async def get_chat_kargs():
    """Produz um dicionário com os parâmetros necessários para ``ChatOpenAI``.

    Inclui ``base_url`` obrigatório a partir da variável ``VLLM_BASE_URL``.
    """
    config = OAuth2ClientConfig.from_env()

    access_token = await get_oauth2_token(config)
    vllm_model_id = get_env("VLLM_MODEL_ID")
    base_url = get_env("VLLM_BASE_URL").rstrip("/")

    chat_kwargs = {
        "model": vllm_model_id,
        "temperature": 0,
        "default_headers": {"Authorization": f"Bearer {access_token}"},
        "base_url": base_url,
        "api_key": "EMPTY",

    }

    return chat_kwargs
