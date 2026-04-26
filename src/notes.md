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
    4. what if there prompt needs a function that doesn't exists (solve it)


































||| Constrained Decoding |||

    Constrained generation is conceptually straightforward — we implement a class to apply RegEx constraints in under 40 lines of Python!
























Step 1:
  State
  "What part of the JSON am I generating?"

Step 2:
  "What structure is expected?"
  List | if else statements

Step 3:
  Allowed_tokens OR Value Tokens

Step 4:
  Masking

Step 5:
  Pick the best token

    

















