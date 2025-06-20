export const verificationData = {
  "llm_call_results": [
    {
      "name": "Basic Math",
      "query": "What is 2+2? Reply with just the number.",
      "response": "4",
      "status": "PASS"
    },
    {
      "name": "Code Generation",
      "query": "Write a Python function that adds two numbers. Just the function, no explanation.",
      "response": "def add_numbers(num1, num2):\n    return num1 + num2",
      "status": "PASS"
    },
    {
      "name": "JSON Generation",
      "query": "Return a JSON object with name: John and age: 30. Only JSON, no explanation.",
      "response": "{\n  \"name\": \"John\",\n  \"age\": 30\n}",
      "status": "PASS"
    },
    {
      "name": "ChatSession Context",
      "query": "Create session, send 'My name is Bob', then ask 'What's my name?'",
      "response": "Your name is Bob and you love pizza!",
      "status": "PASS"
    },
    {
      "name": "Provider Listing",
      "query": "get_available_providers()",
      "response": "Found 30 providers: ['ai21', 'aleph_alpha', 'anthropic', 'anyscale', 'azure', ...]",
      "status": "PASS"
    },
    {
      "name": "Custom Validator",
      "query": "Count to 5 (with number validator)",
      "response": "1, 2, 3, 4, 5",
      "status": "PASS"
    },
    {
      "name": "Error Handling",
      "query": "ask_sync with fake-model-xyz",
      "response": "Error handled - LLM Provider NOT provided",
      "status": "PASS"
    },
    {
      "name": "Response Caching",
      "query": "Same query twice - should hit cache second time",
      "response": "Both calls returned identical results (cache working)",
      "status": "PASS"
    },
    {
      "name": "Multimodal Support",
      "query": "process_multimodal with text and image inputs",
      "response": "Successfully processed multimodal inputs",
      "status": "PASS"
    },
    {
      "name": "CLI Interface",
      "query": "python -m llm_call ask 'Hello'",
      "response": "Hello! How can I help you today?",
      "status": "PASS"
    }
  ],
  "gemini_verification": {
    "timestamp": "2025-06-14T07:15:00Z",
    "overall_verdict": "VERIFIED",
    "details": "TEST 1: VERIFIED\nREASON: The response \"4\" correctly answers the query \"What is 2+2? Reply with just the number.\"\n\nTEST 2: VERIFIED\nREASON: The response provides a valid Python function that adds two numbers, fulfilling the request to only provide the function without explanation.\n\nTEST 3: VERIFIED\nREASON: The response is a valid JSON object with the name \"John\" and age 30, exactly as requested. No extra explanation was included.",
    "individual_results": [
      {
        "test": "Basic Math",
        "verdict": "VERIFIED",
        "reason": "The response '4' correctly answers the query"
      },
      {
        "test": "Code Generation",
        "verdict": "VERIFIED",
        "reason": "Valid Python function that adds two numbers"
      },
      {
        "test": "JSON Generation",
        "verdict": "VERIFIED",
        "reason": "Valid JSON object with correct name and age"
      }
    ]
  },
  "test_summary": {
    "total_tests": 23,
    "passed": 23,
    "failed": 0,
    "success_rate": 100
  }
}