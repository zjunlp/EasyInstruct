import re
from tqdm import tqdm

from easyinstruct import BasePrompt
from .base_selector import BaseSelector

prompt_template = """Below is an instruction from an user and a candidate answer. Evaluate whether or not the answer is a good example of how AI Assistant should respond to the user's instruction. Please assign a score using the following 5-point scale:
1: It means the answer is incomplete, vague, off-topic, controversial, or not exactly what the user asked for. For example, some content seems missing, numbered list does not start from the beginning, the opening sentence repeats user's question. Or the response is from another person's perspective with their personal experience (e.g. taken from blog posts), or looks like an answer from a forum. Or it contains promotional text, navigation text, or other irrelevant information.
2: It means the answer addresses most of the asks from the user. It does not directly address the user's question. For example, it only provides a high-level methodology instead of the exact solution to user's question.
3: It means the answer is helpful but not written by an AI Assistant. It addresses all the basic asks from the user. It is complete and self contained with the drawback that the response is not written from an AI assistant's perspective, but from other people's perspective. The content looks like an excerpt from a blog post, web page, or web search results. For example, it contains personal experience or opinion, mentions comments section, or share on social media, etc.
4: It means the answer is written from an AI assistant's perspective with a clear focus of addressing the instruction. It provide a complete, clear, and comprehensive response to user's question or instruction without missing or irrelevant information. It is well organized, self-contained, and written in a helpful tone. It has minor room for improvement, e.g. more concise and focused.
5: It means it is a perfect answer from an AI Assistant. It has a clear focus on being a helpful AI Assistant, where the response looks like intentionally written to address the user's question or instruction without any irrelevant sentences. The answer provides high quality content, demonstrating expert knowledge in the area, is very well written, logical, easy-to-follow, engaging and insightful. 

Please first provide a brief reasoning you used to derive the rating score, and then write "Score: <rating>" in the last line.

"""


class GPTScoreSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "data/selections/",
        target_file_name: str = "selected_instructions.jsonl",
        engine: str = "gpt-3.5-turbo",
        threshold: int = 4,
        score_only: bool = False,
    ):
        super(GPTScoreSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )
        self.engine = engine
        self.threshold = threshold
        self.score_only = score_only

    def __process__(self, data):
        regex = re.compile(r"[Ss]core:\s*(\d+)")

        selected_data = []

        for d in tqdm(data):
            prompt = BasePrompt()
            if self.data_format == "self_instruct":
                prompt.build_prompt(
                    f'{prompt_template}\n\nInstruction: {d["instruction"]}\n\n Response:{d["instances"][0]["output"]}'
                )
            elif self.data_format == "alpaca":
                if "input" in d.keys():
                    prompt.build_prompt(
                        f'{prompt_template}\n\nInstruction: {d["instruction"]} {d["input"]}\n\n Response:{d["output"]}'
                    )
                else:
                    prompt.build_prompt(
                        f'{prompt_template}\n\nInstruction: {d["instruction"]}\n\n Response:{d["output"]}'
                    )
            elif self.data_format == "alpaca_wo_input":
                prompt.build_prompt(
                    f'{prompt_template}\n\nInstruction: {d["instruction"]}\n\n Response:{d["output"]}'
                )
            else:
                raise ValueError("Unknown data format")

            prompt.get_openai_result(
                engine=self.engine,
                max_tokens=150,
                temperature=0,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=0,
            )

            score_matched = regex.search(prompt.output)
            if score_matched:
                score = int(score_matched.group(1))
                if self.score_only:
                    d["gpt_score"] = score
                elif score >= self.threshold:
                    d["gpt_score"] = score
                    selected_data.append(d)

        return data if self.score_only else selected_data
