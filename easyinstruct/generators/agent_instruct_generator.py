import os
import json
from tqdm import tqdm
import pandas as pd
from easyinstruct import BasePrompt
from base_generator import BaseGenerator

prompt_template1 = (
    "Please check if following sentences contain rich ocean related information."
    " If so, output 'related'. Otherwise, output 'unrelated'"
    "\nSentences:\n")

prompt_template2 = (
    "You are a helpful ocean assistant. You are to extract the question from each of the answer provided."
    "\nAnswer:\n")

prompt_template3 = (
    "Assuming you are an expert in marine engineering and resources, please keep the meaning of the"
    " following sentences unchanged and provide as much professional knowledge as possible."
    "\nSentences:\n")


class AgentInstructGenerator(BaseGenerator):

    def __init__(self,
                 target_dir: str = "data/",
                 data_path: str = "data/train.jsonl",
                 generated_data_path: str = "generated_data.jsonl",
                 engine: str = "gpt-3.5-turbo",
                 ):
        super(AgentInstructGenerator, self).__init__(target_dir)
        self.data_path = data_path
        self.generated_data_path = os.path.join(self.target_dir, generated_data_path)
        self.engine = engine

    def generate_instructions(self):
        df = pd.read_json(self.data_path, lines=True)

        progress_bar = tqdm(total=len(df))

        with open(self.generated_data_path, "a") as fout:
            for index in range(len(df)):
                data_point = df.iloc[index]
                text = data_point['text']

                prompt1 = BasePrompt()
                prompt1.build_prompt(prompt_template1 + text)
                prompt1.get_openai_result(
                    engine=self.engine,
                    max_tokens=150,
                    temperature=0,
                    top_p=0,
                    frequency_penalty=0,
                    presence_penalty=0
                )

                if 'unrelated' in prompt1.output.lower():
                    continue

                prompt2 = BasePrompt()
                prompt2.build_prompt(prompt_template2 + text)
                prompt2.get_openai_result(
                    engine=self.engine,
                    max_tokens=150,
                    temperature=0,
                    top_p=0,
                    frequency_penalty=0,
                    presence_penalty=0
                )

                instruction = prompt2.output

                prompt3 = BasePrompt()
                prompt3.build_prompt(prompt_template3 + text)
                prompt3.get_openai_result(
                    engine=self.engine,
                    max_tokens=150,
                    temperature=0,
                    top_p=0,
                    frequency_penalty=0,
                    presence_penalty=0
                )

                content = prompt3.output

                data = {}
                data["instruction"] = instruction
                data["instances"] = [{
                    "input": "",
                    "output": content
                }]

                fout.write(json.dumps(data, ensure_ascii=False) + "\n")
                progress_bar.update(1)

    def generate(self):
        self.generate_instructions()
