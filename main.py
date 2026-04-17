from llm_sdk import Small_LLM_Model

if __name__ == "__main__":
    model = Small_LLM_Model()
    ids = model.encode()
    print(ids)