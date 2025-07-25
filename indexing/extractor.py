######################
# Extractor Module
######################

import os
import asyncio
import random
from aiolimiter import AsyncLimiter
from google.api_core.exceptions import ResourceExhausted
from typing import List
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.logger import logger
from utils.generate_uid import generate_clause_id
from prompts.extractor_prompt import clause_extraction_prompt, metadata_extraction_prompt
from utils.parser import parse_clause_list_output, parse_metadata_output

load_dotenv()

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

rate_limiter = AsyncLimiter(max_rate=2, time_period=1)  

#############################
# Step 1: Clause Extraction
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
            clause_number = i + 1
            clause_id = generate_clause_id(doc_id, chunk_index, clause_number)

            clause_doc.metadata.update({
                    "clause_number": clause_number,
                    "clause_id": clause_id,
                    "chunk_index": chunk_index,
                    "source_file": source_file,
                    "doc_id": doc_id
                }
            )
            clause_docs.append(clause_doc)

        logger.info(f"[Clause LLM] Extracted {len(clause_docs)} clauses from chunk {chunk_index}")
        return clause_docs
    
    except ResourceExhausted as e:
        logger.warning("[Clause LLM] Rate limit hit. Sleeping for 60 seconds...")
        await asyncio.sleep(60)
        raise e

    except Exception as e:
        logger.error(f"[Clause LLM] Failed for chunk {chunk_index}: {e}")
        return []
    
#############################
# Step 2: Metadata Extraction
#############################

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=2, max=6))
async def async_enrich_clause_with_metadata(clause_doc: Document) -> Document:
    try:
        clause_text = clause_doc.page_content
        clause_id = clause_doc.metadata.get("clause_id", "noid")

        prompt = metadata_extraction_prompt.format_prompt(clause=clause_text)
        response = await llm_gemini.ainvoke(prompt)

        if not hasattr(response, "content"):
            raise ValueError("No content in metadata response.")

        metadata_fields = parse_metadata_output(response.content)
        merged_metadata = {**clause_doc.metadata, **metadata_fields}

        logger.info(f"[Meta LLM] Metadata extracted for clause {clause_id}")
        return Document(page_content=clause_text, metadata=merged_metadata)
    
    except ResourceExhausted as e:
        logger.warning("[Clause LLM] Rate limit hit. Sleeping for 60 seconds...")
        await asyncio.sleep(60)
        raise e

    except Exception as e:
        logger.error(f"[Meta LLM] Metadata extraction failed for {clause_doc.metadata.get('clause_id')}: {e}")
        return clause_doc  
    
#############################
# Batching Functions
#############################

async def async_batch_extract_clauses(chunks: List[Document], concurrency=10) -> List[Document]:
    logger.info(f"[Clause LLM] Extracting clauses from {len(chunks)} chunks (concurrency={concurrency})")
    semaphore = asyncio.Semaphore(concurrency)

    async def sem_task(chunk):
        async with semaphore, rate_limiter:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            return await async_extract_clauses_from_chunk(chunk)

    results = await asyncio.gather(*(sem_task(chunk) for chunk in chunks))
    return [clause for group in results for clause in group]  


async def async_batch_enrich_metadata(clauses: List[Document], concurrency=1) -> List[Document]:
    logger.info(f"[Meta LLM] Enriching metadata for {len(clauses)} clauses (concurrency={concurrency})")
    semaphore = asyncio.Semaphore(concurrency)

    async def sem_task(clause_doc):
        async with semaphore, rate_limiter:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            return await async_enrich_clause_with_metadata(clause_doc)

    return await asyncio.gather(*(sem_task(clause) for clause in clauses))
    