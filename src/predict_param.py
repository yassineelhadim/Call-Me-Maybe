import numpy
from llm_sdk import Small_LLM_Model  # type: ignore
from typing import Any


def choose_next_token2(
    prompt: str,
    prompt_list: list[int],
    ft_name: str,
    llm: Small_LLM_Model,
    function_data: list[dict[str, Any]]
) -> list[int]:
    """
    Generate tokens for the parameters of a specific function.

    Args:
        prompt_list (list[int]): The list of tokens corresponding to
            the prompt.
        ft_name (str): The chosen function name to generate parameters for.
        llm (Small_LLM_Model): The language model used for token prediction.
        function_data (list[dict[str, Any]]): A list of available function
            definitions.

    Returns:
        list[int]: The list of generated token IDs representing the JSON
            parameters object.
    """
    func: dict[str, Any] | None = None
    for f in function_data:
        if f["name"] == ft_name:
            func = f
            break
    if func is None:
        empty_params: list[int] = llm.encode("{}").tolist()[0]
        return empty_params
    params: list[tuple[str, str]] = []
    for param_name, param_dict in func["parameters"].items():
        params.append((param_name, param_dict["type"]))
    if not params:
        empty_params_val: list[int] = llm.encode("{}").tolist()[0]
        return empty_params_val
    state: str = "START"
    generated: list[int] = []
    param_index: int = 0
    generation_list: list[int] = [p for p in prompt_list]
    string_length: int = 0
    while True:
        logits = llm.get_logits_from_input_ids(generation_list)
        allowed_tokens = []
        if state == "START":
            allowed_tokens = llm.encode("{").tolist()[0]
            state = "PARAM_NAME"

        elif state == "PARAM_NAME":
            param_str = f'"{params[param_index][0]}"'
            tokens = llm.encode(param_str).tolist()[0]
            generation_list.extend(tokens)
            generated.extend(tokens)
            state = "NEXT_COLON"
            continue

        elif state == "NEXT_COLON":
            import re
            numbers = re.findall(r"-\d+\.?\d*", prompt)
            is_negative = len(numbers) > 0
            if params[param_index][1] == "number" and is_negative:
                tokens = llm.encode(":").tolist()[0]
            else:
                tokens = llm.encode(": ").tolist()[0]
            generation_list.extend(tokens)
            generated.extend(tokens)
            if params[param_index][1] == "number":
                state = "NUMBER"
            elif params[param_index][1] == "string":
                state = "STRING_START"
            continue

        elif state == "NUMBER":
            best_token = int(numpy.argmax(logits))
            decoded = llm.decode([best_token])
            if (decoded.strip() != "" and
                    all(c in "0123456789.-" for c in decoded.strip())):
                generation_list.append(best_token)
                generated.append(best_token)
            else:
                # I will check if last part generated contains a "."
                full_gen_str = llm.decode(generated)
                val_str = full_gen_str.split(': ')[-1]
                if "." not in val_str:
                    dot_zero = llm.encode(".0").tolist()[0]
                    generation_list.extend(dot_zero)
                    generated.extend(dot_zero)
                state = "AFTER_VALUE"
            continue

        elif state == "STRING_START":
            allowed_tokens = llm.encode('"').tolist()[0]
            state = "STRING_CONTENT"

        elif state == "STRING_CONTENT":
            best_token = int(numpy.argmax(logits))
            decoded = llm.decode([best_token])
            if '"' in decoded or string_length > 200:
                before_quote = decoded.split('"')[0]
                if before_quote:
                    pre_tokens = llm.encode(before_quote).tolist()[0]
                    generation_list.extend(pre_tokens)
                    generated.extend(pre_tokens)
                quote_token = llm.encode('"').tolist()[0][0]
                generation_list.append(quote_token)
                generated.append(quote_token)
                state = "AFTER_VALUE"
                string_length = 0
            else:
                generation_list.append(best_token)
                generated.append(best_token)
                string_length += 1
            continue

        elif state == "AFTER_VALUE":
            if param_index == len(params) - 1:
                close_token = llm.encode("}").tolist()[0][0]
                generation_list.append(close_token)
                generated.append(close_token)
                state = "END"
                continue
            else:
                param_index += 1
                tokens = llm.encode(", ").tolist()[0]
                generation_list.extend(tokens)
                generated.extend(tokens)
                state = "PARAM_NAME"
                continue

        elif state == "END":
            break

        best_idx = int(
            numpy.argmax([logits[token] for token in allowed_tokens])
        )
        best_token = allowed_tokens[best_idx]
        generation_list.append(best_token)
        generated.append(best_token)
    return generated
