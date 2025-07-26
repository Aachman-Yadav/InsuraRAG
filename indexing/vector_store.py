###############################
# Vector Store
###############################

import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, wait_random_exponential, stop_after_attempt
from pinecone import Pinecone as pinecone_client
from langchain_core.documents import Document
from typing import List
from utils.logger import logger

load_dotenv()

pc = pinecone_client(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("insura-rag")

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",  
    task_type="retrieval_document",
    google_api_key=os.getenv("GOOGLE_API_KEY")  
)

NAMESPACE = "insurance-clauses"
BATCH_SIZE = 32 
SEMAPHORE = asyncio.Semaphore(5)

@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
async def embed_batch(batch: List[Document]):
    return await asyncio.to_thread(
        embedding_model.embed_documents, 
        [doc.page_content for doc in batch]
    )

async def upsert_batch(batch: List[Document], embeddings: List[List[float]]):
    items = [
        {
            "id": doc.metadata["clause_id"],
            "values": vector,
            "metadata": doc.metadata
        }
        for doc, vector in zip(batch, embeddings)
    ]
    await asyncio.to_thread(index.upsert, vectors=items, namespace=NAMESPACE)

async def embed_and_store_clauses(clause_docs: List[Document]):
    logger.info(f"[AsyncEmbed] Embedding + storing {len(clause_docs)} clauses...")

    tasks = []
    for i in range(0, len(clause_docs), BATCH_SIZE):
        batch = clause_docs[i:i + BATCH_SIZE]

        async def process(batch=batch, batch_num=i // BATCH_SIZE):
            async with SEMAPHORE:
                try:
                    embeddings = await embed_batch(batch)
                    await upsert_batch(batch, embeddings)
                    logger.info(f"[Batch {batch_num}] Uploaded {len(batch)} clauses.")
                except Exception as e:
                    logger.error(f"[Batch {batch_num}] Error: {e}")


        tasks.append(process())

    await asyncio.gather(*tasks)
    logger.info("[AsyncEmbed] All clauses embedded and upserted.")

