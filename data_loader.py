from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv

load_dotenv()

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384

embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)


def load_and_chunk_pdf(path: str, chunk_size: int = 500, chunk_overlap: int = 100):

    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = embed_model.get_text_embedding_batch(texts)
    return embeddings