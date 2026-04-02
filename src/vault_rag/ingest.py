from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

import chromadb
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

from .config import RagConfig
from .error import OllamaError, check_ollama_connection, handle_ollama_error


def _should_skip(path: Path, cfg: RagConfig) -> bool:
    parts = set(path.parts)
    if any(d in parts for d in cfg.ignore_dirs):
        return True
    return path.suffix.lower() not in cfg.include_exts


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest(cfg: RagConfig) -> dict[str, str]:
    try:
        return cast(dict[str, str], json.loads(cfg.manifest_path.read_text("utf-8")))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def _save_manifest(cfg: RagConfig, manifest: dict[str, str]) -> None:
    cfg.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), "utf-8"
    )


def build_or_update_index(vault_path: Path, cfg: RagConfig) -> tuple[int, int, int]:
    """
    Returns (added, updated, skipped)
    """
    try:
        check_ollama_connection(cfg)
    except OllamaError as e:
        handle_ollama_error(e, "checking connection")

    vault_path = vault_path.expanduser().resolve()
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault path does not exist: {vault_path}")

    try:
        Settings.llm = Ollama(
            model=cfg.llm_model,
            base_url=cfg.ollama_base_url,
            request_timeout=cfg.llm_request_timeout,
        )
        Settings.node_parser = SentenceSplitter(
            chunk_size=800,
            chunk_overlap=120,
        )
        Settings.embed_model = OllamaEmbedding(
            model_name=cfg.embed_model,
            base_url=cfg.ollama_base_url,
            request_timeout=cfg.embed_request_timeout,
        )
    except Exception as e:
        handle_ollama_error(e, "initializing models")

    # Chroma persistent store
    cfg.chroma_dir.mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=str(cfg.chroma_dir))
    chroma_collection = chroma_client.get_or_create_collection(cfg.collection)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Discover files
    all_files = [
        p for p in vault_path.rglob("*") if p.is_file() and not _should_skip(p, cfg)
    ]
    if not all_files:
        raise RuntimeError(f"No ingestible files found under: {vault_path}")

    # Manifest-driven incremental indexing
    manifest = _load_manifest(cfg)

    to_ingest: list[Path] = []
    added = updated = skipped = 0

    for f in all_files:
        key = str(f)
        digest = _sha256_file(f)
        if key not in manifest:
            to_ingest.append(f)
            manifest[key] = digest
            added += 1
        elif manifest[key] != digest:
            to_ingest.append(f)
            manifest[key] = digest
            updated += 1
        else:
            skipped += 1

    if not to_ingest:
        return (0, 0, skipped)

    try:
        for f in to_ingest:
            chroma_collection.delete(where={"file_path": str(f)})

        reader = SimpleDirectoryReader(
            input_files=[str(p) for p in to_ingest],
            filename_as_id=True,
            recursive=False,
        )
        documents = reader.load_data()

        _ = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, show_progress=True
        )

        _save_manifest(cfg, manifest)
    except Exception as e:
        handle_ollama_error(e, "processing documents")

    return (added, updated, skipped)
