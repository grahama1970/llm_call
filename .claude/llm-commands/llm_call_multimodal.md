# LLM Call Multimodal Commands

Advanced multimodal LLM interface supporting images, text files, and corpus/directory analysis.

## Basic Multimodal Commands

/llm_call_multimodal "[prompt]" [file_or_directory] [model]
Description: Analyze images, text files, or entire directories with LLM
Arguments:
  - prompt: Your analysis prompt or question
  - file_or_directory: Path to image, text file, or directory
  - model: (optional) Model to use (default: claude-3-5-sonnet-20241022)
```bash
# Analyze a single image
llm-cli multimodal "What's in this image?" /path/to/image.jpg

# Analyze a text file
llm-cli multimodal "Summarize this document" /path/to/document.txt

# Analyze an entire directory (corpus analysis)
llm-cli multimodal "Analyze the themes in these documents" /path/to/documents/

# With specific model
llm-cli multimodal "Explain this diagram" diagram.png --model gpt-4-vision-preview
```

## Directory/Corpus Analysis

/llm_call_multimodal_corpus "[prompt]" [directory] [options]
Description: Analyze collections of documents in a directory
Arguments:
  - prompt: Analysis prompt for the corpus
  - directory: Path to directory containing documents
  - options: --recursive, --pattern, --max-files, --chunk-size
```bash
# Analyze all text files in a directory
llm-cli multimodal "Find common themes across these documents" /path/to/corpus/

# Recursive directory traversal
llm-cli multimodal "Summarize the key points from all documentation" /docs/ --recursive

# Filter by file pattern
llm-cli multimodal "Extract all API endpoints mentioned" /src/ --pattern "*.py" --recursive

# Limit number of files (for large directories)
llm-cli multimodal "What are the main topics?" /large/corpus/ --max-files 50

# Custom chunk size for large files
llm-cli multimodal "Analyze writing style" /books/ --chunk-size 5000
```

## Supported File Types

### Images
- PNG, JPG/JPEG, GIF, WebP
- Automatic compression for large images
- Support for both local files and URLs

### Text Documents
- Plain text: .txt, .md, .rst
- Code: .py, .js, .java, .cpp, .go, .rs, .ts, .jsx, .tsx
- Data: .json, .yaml, .yml, .xml, .csv
- Documentation: .md, .rst, .tex
- Configuration: .ini, .cfg, .conf, .toml

### Corpus Organization
- Flat directory structure
- Nested directories (with --recursive)
- Mixed content (images + text)
- Filtered by patterns

## Advanced Features

/llm_call_multimodal_batch [directory] [analysis_file]
Description: Batch process directory with multiple analysis prompts
Arguments:
  - directory: Directory to analyze
  - analysis_file: JSON/YAML file with analysis configurations
```bash
# Batch analysis with config file
llm-cli multimodal-batch /project/src/ analysis_config.json

# Example analysis_config.json:
{
  "analyses": [
    {
      "prompt": "Find security vulnerabilities",
      "pattern": "*.py",
      "output": "security_report.md"
    },
    {
      "prompt": "Generate API documentation",
      "pattern": "api/*.py",
      "output": "api_docs.md"
    }
  ]
}
```

/llm_call_multimodal_compare [file1] [file2] "[prompt]"
Description: Compare two files or directories
Arguments:
  - file1: First file or directory
  - file2: Second file or directory
  - prompt: Comparison criteria
```bash
# Compare two images
llm-cli multimodal-compare old_design.png new_design.png "What changed?"

# Compare two directories
llm-cli multimodal-compare v1/docs/ v2/docs/ "What are the major changes?"

# Compare code versions
llm-cli multimodal-compare old_version.py new_version.py "Explain the refactoring"
```

## Context Management

/llm_call_multimodal_chunked "[prompt]" [directory] [strategy]
Description: Smart chunking for large corpus analysis
Arguments:
  - prompt: Analysis prompt
  - directory: Directory to analyze
  - strategy: chunking strategy (token, semantic, file)
