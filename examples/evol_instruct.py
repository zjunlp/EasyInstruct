from easyinstruct import EvolInstructGenerator
from easyinstruct.utils.api import set_openai_key, set_proxy

set_openai_key("")
set_proxy("http://127.0.0.1:7890")

generator = EvolInstructGenerator(num_instructions_to_generate=10)
generator.generate()