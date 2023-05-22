import torch
from transformers import LlamaTokenizer, LlamaForCausalLM, GenerationConfig
from peft import PeftModel, get_peft_model, set_peft_model_state_dict, LoraConfig
from typing import Optional
from transformers import GenerationConfig

class llamaEngine():
    r"""
        llama Engine for inference.
        Example:
        >>>lengine=llamaEngine(base_path=YOUR_BASE_PATH,device_map="auto",adapter_path=YOUR_ADAPTER_PATH)
        >>>print(lengine('介绍一下浙江大学'))
    """
    def __init__(self,base_path:str,device_map:str,adapter_path:Optional[str]=None,):
        
        self.tokenizer = LlamaTokenizer.from_pretrained(base_path)
        self.tokenizer.pad_token_id = 0
        self.tokenizer.padding_side = "left"
        """init model"""
        self.model = LlamaForCausalLM.from_pretrained(
        base_path,
        load_in_8bit=True,
        device_map=device_map,
        )
        if adapter_path is not None:
            """apply lora"""
            # config = LoraConfig(
            #     r=8,
            #     lora_alpha=16,
            #     target_modules=["q_proj", "v_proj"],
            #     lora_dropout=0.05,
            #     bias="none",
            #     task_type="CAUSAL_LM"
            # )
            # self.model = get_peft_model(self.model, config) 
            # adapters_weights = torch.load(adapter_path)
            # self.model = set_peft_model_state_dict(self.model, adapters_weights)
            self.model = PeftModel.from_pretrained(
                self.model, 
                adapter_path,
                torch_dtype=torch.float16
            )

    def __call__(self, prompt, stop=None,**kwargs):
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

if __name__ == "__main__":
   
    # Step1: Initialize according to the your model path and the weight format
    # Load the model in hf format
    lengine=llamaEngine(base_path='/mnt/ceph-user/jyn/model/llama_hf_7B',device_map="auto")

    # Step2: do inference
    generation_config = GenerationConfig(
                        temperature=0.6,
                        top_p=0.95,
                        repetition_penalty=1.15,
                    )
    print(lengine('介绍一下浙江大学',generation_config))
