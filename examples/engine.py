from easyinstruct import ZeroshotCoTPrompt
from easyinstruct import Llama2Engine, ChatGLM2Engine


question = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"

zeroshot_prompts = ZeroshotCoTPrompt()
zeroshot_prompts.build_prompt(question)
engine = Llama2Engine()
# engine = ChatGLM2Engine()
print(zeroshot_prompts.get_engine_result(engine = engine))