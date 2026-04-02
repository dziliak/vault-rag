# vault-rag

Minimal local RAG over an Obsidian vault using Ollama, LlamaIndex, and Chroma
====

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

- `ollama pull qwen2.5:32b` (main LLM for responses)
- `ollama pull bge-m3` (embedding model for vector search)

3) Index your vault:
    `vault index ~/Documents/Obsidian/obsidian_vault`

4) Ask questions:
    `vault ask ~/Documents/Obsidian/obsidian_vault "What notes mention borg backups and sleep?"`

## Installation Troubleshooting

### Common Ollama Issues

**Error: `Connection refused` or `Ollama not running`**
- Ensure Ollama is installed: `ollama --version`
- Start Ollama service: `ollama serve` (or restart your system)
- Verify Ollama is accessible: `curl http://localhost:11434/api/tags`
- If using a custom Ollama URL, set `OLLAMA_BASE_URL` environment variable

**Error: `Model not found` when pulling models**
- Check available models: `ollama list`
- Ensure internet connection is working
- Try pulling with explicit tag: `ollama pull qwen2.5:32b`

**Error: `Out of memory` during model operations**
- Use smaller models: `ollama pull qwen2.5:7b` instead of `qwen2.5:32b`
- Reduce embedding batch size in `.vault-rag.yaml` with `chunk_size: 400`
- Close other memory-intensive applications

### Common Chroma Issues

**Error: `ChromaDB initialization failed`**
- Delete corrupted database: `rm -rf .chroma`
- Ensure directory is writable: `chmod +w .chroma`
- Use a different directory by setting `CHROMA_DB_DIR=/path/to/chroma`

**Error: `Collection already exists`**
- Reset index: `rm -rf .chroma && vault index /path/to/vault`
- Or use a different collection name: `export COLLECTION_NAME="new_collection"`

### Common Dependencies Issues

**Error: `uv pip install` fails with compilation errors**
- Ensure system has build tools: `sudo apt-get install build-essential` (Linux) or Xcode (macOS)
- Try installing with system Python: `pip install -e .`
- Use a specific Python version: `pyenv local 3.11`

**Error: `Module not found` after installation**
- Verify virtual environment is activated: `which python`
- Reinstall: `uv pip install --force-reinstall -e .`
- Check installed packages: `uv pip list | grep llama-index`

### Verify Installation

Run these commands to verify all components work:
```bash
ollama list
curl http://localhost:11434/api/tags
vault --help
vault index /path/to/vault --dry-run
```

## Configuration

### Specifying a different Ollama LLM

By default, the project uses `qwen2.5:32b` for LLM and `bge-m3` for embeddings. To use different models, set environment variables:

```bash
export OLLAMA_LLM_MODEL="llama3:8b"
export OLLAMA_EMBED_MODEL="nomic-embed-text"
```

