from easyinstruct import LengthSelector, Deduplicator, RougeScoreSelector, CompositionalSelector

selector1 = Deduplicator()
selector2 = RougeScoreSelector()
selector3 = LengthSelector()
selector = CompositionalSelector(source_file_path="evolved_instances.jsonl", selectors_list=[selector1, selector2, selector3])
selector.process()