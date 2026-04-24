from llm_sdk import Small_LLM_Model


def main():
    prompt = "hello chat, how are you doing!"
    sdk_object = Small_LLM_Model()
    tensor_ids = sdk_object.encode(prompt)
    list_ids = tensor_ids.tolist()[0]
    generation_list = input_ids.copy()
    for _ in range(5):
        logits_output = sdk_object.get_logits_from_input_ids(generation_list)
        print(logits_output)


if __name__ == "__main__":
    main()
