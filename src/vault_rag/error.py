from __future__ import annotations

from typing import NoReturn

from .config import RagConfig


class OllamaError(Exception):
    pass


class OllamaNotAvailable(OllamaError):
    pass


class OllamaExecutionError(OllamaError):
    pass


def handle_ollama_error(err: Exception, context: str = "") -> NoReturn:
    msg = f"Ollama error ({context}): {err}"
    msg += "\n\nPlease ensure Ollama is running:"
    msg += "\n  - Start Ollama: ollama serve"
    msg += "\n  - Check status: curl http://localhost:11434"
    raise OllamaExecutionError(msg)


def check_ollama_connection(cfg: RagConfig) -> None:
    import requests

    try:
        response = requests.get(f"{cfg.ollama_base_url}/api/tags", timeout=5)
        response.raise_for_status()
    except (requests.ConnectionError, requests.Timeout) as e:
        raise OllamaNotAvailable(
            f"Cannot connect to Ollama at {cfg.ollama_base_url}"
        ) from e
    except Exception as e:
        raise OllamaError(f"Failed to check Ollama status: {e}") from e
