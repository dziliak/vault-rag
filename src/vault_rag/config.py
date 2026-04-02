from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigValidationError(Exception):
    pass


def _is_valid_url(url: str) -> bool:
    """Check if a string is a valid HTTP/HTTPS URL."""
    try:
        from urllib3.util import parse_url

        parsed = parse_url(url)
        return parsed.scheme in ("http", "https") and parsed.host is not None
    except Exception:
        return False


def _is_writable_dir(path: Path) -> bool:
    """Check if a directory is writable."""
    try:
        test_file = path / ".test_write"
        test_file.touch()
        test_file.unlink()
        return True
    except (OSError, IOError):
        return False


def _validate_file_extensions(exts: tuple[str, ...]) -> bool:
    """Validate that all extensions start with a dot."""
    return all(ext.startswith(".") for ext in exts)


def _load_env_config() -> dict[str, Any]:
    """Load configuration from .env file."""
    config = {}
    env_path = Path(".env")
    if env_path.exists():
        with env_path.open("r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip().lower()] = value.strip()
    return config


def _load_yaml_config() -> dict[str, Any]:
    """Load configuration from config.yaml or .vault-rag.yaml file."""
    config = {}
    config_paths = [Path(".vault-rag.yaml"), Path("config.yaml")]
    for config_path in config_paths:
        if config_path.exists():
            with config_path.open("r") as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    config.update(loaded)
            break
    return config


def _parse_bool(value: str) -> bool:
    """Parse string boolean values."""
    return str(value).lower() in ("true", "1", "yes")


def _parse_int_list(value: str) -> tuple[int, ...]:
    """Parse comma-separated string to tuple of ints."""
    return tuple(int(x.strip()) for x in str(value).split(",") if x.strip())


def _parse_str_list(value: str) -> tuple[str, ...]:
    """Parse comma-separated string to tuple of strings."""
    return tuple(x.strip() for x in str(value).split(",") if x.strip())


@dataclass(frozen=True)
class RagConfig:
    chroma_dir: Path = Path(".chroma")
    collection: str = "obsidian"
    manifest_path: Path = Path(".chroma/manifest.json")
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:32b"
    embed_model: str = "bge-m3"
    top_k: int = 8
    include_exts: tuple[str, ...] = (".md", ".txt")
    ignore_dirs: tuple[str, ...] = (".obsidian", ".trash", "Attachments", ".git")
    llm_request_timeout: float = 600.0
    embed_request_timeout: float = 600.0
    chunk_size: int = 800
    chunk_overlap: int = 120

    @classmethod
    def from_file(cls, cli_overrides: dict[str, Any] | None = None) -> RagConfig:
        """Load configuration from file(s) and apply CLI overrides."""
        env_config = _load_env_config()
        yaml_config = _load_yaml_config()

        config = {}
        config.update(yaml_config)
        config.update(env_config)

        def get_value(key: str, cli_key: str | None = None) -> Any:
            cli_key = cli_key or key
            if cli_overrides and cli_overrides.get(cli_key) is not None:
                return cli_overrides[cli_key]
            # Try both the key directly and lowercase version for env vars
            if key.lower() in config:
                value = config[key.lower()]
                if isinstance(value, str):
                    return cls._convert_type(key, value)
                return value
            if key in config:
                value = config[key]
                if isinstance(value, str):
                    return cls._convert_type(key, value)
                return value
            return getattr(cls, key)

        def get_list_value(key: str, default: tuple[str, ...]) -> tuple[str, ...]:
            value = get_value(key)
            if isinstance(value, (list, tuple)):
                return tuple(str(x) for x in value)
            if isinstance(value, str):
                return _parse_str_list(value)
            return default

        return cls(
            chroma_dir=Path(get_value("chroma_dir")),
            collection=get_value("collection"),
            manifest_path=Path(get_value("manifest_path")),
            ollama_base_url=get_value("ollama_base_url"),
            llm_model=get_value("llm_model"),
            embed_model=get_value("embed_model"),
            top_k=int(get_value("top_k")),
            include_exts=get_list_value("include_exts", cls.include_exts),
            ignore_dirs=get_list_value("ignore_dirs", cls.ignore_dirs),
            llm_request_timeout=float(get_value("llm_request_timeout")),
            embed_request_timeout=float(get_value("embed_request_timeout")),
            chunk_size=int(get_value("chunk_size")),
            chunk_overlap=int(get_value("chunk_overlap")),
        )

    @classmethod
    def _convert_type(cls, key: str, value: str) -> Any:
        """Convert string values to appropriate types based on config key."""
        if key in ("top_k", "chunk_size", "chunk_overlap"):
            return int(value)
        elif key in (
            "llm_request_timeout",
            "embed_request_timeout",
        ):
            return float(value)
        elif key in ("include_exts", "ignore_dirs"):
            return _parse_str_list(value)
        return value

    def validate(self) -> None:
        """Validate configuration and raise ValueError if invalid."""
        try:
            if not _is_valid_url(self.ollama_base_url):
                raise ConfigValidationError(
                    f"Invalid ollama_base_url: {self.ollama_base_url}. "
                    "Must be a valid HTTP/HTTPS URL."
                )

            if self.top_k <= 0:
                raise ConfigValidationError(f"top_k must be positive, got {self.top_k}")

            if not self.chroma_dir.is_dir():
                try:
                    self.chroma_dir.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise ConfigValidationError(
                        f"Cannot create chroma_dir: {self.chroma_dir}. Error: {e}"
                    ) from e

            if not _is_writable_dir(self.chroma_dir):
                raise ConfigValidationError(
                    f"chroma_dir is not writable: {self.chroma_dir}"
                )

            if not _validate_file_extensions(self.include_exts):
                raise ConfigValidationError(
                    f"All include_exts must start with '.': {self.include_exts}"
                )
        except ConfigValidationError:
            raise
        except Exception as e:
            raise ConfigValidationError(f"Unexpected validation error: {e}") from e
