import os
import re
import json
import random
from tqdm import tqdm
import pandas as pd
from easyinstruct import BasePrompt
from base_generator import BaseGenerator

prompt_template = (
    "Assuming you are an expert in marine engineering and resources, if any ocean name or place name appears"
    " in the following question, you should replace it with a different ocean name or place name. "
    " Then rewrite the question in a more professional way, but do not answer the question."
    " Question:\n"
)


class OceanGPTGenerator(BaseGenerator):
    def __init__(
        self,
        target_dir: str = "data/",
        data_path: str = "data/train.jsonl",
        generated_data_path: str = "generated_data.jsonl",
        engine: str = "gpt-3.5-turbo",
    ):
        super(OceanGPTGenerator, self).__init__(target_dir)
        self.data_path = data_path
        self.generated_data_path = os.path.join(self.target_dir, generated_data_path)
        self.engine = engine

    def generate_instructions(self):
        # data_list = self.load_data_from_file(self.data_path)
        df = pd.read_json(self.data_path, lines=True)

        progress_bar = tqdm(total=len(df))

        with open(self.generated_data_path, "a") as fout:
            for index in range(len(df)):
                data_point = df.iloc[index]
                en_input = data_point["en_input"]
                prompt = BasePrompt()
                prompt.build_prompt(prompt_template + en_input)
                prompt.get_openai_result(
                    engine=self.engine,
                    max_tokens=150,
                    temperature=0,
                    top_p=0,
                    frequency_penalty=0,
                    presence_penalty=0,
                )

                new_instruction = prompt.output

                prompt = BasePrompt()
                prompt.build_prompt(new_instruction)
                prompt.get_openai_result(
                    engine=self.engine,
                    max_tokens=150,
                    temperature=0,
                    top_p=0,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                content = prompt.output

                data = {}
                data["instruction"] = new_instruction
                data["instances"] = [{"input": "", "output": content}]

                fout.write(json.dumps(data, ensure_ascii=False) + "\n")
                progress_bar.update(1)

    def generate(self):
        self.generate_instructions()
