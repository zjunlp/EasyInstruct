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

self_curation_prompt_template = """Below is an instruction from an user and a candidate answer. Evaluate whether or not the answer is a good example of how AI Assistant should respond to the user's instruction. Please assign a score using the following 5-point scale:
1: It means the answer is incomplete, vague, off-topic, controversial, or not exactly what the user asked for. For example, some content seems missing, numbered list does not start from the beginning, the opening sentence repeats user's question. Or the response is from another person's perspective with their personal experience (e.g. taken from blog posts), or looks like an answer from a forum. Or it contains promotional text, navigation text, or other irrelevant information.
2: It means the answer addresses most of the asks from the user. It does not directly address the user's question. For example, it only provides a high-level methodology instead of the exact solution to user's question.
3: It means the answer is helpful but not written by an AI Assistant. It addresses all the basic asks from the user. It is complete and self contained with the drawback that the response is not written from an AI assistant's perspective, but from other people's perspective. The content looks like an excerpt from a blog post, web page, or web search results. For example, it contains personal experience or opinion, mentions comments section, or share on social media, etc.
4: It means the answer is written from an AI assistant's perspective with a clear focus of addressing the instruction. It provide a complete, clear, and comprehensive response to user's question or instruction without missing or irrelevant information. It is well organized, self-contained, and written in a helpful tone. It has minor room for improvement, e.g. more concise and focused.
5: It means it is a perfect answer from an AI Assistant. It has a clear focus on being a helpful AI Assistant, where the response looks like intentionally written to address the user's question or instruction without any irrelevant sentences. The answer provides high quality content, demonstrating expert knowledge in the area, is very well written, logical, easy-to-follow, engaging and insightful. 

Please first provide a brief reasoning you used to derive the rating score, and then write "Score: <rating>" in the last line.

"""


class BacktranslationGenerator(BaseGenerator):
    def __init__(
        self,
        target_dir: str = "data/generations/",
        unlabelled_data_path: str = "data/unlabelled_data.jsonl",
        generated_data_path: str = "generated_data.jsonl",
        num_instructions_to_generate: int = 100,
        engine: str = "gpt-3.5-turbo",
        threshold: int = 3,
    ):
        super(BacktranslationGenerator, self).__init__(target_dir)
        self.unlabelled_data_path = unlabelled_data_path
        self.generated_data_path = os.path.join(self.target_dir, generated_data_path)
        self.num_instructions_to_generate = num_instructions_to_generate
        self.engine = engine
        self.threshold = threshold

    def self_augmentation(self, unlabelled_data):
        unlabelled_content = [d["content"] for d in unlabelled_data]

        augmented_data = []
        progress_bar = tqdm(total=self.num_instructions_to_generate)

        while len(augmented_data) < self.num_instructions_to_generate:
            content = random.choice(unlabelled_content)
            prompt = BasePrompt()
            prompt.build_prompt(f"{self_augmentation_prompt_template} {content}")
            prompt.get_openai_result(
                engine=self.engine,
                max_tokens=150,
                temperature=0,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=0,
            )

            if re.findall(r"INSTRUCTION:", prompt.output):
                new_instruction = re.split(r"INSTRUCTION:", prompt.output)[1].strip()
            else:
                new_instruction = prompt.output

            data = {}
            data["instruction"] = new_instruction
            data["instances"] = [{"input": "", "output": content}]
            augmented_data.append(data)
            progress_bar.update(1)

        return augmented_data

    def self_curation(self, augmented_data):
        regex = re.compile(r"[Ss]core:\s*(\d+)")
        curated_data = []

        for data in tqdm(augmented_data):
            prompt = BasePrompt()
            prompt.build_prompt(
                f"{self_curation_prompt_template}\n\nInstruction: {data['instruction']}\n\n Response:{data['instances'][0]['output']}"
            )
            prompt.get_openai_result(
                engine=self.engine,
                max_tokens=150,
                temperature=0,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=0,
            )

            curation_response = prompt.output
            data["curation_response"] = curation_response
            score_matched = regex.search(curation_response)
            data["score"] = int(score_matched.group(1)) if score_matched else None
            curated_data.append(data)

        return curated_data

    def generate(self):
        unlabelled_data = self.load_data_from_file(self.unlabelled_data_path)
        augmented_data = self.self_augmentation(unlabelled_data)
        curated_data = self.self_curation(augmented_data)
        self.dump_data_to_file(curated_data, self.generated_data_path)
