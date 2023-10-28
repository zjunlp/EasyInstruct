from easyinstruct import BacktranslationGenerator
from easyinstruct.utils.api import set_openai_key, set_proxy

set_openai_key("")
set_proxy("")

generator = BacktranslationGenerator(num_instructions_to_generate=10)
generator.generate()