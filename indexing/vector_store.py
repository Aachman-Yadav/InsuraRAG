###############################
# Vector Store
###############################

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import Pinecone as Pinecone_langchain
from pinecone import Pinecone as pinecone_client
from langchain_core.documents import Document
from typing import List
from utils.logger import logger

load_dotenv()

pc = pinecone_client(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "insura-rag"

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",  
    task_type="retrieval_document",
    google_api_key=os.getenv("GOOGLE_API_KEY")  
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