Available models are listed at [Ollama library](https://ollama.com/library).

### Configuration Files

The project supports two configuration methods:

1. **Environment variables** (highest priority)
2. **YAML config file**: `.vault-rag.yaml` or `config.yaml`
3. **CLI arguments** (overrides config file)

Example config file: `.vault-rag.yaml`:
```yaml
chroma_dir: ".chroma"
collection: "obsidian"
ollama_base_url: "http://localhost:11434"
llm_model: "qwen2.5:32b"
embed_model: "bge-m3"
top_k: 8
chunk_size: 800
chunk_overlap: 120
include_exts: ".md", ".txt"
ignore_dirs: ".obsidian", ".trash", "Attachments", ".git"
llm_request_timeout: 600.0
embed_request_timeout: 600.0
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base URL for Ollama API |
| `LLM_MODEL` | `qwen2.5:32b` | Ollama model for LLM responses |
| `EMBED_MODEL` | `bge-m3` | Ollama model for embeddings |
| `CHROMA_DB_DIR` | `.chroma` | Directory for Chroma vector store |
| `COLLECTION_NAME` | `obsidian` | Chroma collection name |
| `TOP_K` | `8` | Number of similar chunks to retrieve |
| `CHUNK_SIZE` | `800` | Character chunk size for document splitting |
| `CHUNK_OVERLAP` | `120` | Overlap between chunks |
| `INCLUDE_EXTS` | `.md,.txt` | Comma-separated file extensions to index |
| `IGNORE_DIRS` | `.obsidian,.trash,Attachments,.git` | Comma-separated directory names to skip |
| `LLM_REQUEST_TIMEOUT` | `600.0` | Timeout for LLM requests (seconds) |
| `EMBED_REQUEST_TIMEOUT` | `600.0` | Timeout for embedding requests (seconds) |

## Use Cases

### Basic Research
Search across your entire Obsidian vault for specific topics:
```bash
vault ask ~/Documents/Obsidian/obsidian_vault "What are the key principles of GTD methodology?"
```

### Technical Documentation
Query your project documentation:
```bash
vault ask ~/Documents/GitHub/project-docs "How do I configure the logging system?"
```

### Personal Knowledge Base
Retrieve information from personal notes:
```bash
vault ask ~/Documents/Obsidian/personal "What recipes did I save from chef_mike?"
```

### Multi-File Analysis
Find connections across multiple notes:
```bash
vault ask ~/Documents/Obsidian/obsidian_vault "What notes mention both machine learning and Python?"
```

### Date-Specific Searches
With filtering (future improvement):
```bash
vault ask ~/Documents/Obsidian/obsidian_vault "What did I write about climate change in 2024?"
```

## Performance Tuning

### Indexing Speed

**Increase parallel processing**
- Process files in larger batches by adjusting chunk settings
- Skip_reindexing for unchanged files (automatic in v0.1.0)

**Optimize chunking parameters**
```yaml
chunk_size: 400    # Smaller chunks = faster indexing, less context
chunk_overlap: 50  # Less overlap = faster processing
```

**Limit file types**
```yaml
include_exts: ".md"  # Exclude .txt if not needed
```

### Query Performance

**Reduce retrieval size**
```bash
export TOP_K=4  # Retrieve fewer chunks for faster responses
```

**Use faster models**
```bash
export LLM_MODEL="qwen2.5:7b"      # Faster than 32b
export EMBED_MODEL="nomic-embed-text"  # Faster than bge-m3
```

**Pre-compute embeddings**
- Cache embeddings to avoid recomputing for similar queries
- Use `.env` file for persistent settings

### Memory Optimization

**For large vaults (10k+ files)**
```yaml
chunk_size: 300    # Smaller chunks use less memory
top_k: 4           # Retrieve fewer results
```

**Monitor Chroma storage**
- Chroma database is stored in `.chroma/` directory
- Regularly backup: `cp -r .chroma .chroma-backup-$(date +%Y%m%d)`
- Reset if corrupted: `rm -rf .chroma && vault index /path/to/vault`

### Index Maintenance

**Rebuild index**
```bash
rm -rf .chroma
vault index ~/Documents/Obsidian/obsidian_vault
```

**Incremental updates**
- The system automatically detects changed files
- Only re-process modified files for faster updates

## Planned Improvements

- Heading-aware chunking
- Include PDFs/DOCX/etc attachments
- Add OCR for embedding screenshots of printed text
- Add OCR for handwritten notes using a vision LLM
- Maybe create an Obsidian plugin to integrate this directly into Obsidian

## Configuration Reference

See `.env.example` and `.vault-rag.yaml.example` for complete configuration templates.

All configuration options can be set via environment variables or YAML config file. CLI arguments take precedence over both.

### Example: Development Setup

Create a `.env` file for your project:
```bash
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=qwen2.5:7b
EMBED_MODEL=bge-m3
TOP_K=5
CHUNK_SIZE=600
CHUNK_OVERLAP=100
CHROMA_DB_DIR=.chroma-dev
```

### Example: Production Setup

Create a `.vault-rag.yaml` file:
```yaml
chroma_dir: "/data/chroma"
collection: "production"
ollama_base_url: "http://ollama-server:11434"
llm_model: "llama3:70b"
embed_model: "bge-large"
top_k: 10
chunk_size: 1000
include_exts: ".md", ".txt", ".pdf"
ignore_dirs: ".git", ".svn", "node_modules"
```

## License

MIT
