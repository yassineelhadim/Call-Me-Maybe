from pydantic import BaseModel, Field, model_validator # type: ignore
import json


class ouput_structure(BaseModel):
    def __init__(self, prompt: str, name: str, parameters: list):
        self.prompt: str = prompt
        self.name: str = name
        self.parameters: list = parameters
    
    def output_writer(self, data: list):
        x = {
            "prompt" : self.prompt,
            "name" : self.name,
            "parameters" : self.parameters
        }

        data.append(x)
        with open("data/output/prompt_output.json", "w") as f:
            json.dump(data, f, indent=2)