```bash
# Token-based chunking (default 4000 tokens)
llm-cli multimodal "Summarize content" /large/docs/ --strategy token

# Semantic chunking (keeps related content together)
llm-cli multimodal "Extract key concepts" /research/ --strategy semantic

# File-based chunking (process files individually)
llm-cli multimodal "Review each file" /code/ --strategy file

# Custom token limit
llm-cli multimodal "Analyze" /data/ --strategy token --max-tokens 8000
```

## Output Formats

/llm_call_multimodal_report "[prompt]" [directory] [format]
Description: Generate structured reports from corpus analysis
Arguments:
  - prompt: Analysis prompt
  - directory: Directory to analyze
  - format: Output format (markdown, json, html, csv)
```bash
# Markdown report
llm-cli multimodal "Technical review" /project/ --output-format markdown > report.md

# JSON structured data
llm-cli multimodal "Extract entities" /documents/ --output-format json > entities.json

# HTML report with visualizations
llm-cli multimodal "Statistical analysis" /data/ --output-format html > analysis.html

# CSV for data extraction
llm-cli multimodal "Extract table data" /reports/ --output-format csv > data.csv
```

## Implementation Examples

### Python Implementation
```python
import asyncio
from pathlib import Path
from llm_call.core.caller import call_llm
from llm_call.core.utils.multimodal_utils import prepare_multimodal_messages

async def analyze_corpus(directory: str, prompt: str, recursive: bool = False, pattern: str = "*"):
    """Analyze a directory of documents"""
    path = Path(directory)
    
    # Collect files
    if recursive:
        files = list(path.rglob(pattern))
    else:
        files = list(path.glob(pattern))
    
    # Filter to supported text files
    text_extensions = {'.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', '.xml', '.csv'}
    text_files = [f for f in files if f.suffix.lower() in text_extensions]
    
    # Read and concatenate content
    corpus_content = []
    for file in text_files[:50]:  # Limit to prevent token overflow
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            corpus_content.append(f"=== {file.name} ===\n{content}\n")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Prepare message
    full_content = "\n".join(corpus_content)
    messages = [{
        "role": "user",
        "content": f"{prompt}\n\nDocuments:\n{full_content}"
    }]
    
    # Call LLM
    response = await call_llm({
        "messages": messages,
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4000
    })
    
    return response.choices[0].message.content

# Usage
result = asyncio.run(analyze_corpus(
    "/path/to/docs/",
    "Summarize the main topics covered in these documents",
    recursive=True,
    pattern="*.md"
))
```

### CLI Implementation
```bash
#!/bin/bash
# Analyze directory with chunking

DIRECTORY="$1"
PROMPT="$2"
CHUNK_SIZE=${3:-10}  # Files per chunk

# Find all text files
find "$DIRECTORY" -type f \( -name "*.txt" -o -name "*.md" -o -name "*.py" \) | \
while IFS= read -r file; do
    echo "=== $(basename "$file") ==="
    head -n 1000 "$file"  # Limit lines per file
done | \
xargs -I {} llm-cli ask "$PROMPT\n\nContent:\n{}" --model claude-3-5-sonnet-20241022
```

## Multimodal Combinations

/llm_call_multimodal_mixed "[prompt]" [directory]
Description: Analyze directories containing both images and text
Arguments:
  - prompt: Analysis prompt
  - directory: Directory with mixed content
```bash
# Analyze documentation with diagrams
llm-cli multimodal "Create a comprehensive guide from these materials" /docs/with/images/

# Process screenshots with code
llm-cli multimodal "Explain the UI implementation" /ui/screenshots/and/code/

# Analyze design documents
llm-cli multimodal "Extract design decisions" /design/folder/ --include-images
```

## Performance Optimization

/llm_call_multimodal_parallel "[prompt]" [directory] [workers]
Description: Parallel processing for large corpus
Arguments:
  - prompt: Analysis prompt
  - directory: Directory to analyze
  - workers: Number of parallel workers (default: 4)
```bash
# Parallel file processing
llm-cli multimodal "Analyze each file" /large/corpus/ --parallel --workers 8

# Parallel with batching
llm-cli multimodal "Extract data" /data/ --parallel --batch-size 5

# Progress tracking
llm-cli multimodal "Process documents" /docs/ --parallel --progress
```

## Caching and Incremental Analysis

