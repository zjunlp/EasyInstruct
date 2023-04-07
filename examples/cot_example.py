from easyinstruct import ZeroshotCoTPrompt, FewshotCoTPrompt
from easyinstruct.utils.api import set_openai_key, set_proxy

set_openai_key("")
set_proxy("http://127.0.0.1:7890")

question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
in_context_examples = [{"question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?", 
                        "answer": "Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10.\n#### 10"}]

zeroshot_prompts = ZeroshotCoTPrompt()
zeroshot_prompts.build_prompt(question)
print(zeroshot_prompts.get_openai_result(engine = "gpt-3.5-turbo-0301"))

fewshot_prompts = FewshotCoTPrompt()
fewshot_prompts.build_prompt(question, 
                             in_context_examples = in_context_examples, 
                             n_shots = 1)
print(fewshot_prompts.get_openai_result(engine = "gpt-3.5-turbo-0301"))