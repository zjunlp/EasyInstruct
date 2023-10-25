import copy
import re

from easyinstruct.utils.api import API_NAME_DICT
from .base_prompt import BasePrompt


class BatchPrompt(BasePrompt):
    """Class for batch prompt"""

    def __init__(self):
        super().__init__()

    def build_prompt(self, prompt_list: list):
        self.prompt_list = prompt_list
        self.prompt = (
            "You can answer questions. I will give you a few batches of test samples in format Q[idx]: question. "
            "Each question is independent and cannot interact with each other in context. "
            "Answer the test samples in format A[idx]: answer. The idx of question and "
            "answer must correspond and increment the output.\nQuestions are as follows: \n\n"
        )
        for index, prompt in enumerate(prompt_list):
            self.prompt = str(self.prompt) + "Q[{}]:\n{}\n\n".format(
                index, prompt.prompt
            )

        print(self.prompt)
        return self.prompt

    def batch_split(self, index, input_str: str):
        # 使用正则表达式匹配A[index]和A[index+1]之间的内容
        pattern = f"A\[{index}\]:\s*(.*?)A\[{index + 1}\]:"
        result = re.findall(pattern, input_str, re.DOTALL)

        # 输出结果
        if result:
            result[0] = result[0].encode("utf-8").decode("unicode_escape")
            return result[0]
        else:
            pattern1 = f"A\[{index}\]:\s*(.*?)$"
            result1 = re.findall(pattern1, input_str, re.DOTALL)
            if result1:
                result1[0] = result1[0].encode("utf-8").decode("unicode_escape")
                return result1[0]
            else:
                return "batch split error"

    def parse_response(self):
        response = self.response
        response.pop("usage", None)

        if self.engine in API_NAME_DICT["openai"]["gpt3"]:
            content = response["choices"][0]["text"].strip()
            for index, prompt in enumerate(self.prompt_list):
                prompt_res = copy.deepcopy(response)
                prompt_res["choices"][0]["text"] = self.batch_split(
                    index=index, input_str=content
                )
                prompt.response = copy.deepcopy(prompt_res)
                prompt.output = prompt_res["choices"][0]["text"]
        else:
            content = response["choices"][0]["message"]["content"].strip()
            for index, prompt in enumerate(self.prompt_list):
                prompt_res = copy.deepcopy(response)
                prompt_res["choices"][0]["message"]["content"] = self.batch_split(
                    index=index, input_str=content
                )
                prompt.response = copy.deepcopy(prompt_res)
                prompt.output = prompt_res["choices"][0]["message"]["content"]
        return self.response
