from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import RagConfig
from .error import OllamaExecutionError
from .ingest import build_or_update_index
from .query import ask

logger = None


def get_logger():
    global logger
    if logger is None:
        import logging

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger("vault-rag")
    return logger


def main() -> None:
    p = argparse.ArgumentParser(
        prog="vault", description="Minimal local RAG over an Obsidian vault"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index", help="Ingest vault markdown into Chroma")
    p_index.add_argument("vault_path", type=str, help="Path to Obsidian vault")

    p_ask = sub.add_parser(
        "ask", help="Ask a question (retrieves from Chroma + answers with Ollama)"
    )
    p_ask.add_argument(
        "vault_path",
        type=str,
        help="Path to Obsidian vault (used only for consistency)",
    )
    p_ask.add_argument("question", type=str, help="Question to ask")
    p_ask.add_argument(
        "--top-k", type=int, default=None, help="Override retrieval top_k"
    )

    p_ret = sub.add_parser("retrieve", help="Show retrieved chunks (debug retrieval)")
    p_ret.add_argument("question", type=str)
    p_ret.add_argument("--top-k", type=int, default=None)

    args = p.parse_args()
    cfg = RagConfig()
    logger = get_logger()

    try:
        if args.cmd == "index":
            added, updated, skipped = build_or_update_index(Path(args.vault_path), cfg)
            logger.info(f"Indexed into {cfg.chroma_dir}/ (collection={cfg.collection})")
            logger.info(f"added={added} updated={updated} skipped={skipped}")
            return

        if args.cmd == "ask":
            if args.top_k is not None:
                cfg = RagConfig(top_k=args.top_k)

            answer, sources = ask(args.question, cfg)

            logger.info("Answer retrieved successfully")
            print("\n=== ANSWER ===\n")
            print(answer)

            print("\n=== SOURCES ===\n")
            for i, s in enumerate(sources, 1):
                path = (
                    s.metadata.get("file_path")
                    or s.metadata.get("filename")
                    or s.metadata.get("file_name")
                )
                print(f"[{i}] score={s.score}  {path}")
                snippet = (s.text or "").strip().replace("\n", " ")
                print(f"    {snippet[:240]}{'…' if len(snippet) > 240 else ''}\n")
            return

        if args.cmd == "retrieve":
            if args.top_k is not None:
                cfg = RagConfig(top_k=args.top_k)
            _, sources = ask(args.question, cfg)
            logger.info(f"Retrieved {len(sources)} sources")
            for i, s in enumerate(sources, 1):
                path = (
                    s.metadata.get("file_path")
                    or s.metadata.get("filename")
                    or s.metadata.get("file_name")
                )
                print(f"[{i}] score={s.score} {path}")
                print((s.text or "").strip()[:800])
                print()
            return
    except OllamaExecutionError as e:
        logger.error(f"Ollama error: {e}")
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
