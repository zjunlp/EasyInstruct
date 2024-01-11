import os
import sys

import fire
import torch
import transformers
from peft import PeftModel
from transformers import GenerationConfig, LlamaForCausalLM, LlamaTokenizer
import json
from tqdm import tqdm

from utils.prompter import Prompter

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

def main(
    load_8bit: bool = False,
    base_model: str = "",
    lora_weights: str = "",
    share_gradio: bool = False,
    output_file: str= "generates/default.json",
    input_file: str='alpaca_data_cleaned.json',
    model_name: str="none"
):
    assert (
        base_model
    ), "Please specify a --base_model, e.g. --base_model='decapoda-research/llama-7b-hf'"

    prompter = Prompter()
    tokenizer = LlamaTokenizer.from_pretrained(base_model)
    if device == "cuda":
        model = LlamaForCausalLM.from_pretrained(
            base_model,
            load_in_8bit=load_8bit,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        if lora_weights != "":
            model = PeftModel.from_pretrained(
                model,
                lora_weights,
                torch_dtype=torch.bfloat16,
            )

    model.eval()

    def evaluate(
        instruction,
        input=None,
        temperature=0.1,
        top_p=0.75,
        top_k=40,
        num_beams=4,
        max_new_tokens=512,
        **kwargs,
    ):
        prompt = prompter.generate_prompt(instruction, input)
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(device)
        generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_beams=num_beams,
            **kwargs,
        )
        with torch.no_grad():
            generation_output = model.generate(
                input_ids=input_ids,
                generation_config=generation_config,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=max_new_tokens,
            )
        s = generation_output.sequences[0]
        output = tokenizer.decode(s)
        return prompter.get_response(output)


    instructions = json.load(open(input_file, 'r'))
    for instruction in tqdm(instructions):
        result = {
            'instruction': instruction['instruction'],
            'input': instruction['input'],
            'output': evaluate(instruction),
            'generator': model_name,
            "dataset": instruction["dataset"],
            "datasplit": instruction["datasplit"],
        }
        print("Instruction:", instruction)
        print("Response:", result['output'])
        with open(output_file, "a+") as f:
            f.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    fire.Fire(main)