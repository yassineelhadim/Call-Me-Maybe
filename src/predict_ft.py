import numpy
from llm_sdk import Small_LLM_Model


def function_list_tokenizer(llm: Small_LLM_Model, function_data: list) -> list:
    sequences = []
    for func in function_data:
        ft_ids = llm.encode(func["name"]).tolist()[0]
        sequences.append(ft_ids)
    return sequences


def choose_next_token1(logits: list, generated_part: list, sequences: list) -> int:
    allowed_tokens = []
    matching = [seq for seq in sequences if seq[:len(generated_part)] == generated_part]
    state = len(generated_part)
    for matched in matching:
        if state < len(matched):
            allowed_tokens.append(matched[state])
    best_idx = numpy.argmax([logits[token] for token in allowed_tokens])
    return allowed_tokens[best_idx]