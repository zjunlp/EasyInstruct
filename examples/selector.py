from easyinstruct.utils.api import set_openai_key, set_proxy
from easyinstruct import LengthSelector, Deduplicator, RougeSelector, GPTScoreSelector, MTLDSelector, PPLSelector, MultiSelector

set_openai_key("")
set_proxy("")

selector1 = Deduplicator()
selector2 = RougeSelector()
selector3 = LengthSelector()
selector4 = GPTScoreSelector()
selector5 = MTLDSelector()
selector6 = PPLSelector()
selector = MultiSelector(source_file_path="evolved_instances.jsonl", selectors_list=[selector4])
selector.process()