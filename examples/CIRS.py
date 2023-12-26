from easyinstruct import CodeSelector

src_file = "data/code_example.json"

selector = CodeSelector(
    source_file_path=src_file, 
    target_dir="data/selections/",
    manually_partion_data=True,
    min_boundary = 0.125,
    max_boundary = 0.5,
    automatically_partion_data = True,
    k_means_cluster_number = 2,
    )

selector.process()
