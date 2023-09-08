from easyinstruct import SelfInstructGenerator
from easyinstruct.utils.api import set_openai_key, set_proxy

set_openai_key("")
set_proxy("http://127.0.0.1:7890")

generator = SelfInstructGenerator(num_instructions_to_generate=20)
generator.generate()