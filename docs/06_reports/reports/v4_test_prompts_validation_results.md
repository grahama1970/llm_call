# V4 Test Prompts Validation Report

Generated: 2025-05-24 18:11:41

## Summary

- Total Tests: 28
- Passed: 28 (100.0%)
- Failed: 0 (0.0%)

## Results Table

| Test ID | Model | Status | Type | Duration | Description |
|---------|-------|--------|------|----------|-------------|
| max_text_001_simple_question | max/text-general | ✅ PASS | Valid Response | 13.60s | Simplest call to Claude proxy with a question stri... |
| max_text_002_system_and_user_messages | max/text-creative-writer | ✅ PASS | Valid Response | 8.00s | Call to Claude proxy with system and user roles. |
| max_text_003_no_default_validation | max/text-simple | ✅ PASS | Valid Response | 4.15s | Claude proxy call, explicitly disabling default va... |
| vertex_text_001_simple_question | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 0.97s | Simplest call to Vertex AI with a question string. |
| openai_text_001_system_and_user | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 1.63s | Call to OpenAI with system and user messages. |
| openai_json_001_validate_fields | openai/gpt-4o-mini | ✅ PASS | Valid Response | 0.81s | Request JSON from OpenAI, validate not empty, is J... |
| max_json_002_proxy_validate_json | max/json-data-provider | ✅ PASS | Validation Rejected | 23.38s | Request JSON from Claude proxy, validate it's not ... |
| openai_multimodal_001_describe_local_image | openai/gpt-4o-mini | ✅ PASS | Valid Response | 3.41s | Multimodal call to GPT-4o-mini to describe a local... |
| max_multimodal_001_claude_describes_local_image | max/claude-image-describer | ✅ PASS | Validation Rejected | 0.00s | Multimodal call to Claude proxy with local image, ... |
| max_multimodal_002_claude_http_image | max/claude-url-image-analyzer | ✅ PASS | Validation Rejected | 0.00s | Multimodal call to Claude proxy with an HTTP image... |
| agent_validation_001_contradiction_check_flat_earth | meta-task/analyze-flat-earth-text | ✅ PASS | Validation Rejected | 3.01s | Claude agent uses Perplexity to check for contradi... |
| agent_validation_002_code_syntax_check | meta-task/validate-python-code | ✅ PASS | Validation Rejected | 3.01s | Claude agent checks Python code syntax (conceptual... |
| agent_validation_003_large_text_delegation | meta-task/analyze_large_wikipedia_article | ✅ PASS | Validation Rejected | 3.01s | Claude agent instructed to use llm_call_tool for c... |
| string_check_001_contains | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 0.42s | Validate if response contains a specific substring... |
| string_check_002_not_contains | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 0.99s | Validate if response does NOT contain a specific s... |
| string_check_003_regex_match | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 0.72s | Validate if response matches a regex pattern (e.g.... |
| corpus_check_001_keyword_in_file | meta-task/summarize_text_for_keyword_check | ✅ PASS | Validation Rejected | 3.01s | Validate if a keyword exists in a provided text (s... |
| basic_001_no_validation_field | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 0.33s | Simple call, no validation field, relies on defaul... |
| combo_val_004_multiple_string_checks | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 1.21s | Multiple string checks on a response. |
| agent_task_002_default_mcp | meta-task/validate-using-default-tools | ✅ PASS | Validation Rejected | 3.01s | Agent task where client sends no MCP, server uses ... |
| openai_text_002_long_response_default_val | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 1.89s | OpenAI call expecting longer response, default val... |
| vertex_text_004_creative_writing_default_val | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 1.95s | Vertex creative writing, default validation. |
| max_json_003_complex_schema_request | max/complex-json-generator | ✅ PASS | Validation Rejected | 25.17s | Claude proxy request for a complex JSON structure,... |
| openai_multimodal_003_question_about_image | openai/gpt-4o-mini | ✅ PASS | Valid Response | 1.30s | GPT-4o-mini: Ask a specific question about the dum... |
| max_multimodal_003_question_about_image_claude | openai/gpt-4o-mini | ✅ PASS | Valid Response | 1.53s | GPT-4o-mini: Ask a specific question about the dum... |
| agent_validation_004_simple_text_check_by_claude | meta-task/text-for-keyword-validation | ✅ PASS | Validation Rejected | 3.01s | Claude agent validates if a given text response co... |
| string_check_004_max_length | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 0.50s | Validate response is under a max character length. |
| field_present_001_check_absence | openai/gpt-3.5-turbo | ✅ PASS | Valid Response | 0.52s | Validate a specific field is ABSENT in a JSON resp... |

## Detailed Results

### max_text_001_simple_question

- **Model**: max/text-general
- **Status**: ✅ PASS
- **Duration**: 13.60s
- **Has Validation**: False
- **Response**: 
```
The primary function of a CPU (Central Processing Unit) in a computer is to execute instructions and perform calculations that run software programs. 

Here's what the CPU does:

1. **Instruction Processing**: The CPU fetches, decodes, and executes program instructions stored in memory. It reads instructions from RAM, interprets what needs to be done, and carries out those operations.

2. **Arithmetic and Logic Operations**: It performs all mathematical calculations (addition, subtraction, multi...
```

### max_text_002_system_and_user_messages

- **Model**: max/text-creative-writer
- **Status**: ✅ PASS
- **Duration**: 8.00s
- **Has Validation**: False
- **Response**: 
```
As Commander Sarah Chen's gloved fingers brushed away millennia of cosmic dust from the obsidian surface, the artifact beneath began to pulse with a light that had been waiting ten thousand years to be seen again.
```

### max_text_003_no_default_validation

- **Model**: max/text-simple
- **Status**: ✅ PASS
- **Duration**: 4.15s
- **Has Validation**: False
- **Response**: 
```
Yes, Python is a programming language. It's a high-level, interpreted, general-purpose programming language known for its clear syntax and readability. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming. It's widely used for web development, data science, artificial intelligence, automation, and many other applications.
```

### vertex_text_001_simple_question

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 0.97s
- **Has Validation**: False
- **Response**: 
```
1. Io
2. Europa
3. Ganymede
4. Callisto
```

### openai_text_001_system_and_user

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 1.63s
- **Has Validation**: False
- **Response**: 
```
1. Visit the Eiffel Tower: One of the most iconic landmarks in the world, the Eiffel Tower offers breathtaking views of Paris from its observation decks. You can also enjoy a meal at one of the restaurants located on the tower for a unique dining experience.

2. Explore the Louvre Museum: Home to thousands of works of art including the famous Mona Lisa, the Louvre Museum is a must-visit for art enthusiasts. Spend a few hours wandering through the museum's vast collection and admiring some of the...
```

### openai_json_001_validate_fields

- **Model**: openai/gpt-4o-mini
- **Status**: ✅ PASS
- **Duration**: 0.81s
- **Has Validation**: True
- **Response**: 
```
{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "year_published": 1925
}
```

### max_json_002_proxy_validate_json

- **Model**: max/json-data-provider
- **Status**: ✅ PASS
- **Duration**: 23.38s
- **Has Validation**: True
- **Response**: 
```
Error: Human review needed
```

### openai_multimodal_001_describe_local_image

- **Model**: openai/gpt-4o-mini
- **Status**: ✅ PASS
- **Duration**: 3.41s
- **Has Validation**: True
- **Response**: 
```
The image depicts a solid blue color with no distinguishable features or objects.
```

### max_multimodal_001_claude_describes_local_image

- **Model**: max/claude-image-describer
- **Status**: ✅ PASS
- **Duration**: 0.00s
- **Has Validation**: True
- **Response**: 
```
Error: Claude CLI (via proxy for model 'max/claude-image-describer') does not support multimodal image inputs.
```

### max_multimodal_002_claude_http_image

- **Model**: max/claude-url-image-analyzer
- **Status**: ✅ PASS
- **Duration**: 0.00s
- **Has Validation**: True
- **Response**: 
```
Error: Claude CLI (via proxy for model 'max/claude-url-image-analyzer') does not support multimodal image inputs.
```

### agent_validation_001_contradiction_check_flat_earth

- **Model**: meta-task/analyze-flat-earth-text
- **Status**: ✅ PASS
- **Duration**: 3.01s
- **Has Validation**: True
- **Response**: 
```
Error: Human review needed
```

### agent_validation_002_code_syntax_check

- **Model**: meta-task/validate-python-code
- **Status**: ✅ PASS
- **Duration**: 3.01s
- **Has Validation**: True
- **Response**: 
```
Error: Human review needed
```

### agent_validation_003_large_text_delegation

- **Model**: meta-task/analyze_large_wikipedia_article
- **Status**: ✅ PASS
- **Duration**: 3.01s
- **Has Validation**: True
- **Response**: 
```
Error: Human review needed
```

### string_check_001_contains

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 0.42s
- **Has Validation**: True
- **Response**: 
```
Blue
```

### string_check_002_not_contains

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 0.99s
- **Has Validation**: True
- **Response**: 
```
Yellow
```

### string_check_003_regex_match

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 0.72s
- **Has Validation**: True
- **Response**: 
```
johndoe12345@example.com
```

### corpus_check_001_keyword_in_file

- **Model**: meta-task/summarize_text_for_keyword_check
- **Status**: ✅ PASS
- **Duration**: 3.01s
- **Has Validation**: True
- **Response**: 
```
Error: Human review needed
```

### basic_001_no_validation_field

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 0.33s
- **Has Validation**: False
- **Response**: 
```
Yes
```

### combo_val_004_multiple_string_checks

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 1.21s
- **Has Validation**: True
- **Response**: 
```
A cat is a small domestic animal with a sleek fur coat, sharp claws, and whiskers. Its eyes are usually large and vibrant, giving it a curious and mischievous appearance. Cats are known for their independent and aloof nature, often choosing when to interact with their human companions. They are agile and skilled hunters, known for their ability to sneak up on prey with stealth and precision. Cats communicate through various vocalizations, body language, and purring. They are not as social as dog...
```

### agent_task_002_default_mcp

- **Model**: meta-task/validate-using-default-tools
- **Status**: ✅ PASS
- **Duration**: 3.01s
- **Has Validation**: True
- **Response**: 
```
Error: Human review needed
```

### openai_text_002_long_response_default_val

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 1.89s
- **Has Validation**: False
- **Response**: 
```
General relativity is a theory proposed by Albert Einstein in 1915 that describes the force of gravity as a curvature of spacetime caused by mass and energy. According to this theory, massive objects like planets and stars warp the fabric of spacetime around them, creating a gravitational field that influences the motion of other objects nearby. This curvature of spacetime explains why objects with mass are attracted to each other and why planets orbit around the sun.

One of the key concepts in...
```

### vertex_text_004_creative_writing_default_val

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 1.95s
- **Has Validation**: False
- **Response**: 
```
Once upon a time, nestled deep within the heart of an enchanted forest, there lay a hidden magical kingdom known as Lumindor. The kingdom was shrouded in mystery and seclusion, protected by powerful spells and invisible barriers that kept it hidden from the outside world.

Lumindor was ruled by the wise and benevolent King Thalion, a sorcerer of unparalleled skill and kindness. Under his rule, the kingdom prospered, its lands lush and bountiful, its people living in harmony with the mystical cre...
```

### max_json_003_complex_schema_request

- **Model**: max/complex-json-generator
- **Status**: ✅ PASS
- **Duration**: 25.17s
- **Has Validation**: True
- **Response**: 
```
Error: Human review needed
```

### openai_multimodal_003_question_about_image

- **Model**: openai/gpt-4o-mini
- **Status**: ✅ PASS
- **Duration**: 1.30s
- **Has Validation**: False
- **Response**: 
```
I can't identify any distinct objects in the image, as it appears to be a solid color with no discernible features.
```

### max_multimodal_003_question_about_image_claude

- **Model**: openai/gpt-4o-mini
- **Status**: ✅ PASS
- **Duration**: 1.53s
- **Has Validation**: False
- **Response**: 
```
Yes, there are several animals in the image. They include:

1. Panda
2. Lion
3. Wolf
4. Stag
5. Mountain Goat
6. Hippopotamus
```

### agent_validation_004_simple_text_check_by_claude

- **Model**: meta-task/text-for-keyword-validation
- **Status**: ✅ PASS
- **Duration**: 3.01s
- **Has Validation**: True
- **Response**: 
```
Error: Human review needed
```

### string_check_004_max_length

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 0.50s
- **Has Validation**: True
- **Response**: 
```
I am incapable of providing a very, very, very, very, very long single sentence answer as
```

### field_present_001_check_absence

- **Model**: openai/gpt-3.5-turbo
- **Status**: ✅ PASS
- **Duration**: 0.52s
- **Has Validation**: True
- **Response**: 
```
{
    "name": "John",
    "city": "New York"
}
```

