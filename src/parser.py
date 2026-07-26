import json
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class ReturnSchema(BaseModel):
    """Schema for a function return value."""
    model_config = ConfigDict(extra="forbid")
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Return type cannot be empty.")
        return value


class ParameterSchema(BaseModel):
    """Schema for a function parameter."""
    model_config = ConfigDict(extra="forbid")
    type: str

    @field_validator("type")
    def validate_type(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Parameter type cannot be empty.")
        return value


class FunctionDefinition(BaseModel):
    """Schema describing a function definition."""
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    parameters: dict[str, ParameterSchema]
    returns: ReturnSchema

    @field_validator("name", "description")
    def validate_string(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty.")
        return value


class Prompt(BaseModel):
    """Schema for an input prompt."""
    model_config = ConfigDict(extra="forbid")
    prompt: str

    @field_validator("prompt")
    def validate_prompt(cls, value: str) -> str:
        value = value.strip()
        # if not value:
        #     raise ValueError("Prompt cannot be empty.")
        return value


def format_ft_file(fp: str) -> list[FunctionDefinition]:
    """
    Validate the functions definition JSON file.

    Args:
        fp: Path to the functions definition file.

    Returns:
        List of validated FunctionDefinition objects.

    Raises:
        TypeError: If the root JSON object is not a list.
        ValueError: If duplicate function names exist or validation fails.
    """
    with open(fp, "r") as f:
        data: Any = json.load(f)
    if not isinstance(data, list):
        raise TypeError("Functions file data must be inside a list.")
    try:
        functions = [
            FunctionDefinition.model_validate(item)
            for item in data
        ]
    except ValidationError as e:
        raise ValueError(str(e)) from e
    names = [func.name for func in functions]
    if len(names) != len(set(names)):
        raise ValueError(
            "There are duplicate function names in the definitions file."
        )
    return functions


def function_calling_tests_parser(fp: str) -> list[Prompt]:
    """
    Validate the input prompts JSON file.

    Args:
        fp: Path to the input prompts file.

    Returns:
        List of validated Prompt objects.

    Raises:
        TypeError: If the root JSON object is not a list.
        ValueError: If validation fails.
    """
    with open(fp, "r") as f:
        data: Any = json.load(f)
    if not isinstance(data, list):
        raise TypeError("All prompts must be inside a list.")
    try:
        prompts = [
            Prompt.model_validate(item)
            for item in data
        ]
    except ValidationError as e:
        raise ValueError(str(e)) from e
    return prompts
