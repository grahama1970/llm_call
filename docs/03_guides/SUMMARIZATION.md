# Document Summarization Guide

## Overview

LLM Call now includes powerful document summarization capabilities that leverage large context models like Gemini to handle documents of any size. The summarizer automatically selects the best strategy based on document length and model capabilities.

## Features

- **Automatic Strategy Selection**: Chooses between simple, rolling window, or hierarchical summarization
- **Large Context Model Support**: Optimized for Gemini's 1M token context window
- **Multiple Output Formats**: Plain text or JSON with metadata
- **Custom Prompts**: Tailor summaries to your needs
- **Streaming Support**: For real-time feedback on long documents

## Quick Start

### Prerequisites

Before using summarization, ensure you have:

1. **API Credentials configured** in your `.env` file:
   - For Gemini (default): `GOOGLE_APPLICATION_CREDENTIALS` and valid service account
   - For OpenAI models: Valid `OPENAI_API_KEY`
   - For Claude: Claude proxy server running (see Claude CLI setup)

2. **Virtual environment activated**:
   ```bash
   source .venv/bin/activate
   ```

### Command Line Usage

```bash
# Summarize a file
python -m llm_call.cli.main summarize document.txt

# Or use the shortcut script
./summarize document.txt

# Summarize from stdin
cat document.txt | python -m llm_call.cli.main summarize -

# Save to file
python -m llm_call.cli.main summarize document.pdf -o summary.md

# Use specific model (e.g., if Gemini auth fails)
python -m llm_call.cli.main summarize document.txt --model gpt-3.5-turbo

# Custom prompt
python -m llm_call.cli.main summarize document.txt --prompt "Focus on the technical aspects:"
```

### Python API Usage

```python
from llm_call.core.utils.document_summarizer import summarize_document, summarize_file

# Summarize text
result = await summarize_document(
    text="Your long document text here...",
    strategy="auto"  # auto, simple, rolling_window, hierarchical
)
print(result["summary"])

# Summarize file
result = await summarize_file(
    "path/to/document.pdf",
    output_path="summary.md"
)
```

## Summarization Strategies

### 1. Simple Strategy
- **When**: Document fits within model's context window
- **How**: Processes entire document in one request
- **Best for**: Documents under ~800k tokens with large context models

### 2. Rolling Window Strategy
- **When**: Document exceeds context window but is moderate in size
- **How**: Summarizes overlapping chunks, then combines summaries
- **Best for**: Documents between 50k-500k tokens with standard models

### 3. Hierarchical Strategy
- **When**: Very large documents
- **How**: Multi-level summarization - chunks → group summaries → final summary
- **Best for**: Books, research papers, massive documents

## Configuration

### Environment Variables

```bash
# Preferred model for summarization (uses Gemini by default)
LITELLM_SUMMARIZATION_MODEL=vertex_ai/gemini-2.5-flash-preview-05-20

# Falls back to default model if not set
LITELLM_DEFAULT_MODEL=vertex_ai/gemini-1.5-pro
```

### CLI Options

- `--model`: Override the default model
- `--strategy`: Force a specific strategy (auto, simple, rolling_window, hierarchical)
- `--max-length`: Maximum summary length in tokens
- `--window-size`: Chunks per window for rolling strategy
- `--output`: Save to file instead of printing

## Examples

### Summarize a Research Paper
```bash
# Let the system choose the best strategy
llm summarize research_paper.pdf

# Force hierarchical for very detailed summary
llm summarize research_paper.pdf --strategy hierarchical
```

### Summarize with Custom Focus
```bash
# Technical summary
llm summarize document.txt --prompt "Summarize the technical implementation details:"

# Executive summary
llm summarize report.pdf --prompt "Create an executive summary focusing on business impact:"
```

### Batch Processing
```bash
# Summarize all documents in a directory
for file in documents/*.txt; do
    llm summarize "$file" -o "summaries/$(basename "$file" .txt).summary.md"
done
```

### Integration with Claude

You can use the `/summarize` command in Claude:

```
/summarize path/to/document.txt
```

Or with options:
```
/summarize document.pdf --strategy hierarchical --output summary.md
```

## API Integration

### In Your Python Code

```python
import asyncio
from llm_call.core.utils.document_summarizer import DocumentSummarizer

async def process_documents():
    summarizer = DocumentSummarizer(
        model="vertex_ai/gemini-1.5-pro",
        summary_max_tokens=1000
    )
    
    # Process multiple documents
    for doc_path in document_paths:
        with open(doc_path) as f:
            text = f.read()
        
        if len(text) < 10000:
            # Short document - simple summary
            summary = await summarizer.summarize_simple(text)
        else:
            # Long document - use rolling window
            result = await summarizer.summarize_rolling_window(text)
            summary = result["summary"]
        
        print(f"Summary of {doc_path}:\n{summary}\n")
```

### With LLM Call API

```python
from llm_call import make_llm_request

# Use summarization as part of a larger workflow
async def analyze_and_summarize(document_text):
    # First, summarize the document
    summary_result = await summarize_document(document_text)
    
    # Then, analyze the summary
    analysis = await make_llm_request({
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a document analyst."},
            {"role": "user", "content": f"Analyze this summary and identify key themes:\n\n{summary_result['summary']}"}
        ]
    })
    
    return {
        "summary": summary_result["summary"],
        "analysis": analysis,
        "metadata": summary_result
    }
```

## Performance Tips

1. **Use Large Context Models**: Gemini models can handle entire books in one request
2. **Adjust Window Size**: Larger windows = better context preservation but more API calls
3. **Cache Results**: Save summaries to avoid re-processing
4. **Batch Processing**: Process multiple documents in parallel

## Troubleshooting

### Authentication Errors
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account JSON
- Check that the service account has Vertex AI permissions
- Verify project ID and location in environment variables

### Out of Memory
- Use hierarchical strategy for very large documents
- Reduce chunk size with smaller models
- Process documents in batches

### Poor Summary Quality
- Try a different strategy
- Provide custom prompts for domain-specific content
- Use a more capable model (e.g., gemini-1.5-pro vs gemini-1.5-flash)

## Advanced Usage

### Custom Chunking
```python
from llm_call.core.utils.document_summarizer import DocumentSummarizer

# Custom chunk size for specific use case
summarizer = DocumentSummarizer(
    max_tokens_per_chunk=10000,  # Smaller chunks
    chunk_overlap=500,  # More overlap
    summary_max_tokens=2000  # Longer summaries
)
```

### Progress Tracking
```python
# For very large documents, track progress
async def summarize_with_progress(text):
    summarizer = DocumentSummarizer()
    chunks = summarizer.chunk_text(text)
    
    print(f"Processing {len(chunks)} chunks...")
    
    summaries = []
    for i, chunk in enumerate(chunks):
        summary = await summarizer.summarize_simple(chunk["text"])
        summaries.append(summary)
        print(f"Progress: {i+1}/{len(chunks)}")
    
    # Combine summaries
    final = await summarizer.summarize_simple("\n\n".join(summaries))
    return final
```

## See Also

- [LLM Call Documentation](../README.md)
- [Runpod Integration](./RUNPOD_INTEGRATION.md) - For using large models via Runpod
- [Configuration Guide](./usage/CLI_CONFIG_SCHEMA.md)