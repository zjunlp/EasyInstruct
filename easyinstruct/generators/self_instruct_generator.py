import os
import json
import random
import re
import string
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool
from functools import partial
from rouge_score import rouge_scorer

from easyinstruct import FewshotCoTPrompt, BatchPrompt
from .base_generator import BaseGenerator

class SelfInstructGenerator(BaseGenerator):
    
    def __init__(self,
                 batch_dir: str = "data/generations/",
                 seed_tasks_path: str = "data/seed_tasks.jsonl",
                 num_instructions_to_generate: int = 100,
                 engine: str = "gpt-3.5-turbo",
                 num_prompt_instructions: int = 8,
                 batch_size: int = 1
                 ):
        super().__init__()
        self.batch_dir = batch_dir
        self.seed_tasks_path = seed_tasks_path
        self.num_instructions_to_generate = num_instructions_to_generate
        self.engine = engine
        self.num_prompt_instructions = num_prompt_instructions
        self.batch_size = batch_size


    def find_word_in_string(self, w, s):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search(s)


    def post_process_generations(self, response, message):
        if response is None or response["choices"][0]["finish_reason"] == "length":
            return []
        raw_instructions = re.split(r"\n\d+\s?\. ", message)
        instructions = []
        for inst in raw_instructions:
            inst = re.sub(r"\s+", " ", inst).strip()
            inst = inst.strip().capitalize()
            if inst == "":
                continue
            # filter out too short or too long instructions
            if len(inst.split()) <= 3 or len(inst.split()) > 150:
                continue
            # filter based on keywords that are not suitable for language models.
            if any(self.find_word_in_string(word, inst) for word in ["image", "images", "graph", "graphs", "picture", "pictures", "file", "files", "map", "maps", "draw", "plot", "go to", "program"]):
                continue
            # We found that the model tends to add "write a program" to some existing instructions, which lead to a lot of such instructions.
            # And it's a bit comfusing whether the model need to write a program or directly output the result. 
            # Here we filter them out.
            # Note this is not a comprehensive filtering for all programming instructions.
            if inst.startswith("Write a program"):
                continue
            # filter those starting with punctuation
            if inst[0] in string.punctuation:
                continue
            # filter those starting with non-english character
            if not inst[0].isascii():
                continue
            instructions.append(inst)
        return instructions
    
    def generate(self):
        seed_tasks = [json.loads(l) for l in open(self.seed_tasks_path, "r")]
        seed_instructions = [t["instruction"] for t in seed_tasks]
        print(f"Loaded {len(seed_instructions)} human-written seed instructions.")

        os.makedirs(self.batch_dir, exist_ok=True)
        request_idx = 0
        generated_instructions = []
        if os.path.exists(os.path.join(self.batch_dir, "generated_instructions.jsonl")):
            with open(os.path.join(self.batch_dir, "generated_instructions.jsonl"), "r") as f:
                for l in f:
                    instruction_info = json.loads(l)
                    generated_instructions.append(instruction_info["instruction"])
                    request_idx = instruction_info["request_idx"] + 1
            print(f"Loaded {len(generated_instructions)} generated instructions.")

        scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)

        progress_bar = tqdm(total=self.num_instructions_to_generate)
        if len(generated_instructions) > 0:
            progress_bar.update(len(generated_instructions))

        with open(os.path.join(self.batch_dir, "generated_instructions.jsonl"), "a") as fout:
            while len(generated_instructions) < self.num_instructions_to_generate:

                batch_inputs = []
                for _ in range(self.batch_size):
                    prompt_instructions = random.sample(seed_instructions, self.num_prompt_instructions)
                    random.shuffle(prompt_instructions)
                    fewshot_prompt = FewshotCoTPrompt()
                    fewshot_prompt.build_prompt(
                        prompt = "Come up with a series of tasks:\n", in_context_examples = prompt_instructions,
                        n_shots = self.num_prompt_instructions)
                    batch_inputs.append(fewshot_prompt)

                batch_prompt = BatchPrompt()
                batch_prompt.build_prompt(batch_inputs)
                batch_prompt.get_openai_result(
                    engine = self.engine,
                    temperature = 0.7,
                    top_p = 0.5,
                    frequency_penalty=0,
                    presence_penalty=2
                )
                batch_prompt.parse_response()

                instructions = []
                for prompt_request in batch_prompt.prompt_list:
                    new_instructions = self.post_process_generations(prompt_request.response, prompt_request.output)
                    instructions += new_instructions

                for inst in instructions:
                    with Pool(4) as p:
                        rouge_scores = p.map(partial(scorer.score, inst), seed_instructions + generated_instructions)
                    rouge_scores = [score["rougeL"].fmeasure for score in rouge_scores]
                    if max(rouge_scores) > 0.7:
                        continue
                    all_instructions = seed_instructions + generated_instructions
                    most_similar_instructions = {
                        all_instructions[i] : rouge_scores[i] for i in np.argsort(rouge_scores)[-10:][::-1]
                    }
                    generated_instructions.append(inst)
                    fout.write(json.dumps({
                        "instruction": inst,
                        "most_similar": most_similar_instructions,
                        "avg_similarity_score": float(np.mean(rouge_scores)),
                        "request_idx": request_idx
                    }) + "\n")
                    progress_bar.update(1)
                request_idx += 1


    def post_process():
        raise NotImplementedError