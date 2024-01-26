import gradio as gr
import json

from easyinstruct import SelfInstructGenerator, EvolInstructGenerator, BacktranslationGenerator
from easyinstruct import LengthSelector, Deduplicator, RougeSelector, GPTScoreSelector, MTLDSelector, PPLSelector, RandomSelector, MultiSelector
from easyinstruct.utils.api import set_openai_key, set_proxy

set_proxy("http://127.0.0.1:7890")

def generate(seed_data_file_path, openai_api_key, engine, input_generator, num_instructions_to_generate):
    set_openai_key(openai_api_key)
    
    if input_generator == "Self-Instruct":
        generator = SelfInstructGenerator(
            seed_tasks_path=seed_data_file_path,
            engine=engine,
            num_instructions_to_generate=num_instructions_to_generate
        )
    elif input_generator == "Evol-Instruct":
        generator = EvolInstructGenerator(
            seed_tasks_path=seed_data_file_path,
            engine=engine,
            num_instructions_to_generate=num_instructions_to_generate
        )
    elif input_generator == "KG2Instruct":
        return "Hello World!"
    elif input_generator == "Backtranslation":
        generator = BacktranslationGenerator(
            unlabelled_data_path=seed_data_file_path,
            engine=engine,
            num_instructions_to_generate=num_instructions_to_generate
        )
    else:
        raise ValueError(f"Unknown generator: {generator}")
    
    generated_data = generator.generate()
    result_string = ""
    for data in generated_data:
        result_string += json.dumps(data, ensure_ascii=False) + "\n"
    return result_string
    
def process(raw_instructions_file_path, openai_api_key, engine, selectors):
    print(f'raw_instructions_file_path: {raw_instructions_file_path}')
    print(f'openai_api_key: {openai_api_key}')
    print(f'engine: {engine}')
    print(f'selectors: {selectors}')
    
    selectors_list = []
    if "Deduplicator" in selectors:
        deduplicator = Deduplicator()
        selectors_list.append(deduplicator)
    if "RougeSelector" in selectors:
        rouge_selector = RougeSelector(threshold=0.3)
        selectors_list.append(rouge_selector)
    if "LengthSelector" in selectors:
        length_selector = LengthSelector(max_response_length=320)
        selectors_list.append(length_selector)
    if "GPTScoreSelector" in selectors:
        set_openai_key(openai_api_key)
        gpt_score_selector = GPTScoreSelector(threshold=5, engine=engine)
        selectors_list.append(gpt_score_selector)
    if "MTLDSelector" in selectors:
        mtld_selector = MTLDSelector()
        selectors_list.append(mtld_selector)
    if "PPLSelector" in selectors:
        ppl_selector = PPLSelector(threshold=50)
        selectors_list.append(ppl_selector)
    if "RandomSelector" in selectors:
        random_selector = RandomSelector(num_instructions_to_sample=5000)
        selectors_list.append(random_selector)
    
    selector = MultiSelector(source_file_path=raw_instructions_file_path, selectors_list=selectors_list)
    
    selected_data =  selector.process()
    result_string = ""
    for data in selected_data:
        result_string += json.dumps(data, ensure_ascii=False) + "\n"
    return result_string
    
