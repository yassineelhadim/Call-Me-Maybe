import json
import sys
import time
import os
from typing import Any
from llm_sdk import Small_LLM_Model  # type: ignore
try:
    from .parser import format_ft_file
    from .parser import function_calling_tests_parser
    from .predict_ft import choose_next_token1
    from .predict_ft import function_list_tokenizer
    from .predict_ft import find_best_matching_function
    from .predict_param import choose_next_token2
except ImportError:
    from parser import format_ft_file
    from parser import function_calling_tests_parser
    from predict_ft import choose_next_token1
    from predict_ft import function_list_tokenizer
    from predict_ft import find_best_matching_function
    from predict_param import choose_next_token2


def create_function_context(functions_list: list[dict[str, Any]]) -> str:
    """
    Create a text context string from a list of function definitions.

    Args:
        functions_list (list[dict[str, Any]]): A list of dictionaries,
            each describing a function.

    Returns:
        str: A formatted string describing the available functions and usage.
    """
    unk_dict = {
        "name": "fn_unknown",
        "description": "Use when no available function "
                       "matches the user's request.",
        "parameters": {},
        "returns": {
            "type": "string"
        }
    }
    functions_list = functions_list + [unk_dict]
    context = "Available functions:\n"
    for func in functions_list:
        param_names = ", ".join(func["parameters"].keys())
        m = f"{func['description']} (params: {param_names})\n"
        context += f"- {func['name']}: {m}"
    context += "\n"
    context += "\nExample:\n"
    context += "Call: fn_substitute_string_with_regex"
    context += "{\"source_string\": \"hello world foo\", "
    context += "\"regex\": \"\\\\s+\", \"replacement\": \"_\"}\n\n"
    return context


def function_calling(
    prompts: list[str],
    llm: Small_LLM_Model,
    function_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Generate function calls for a list of user prompts.

    Args:
        prompts (list[str]): A list of user prompts.
        llm (Small_LLM_Model): The language model to use for generation.
        function_data (list[dict[str, Any]]): A list of available
            function definitions.

    Returns:
        list[dict[str, Any]]: A list of dictionaries containing the parsed
            function calls with their respective names and parameters.
    """
    results: list[dict[str, Any]] = []
    for prompt in prompts:
        if not prompt.strip():
            print("Empty prompt, it will be skipped.")
            continue
        # Necessary lists and objects for generating tokens
        function_context = create_function_context(function_data)
        full_prompt = (
            function_context + "User request: " + prompt + "\nCall: "
        )
        p_t_ids = llm.encode(full_prompt).tolist()[0]
        generation_list: list[int] = p_t_ids.copy()
        generated_part: list[int] = []
        sequences: list[list[int]] = function_list_tokenizer(
            llm, function_data
        )
        # checking if the function name generated matches
        # the function names in json file
        best_function = find_best_matching_function(
            prompt,
            function_data,
        )
        if best_function is None:
            results.append({
                "prompt": prompt,
                "name": "fn_unknown",
                "parameters": {}
            })
            continue
        for _ in range(200):
            logits = llm.get_logits_from_input_ids(generation_list)
            chosen = choose_next_token1(logits, generated_part, sequences)
            generated_part.append(chosen)
            generation_list.append(chosen)
            if generated_part in sequences:
                break
        function_name = llm.decode(generated_part)
        generated = choose_next_token2(
            prompt, generation_list, function_name, llm, function_data
        )
        parameters_str = llm.decode(generated)
        print(parameters_str)
        parameters = json.loads(parameters_str)
        results.append({
            "prompt": prompt,
            "name": function_name,
            "parameters": parameters
        })
    return results


def main() -> None:
    """
    Main entry point for the script. Parses arguments, validates
    the input and functions definition files, and generates output.
    """
    args: list[str] = sys.argv[1:]
    functions_definition: str | None = None
    input_file: str | None = None
    output_file: str | None = None
    functions_definition = "data/input/functions_definition.json"
    input_file = "data/input/function_calling_tests.json"
    output_file = "data/output/function_calls.json"
    # I need to fix this and add defaults
    for i in range(len(args)):
        if args[i] == "--functions_definition":
            functions_definition = args[i + 1]
        elif args[i] == "--input":
            input_file = args[i + 1]
        elif args[i] == "--output":
            output_file = args[i + 1]
    if not functions_definition or not input_file or not output_file:
        raise Exception(
            "Usage: uv run python main.py --functions_definition "
            "<file> --input <file> --output <file>"
        )
    try:
        function_calling_tests_parser(input_file)
        format_ft_file(functions_definition)
    except Exception as e:
        raise Exception(f'Error during validation: {e}')
    try:
        with open(input_file, "r") as f:
            input_data = json.load(f)
        with open(functions_definition, "r") as f:
            function_data = json.load(f)
    except Exception as e:
        raise Exception(f'Json file related Error, {e}')
    prompts = [data["prompt"] for data in input_data]
    llm = Small_LLM_Model()

    start_time = time.time()
    try:
        results = function_calling(prompts, llm, function_data)
    except Exception as e:
        raise Exception(f'Function Calling Error, {e}')
    end_time = time.time()
    duration = end_time - start_time

    directory = os.path.dirname(output_file)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print("-" * 30)
    print("Execution Summary:")
    print(f"Total prompts processed: {len(prompts)}")
    print(f"Output saved to:         {output_file}")
    print(f"Total execution time:    {duration:.2f} seconds")
    print("-" * 30)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'Error: {e}')
