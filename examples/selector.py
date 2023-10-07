from easyinstruct import Deduplicator, RougeScoreSelector, CompositionalSelector

selector1 = Deduplicator()
selector2 = RougeScoreSelector()
selector = CompositionalSelector(source_file_path="generated_data.jsonl", selectors_list=[selector1, selector2])
selector.process()