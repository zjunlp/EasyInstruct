import torch
from transformers import LlamaTokenizer, LlamaForCausalLM, GenerationConfig
from peft import PeftModel, get_peft_model, set_peft_model_state_dict, LoraConfig
from llama_cpp import Llama
from typing import Optional

from .base_engine import BaseEngine


class llamaEngine(BaseEngine):
    r"""
        llama Engine wrapper according to choosing use gpu or not
    """

    def __init__(self,base_path:str,gpu:bool=True,adapter_path:Optional[str]=None,multi_gpu:Optional[bool]=False):
        if gpu:
            self.engine=llama_gpu_Engine(base_path=base_path,adapter_path=adapter_path,multi_gpu=multi_gpu)
        else:
            self.engine=llama_cpp_Engine(base_path=base_path)
    def _call(self, prompt, stop=None,**kwargs):
        return self.engine(prompt,stop=stop,**kwargs)


class llama_gpu_Engine(BaseEngine):
    r"""
        llama Engine for inference.
        Example:
        >>>lengine=llamaEngine(base_path=YOUR_BASE_PATH,adapter_path=YOUR_ADAPTER_PATH)
        >>>print(lengine('介绍一下浙江大学'))
    """

    def __init__(self,base_path:str,adapter_path:Optional[str]=None,multi_gpu:Optional[bool]=False):
        
        self.tokenizer = LlamaTokenizer.from_pretrained(base_path)
        self.tokenizer.pad_token_id = 0
        self.tokenizer.padding_side = "left"
        """init model"""
        if not multi_gpu:
            self.model = LlamaForCausalLM.from_pretrained(
            base_path,
            load_in_8bit=True,
            device_map={'':'cuda:1'},
            )
            if adapter_path is not None:
                """apply lora"""
                config = LoraConfig(
                    r=8,
                    lora_alpha=16,
                    target_modules=["q_proj", "v_proj"],
                    lora_dropout=0.05,
                    bias="none",
                    task_type="CAUSAL_LM"
                )
                self.model = get_peft_model(self.model, config) 
                adapters_weights = torch.load(adapter_path, map_location="cuda:1")
                self.model = set_peft_model_state_dict(self.model, adapters_weights)
        else:
            """multi GPU enable float16"""
            self.model = LlamaForCausalLM.from_pretrained(
                base_path,
                torch_dtype=torch.float16,
                device_map="auto",
            )
            if adapter_path is not None:
                """apply lora"""
                self.model = PeftModel.from_pretrained(
                    self.model, 
                    adapter_path,
                    torch_dtype=torch.float16
                )

    def _call(self, prompt, stop=None,**kwargs):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].cuda()      
        #set default values
        temperature=kwargs.pop('temperature',0.6)
        top_p=kwargs.pop('top_p',0.95)
        repetition_penalty=kwargs.pop('repetition_penalty',1.15)
        max_new_tokens=kwargs.pop('max_new_tokens',256)
        generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
        )
        with torch.no_grad():
            generation_output = self.model.generate(
                input_ids=input_ids,
                generation_config=generation_config,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=max_new_tokens,
            )
        s = generation_output.sequences[0]
        output = self.tokenizer.decode(s,skip_special_tokens=True)
        del input_ids, generation_output,s
        torch.cuda.empty_cache()
        return output

class llama_cpp_Engine(BaseEngine):
    def __init__(self,base_path:str):
        self.model= Llama(model_path=base_path)

    def _call(self, prompt, stop=None,**kwargs):
        if stop is None:
            stop=["\n"]
        max_tokens=kwargs.pop('max_new_tokens',256),
        output=self.model(prompt,stop=stop,max_tokens=max_tokens)
        return output
