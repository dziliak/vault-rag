from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RagConfig:
    # Where Chroma persists embeddings (relative to project root by default)
    chroma_dir: Path = Path(".chroma")
    collection: str = "obsidian"
    manifest_path: Path = Path(".chroma/manifest.json")

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:32b"
    embed_model: str = "bge-m3"

    # Retrieval
    top_k: int = 8

    # Vault ingest rules
    include_exts: tuple[str, ...] = (".md", ".txt")
    ignore_dirs: tuple[str, ...] = (".obsidian", ".trash", "Attachments", ".git")

    llm_request_timeout: float = 600.0   # 10 minutes
    embed_request_timeout: float = 600.0 # 10 minutes

