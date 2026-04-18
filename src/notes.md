uv run python -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]


uv run python -m src
--functions_definition data/input/functions_definition.json
--input data/input/function_calling_tests.json
--output data/output/function_calls.json




**steps for the project:**

    1. encode 
    2. for loop sending token by token
    3. get logits and choose next token based on score
    4. Append it
        input_ids = input_ids + [new_token]

        Now your sequence is longer.
    5. repeat
    6. I will stop after 5 times of repeating, meanin for range(5)
        The reason is because later the stop should be after generating a specific structure output.
            


for each prompt:
    encode prompt
    generate tokens (loop)
    decode result
    store output








































the first step is: generation_list = the first work's token_id
the second step is: send the generation list to the get_logits..... function in llm-sdk
the third step is: append it to the generation list








What I am doing now:
    trying to append the prediction of the llm to the generation_list









