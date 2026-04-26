import json
from pydantic import BaseModel, Field, model_validator # type: ignore
import numpy # type: ignore
from typing import Any
from llm_sdk import Small_LLM_Model

def output_list(data: list, prompt: str, name: str, parameters: dict) -> None:

    x = {
        "prompt" : prompt,
        "name" : name,
        "parameters" : parameters
    }
    data.append(x)

def check(generated_part: list, seq: list, index: int) -> bool:
    for i in range(index - 1):
        if generated_part[i] is not seq[i]:
            return False
        else:
            continue
    return True

def choose_next_token1(logits: list, generated_part: list, sequences: list):
    # 1. find matching sequences
    index = len(generated_part) - 1
    matching = [
        seq for seq in sequences
        if check(generated_part, seq, index) is True
    ]
    # 2. I create a set of allowed tokens
    allowed_tokens = set()
    state = len(generated_part)
    for matched in matching:
        allowed_tokens.add(matched[state])
    # 3. I mask then I choose the best token
    for logit in logits:
        if logit not in allowed_tokens:
            logit = -float("inf")
    return logits.index(max(logits))


def function_list_tokenizer() -> list:
    llm = Small_LLM_Model()
    ft_list = [
        "fn_add_numbers",
        "fn_greet",
        "fn_reverse_string",
        "fn_get_square_root",
        "fn_substitute_string_with_regex"
    ]
    sequences = []
    for ft in ft_list:
        ft_ids = llm.encode(ft).tolist()[0]
        sequences.append(ft_ids)
    return sequences


def function_calling(prompts: list[str]) -> None:
    sdk_object = Small_LLM_Model()
    for prompt in prompts:
        # p_t_ids is prompt_token_ids, which is the 2D Tensor that has the id of each token
        p_t_ids = sdk_object.encode(prompt)
        p_t_ids = p_t_ids.tolist()[0]
        token_ids = p_t_ids.copy()
        generation_list = token_ids.copy()
        generated_part = []
        sequences = [ft_id for ft_id in function_list_tokenizer()]
        for _ in range(20):
            logits = sdk_object.get_logits_from_input_ids(generation_list)
            logits = logits.tolist()[0]
            chosen = choose_next_token1(logits, generated_part, sequences)
            generated_part.append(chosen)
            generation_list.append(chosen)
            if generated_part in sequences:
                break
        for _ in range (30):
            pass


# Still need to check the functions in json file: no duplicates 
# (create a list and store seen ones on it and check on each new one),
# only spicific functions (so hardcoded statment with a list)
def format_ft_file(fd: str) -> None:
    with open(fd, "r") as f:
        func_json = json.load(f)
    if not isinstance(func_json, list):
        raise TypeError("Functions file data myst be inside a list!")
    for ft in func_json:
        if not isinstance(ft, dict):
            raise TypeError("An item in the file is not a dict!")

        if "name" not in ft: # name
            raise KeyError("Missing 'name' key")
        if not isinstance(ft["name"], str):
            raise TypeError("The name should be a str Datatype.")
        if ft["name"].strip() == "":
            raise ValueError("Empty name!")

        if "description" not in ft: # description
            raise KeyError("Missing 'description' key")
        if not isinstance(ft["description"], str):
            raise TypeError("The description should be a str Datatype.")
        if ft["description"].strip() == "":
            raise ValueError("Empty description!")

        if "returns" not in ft: # returns
            raise KeyError("Returns is MISSING!")
        if not isinstance(ft["returns"], dict):
            raise TypeError("The returns should be a dict!")
        if "type" not in ft["returns"]:
            raise ValueError("Type of returns is MISSING!")
        if not (ft["returns"]["type"] == "number" or ft["returns"]["type"] == "string"):
            raise ValueError("The type of returns should either be \"string\" or \"number\"!")

        if "parameters" not in ft: # paramaters
            raise KeyError("Parameters are MISSING!")
        if not isinstance(ft["parameters"], dict):
            raise TypeError("The parameters should be a dict!")
        for k, v in ft["parameters"].items():
            # check if the key is a str and its value is a dict and then we check the k, v inside the dict
            if not isinstance(k, str):
                raise TypeError("The parameter should be in form \"paramater1\"")
            if not isinstance(v, dict):
                raise TypeError("The paramter value should be a dict!")
            if "type" not in v:
                raise KeyError("Type of one of the parameters is MISSING!")
            if not (v["type"] == "number" or v["type"] == "string"):
                raise ValueError("The type of arguments should be either \"string\" or \"number\"")


def main() -> None:

    with open("data/input/function_calling_tests.json", "r") as f:
        input_data = json.load(f) # input_data is a list of dict

    try:
        if not isinstance(input_data, list):
            raise TypeError("All prompts must be in a list!")
        for d in input_data:
            if not isinstance(d, dict):
                raise TypeError("Each item inside the list must be a dict!")
            if "prompt" not in d:
                raise KeyError("Prompt key is MISSING.")
            if not isinstance(d["prompt"], str):
                raise TypeError("The prompt should be a str Datatype.")
            if d["prompt"].strip() == "":
                raise ValueError("Empty Prompt!")
    except Exception as e:
        print(f"Error: {e}")

    try:
        format_ft_file("data/input/functions_definition.json")
    except Exception as e:
        print(f"Error: {e}")

    # I put the data in output json file -  only for the final result
    data = []
    for prompt in input_data:
        # create an object with one prompt then append it to ouput file
        parameters = {}
        output_list(data, prompt["prompt"], "fn_fake", parameters)

    with open("data/output/prompt_output.json", "w") as f:
        json.dump(data, f, indent=2)

    # Function-calling wiht the LLM
    # encode, send token IDs, choose the highest prob, then repeat 5 times
    function_calling(input_data)


if __name__ == "__main__":
    main() 
