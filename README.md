# vault-rag

=======

Minimal local RAG over an Obsidian vault using Ollama, LlamaIndex, and Chroma
=======

Minimal local RAG over an Obsidian vault using:
- Ollama (LLM + embeddings)
- LlamaIndex (RAG)
- Chroma (vector store)

## Quickstart

1) Install deps (uv recommended):
   uv venv
   source .venv/bin/activate
   uv pip install -e .

2) Pull models:
   ollama pull qwen2.5:32b
   ollama pull bge-m3

3) Index your vault:
   vault index ~/Documents/Obsidian/obsidian_vault

4) Ask questions:
   vault ask ~/Documents/Obsidian/obsidian_vault "What notes mention borg backups and sleep?"

