uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]


uv run python -m src
--functions_definition data/input/functions_definition.json
--input data/input/function_calling_tests.json
--output data/output/function_calls.json




**steps for the project:**

Things to change or add:

    1.parsing: check functions and more
    2.function calling
    3.constrained decoding
























Constrained Decoding:
✅ Step 1

Take your function names:

fn_add_numbers
fn_greet
fn_reverse_string
✅ Step 2

Encode them

→ token IDs
✅ Step 3

Now you have:

[
  [id1, id2, id3, ...],
  [id4, id5, ...],
  ...
]
✅ Step 4

During generation:

At each step:

compare current generation
→ filter valid next tokens
→ restrict logits










||| Constrained Decoding |||

    Constrained generation is conceptually straightforward — we implement a class to apply RegEx constraints in under 40 lines of Python!

    

















