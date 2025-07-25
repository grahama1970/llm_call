"""
Module: document_summarizer.py
Description: General-purpose document summarization with rolling window support

This module provides functionality for summarizing large documents using LLMs,
with support for rolling window context management for documents that exceed
model context limits.

External Dependencies:
- litellm: https://docs.litellm.ai/
- tiktoken: https://github.com/openai/tiktoken

Sample Input:
>>> text = "Long document text here..."
>>> summary = await summarize_document(text, model="vertex_ai/gemini-1.5-pro")

Expected Output:
>>> {
...     "summary": "Overall document summary...",
...     "chunk_summaries": ["chunk 1 summary", "chunk 2 summary"],
...     "total_chunks": 5,
...     "total_tokens": 15000
... }

Example Usage:
>>> from llm_call.core.utils.document_summarizer import summarize_document
>>> result = await summarize_document(text, strategy="rolling_window")
"""

import asyncio
from typing import Dict, Any, List, Optional, Literal
from pathlib import Path
import tiktoken
from loguru import logger

from llm_call.core.caller import make_llm_request
from llm_call.core.utils.auth_diagnostics import diagnose_auth_error


class DocumentSummarizer:
    """Handles document summarization with various strategies."""
    
    # Models with large context windows (can handle large documents in one go)
    LARGE_CONTEXT_MODELS = {
        "vertex_ai/gemini-1.5-pro": 1000000,  # 1M tokens
        "vertex_ai/gemini-1.5-flash": 1000000,  # 1M tokens
        "vertex_ai/gemini-2.5-flash-preview-04-17": 1000000,  # 1M tokens
        "vertex_ai/gemini-2.5-flash-preview-05-20": 1000000,  # 1M tokens
        "vertex_ai/gemini-2.0-flash-exp": 1000000,  # 1M tokens
        "gemini/gemini-1.5-pro": 1000000,  # 1M tokens (direct API)
        "gemini/gemini-1.5-flash": 1000000,  # 1M tokens (direct API)
        "gemini/gemini-2.5-flash-preview-04-17": 1000000,  # 1M tokens (direct API)
        "gemini/gemini-2.5-flash-preview-05-20": 1000000,  # 1M tokens (direct API)
        "claude-3-opus": 200000,  # 200k tokens
        "claude-3-sonnet": 200000,  # 200k tokens
        "gpt-4-turbo": 128000,  # 128k tokens
        "gpt-4o": 128000,  # 128k tokens
    }
    
    def __init__(
        self,
        model: str = None,
        max_tokens_per_chunk: int = 4000,
        chunk_overlap: int = 200,
        summary_max_tokens: int = 1000
    ):
        """
        Initialize the document summarizer.
        
        Args:
            model: LLM model to use for summarization (defaults to LITELLM_DEFAULT_MODEL from env)
            max_tokens_per_chunk: Maximum tokens per chunk (for models with smaller contexts)
            chunk_overlap: Number of tokens to overlap between chunks
            summary_max_tokens: Maximum tokens for each summary
        """
        # Use model from env if not specified
        if model is None:
            import os
            # Prefer LITELLM_SUMMARIZATION_MODEL, fall back to LITELLM_DEFAULT_MODEL
            model = os.getenv("LITELLM_SUMMARIZATION_MODEL") or os.getenv("LITELLM_DEFAULT_MODEL", "vertex_ai/gemini-2.5-flash-preview-05-20")
        
        self.model = model
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.chunk_overlap = chunk_overlap
        self.summary_max_tokens = summary_max_tokens
        
        # Check if model has large context window
        self.has_large_context = any(
            model.startswith(prefix) for prefix in self.LARGE_CONTEXT_MODELS
        )
        
        if self.has_large_context:
            # Get the context size for this model
            for model_prefix, context_size in self.LARGE_CONTEXT_MODELS.items():
                if model.startswith(model_prefix):
                    # Use 80% of context to leave room for prompts and output
                    self.max_tokens_per_chunk = int(context_size * 0.8)
                    break
            logger.info(f"Using large context model {model} with {self.max_tokens_per_chunk} tokens per chunk")
        
        # Simple chunking setup
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4")
        except KeyError:  # Model not found, fallback to default encoding
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Simple text chunking for summarization.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        
        if total_tokens <= self.max_tokens_per_chunk:
            # Text fits in one chunk
            return [{
                "text": text,
                "token_count": total_tokens,
                "chunk_index": 0,
                "total_chunks": 1
            }]
        
        # Split into chunks with overlap
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < total_tokens:
            # Calculate end position
            end = min(start + self.max_tokens_per_chunk, total_tokens)
            
            # Get chunk tokens and decode
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunks.append({
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "chunk_index": chunk_index,
                "start_token": start,
                "end_token": end
            })
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap if end < total_tokens else end
            chunk_index += 1
        
        # Add total chunks to each chunk
        for chunk in chunks:
            chunk["total_chunks"] = len(chunks)
        
        return chunks
        
    async def summarize_simple(self, text: str, custom_prompt: Optional[str] = None) -> str:
        """
        Simple summarization for texts that fit within model context.
        
        Args:
            text: Text to summarize
            custom_prompt: Optional custom summarization prompt
            
        Returns:
            Summary text
        """
        prompt = custom_prompt or (
            "Please provide a concise summary of the following text, "
            "highlighting the key points and main ideas:\n\n"
        )
        
        messages = [
            {"role": "system", "content": "You are an expert at creating clear, concise summaries."},
            {"role": "user", "content": f"{prompt}{text}"}
        ]
        
        try:
            response = await make_llm_request({
                "model": self.model,
                "messages": messages,
                "max_tokens": self.summary_max_tokens,
                "temperature": 0.3
            })
            
            # Extract the text content from the response
            if hasattr(response, 'choices') and response.choices:
                return response.choices[0].message.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
        except Exception as e:
            logger.error(f"Failed to get summary with {self.model}: {e}")
            
            # Provide detailed diagnostics for auth errors
            error_str = str(e).lower()
            if any(auth_term in error_str for auth_term in ["jwt", "token", "auth", "credential", "forbidden", "unauthorized", "403", "401"]):
                diagnose_auth_error(e, self.model, verbose=True)
                return f"[Summary generation failed due to authentication error. See detailed diagnosis above.]"
            else:
                # Non-auth error - return generic message
                return f"[Summary generation failed: {type(e).__name__} - {str(e)[:100]}...]"
    
    async def summarize_rolling_window(
        self, 
        text: str, 
        window_size: int = 3,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Summarize using a rolling window approach for large documents.
        
        This method:
        1. Chunks the document
        2. Summarizes chunks in windows
        3. Combines window summaries
        4. Creates final summary
        
        Args:
            text: Text to summarize
            window_size: Number of chunks to summarize together
            custom_prompt: Optional custom summarization prompt
            
        Returns:
            Dictionary with summary and metadata
        """
        # Chunk the text
        chunks = self.chunk_text(text)
        logger.info(f"Document split into {len(chunks)} chunks")
        
        if len(chunks) <= window_size:
            # Document is small enough for simple summarization
            summary = await self.summarize_simple(text, custom_prompt)
            return {
                "summary": summary,
                "strategy": "simple",
                "total_chunks": len(chunks),
                "total_tokens": sum(chunk['token_count'] for chunk in chunks)
            }
        
        # Process chunks in rolling windows
        window_summaries = []
        for i in range(0, len(chunks), window_size):
            window_chunks = chunks[i:i + window_size]
            window_text = "\n\n".join(chunk['text'] for chunk in window_chunks)
            
            prompt = custom_prompt or (
                f"Summarize the following section (chunks {i+1} to {min(i+window_size, len(chunks))}) "
                f"of a larger document:\n\n"
            )
            
            window_summary = await self.summarize_simple(window_text, prompt)
            window_summaries.append({
                "chunks": f"{i+1}-{min(i+window_size, len(chunks))}",
                "summary": window_summary
            })
            
            logger.info(f"Summarized chunks {i+1} to {min(i+window_size, len(chunks))}")
        
        # Combine window summaries into final summary
        combined_summaries = "\n\n".join(
            f"[Chunks {ws['chunks']}]: {ws['summary']}" 
            for ws in window_summaries
        )
        
        final_prompt = (
            "Based on these section summaries from a larger document, "
            "create a comprehensive overall summary that captures the main themes, "
            "key points, and important details:\n\n"
        )
        
        final_summary = await self.summarize_simple(combined_summaries, final_prompt)
        
        return {
            "summary": final_summary,
            "strategy": "rolling_window",
            "window_summaries": window_summaries,
            "total_chunks": len(chunks),
            "total_tokens": sum(chunk['token_count'] for chunk in chunks),
            "window_size": window_size
        }
    
    async def summarize_hierarchical(self, text: str, levels: int = 2) -> Dict[str, Any]:
        """
        Hierarchical summarization - summarize chunks, then summarize summaries.
        
        Args:
            text: Text to summarize
            levels: Number of hierarchical levels
            
        Returns:
            Dictionary with summary and metadata
        """
        chunks = self.chunk_text(text)
        logger.info(f"Document split into {len(chunks)} chunks for hierarchical summarization")
        
        current_summaries = []
        
        # Level 1: Summarize individual chunks
        for i, chunk in enumerate(chunks):
            chunk_summary = await self.summarize_simple(
                chunk['text'],
                f"Summarize this section (chunk {i+1} of {len(chunks)}):"
            )
            current_summaries.append(chunk_summary)
            logger.debug(f"Summarized chunk {i+1}/{len(chunks)}")
        
        # Additional levels: Summarize groups of summaries
        for level in range(1, levels):
            if len(current_summaries) <= 3:
                break  # No need for more levels
                
            next_summaries = []
            group_size = max(3, len(current_summaries) // 5)
            
            for i in range(0, len(current_summaries), group_size):
                group = current_summaries[i:i + group_size]
                combined = "\n\n".join(f"[Part {i+j+1}]: {s}" for j, s in enumerate(group))
                
                group_summary = await self.summarize_simple(
                    combined,
                    f"Combine these {len(group)} summaries into one:"
                )
                next_summaries.append(group_summary)
            
            current_summaries = next_summaries
            logger.info(f"Level {level+1}: Reduced to {len(current_summaries)} summaries")
        
        # Final summary
        if len(current_summaries) > 1:
            final_combined = "\n\n".join(
                f"[Section {i+1}]: {s}" for i, s in enumerate(current_summaries)
            )
            final_summary = await self.summarize_simple(
                final_combined,
                "Create a final comprehensive summary from these section summaries:"
            )
        else:
            final_summary = current_summaries[0]
        
        return {
            "summary": final_summary,
            "strategy": "hierarchical",
            "total_chunks": len(chunks),
            "total_tokens": sum(chunk['token_count'] for chunk in chunks),
            "hierarchy_levels": levels
        }


async def summarize_document(
    text: str,
    model: str = "vertex_ai/gemini-1.5-pro",
    strategy: Literal["auto", "simple", "rolling_window", "hierarchical"] = "auto",
    max_tokens_per_chunk: int = 4000,
    custom_prompt: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Summarize a document using the specified strategy.
    
    Args:
        text: Document text to summarize
        model: LLM model to use
        strategy: Summarization strategy
        max_tokens_per_chunk: Maximum tokens per chunk
        custom_prompt: Optional custom summarization prompt
        **kwargs: Additional arguments for specific strategies
        
    Returns:
        Dictionary with summary and metadata
    """
    summarizer = DocumentSummarizer(
        model=model,
        max_tokens_per_chunk=max_tokens_per_chunk
    )
    
    # Auto-select strategy based on document size and model capabilities
    if strategy == "auto":
        try:
            encoding = tiktoken.encoding_for_model("gpt-4")
        except Exception:  # Generic file processing error
            encoding = tiktoken.get_encoding("cl100k_base")
        
        token_count = len(encoding.encode(text))
        
        # Check if we have a large context model
        if summarizer.has_large_context and token_count < summarizer.max_tokens_per_chunk:
            # Document fits in context window - use simple strategy
            strategy = "simple"
            logger.info(f"Using simple strategy with large context model (document: {token_count} tokens, model capacity: {summarizer.max_tokens_per_chunk} tokens)")
        else:
            # Need chunking strategy
            if token_count < 50000:
                strategy = "rolling_window"
            else:
                strategy = "hierarchical"
            logger.info(f"Auto-selected strategy: {strategy} (document has {token_count} tokens)")
    
    if strategy == "simple":
        summary = await summarizer.summarize_simple(text, custom_prompt)
        return {
            "summary": summary,
            "strategy": "simple",
            "model": model
        }
    elif strategy == "rolling_window":
        return await summarizer.summarize_rolling_window(
            text,
            window_size=kwargs.get("window_size", 3),
            custom_prompt=custom_prompt
        )
    elif strategy == "hierarchical":
        return await summarizer.summarize_hierarchical(
            text,
            levels=kwargs.get("levels", 2)
        )
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


async def summarize_file(
    file_path: str,
    model: str = "vertex_ai/gemini-1.5-pro",
    strategy: Literal["auto", "simple", "rolling_window", "hierarchical"] = "auto",
    output_path: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Summarize a file's contents.'
    
    Args:
        file_path: Path to file to summarize
        model: LLM model to use
        strategy: Summarization strategy
        output_path: Optional path to save summary
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with summary and metadata
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = await summarize_document(text, model, strategy, **kwargs)
    result["source_file"] = str(path)
    
    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        if output.suffix == '.json':
            import json
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
        else:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result["summary"])
        
        result["output_file"] = str(output)
        logger.success(f"Summary saved to {output}")
    
    return result


# Test function
if __name__ == "__main__":
    import sys
    
    async def test_summarizer():
        # Test text
        test_text = """
        Artificial Intelligence (AI) has evolved significantly over the past decade.
        Machine learning algorithms have become more sophisticated, enabling
        applications in healthcare, finance, and transportation. Deep learning,
        a subset of machine learning, has revolutionized computer vision and
        natural language processing. However, challenges remain in making AI
        systems more interpretable and ethically aligned with human values.
        """ * 50  # Make it longer to test chunking
        
        logger.info("Testing document summarizer...")
        
        # Test simple summarization
        try:
            result = await summarize_document(test_text, strategy="simple")
            logger.success(f" Simple strategy: {result['summary'][:100]}...")
        except Exception as e:
            logger.error(f" Simple strategy failed: {e}")
        
        # Test rolling window
        try:
            result = await summarize_document(test_text, strategy="rolling_window")
            logger.success(f" Rolling window strategy: Generated {len(result.get('window_summaries', []))} window summaries")
        except Exception as e:
            logger.error(f" Rolling window strategy failed: {e}")
        
        # Test hierarchical
        try:
            result = await summarize_document(test_text, strategy="hierarchical")
            logger.success(f" Hierarchical strategy: {result['summary'][:100]}...")
        except Exception as e:
            logger.error(f" Hierarchical strategy failed: {e}")
    
    asyncio.run(test_summarizer())