# call-me-maybe

*This project has been created as part of the 42 curriculum by yel-hadi.*

---

## Description

**call-me-maybe** is a function calling tool that translates natural language prompts into structured function calls using a small language model (Qwen3-0.6B). Given a prompt like *"What is the sum of 2 and 3?"*, the system does not answer the question — instead it identifies the correct function to call and extracts the arguments with proper types:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}
```

The core technique used is **constrained decoding**: instead of relying on the model to spontaneously produce valid JSON, the generation process is guided token-by-token to guarantee 100% structurally valid and schema-compliant output.

---

## Instructions

### Requirements

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

Clone the repository and install dependencies:

```bash
git clone <your-repo-url>
cd call-me-maybe
make install
```

### Running the program

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calls.json
```

All arguments are optional — by default the program reads from `data/input/` and writes to `data/output/`.

### Makefile commands

| Command | Description |
|---|---|
| `make install` | Install project dependencies |
| `make run` | Run the program with default paths |
| `make debug` | Run in debug mode using pdb |
| `make clean` | Remove caches and temporary files |
| `make lint` | Run flake8 and mypy checks |

---

## Algorithm Explanation

The generation pipeline is split into two phases:

### Phase 1 — Function Name Selection

The model generates the function name token-by-token under constraints. At each step:

1. The model produces logits over all tokens in the vocabulary.
2. Only tokens that are valid continuations of a known function name are allowed.
3. The token with the highest logit among allowed tokens is selected.
4. This repeats until a complete function name is produced.

This is implemented using prefix matching: at each step, only sequences that match the already-generated prefix are kept as candidates.

### Phase 2 — Parameter Generation

Once the function name is known, its parameter schema is retrieved from `functions_definition.json`. A state machine then generates each parameter value in order:

```
START → PARAM_NAME → NEXT_COLON → NUMBER or STRING_START
NUMBER → AFTER_VALUE
STRING_START → STRING_CONTENT → AFTER_VALUE
AFTER_VALUE → PARAM_NAME (next param) or END
```

- **Numbers**: The model generates digit tokens freely until a non-digit token is chosen, at which point `.0` is appended to enforce float format.
- **Strings**: The model generates tokens freely until a closing quote token is detected or a safety limit is reached.
- **Structural tokens** (`{`, `}`, `"`, `:`, `,`) are forced directly — never generated freely.

---

## Design Decisions

- **State machine for parameter generation**: Each parameter type (number, string) has its own generation rules enforced by a deterministic state machine, guaranteeing schema compliance regardless of model behavior.
- **Forced structural tokens**: Tokens like `{`, `}`, `"param_name"`, `: ` are injected directly into the token stream without asking the model, eliminating any chance of structural errors.
- **Float enforcement**: All numbers are forced to include a decimal point (`.0`) to match the `number` type in the schema.
- **String termination**: String generation stops when the model naturally produces a closing quote, or after a 200-token safety limit to prevent infinite loops.
- **Pydantic validation**: Input files are validated using Pydantic models before processing begins, ensuring graceful error messages on malformed input.

---

## Performance Analysis

- **Accuracy**: ~10/11 correct on the provided test suite (90%+), with one edge case involving complex regex generation being slightly off due to small model limitations.
- **JSON validity**: 100% — every output is parseable thanks to constrained decoding.
- **Speed**: Processes 11 prompts in approximately 2-3 minutes on standard CPU hardware.
- **Reliability**: The state machine guarantees valid output structure regardless of what the model wants to generate.

---

## Challenges Faced

- **Multi-character tokens**: The tokenizer sometimes encodes multiple characters as a single token (e.g., `john"` as one token). This required checking if a closing quote character appears anywhere in a decoded token, not just matching the exact quote token ID.
- **Number inflation**: Early versions produced numbers like `160` instead of `16` because the model's best token was a multi-digit token not in the single-digit allowed list. Fixed by checking decoded token content rather than token IDs.
- **Infinite string generation**: Without a safety limit, some prompts caused the model to generate endlessly inside a string. Fixed with a 200-token string length guard.
- **Extra data after JSON**: The model sometimes appended extra text after the closing `}`. Fixed by forcing the `}` token directly instead of picking it via argmax.
- **Nested list appending**: Early bugs caused lists to be appended as nested elements instead of flat token IDs, corrupting the generation context.

---

## Testing Strategy

Testing was done in several stages:

1. **Unit-level**: Each state in the state machine was tested individually by observing decoded output at each step.
2. **Integration**: The full pipeline was run against the provided `function_calling_tests.json` and output was validated manually.
3. **Edge cases**: Additional test files were created to cover:
   - Empty strings
   - Large numbers (e.g., 999999999)
   - Special characters in strings (e.g., `@`, `#`)
   - Ambiguous prompts (e.g., "Calculate something with 5 and 3")
   - Functions with multiple parameters
4. **Debug mode**: A separate testing script was used to print decoded parameters at each step to trace bugs.

---

## Example Usage

**Input** (`function_calling_tests.json`):
```json
[
  {"prompt": "What is the sum of 2 and 3?"},
  {"prompt": "Greet shrek"},
  {"prompt": "Reverse the string 'hello'"}
]
```

**Run**:
```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calls.json
```

**Output** (`function_calls.json`):
```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {"a": 2.0, "b": 3.0}
  },
  {
    "prompt": "Greet shrek",
    "name": "fn_greet",
    "parameters": {"name": "shrek"}
  },
  {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": {"s": "hello"}
  }
]
```

---

## Resources

- [Qwen3 Model — Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Constrained Decoding — Overview](https://huggingface.co/blog/constrained-beam-search)
- [JSON Schema Specification](https://json-schema.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [flake8 Linter](https://flake8.pycqa.org/)
- [mypy Static Type Checker](https://mypy.readthedocs.io/)

### AI Usage

Claude (Anthropic) was used throughout this project for:
- Debugging the constrained decoding state machine
- Identifying token-level edge cases (multi-character tokens, quote detection)
- Suggesting fixes for infinite loop and JSON corruption bugs
- Reviewing code structure and identifying unnecessary or missing parts

All AI-generated suggestions were reviewed, tested, and understood before being incorporated into the project.