from easyinstruct.prompts import IndexPrompt
from easyinstruct.utils.api import set_openai_key

# set your own API-KEY
set_openai_key("YOUR-KEY")

# example for building a simple_vector_index
simple_index = IndexPrompt("simple_vector_index")
_ = simple_index.build_index("./data", chunk_size_limit=500) # return the documents
response = simple_index.query("Where is A.E Dimitra Efxeinoupolis club?")
print(response)
simple_index.save_to_disk("./simple_index.json")

# example for building a kg_index
kg_index = IndexPrompt("kg_index")
_ = kg_index.build_index("./data", llm_model_name="text-davinci-002", max_triplets_per_chunk=5, chunk_size_limit=512)
response = kg_index.query("Where is A.E Dimitra Efxeinoupolis club?")
kg_index.save_to_disk("./kg_index.json")
print(response)

# example for loading a kg_index from local file
kg_load_index = IndexPrompt("kg_index", "./kg_index.json")
response = kg_load_index.query("Where is A.E Dimitra Efxeinoupolis club?")
print(response)