from easyinstruct import SelfInstructGenerator
from easyinstruct.utils.api import set_openai_key, set_proxy

set_openai_key("")
set_proxy("")

generator = SelfInstructGenerator(num_instructions_to_generate=10)
generator.parse_instances()