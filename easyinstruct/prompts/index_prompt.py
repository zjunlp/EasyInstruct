from llama_index import SimpleDirectoryReader, LLMPredictor, GPTSimpleVectorIndex
from llama_index.indices.knowledge_graph.base import GPTKnowledgeGraphIndex
from langchain import OpenAI

INDEX_CLASSES = {
    "simple_vector_index": GPTSimpleVectorIndex,
    "kg_index": GPTKnowledgeGraphIndex
}


class IndexPrompt:
    """class for retrieving from an index

    Build different type of index.
    The class is implemented based on `llama_index`.
    NOTE: the class only supports `SimpleVectorIndex` and `KGIndex` right now.

    Args:
        index_name (str): The type of index to load or build, should be in [simple_vector_index, kg_index].
            Default to be `simple_vector_index`.
        index_path (str): Optional path of a saved index. If provided, will load the index during initialization.

    """

    def __init__(self, index_name="simple_vector_index", index_path=None):
        """Initialize params."""
        self.index_name = index_name
        self.index = None
        self.documents = None
        # Load the index during initialization
        if index_path is not None:
            self.load_from_disk(index_path)

    def load_from_disk(self, index_path):
        """Load index from saved path"""
        self.index = INDEX_CLASSES[self.index_name].load_from_disk(index_path)

    def save_to_disk(self, save_path):
        """Save index to local path"""
        self.index.save_to_disk(save_path)

    def query(self, prompt):
        """Query for ChatGPT/GPT3.
        Retrieve from built index, and concat the retrieved knowledge with the input prompt.
        """
        return self.index.query(prompt)

    def _read_doc(self, data_path):
        self.documents = SimpleDirectoryReader(data_path).load_data()

    def build_index(
            self,
            data_path=None,
            llm_model_name="text-davinci-002",
            chunk_size_limit=512,
            max_triplets_per_chunk=5,
    ):
        """Build index from raw documents

        Args:
            data_path: The document data path.
            llm_model_name(str): Large language model type to predict triplets from raw text. If not provided,
                will use the default setting "text-dacinci-002" for prediction.
            chunk_size_limit(int): Chunk size limit. Default is 512 (4096 max input size).
            max_triplets_per_chunk(int): Triplets number limit. Default is 5.

        Returns:
            List[Document]: A list of documents. `Document` is a class from llama_index.

        """

        self._read_doc(data_path=data_path)

        if self.index_name == "simple_vector_index":
            self._build_simple_vector_index(chunk_size_limit=chunk_size_limit)

        elif self.index_name == "kg_index":
            self._build_index_kg(llm_model_name=llm_model_name, chunk_size_limit=chunk_size_limit,
                                 max_triplets_per_chunk=max_triplets_per_chunk)

        return self.documents

    def _build_index_kg(self, llm_model_name, chunk_size_limit, max_triplets_per_chunk):
        """Build KG Index"""
        llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name=llm_model_name))
        self.index = GPTKnowledgeGraphIndex(
            self.documents,
            chunk_size_limit=chunk_size_limit,
            max_triplets_per_chunk=max_triplets_per_chunk,
            llm_predictor=llm_predictor
        )

    def _build_simple_vector_index(self, chunk_size_limit):
        """Build Simple Vector Index"""
        self.index = GPTSimpleVectorIndex(self.documents, chunk_size_limit=chunk_size_limit)
