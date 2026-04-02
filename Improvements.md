# Vault RAG Improvements

## Code Quality & Maintainability

### 1. Logging Instead of Print Statements
- Replace `print()` with Python `logging` module
- Add different log levels (DEBUG, INFO, WARNING, ERROR)
- Makes production debugging and monitoring much easier

### 2. Configuration Validation
- Add validation to `RagConfig` to ensure:
  - `ollama_base_url` is a valid URL
  - `top_k` is positive
  - `chroma_dir` is writable
  - Required file extensions start with `.`
- Add method to validate configuration before startup

## Functionality & Features

### 3. Add Configuration File Support
- Support loading config from `.env` file or `config.yaml`
- Allow users to specify default values in a config file
- CLI args should override config file values
- Example: `.vault-rag.yaml` with default models, chunk sizes, etc.

### 4. Better Chunking Strategy
- Currently uses fixed `SentenceSplitter` with hardcoded chunk size
- Implement heading-aware chunking (respecting Markdown structure)
- Add option for overlapping chunks based on semantic boundaries
- Consider document-type specific chunking (code blocks, lists, etc.)

### 5. File Format Support
- Add support for PDF, DOCX, RTF files
- Support Obsidian attachments (images, CSV, etc.)
- Add OCR for scanned documents (as mentioned in README)
- Consider Obsidian frontmatter processing

### 6. Metadata Enrichment
- Extract and store metadata from Markdown frontmatter (tags, title, creation date)
- Add file-level metadata (creation/modification time)
- Support custom metadata fields from config

### 7. Query Enhancements
- Add filtering by metadata (file path, tags, date range)
- Implement hybrid search (keyword + vector)
- Add re-ranking of results
- Support follow-up questions with conversation history

### 8. Incremental Indexing Improvements
- Currently deletes and re-ingests entire file on change
- Consider partial updates for large documents
- Add change detection based on file mtime in addition to hash

## Performance & Scalability

### 9. Batch Processing
- Process files in batches instead of one-by-one
- Use parallel processing for file hashing and ingestion
- Add progress bars with `tqdm` (partially implemented)

### 10. Embedding Caching
- Cache embeddings to avoid recomputing
- Useful when switching between different queries
- Can significantly speed up repeated queries

### 11. Chroma Configuration
- Allow tuning Chroma settings (distance metric, index type)
- Consider HNSW vs Flat index based on use case
- Add compression options for memory efficiency

## Testing & Development

### 12. Add Unit Tests
- Currently no tests exist
- Add tests for core functions with pytest
- Mock external dependencies (Ollama, Chroma)
- Test edge cases (empty vault, permission errors, etc.)

### 13. Integration Tests
- Add tests that run against actual Ollama/Chroma instances
- Create fixture vault for testing
- Test full pipeline: index → query → answer

### 14. Add Basic CLI Tests
- Test CLI argument parsing
- Test help output
- Test error handling for invalid paths

## Documentation

### 15. Improve README
- Add installation troubleshooting section
- Include examples of common use cases
- Add performance tuning tips
- Document environment variables better

### 16. Add Code Documentation
- Add docstrings to all public functions/classes
- Add type hints to all function signatures
- Document exception behavior

## Security & Reliability

### 17. Input Validation
- Sanitize file paths to prevent path traversal
- Validate user input for question/queries
- Handle malicious file names in vault

### 18. Manifest File Safety
- Add checksums to manifest for integrity verification
- Handle manifest corruption gracefully
- Backup manifest before writes

### 19. Timeout Configuration
- Make timeouts configurable via environment variables
- Add per-operation timeouts (ingest vs query)
- Consider adding progress timeouts

## User Experience

### 20. CLI Improvements
- Add `--verbose` flag for detailed output
- Add `--dry-run` mode to preview changes
- Add `--force` flag to override existing index
- Add `status` command to show index stats

### 21. Interactive Mode
- Add interactive chat mode for multi-turn conversations
- Add "ask again with different parameters" option
- Allow users to refine queries interactively

### 22. Export & Sharing
- Add ability to export query results
- Support saving query sessions
- Allow sharing of indexed vault (with proper licensing)

## Technical Debt

### 23. Modernize Imports
- Use modern Python imports: `dict` instead of `Dict`
- Replace `getattr()` patterns with proper type checking
- Use `Path` objects consistently instead of string paths

### 24. Remove Code Duplication
- `_load_index` in `query.py` and `build_or_update_index` in `ingest.py` duplicate model initialization
- Extract model initialization to a shared function
- Create a context manager for index access

### 25. Dependency Updates
- Check for newer LlamaIndex versions (0.10.0 is quite old)
- Consider using `llama-index-core` with `llama-index-llms-ollama` explicitly
- Review and update chromadb requirements

## Deployment & Operations

### 26. Docker Support
- Create Dockerfile for containerized deployment
- Add docker-compose for easy local development
- Include health checks and volume mounts

### 27. Health Monitoring
- Add `vault health` command to check system status
- Monitor Ollama and Chroma health
- Report disk usage for vector store

### 28. Backup Strategy
- Document backup procedures for `.chroma` directory
- Add `vault backup` command
- Consider incremental backup support
