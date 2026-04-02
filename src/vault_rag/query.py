from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import chromadb
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

from .config import RagConfig
from .error import check_ollama_connection, handle_ollama_error, OllamaError


@dataclass
class Source:
    text: str
    score: float | None
    metadata: dict


def _load_index(cfg: RagConfig) -> VectorStoreIndex:
    try:
        check_ollama_connection(cfg)
    except OllamaError as e:
        handle_ollama_error(e, "loading index")

    try:
        Settings.llm = Ollama(
            model=cfg.llm_model,
            base_url=cfg.ollama_base_url,
            request_timeout=cfg.llm_request_timeout,
        )
        Settings.embed_model = OllamaEmbedding(
            model_name=cfg.embed_model,
            base_url=cfg.ollama_base_url,
            request_timeout=cfg.embed_request_timeout,
        )
    except Exception as e:
        handle_ollama_error(e, "initializing models")

    chroma_client = chromadb.PersistentClient(path=str(cfg.chroma_dir))
    chroma_collection = chroma_client.get_or_create_collection(cfg.collection)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store, storage_context=storage_context
    )


def ask(question: str, cfg: RagConfig) -> tuple[str, List[Source]]:
    try:
        index = _load_index(cfg)
        qe = index.as_query_engine(similarity_top_k=cfg.top_k)

        resp = qe.query(question)

        sources: List[Source] = []
        for sn in getattr(resp, "source_nodes", []) or []:
            sources.append(
                Source(
                    text=sn.node.get_text(),
                    score=getattr(sn, "score", None),
                    metadata=sn.node.metadata or {},
                )
            )

        return str(resp), sources
    except Exception as e:
        handle_ollama_error(e, "querying")
