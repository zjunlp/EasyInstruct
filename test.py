import os
from easyinstruct.prompt import PromptBase

os.environ["https_proxy"] = "http://127.0.0.1:7890"

promts = PromptBase()
promts.build_prompt("Give me three names of cats.")
print(promts.get_openai_result(engine = "gpt-3.5-turbo-0301"))