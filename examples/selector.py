from easyinstruct.utils.api import set_openai_key, set_proxy
from easyinstruct import LengthSelector, Deduplicator, RougeSelector, GPTScoreSelector, MTLDSelector, PPLSelector, MultiSelector

set_openai_key("")
set_proxy("")

src_file = ""

selector1 = Deduplicator()
selector2 = RougeSelector()
selector3 = LengthSelector()
selector4 = GPTScoreSelector()
selector5 = MTLDSelector()
selector6 = PPLSelector()
selector = MultiSelector(source_file_path=src_file, selectors_list=[selector1])
selector.process()