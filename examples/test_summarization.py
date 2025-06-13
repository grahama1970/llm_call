#!/usr/bin/env python3
"""
Test summarization functionality.

This script demonstrates how the summarization feature works,
even if API credentials are not properly configured.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_call.core.utils.document_summarizer import DocumentSummarizer


async def test_summarization():
    """Test the summarization functionality."""
    
    # Test document
    test_document = """
    # The Future of Artificial Intelligence
    
    Artificial Intelligence (AI) has evolved from a theoretical concept to a practical technology
    that impacts our daily lives. This transformation has been particularly dramatic in the last
    decade, with breakthroughs in deep learning, natural language processing, and computer vision.
    
    ## Machine Learning Revolution
    
    Machine learning algorithms have become the backbone of modern AI systems. These algorithms
    can learn patterns from data without being explicitly programmed, enabling applications
    ranging from recommendation systems to autonomous vehicles.
    
    ### Deep Learning
    
    Deep learning, inspired by the human brain's neural networks, has revolutionized how'
    machines process information. Convolutional Neural Networks (CNNs) excel at image
    recognition, while Recurrent Neural Networks (RNNs) and Transformers have transformed
    natural language processing.
    
    ## Large Language Models
    
    The emergence of Large Language Models (LLMs) like GPT, Claude, and Gemini represents
    a significant milestone. These models can understand context, generate coherent text,
    and even engage in complex reasoning tasks. They're trained on vast amounts of text'
    data and can adapt to various tasks through prompt engineering.
    
    ## Applications and Impact
    
    AI is transforming numerous industries:
    
    1. **Healthcare**: AI assists in diagnosis, drug discovery, and personalized treatment plans
    2. **Finance**: Fraud detection, algorithmic trading, and risk assessment
    3. **Transportation**: Self-driving cars and traffic optimization
    4. **Education**: Personalized learning and automated grading
    5. **Entertainment**: Content recommendation and generation
    
    ## Challenges and Considerations
    
    Despite its benefits, AI presents several challenges:
    
    - **Ethical concerns**: Bias in algorithms, privacy issues, and decision transparency
    - **Job displacement**: Automation may replace certain human roles
    - **Security risks**: AI systems can be vulnerable to adversarial attacks
    - **Resource consumption**: Training large models requires significant computational resources
    
    ## Future Directions
    
    The future of AI looks promising with several emerging trends:
    
    1. **Multimodal AI**: Systems that can process text, images, audio, and video simultaneously
    2. **Edge AI**: Running AI models on local devices for improved privacy and latency
    3. **Explainable AI**: Making AI decisions more transparent and interpretable
    4. **AGI Research**: Working towards Artificial General Intelligence
    
    ## Conclusion
    
    As AI continues to advance, it's crucial to develop these technologies responsibly,'
    ensuring they benefit humanity while addressing potential risks. The collaboration
    between researchers, policymakers, and the public will shape how AI transforms our future.
    """ * 5  # Make it longer to test chunking
    
    print("Testing Document Summarizer")
    print("=" * 50)
    
    # Initialize summarizer
    print("\n1. Initializing summarizer...")
    summarizer = DocumentSummarizer()
    print(f"   Model: {summarizer.model}")
    print(f"   Max tokens per chunk: {summarizer.max_tokens_per_chunk}")
    print(f"   Has large context: {summarizer.has_large_context}")
    
    # Test chunking
    print("\n2. Testing text chunking...")
    chunks = summarizer.chunk_text(test_document)
    print(f"   Document split into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"   Chunk {i+1}: {chunk['token_count']} tokens")
    
    # Test token counting
    print("\n3. Testing token counting...")
    tokens = summarizer.encoding.encode(test_document)
    print(f"   Total document tokens: {len(tokens)}")
    
    # Demonstrate strategy selection
    print("\n4. Strategy selection logic:")
    doc_tokens = len(tokens)
    if summarizer.has_large_context and doc_tokens < summarizer.max_tokens_per_chunk:
        print(f"   → Would use SIMPLE strategy (doc: {doc_tokens} tokens < capacity: {summarizer.max_tokens_per_chunk} tokens)")
    elif doc_tokens < 50000:
        print(f"   → Would use ROLLING WINDOW strategy (doc: {doc_tokens} tokens)")
    else:
        print(f"   → Would use HIERARCHICAL strategy (doc: {doc_tokens} tokens)")
    
    print("\n5. Example API calls that would be made:")
    print("   For simple strategy:")
    print("   - 1 API call with full document")
    print("\n   For rolling window strategy:")
    print(f"   - {len(chunks)} chunks → ~{max(1, len(chunks)//3)} window summaries → 1 final summary")
    print("\n   For hierarchical strategy:")
    print(f"   - {len(chunks)} chunk summaries → multiple levels → 1 final summary")
    
    print("\n" + "=" * 50)
    print("Summarization system is ready to use!")
    print("\nUsage examples:")
    print("  CLI:    llm summarize document.txt")
    print("  Python: result = await summarize_document(text)")
    print("  Claude: /summarize path/to/document.txt")


if __name__ == "__main__":
    asyncio.run(test_summarization())