from llm_sdk import Small_LLM_Model


def main():
    prompt = "hello chat, how are you doing!"
    sdk_object = Small_LLM_Model()
    tensor_ids = sdk_object.encode(prompt)
    list_ids = tensor_ids.tolist()
    list_ids = list_ids[0]
    for token_id in list_ids:
        logits_output = sdk_object.get_logits_from_input_ids(token_id)
        print(logits_output)


if __name__ == "__main__":
    main()
