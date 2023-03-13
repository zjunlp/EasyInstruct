import os
from easyinstruct import BasePrompt
from easyinstruct.utils import set_openai_key, set_proxy

set_openai_key("")
set_proxy("http://127.0.0.1:7890")

promts = BasePrompt()
promts.build_prompt("Give me three names of cats.")
print(promts.get_openai_result(engine = "gpt-3.5-turbo-0301"))