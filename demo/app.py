import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes
from typing import Iterable

from easyinstruct import (
    SelfInstructGenerator,
    EvolInstructGenerator,
    BacktranslationGenerator,
)
from easyinstruct import (
    LengthSelector,
    Deduplicator,
    RougeSelector,
    GPTScoreSelector,
    MTLDSelector,
    PPLSelector,
    RandomSelector,
    MultiSelector,
)
from easyinstruct.utils.api import set_openai_key, set_proxy, set_openai_base_url

set_proxy()
set_openai_base_url()


class Seafoam(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.emerald,
        secondary_hue: colors.Color | str = colors.blue,
        neutral_hue: colors.Color | str = colors.blue,
        spacing_size: sizes.Size | str = sizes.spacing_md,
        radius_size: sizes.Size | str = sizes.radius_md,
        font: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("Quicksand"),
            "ui-sans-serif",
            "sans-serif",
        ),
        font_mono: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("IBM Plex Mono"),
            "ui-monospace",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            font=font,
            font_mono=font_mono,
        )
        super().set(
            button_primary_background_fill="linear-gradient(90deg, *primary_300, *secondary_400)",
            button_primary_background_fill_hover="linear-gradient(90deg, *primary_200, *secondary_300)",
            button_primary_text_color="white",
            slider_color="*secondary_300",
            slider_color_dark="*secondary_600",
        )

seafoam = Seafoam()

def generate(
    seed_data_file_path,
    openai_api_key,
    engine,
    input_generator,
    num_instructions_to_generate,
):
    set_openai_key(openai_api_key)

    if input_generator == "Self-Instruct":
        generator = SelfInstructGenerator(
            seed_tasks_path=seed_data_file_path,
            engine=engine,
            num_instructions_to_generate=num_instructions_to_generate,
        )
    elif input_generator == "Evol-Instruct":
        generator = EvolInstructGenerator(
            seed_tasks_path=seed_data_file_path,
            engine=engine,
            num_instructions_to_generate=num_instructions_to_generate,
        )
    elif input_generator == "KG2Instruct":
        return "Hello World!"
    elif input_generator == "Backtranslation":
        generator = BacktranslationGenerator(
            unlabelled_data_path=seed_data_file_path,
            engine=engine,
            num_instructions_to_generate=num_instructions_to_generate,
        )
    else:
        raise ValueError(f"Unknown generator: {generator}")

    generated_data = generator.generate()
    return generated_data


def process(
    raw_instructions_file_path,
    openai_api_key,
    engine,
    selectors,
    min_instruction_length,
    max_instruction_length,
    min_response_length,
    max_response_length,
    rouge_threshold,
    min_mtld,
    max_mtld,
    gpt_score_threshold,
    num_instructions_to_sample,
):
    print(f"raw_instructions_file_path: {raw_instructions_file_path}")
    print(f"openai_api_key: {openai_api_key}")
    print(f"engine: {engine}")
    print(f"selectors: {selectors}")

    selectors_list = []
    if "Deduplicator" in selectors:
        deduplicator = Deduplicator()
        selectors_list.append(deduplicator)
    if "RougeSelector" in selectors:
        rouge_selector = RougeSelector(threshold=rouge_threshold)
        selectors_list.append(rouge_selector)
    if "LengthSelector" in selectors:
        length_selector = LengthSelector(
            min_instruction_length=min_instruction_length,
            max_instruction_length=max_instruction_length,
            min_response_length=min_response_length,
            max_response_length=max_response_length,
        )
        selectors_list.append(length_selector)
    if "GPTScoreSelector" in selectors:
        set_openai_key(openai_api_key)
        gpt_score_selector = GPTScoreSelector(
            threshold=gpt_score_threshold, engine=engine
        )
        selectors_list.append(gpt_score_selector)
    if "MTLDSelector" in selectors:
        mtld_selector = MTLDSelector(
            min_mtld=min_mtld,
            max_mtld=max_mtld,
        )
        selectors_list.append(mtld_selector)
    # if "PPLSelector" in selectors:
    #     ppl_selector = PPLSelector(threshold=50)
    #     selectors_list.append(ppl_selector)
    if "RandomSelector" in selectors:
        random_selector = RandomSelector(
            num_instructions_to_sample=num_instructions_to_sample
        )
        selectors_list.append(random_selector)

    selector = MultiSelector(
        source_file_path=raw_instructions_file_path, selectors_list=selectors_list
    )

    selected_data = selector.process()
    return selected_data


