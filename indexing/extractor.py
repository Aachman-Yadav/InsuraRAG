######################
# Extractor Module
######################

import os
import asyncio
import random
from typing import List
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from aiolimiter import AsyncLimiter
from google.api_core.exceptions import ResourceExhausted

from utils.logger import logger
from utils.generate_uid import generate_clause_id
from prompts.extractor_prompt import clause_extraction_prompt
from utils.parser import parse_clause_list_output

load_dotenv()

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

rate_limiter = AsyncLimiter(max_rate=2, time_period=1)

#############################
# Clause Extraction
#############################

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=2, max=6))
async def async_extract_clauses_from_chunk(chunk: Document) -> List[Document]:
    
    chunk_index = chunk.metadata.get("chunk_index", -1)
    source_file = chunk.metadata.get("source", "unknown")
    doc_id = chunk.metadata.get("doc_id", "noid")

    logger.info(f"[Clause LLM] Extracting clauses from chunk {chunk_index}")
    
    try:
        prompt = clause_extraction_prompt.format_prompt(chunk=chunk.page_content)
        response = await llm_gemini.ainvoke(prompt)

        if not hasattr(response, "content"):
            raise ValueError("No response content from LLM.")

        raw_clauses = parse_clause_list_output(response.content, chunk.metadata)
        clause_docs = []

        for i, clause_doc in enumerate(raw_clauses):
            clause_id = generate_clause_id(doc_id, chunk_index, i + 1)
            clause_doc.metadata.update({
                "clause_number": i + 1,
                "clause_id": clause_id,
                "chunk_index": chunk_index,
                "source_file": source_file,
                "doc_id": doc_id,
            })
            clause_docs.append(clause_doc)

        logger.info(f"[Clause LLM] Extracted {len(clause_docs)} clauses from chunk {chunk_index}")
        return clause_docs
    
    except ResourceExhausted:
        logger.warning("[Clause LLM] Rate limit hit. Sleeping for 60 seconds...")
        await asyncio.sleep(60)
        raise 

    except Exception as e:
        logger.error(f"[Clause LLM] Failed for chunk {chunk_index}: {e}")
        return []
            
#############################
# Async Orchestration Function
#############################

async def async_streaming_pipeline(chunks: List[Document], extract_concurrency=10) -> List[Document]:
    logger.info(f"[Pipeline] Starting clause extraction for {len(chunks)} chunks...")
    extract_semaphore = asyncio.Semaphore(extract_concurrency)
    all_clauses: List[Document] = []

    async def extract_task(chunk):
        async with extract_semaphore, rate_limiter:
            await asyncio.sleep(random.uniform(0.3, 1.2))  # jitter
            clauses = await async_extract_clauses_from_chunk(chunk)
            all_clauses.extend(clauses)

    extract_tasks = [asyncio.create_task(extract_task(chunk)) for chunk in chunks]
    await asyncio.gather(*extract_tasks)

    logger.info(f"[Pipeline] Extraction complete. Total clauses: {len(all_clauses)}")
    return all_clauses