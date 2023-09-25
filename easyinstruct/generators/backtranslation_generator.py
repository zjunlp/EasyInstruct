import os
import re
import json
import random
from tqdm import tqdm

from easyinstruct import BasePrompt
from .base_generator import BaseGenerator


self_augmentation_prompt_template = """This is a chat between a curious user and a helpful artificial intelligence assistant.

Given the assistant's reponse, please try to predict the user's instruction. Please avoid giving uncertain instruction. 

RESPONSE: 1. Werewolf 2. Who Am I?  3. Charades 4. Balderdash 5. Pictionary 6. Two Truths and a Lie 7. Uno 8. Story Starters 9. Truth or Dare 10. Kubb

INSTRUCTION: Suggest some games that can be played by a group of people.

RESPONSE: The observer effect in quantum mechanics refers to the impact of measurement on a quantum system.  In quantum computing, qubits exist in superpositions of states until measured.  Measurement collapses the qubits into definite states, affecting the outcome.  This phenomenon introduces the need for quantum algorithms to be carefully designed to harness superposition and entanglement while minimizing the impact of measurement during computation.

INSTRUCTION: How does the phenomenon of an observer affect the way quantum computers process data?

RESPONSE:"""


class BacktranslationGenerator(BaseGenerator):
    
    def __init__(self,
                 seed_data_path: str = "data/seed_data.jsonl",
                 unlabelled_data_path: str = "data/unlabelled_data.jsonl",
                 augmented_data_path: str = "augmented_data.jsonl",
                 num_instructions_to_augement: int = 10,
                 engine: str = "gpt-3.5-turbo",
                 ):
        super().__init__()
        self.seed_data_path = seed_data_path
        self.unlabelled_data_path = unlabelled_data_path
        self.augmented_data_path = os.path.join(self.target_dir, augmented_data_path)
        self.num_instructions_to_augement = num_instructions_to_augement
        self.engine = engine     

    def self_augmentation(self):
        unlabelled_data = [json.loads(l) for l in open(self.unlabelled_data_path, "r")]
        unlabelled_content = [d["content"] for d in unlabelled_data]
        print(f"Loaded {len(unlabelled_content)} unlabelled data.")

        augmented_instructions = []
        if os.path.exists(self.augmented_data_path):
            with open(self.augmented_data_path, "r") as f:
                for l in f:
                    instruction_info = json.loads(l)
                    augmented_instructions.append(instruction_info["instruction"])
            print(f"Loaded {len(augmented_instructions)} augmented instructions.")

        progress_bar = tqdm(total=self.num_instructions_to_augement)
        if len(augmented_instructions) > 0:
            progress_bar.update(len(augmented_instructions))

        with open(self.augmented_data_path, "a") as fout:
            while len(augmented_instructions) < self.num_instructions_to_augement:
                content = random.choice(unlabelled_content)
                prompt = BasePrompt()
                prompt.build_prompt(f"{self_augmentation_prompt_template} {content}")
                prompt.get_openai_result(
                    engine = self.engine,
                    max_tokens = 150,
                    temperature = 0,
                    top_p = 0,
                    frequency_penalty = 0,
                    presence_penalty = 1.5
                )

                if re.findall(r"INSTRUCTION:", prompt.output):
                    new_instruction = re.split(r"INSTRUCTION:", prompt.output)[1].strip()
                else:
                    new_instruction = prompt.output

                augmented_instructions.append(new_instruction)

                fout.write(json.dumps({
                    "instruction": new_instruction,
                    "response": content
                }) + "\n")
                progress_bar.update(1)
    
    def self_curation(self):
        raise NotImplementedError
    
    def generate(self):
        self.self_augmentation()