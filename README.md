# vault-rag

Minimal local RAG over an Obsidian vault using Ollama, LlamaIndex, and Chroma
=======

Minimal local RAG over an Obsidian vault using:
- Ollama (LLM + embeddings)
- LlamaIndex (RAG)
- Chroma (vector store)

Shamelessly vibe coded w/ ChatGPT

## Quickstart

1) Install deps (uv recommended):
- `uv venv`
- `source .venv/bin/activate`
- `uv pip install -e .`

2) Pull models:

- `ollama pull qwen2.5:32b`
- `ollama pull bge-m3`

3) Index your vault:
    `vault index ~/Documents/Obsidian/obsidian_vault`

4) Ask questions:
    `vault ask ~/Documents/Obsidian/obsidian_vault "What notes mention borg backups and sleep?"`

## Configuration

### Specifying a different Ollama LLM

By default, the project uses `qwen2.5:32b` for LLM and `bge-m3` for embeddings. To use different models, set environment variables:

```bash
export OLLAMA_LLM_MODEL="llama3:8b"
export OLLAMA_EMBED_MODEL="nomic-embed-text"
```

Available models are listed at [Ollama library](https://ollama.com/library).

### Other configuration options

The project reads the following environment variables:

- `OLLAMA_BASE_URL` - Ollama API URL (default: `http://localhost:11434`)
- `CHROMA_DB_DIR` - Directory for Chroma vector store (default: `.chroma`)
- `COLLECTION_NAME` - Chroma collection name (default: `obsidian`)

## Planned Improvements

- Heading-aware chunking
- Include PDFs/DOCX/etc attachments
- Add OCR for embedding screenshots of printed text
- Add OCR for handwritten notes using a vision LLM
- Maybe create an Obsidian plugin to integrate this directly into Obsidian
