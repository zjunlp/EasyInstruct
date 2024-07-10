import torch
from transformers import (
    AutoConfig,
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig
)
import argparse
from peft import PeftModel
import json


def prompt_template(prompt_name, ins):
    if prompt_name == 'baichuan2':
        return '<reserved_106>' + ins + '<reserved_107>'
    elif prompt_name == 'llama2_zh':
        return '[INST] ' + '<<SYS>>\nYou are a helpful assistant. 你是一个乐于助人的助手。\n<</SYS>>\n\n' + ins + '[/INST]'
    elif prompt_name == 'llama2':
        return '[INST] ' + "<<SYS>>\nYou are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\n<</SYS>>\n\n" + ins + '[/INST]'
    return ins


def get_tokenizer_model(model_name_or_path, lora_path=None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = AutoConfig.from_pretrained(model_name_or_path, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        config=config,
        device_map="auto",  
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    if lora_path is not None:
        model = PeftModel.from_pretrained(
            model,
            lora_path,
        )
    model.eval()
    return tokenizer, model, device


def get_llm_sampling(model_name_or_path, options):
    from vllm import LLM, SamplingParams
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
    llm = LLM(model=model_name_or_path, trust_remote_code=True)
    sampling_params = SamplingParams(
        temperature=0.2,
        use_beam_search=False,
        max_tokens=options.max_new_tokens,
    )
    return tokenizer, llm, sampling_params


def get_ie_llm_cpl(sintruct, tokenizer, model, device, prompt_name, options):
    sintruct = prompt_template(prompt_name, sintruct) 
    input_ids = tokenizer.encode(sintruct, return_tensors="pt").to(device)
    input_length = input_ids.size(1)
    generation_output = model.generate(
        input_ids=input_ids, 
        generation_config=GenerationConfig(max_length=options.max_length, max_new_tokens=options.max_new_tokens, return_dict_in_generate=True), 
        pad_token_id=tokenizer.eos_token_id
    )
    generation_output = generation_output.sequences[0]
    generation_output = generation_output[input_length:]
    output = tokenizer.decode(generation_output, skip_special_tokens=True)
    return output


def get_ie_llm_cpl_vllm(sintruct, tokenizer, llm, sampling_params, prompt_name, device):
    sintruct = prompt_template(prompt_name, sintruct) 
    input_ids = tokenizer.encode(sintruct, return_tensors="pt").to(device)
    output = llm.generate(
        sampling_params=sampling_params,
        prompt_token_ids=input_ids, 
        use_tqdm=True
    )
    if type(output) == list:
        output = output[0]
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="")
    parser.add_argument("--output_file", type=str, default="")
    parser.add_argument("--model_name_or_path", type=str, default="")
    parser.add_argument("--prompt_name", type=str, default="baichuan2")
    parser.add_argument("--lora_path", type=str, default=None)
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    parser.add_argument("--use_vllm", action="store_true")
    options = parser.parse_args()

    if options.use_vllm:
        tokenizer, llm, sampling_params = get_llm_sampling(options.model_name_or_path, options)
    else:
        tokenizer, model, device = get_tokenizer_model(options.model_name_or_path, options.lora_path)
    
    records = []
    with open(options.input_file, "r") as reader:
        for line in reader:
            data = json.loads(line)
            records.append(data)

    with open(options.output_file, 'w') as writer:
        for i, record in enumerate(records):
            if options.use_vllm:
                result = get_ie_llm_cpl(record['instruction'], tokenizer, model, device, options.prompt_name, options)
            else:
                result = get_ie_llm_cpl_vllm(record['instruction'], tokenizer, llm, sampling_params, options.prompt_name, device)
            record['output'] = result
            writer.write(json.dumps(record, ensure_ascii=False)+'\n') 