with gr.Blocks() as gradio_app:
    
    ##############
    # Head Block #
    ##############
    with gr.Row(equal_height=True):
        with gr.Column(scale=5):
            gr.HTML(
                """
                <div align="center">

                    <img src="https://raw.githubusercontent.com/zjunlp/EasyInstruct/main/figs/logo.png" width="300px">
                    
                    <h3>An Easy-to-use Instruction Processing Framework for Large Language Models.</h3>

                    <p align="center">
                        <a href="">Project</a> •
                        <a href="">Paper</a> •
                        <a href="https://github.com/zjunlp/EasyInstruct">Code</a> •
                        <a href="https://zjunlp.gitbook.io/easyinstruct/">Docs</a> •
                        <a href="">Demo</a>
                    </p>

                </div>
                """
            )
        with gr.Column(scale=1):
            openai_api_key = gr.Textbox(label="OpenAI API Key")
            engine = gr.Dropdown(choices=["gpt-3.5-turbo-instruct", "gpt-3.5-turbo", "gpt-4"], value="gpt-3.5-turbo", label="Engine")
            
    ##############
    # Body Block #
    ##############
    with gr.Row(equal_height=True):
        
        ##############
        # Left Block #
        ##############
        with gr.Column(scale=1):
            gr.HTML(
                """
                <h2>Instruction Generation</h2>
                """
            )
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    generator = gr.Dropdown(choices=["Self-Instruct", "Evol-Instruct", "KG2Instruct", "Backtranslation"], value="Self-Instruct", label="Generators")
                with gr.Column(scale=1):
                    num_instructions_to_generate = gr.Slider(minimum=0, maximum=1000, value=10, step=10, label="Generation Number")
            seed_data_file_path = gr.File(label="Seed Data", file_types=["text", ".json", ".jsonl"])
            with gr.Row():
                with gr.Column(scale=1):
                    submit_button_1 = gr.Button("Generate", variant="primary")
                with gr.Column(scale=1):
                    clear_button_1 = gr.ClearButton()
                    
            generated_instances = gr.Textbox(label="Generated Instances",show_copy_button=True)
            
            submit_button_1.click(generate, inputs=[seed_data_file_path, openai_api_key, engine, generator, num_instructions_to_generate], outputs=generated_instances)
            clear_button_1.click(lambda: ("", ""), outputs=[seed_data_file_path, generated_instances])
        
        ###############
        # Right Block #
        ###############
        with gr.Column(scale=1):
            gr.HTML(
                """
                <h2>Instruction Selection</h2>
                """
            )
            with gr.Row(equal_height=True):
                selectors = gr.CheckboxGroup(choices=["Deduplicator", "RougeSelector", "LengthSelector", "GPTScoreSelector", "MTLDSelector", "PPLSelector", "RandomSelector"], label="Selectors")
            raw_instructions_file_path = gr.File(label="Raw Instructions", file_types=["text", ".json", ".jsonl"])
            with gr.Row():
                with gr.Column(scale=1):
                    submit_button_2 = gr.Button("Process", variant="primary")
                with gr.Column(scale=1):
                    clear_button_2 = gr.ClearButton()
                    
            selected_instances = gr.Textbox(label="Selected Instances",show_copy_button=True)
            
            submit_button_2.click(process, inputs=[raw_instructions_file_path, openai_api_key, engine, selectors], outputs=selected_instances)
            clear_button_2.click(lambda: ("", ""), outputs=[raw_instructions_file_path, selected_instances])
    
    ##############
    # Foot Block #
    ##############
    with gr.Accordion("Citation", open=False):
        gr.Markdown(
            """
            ```bibtex
            @misc{easyinstruct,
              author = {Yixin Ou and Ningyu Zhang and Honghao Gui and Zhen Bi and Yida Xue and Runnan Fang and Kangwei Liu and Lei Li and Shuofei Qiao and Huajun Chen},
              title = {EasyInstruct: An Easy-to-use Instruction Processing Framework for Large Language Models},
              year = {2023},
              url = {https://github.com/zjunlp/EasyInstruct},
            }

            @misc{knowlm,
              author = {Ningyu Zhang and Jintian Zhang and Xiaohan Wang and Honghao Gui and Kangwei Liu and Yinuo Jiang and Xiang Chen and Shengyu Mao and Shuofei Qiao and Yuqi Zhu and Zhen Bi and Jing Chen and Xiaozhuan Liang and Yixin Ou and Runnan Fang and             Zekun Xi and Xin Xu and Lei Li and Peng Wang and Mengru Wang and Yunzhi Yao and Bozhong Tian and Yin Fang and Guozhou Zheng and Huajun Chen},
              title = {KnowLM: An Open-sourced Knowledgeable Large Langugae Model Framework},
              year = {2023},
             url = {http://knowlm.zjukg.cn/},
            }

            @misc{bi2023programofthoughts,
                  author={Zhen Bi and Ningyu Zhang and Yinuo Jiang and Shumin Deng and Guozhou Zheng and Huajun Chen},
                  title={When Do Program-of-Thoughts Work for Reasoning?}, 
                  year={2023},
                  eprint={2308.15452},
                  archivePrefix={arXiv},
                  primaryClass={cs.CL}
            }
            ```
            """
        )

if __name__ == "__main__":
    gradio_app.launch(debug=True, server_port=8080)
