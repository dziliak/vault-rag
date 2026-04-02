from __future__ import annotations

import sys


class OllamaError(Exception):
    pass


class OllamaNotAvailable(OllamaError):
    pass


def handle_ollama_error(err: Exception, context: str = "") -> None:
    msg = f"Ollama error ({context}): {err}"
    msg += "\n\nPlease ensure Ollama is running:"
    msg += "\n  - Start Ollama: ollama serve"
    msg += "\n  - Check status: curl http://localhost:11434"
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def check_ollama_connection(cfg) -> None:
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
