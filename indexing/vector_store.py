###############################
# Vector Store
###############################

import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import Pinecone as Pinecone_langchain
from pinecone import Pinecone as pinecone_client
from langchain_core.documents import Document
from typing import List
from utils.logger import logger

load_dotenv()

pc = pinecone_client(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "insurance-rag"

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True}
)

def embed_and_store_clauses(clause_docs: List[Document]):
    logger.info(f"[Embed] Embedding and storing {len(clause_docs)} enriched clauses...")

    vectorstore = Pinecone_langchain.from_documents(
        documents=clause_docs,
        embedding=embedding_model,
        index_name=index_name,
        namespace="insurance-clauses",
        ids=[doc.metadata["clause_id"] for doc in clause_docs]  
    )

    logger.info("[Embed] Successfully stored clauses in Pinecone.")
    return vectorstore
