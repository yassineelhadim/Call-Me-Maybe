import numpy
from llm_sdk import Small_LLM_Model  # type: ignore
from typing import Any


def function_list_tokenizer(
    llm: Small_LLM_Model, function_data: list[dict[str, Any]]
) -> list[list[int]]:
    """
    Tokenize the list of function names from the function data.

    Args:
        llm (Small_LLM_Model): The language model for encoding.
        function_data (list): A list of function definitions.

    Returns:
        list[list[int]]: A list of encoded token sequences for each function name.
    """
    sequences: list[list[int]] = []
    for func in function_data:
        ft_ids = llm.encode(func["name"]).tolist()[0]
        sequences.append(ft_ids)
    return sequences


def is_function_match(
    prompt: str,
    function_data: list[dict[str, Any]],
) -> bool:
    """
    Determine if any available function matches the user prompt by checking
    if any meaningful words from the prompt appear in function names or
    descriptions.

    Args:
        prompt (str): The user's natural language request.
        function_data (list[dict[str, Any]]): A list of available function
            definitions, each containing a name and description.

    Returns:
        bool: True if a function likely matches the request, False otherwise.
    """
    stopwords = {
        "a", "an", "the", "is", "in", "of", "to", "and", "or",
        "for", "with", "what", "how", "can", "me", "my", "i",
        "it", "this", "that", "do", "does", "please", "could",
        "would", "all", "some", "any", "from", "by", "on", "at"
    }
    prompt_words = {
        w.strip("'\"?,!.").lower() for w in prompt.split()
    } - stopwords

    for func in function_data:
        if func["name"] == "fn_unknown":
            continue
        combined = (
            func["description"] + " " +
            func["name"].replace("fn_", "").replace("_", " ")
        )
        func_words = {
            w.strip("'\"?,!.") for w in combined.lower().split()
        } - stopwords
        if any(
            pw in fw or fw in pw
            for pw in prompt_words
            for fw in func_words
        ):
            return True
    return False


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
    best_idx = numpy.argmax([logits[token] for token in allowed_tokens])
    return allowed_tokens[best_idx]