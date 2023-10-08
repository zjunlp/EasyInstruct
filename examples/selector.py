from easyinstruct.utils.api import set_openai_key, set_proxy
from easyinstruct import LengthSelector, Deduplicator, RougeScoreSelector, CompositionalSelector, GPTScoreSelector

set_openai_key("")
set_proxy("http://127.0.0.1:7890")

selector1 = Deduplicator()
selector2 = RougeScoreSelector()
selector3 = LengthSelector()
selector4 = GPTScoreSelector()
selector = CompositionalSelector(source_file_path="evolved_instances.jsonl", selectors_list=[selector4])
selector.process()