import os
import json
import random
from tqdm import tqdm

from easyinstruct import BasePrompt
from .self_instruct_generator import SelfInstructGenerator

base_breadth_instruction = """I want you act as a Prompt Creator.
Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.
This new prompt should belong to the same domain as the #Given Prompt# but be even more rare.
The LENGTH and complexity of the #Created Prompt# should be similar to that of the #Given Prompt#.
The #Created Prompt# must be reasonable and must be understood and responded by humans."""

base_depth_instruction = """I want you act as a Prompt Rewriter.
Your objective is to rewrite a given prompt into a more complex version to make those famous AI systems (e.g., chatgpt and GPT4) a bit harder to handle.
But the rewritten prompt must be reasonable and must be understood and responded by humans.
Your rewriting cannot omit the non-text parts such as the table and code in #The Given Prompt#:. Also, please do not omit the input in #The Given Prompt#.
You SHOULD complicate the given prompt using the following method: 
{}
You should try your best not to make the #Rewritten Prompt# become verbose, #Rewritten Prompt# can only add 10 to 20 words into #The Given Prompt#."""


class EvolInstructGenerator(SelfInstructGenerator):
    def __init__(
        self,
        target_dir: str = "data/generations/",
        data_format: str = "alpaca",
        seed_tasks_path: str = "data/seed_tasks.jsonl",
        generated_instructions_path: str = "evolved_instructions.jsonl",
        generated_instances_path: str = "evolved_instances.jsonl",
        num_instructions_to_generate: int = 100,
        engine: str = "gpt-3.5-turbo",
    ):
        super(EvolInstructGenerator, self).__init__(
            target_dir,
            data_format,
            seed_tasks_path,
            generated_instructions_path,
            generated_instances_path,
            num_instructions_to_generate,
            engine,
        )

    def createBreadthPrompt(self, instruction):
        prompt = base_breadth_instruction
        prompt += "#Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Created Prompt#:\r\n"
        return prompt

    def createConstraintsPrompt(self, instruction):
        prompt = base_depth_instruction.format(
            "Please add one more constraints/requirements into #The Given Prompt#'"
        )
        prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Rewritten Prompt#:\r\n"
        return prompt

    def createDeepenPrompt(self, instruction):
        prompt = base_depth_instruction.format(
            "If #The Given Prompt# contains inquiries about certain issues, the depth and breadth of the inquiry can be increased."
        )
        prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Rewritten Prompt#:\r\n"
        return prompt

    def createConcretizingPrompt(self, instruction):
        prompt = base_depth_instruction.format(
            "Please replace general concepts with more specific concepts."
        )
        prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Rewritten Prompt#:\r\n"
        return prompt

    def createReasoningPrompt(self, instruction):
        prompt = base_depth_instruction.format(
            "If #The Given Prompt# can be solved with just a few simple thinking processes, you can rewrite it to explicitly request multiple-step reasoning."
        )
        prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
        prompt += "#Rewritten Prompt#:\r\n"
        return prompt

    def generate_instructions(self):
        seed_instructions = [
            t["instruction"] for t in self.load_data_from_file(self.seed_tasks_path)
        ]
        print(f"Loaded {len(seed_instructions)} human-written seed instructions.")

        generated_instructions = []
        if os.path.exists(self.generated_instructions_path):
            generated_instructions = [
                inst["instruction"]
                for inst in self.load_data_from_file(self.generated_instructions_path)
            ]
            print(f"Loaded {len(generated_instructions)} generated instructions.")

        progress_bar = tqdm(total=self.num_instructions_to_generate)
        if len(generated_instructions) > 0:
            progress_bar.update(len(generated_instructions))

        with open(self.generated_instructions_path, "a") as fout:
            while len(generated_instructions) < self.num_instructions_to_generate:
                instruction = random.choice(seed_instructions)

                evol_prompts = []
                evol_prompts.append(self.createBreadthPrompt(instruction))
                evol_prompts.append(self.createConstraintsPrompt(instruction))
                evol_prompts.append(self.createDeepenPrompt(instruction))
                evol_prompts.append(self.createConcretizingPrompt(instruction))
                evol_prompts.append(self.createReasoningPrompt(instruction))

                prompt_instruction = random.choice(evol_prompts)

                prompt = BasePrompt()
                prompt.build_prompt(prompt_instruction)
                prompt.get_openai_result(
                    engine=self.engine,
                    max_tokens=2048,
                    temperature=1,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                )

                if any(
                    self.find_word_in_string(word, prompt.output)
                    for word in [
                        "#Given Prompt#",
                        "given prompt" "#The Given Prompt#",
                        "#Created Prompt#",
                        "created prompt",
                        "#Rewritten Prompt#",
                        "rewritten prompt",
                    ]
                ):
                    continue
                generated_instructions.append(prompt.output)

                fout.write(json.dumps({"instruction": prompt.output}) + "\n")
                progress_bar.update(1)