/llm_call_multimodal_cached "[prompt]" [directory]
Description: Cache results for incremental analysis
Arguments:
  - prompt: Analysis prompt
  - directory: Directory to analyze
```bash
# Initial analysis with caching
llm-cli multimodal "Index content" /knowledge/base/ --cache

# Incremental update (only new/modified files)
llm-cli multimodal "Update index" /knowledge/base/ --cache --incremental

# Clear cache and reanalyze
llm-cli multimodal "Reindex everything" /knowledge/base/ --cache --clear-cache
```

## Error Handling

```bash
# Skip files with errors
llm-cli multimodal "Analyze readable files" /mixed/content/ --skip-errors

# Detailed error reporting
llm-cli multimodal "Process all" /data/ --error-report errors.log

# Retry failed files
llm-cli multimodal "Analyze with retries" /unstable/source/ --retry-failed 3
```

## Integration with Other Tools

### With grep/ripgrep
```bash
# Pre-filter with ripgrep
rg -l "TODO|FIXME" /src/ | xargs llm-cli multimodal "Prioritize these tasks"

# Pattern-based corpus
rg -l "class.*API" /project/ | xargs llm-cli multimodal "Document these APIs"
```

### With find
```bash
# Recent files only
find /docs/ -mtime -7 -name "*.md" | xargs llm-cli multimodal "Summarize recent updates"

# Large files
find /data/ -size +1M -name "*.json" | xargs llm-cli multimodal "Extract key data"
```

### With Git
```bash
# Analyze changed files
git diff --name-only | xargs llm-cli multimodal "Review these changes"

# Analyze commit history
git log --oneline -n 50 | llm-cli multimodal "Summarize recent development"
```

## Common Use Cases

### Code Review
```bash
llm-cli multimodal "Review this codebase for best practices" /src/ --pattern "*.py" --recursive
```

### Documentation Generation
```bash
llm-cli multimodal "Generate user documentation from these files" /project/ --output-format markdown
```

### Knowledge Extraction
```bash
llm-cli multimodal "Extract all mentioned technologies and concepts" /research/papers/ --output-format json
```

### Translation
```bash
llm-cli multimodal "Translate these documents to Spanish" /docs/en/ --output-dir /docs/es/
```

### Content Analysis
```bash
llm-cli multimodal "Analyze sentiment and tone" /customer/feedback/ --recursive
```

### Data Extraction
```bash
llm-cli multimodal "Extract all email addresses and phone numbers" /documents/ --output-format csv
```

## Best Practices

1. **File Limits**: Use --max-files to prevent token overflow
2. **Chunking**: Use appropriate chunk strategies for your content
3. **Filtering**: Pre-filter files with --pattern to reduce noise
4. **Caching**: Enable caching for iterative analysis
5. **Parallel**: Use parallel processing for large directories
6. **Progress**: Enable progress tracking for long operations
7. **Incremental**: Use incremental updates for growing corpora

## Troubleshooting

### Token Limit Exceeded
```bash
# Reduce chunk size
llm-cli multimodal "Analyze" /large/dir/ --chunk-size 2000

# Limit files
llm-cli multimodal "Analyze" /large/dir/ --max-files 20

# Use summarization
llm-cli multimodal "Analyze" /large/dir/ --pre-summarize
```

### Memory Issues
```bash
# Stream processing
llm-cli multimodal "Analyze" /huge/dir/ --stream

# File-by-file processing
llm-cli multimodal "Analyze" /huge/dir/ --strategy file
```

### Performance Issues
```bash
# Increase workers
llm-cli multimodal "Analyze" /dir/ --parallel --workers 16

# Use local model for pre-processing
llm-cli multimodal "Analyze" /dir/ --pre-process-model ollama/llama2
```

---

## Quick Reference Card

```bash
# Single file
llm-cli multimodal "Analyze" file.txt

# Directory
llm-cli multimodal "Summarize" /docs/

# Recursive with pattern
llm-cli multimodal "Review" /src/ --recursive --pattern "*.py"

# Parallel with progress
llm-cli multimodal "Process" /data/ --parallel --progress

# Cached incremental
llm-cli multimodal "Update analysis" /kb/ --cache --incremental

# Structured output
llm-cli multimodal "Extract data" /reports/ --output-format json > data.json
```