from easyinstruct.utils.api import set_openai_key, set_proxy
from easyinstruct import CodeSelector

set_openai_key("")
set_proxy("")

selector = CodeSelector(
    source_dir="data/",
    source_file_path="code_example.jsonl", 
    target_dir="data/",
    manually_partion_data=True,
    min_boundary = 0.125,
    max_boundary = 0.5,
    automatically_partion_data = True,
    k_means_cluster_number = 2,
    )

selector.process()
