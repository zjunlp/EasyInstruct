from easyinstruct import MMPrompt
from easyinstruct.utils.api import set_openai_key, set_proxy

set_openai_key("")
set_proxy("http://127.0.0.1:7890")

# ASCII
mm_prompts = MMPrompt(resize=24)
mm_prompts.build_prompt(prompt='What is the image about?',
                        img_path='',
                        encode_format='ASCII',
                        scale=10
                    )
print(mm_prompts.get_openai_result(engine="text-davinci-003"))

# Caption
mm_prompts.build_prompt(prompt='What is the image about?',
                        img_path='',
                        encode_format='caption'
                    )

print(mm_prompts.get_openai_result(engine="text-davinci-003"))