with gr.Blocks(theme=seafoam) as gradio_app:
    ##############
    # Head Block #
    ##############
    with gr.Row(equal_height=True):
        gr.HTML(
            """
            <div>
                <h1>🎨EasyInstruct: An Easy-to-use Instruction Processing Framework for Large Language Models</h1>
                
                <p>
                📍[<a href="https://zjunlp.github.io/project/EasyInstruct" target="_blank">Project Page</a>]
                📑[<a href="" target="_blank">Paper</a>]
                👨‍💻[<a href="https://github.com/zjunlp/EasyInstruct" target="_blank"><span class="icon"><i class="fab fa-github"></i></span>Code</a>]
                🤗[<a href="https://huggingface.co/spaces/zjunlp/EasyInstruct" target="_blank">Demo</a>]
                </p>

            </div>
            """
        )
    with gr.Row(equal_height=True):
        openai_api_key = gr.Textbox(label="OpenAI API Key")
        engine = gr.Dropdown(
            choices=["gpt-3.5-turbo-instruct", "gpt-3.5-turbo", "gpt-4"],
            value="gpt-3.5-turbo",
            label="Engine",
        )

    ##############
    # Body Block #
    ##############
    with gr.Row():
        gr.HTML(
            """
            <h2>Instruction Generation</h2>
            """
        )
    with gr.Row(equal_height=True):
        generator = gr.Dropdown(
            choices=[
                "Self-Instruct",
                "Evol-Instruct",
                "KG2Instruct",
                "Backtranslation",
            ],
            value="Self-Instruct",
            label="Generators",
        )
        num_instructions_to_generate = gr.Slider(
            minimum=5,
            maximum=100,
            value=10,
            step=5,
            label="Generation Number",
        )
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            seed_data_file_path = gr.File(
                label="Seed Data", file_types=["text", ".json", ".jsonl"]
            )
            with gr.Row(equal_height=True):
                clear_button_1 = gr.ClearButton()
                submit_button_1 = gr.Button("Generate", variant="primary")
        with gr.Column(scale=1):
            gr.Examples(
                label="Example Seed Data",
                examples=[
                    "data/example_seed_data.jsonl",
                ],
                inputs=[
                    seed_data_file_path,
                ]
            )
            generated_instances = gr.JSON(label="Generated Instances")

        submit_button_1.click(
            generate,
            inputs=[
                seed_data_file_path,
                openai_api_key,
                engine,
                generator,
                num_instructions_to_generate,
            ],
            outputs=generated_instances,
        )
        clear_button_1.click(
            lambda: ("", ""), outputs=[seed_data_file_path, generated_instances]
        )

    with gr.Row(equal_height=True):
        gr.HTML(
            """
            <h2>Instruction Selection</h2>
            """
        )
    with gr.Row():
        selectors = gr.CheckboxGroup(
            choices=[
                "Deduplicator",
                "RougeSelector",
                "LengthSelector",
                "GPTScoreSelector",
                "MTLDSelector",
                # "PPLSelector",
                "RandomSelector",
            ],
            label="Selectors",
        )
    with gr.Row():
        with gr.Accordion("Parameters", open=False):
            with gr.Accordion("Length Selector", open=False):
                min_instruction_length = gr.Slider(
                    label="Min Instruction Length",
                    minimum=1,
                    maximum=1024,
                    value=3,
                    step=1,
                )
                max_instruction_length = gr.Slider(
                    label="Max Instruction Length",
                    minimum=1,
                    maximum=1024,
                    value=150,
                    step=1,
                )
                min_response_length = gr.Slider(
                    label="Min Response Length", minimum=1, maximum=2048, value=1
                )
                max_response_length = gr.Slider(
                    label="Max Response Length", minimum=1, maximum=2048, value=350
                )
            with gr.Accordion("Rouge Selector", open=False):
                rouge_threshold = gr.Slider(
                    label="Rouge Threshold",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                )
            with gr.Accordion("MTLD Selector", open=False):
                min_mtld = gr.Slider(
                    label="Min MTLD", minimum=0, maximum=100, value=8, step=1
                )
                max_mtld = gr.Slider(
                    label="Max MTLD", minimum=0, maximum=100, value=22, step=1
                )

            with gr.Accordion("GPT Score Selector", open=False):
                gpt_score_threshold = gr.Slider(
                    label="GPT Score Threshold", minimum=1, maximum=5, value=4, step=1
                )
            with gr.Accordion("Random Selector", open=False):
                num_instructions_to_sample = gr.Slider(
                    label="Number of Instructions to Sample",
                    minimum=5,
                    maximum=1000,
                    value=50,
                    step=5,
                )
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            raw_instructions_file_path = gr.File(
                label="Raw Instructions", file_types=["text", ".json", ".jsonl"]
            )
            with gr.Row(equal_height=True):
                clear_button_2 = gr.ClearButton()
                submit_button_2 = gr.Button("Process", variant="primary")
        with gr.Column(scale=1):
            gr.Examples(
                label="Example Raw Instructions",
                examples=[
                    "data/example_raw_instructions.jsonl",
                ],
                inputs=[
                    raw_instructions_file_path,
                ]
            )
            selected_instances = gr.JSON(label="Selected Instances")

        submit_button_2.click(
            process,
            inputs=[
                raw_instructions_file_path,
                openai_api_key,
                engine,
                selectors,
                min_instruction_length,
                max_instruction_length,
                min_response_length,
                max_response_length,
                rouge_threshold,
                min_mtld,
                max_mtld,
                gpt_score_threshold,
                num_instructions_to_sample,
            ],
            outputs=selected_instances,
        )
        clear_button_2.click(
            lambda: ("", ""),
            outputs=[raw_instructions_file_path, selected_instances],
        )

    ##############
    # Foot Block #
    ##############
    with gr.Accordion("Citation", open=False):
        gr.Markdown(
            """
            ```bibtex
            @article{ou2024easyinstruct,
            title={EasyInstruct: An Easy-to-use Instruction Processing Framework for Large Language Models},
            author={Ou, Yixin and Zhang, Ningyu and Gui, Honghao and Xu, Ziwen and Qiao, Shuofei and Bi, Zhen and Chen, Huajun},
            journal={arXiv preprint arXiv:2402.03049},
            year={2024}
            }
            ```
            """
        )

if __name__ == "__main__":
    gradio_app.launch(debug=True, server_port=8080)
