import json
from typing import Any


# Still need to check the functions in json file: no duplicates
# (create a list and store seen ones on it and check on each new one),
# only spicific functions (so hardcoded statment with a list)
def format_ft_file(fp: str) -> None:
    """
    Validate the functions definition JSON file.

    Args:
        fp (str): File path to the functions definition file.

    Raises:
        TypeError: If the JSON data is of incorrect type.
        KeyError: If required keys are missing in the data.
        ValueError: If data contains empty strings, invalid types, or duplicates.
    """
    with open(fp, "r") as f:
        func_json: Any = json.load(f)
    funcs_names: list[str] = []
    if not isinstance(func_json, list):
        raise TypeError("Functions file data myst be inside a list!")
    for ft in func_json:
        if not isinstance(ft, dict):
            raise TypeError("An item in the file is not a dict!")

        if "name" not in ft:  # name
            raise KeyError("Missing 'name' key")
        if not isinstance(ft["name"], str):
            raise TypeError("The name should be a str Datatype.")
        if ft["name"].strip() == "":
            raise ValueError("Empty name!")

        if "description" not in ft:  # description
            raise KeyError("Missing 'description' key")
        if not isinstance(ft["description"], str):
            raise TypeError("The description should be a str Datatype.")
        if ft["description"].strip() == "":
            raise ValueError("Empty description!")

        if "returns" not in ft:  # returns
            raise KeyError("Returns is MISSING!")
        if not isinstance(ft["returns"], dict):
            raise TypeError("The returns should be a dict!")
        if "type" not in ft["returns"]:
            raise ValueError("Type of returns is MISSING!")
        if not (ft["returns"]["type"] == "number" or
                ft["returns"]["type"] == "string"):
            raise ValueError(
                "The type of returns should be \"string\" or \"number\"!"
            )

        if "parameters" not in ft:  # paramaters
            raise KeyError("Parameters are MISSING!")
        if not isinstance(ft["parameters"], dict):
            raise TypeError("The parameters should be a dict!")
        for k, v in ft["parameters"].items():
            # check if the key is a str and its value is a dict
            # and then we check the k, v inside the dict
            if not isinstance(k, str):
                raise TypeError(
                    "The parameter should be in form \"paramater1\""
                )
            if not isinstance(v, dict):
                raise TypeError("The paramter value should be a dict!")
            if "type" not in v:
                raise KeyError("Type of one of the parameters is MISSING!")
            if not (v["type"] == "number" or v["type"] == "string"):
                raise ValueError(
                    "The type of arguments should be either "
                    "\"string\" or \"number\""
                )
        funcs_names.append(ft["name"])
    if len(funcs_names) != len(set(funcs_names)):
        raise ValueError("There is Duplicates in Functions Definitions File.")


def function_calling_tests_parser(fp: str) -> None:
    """
    Validate the input prompts JSON file.

    Args:
        fp (str): File path to the input data file.

    Raises:
        TypeError: If the data or prompt elements are of incorrect type.
        KeyError: If the prompt key is missing.
        ValueError: If a prompt is empty.
    """
    with open(fp, "r") as f:
        input_data: Any = json.load(f)  # input_data is a list of dict

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
