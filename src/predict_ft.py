import numpy
from llm_sdk import Small_LLM_Model
from typing import Any
import re


def function_list_tokenizer(
    llm: Small_LLM_Model, function_data: list[dict[str, Any]]
) -> list[list[int]]:
    """
    Tokenize the list of function names from the function data.

    Args:
        llm (Small_LLM_Model): The language model for encoding.
        function_data (list[dict[str, Any]]): A list of function
            definitions.

    Returns:
        list[list[int]]: A list of encoded token sequences for each
            function name.
    """
    sequences: list[list[int]] = []
    for func in function_data:
        ft_ids = llm.encode(func["name"]).tolist()[0]
        sequences.append(ft_ids)
    return sequences


def normalize_words(text: str) -> set[str]:
    """
    Normalize a string into a set of lowercase words.
    """
    text = text.lower().replace("_", " ")
    words = re.findall(r"[a-z0-9]+", text)
    return set(words)


def find_best_matching_function(
    prompt: str,
    function_data: list[dict[str, Any]],
) -> str | None:
    """
    Return the name of the function that best matches the prompt,
    or None if no function is similar enough.
    """
    stopwords = {
        "a", "an", "the", "is", "in", "of", "to", "and", "or",
        "for", "with", "what", "how", "can", "me", "my", "i",
        "it", "this", "that", "do", "does", "please", "could",
        "would", "all", "some", "any", "from", "by", "on", "at"
    }

    prompt_words = normalize_words(prompt) - stopwords

    best_name: str | None = None
    best_score = 0

    for func in function_data:
        function_words = (
            normalize_words(func["name"]) |
            normalize_words(func["description"])
        ) - stopwords

        score = len(prompt_words & function_words)

        if score > best_score:
            best_score = score
            best_name = func["name"]

    # Require at least one meaningful common word.
    if best_score == 0:
        return None

    return best_name


def choose_next_token1(
    logits: list[float], generated_part: list[int], sequences: list[list[int]]
) -> int:
    """
    Choose the next token for generating a function name, restricted
    by the allowed tokens from the known function name sequences.

    Args:
        logits (list): Logits from the language model.
        generated_part (list): The sequence of tokens generated so far.
        sequences (list): A list of all valid function name sequences.

    Returns:
        int: The next token ID to append to the generation.
    """
    allowed_tokens: list[int] = []
    matching: list[list[int]] = [
        seq for seq in sequences
        if seq[:len(generated_part)] == generated_part
    ]
    state = len(generated_part)
    for matched in matching:
        if state < len(matched):
            allowed_tokens.append(matched[state])
    best_idx = int(numpy.argmax([logits[token] for token in allowed_tokens]))
    return allowed_tokens[best_idx]
