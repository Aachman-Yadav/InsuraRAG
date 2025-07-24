######################
# Indexing Pipeline
######################

import asyncio
from pathlib import Path
from typing import List
from langchain_core.documents import Document

from indexing.universal_loader import load_document
from indexing.chunker import chunk_documents
from indexing.extractor import async_extract_clauses_from_chunk, async_enrich_clause_with_metadata
from indexing.vector_store import embed_and_store_clauses
from utils.logger import logger

PDF_FOLDER = "./data/"
CHUNK_SIZE = 5000
CHUNK_OVERLAP = 500

async def process_file(file_path: str) -> List[Document]:
    logger.info(f"\nProcessing: {file_path}")

    loaded_docs = list(load_document(file_path))
    logger.info(f"Loaded {len(loaded_docs)} raw pages")

    chunks = chunk_documents(loaded_docs, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    logger.info(f"Split into {len(chunks)} chunks")

    clause_tasks = [async_extract_clauses_from_chunk(chunk) for chunk in chunks]
    clause_lists = await asyncio.gather(*clause_tasks)
    all_clauses = [clause for sublist in clause_lists for clause in sublist]
    logger.info(f"Extracted {len(all_clauses)} clauses")

    enrich_tasks = [async_enrich_clause_with_metadata(clause) for clause in all_clauses]
    enriched_clauses = await asyncio.gather(*enrich_tasks)
    logger.info(f"Enriched {len(enriched_clauses)} clauses with metadata")

    return enriched_clauses

async def process_all_files() -> List[Document]:
    all_final_clauses = []

    pdf_files = list(Path(PDF_FOLDER).glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in the folder.")
        return []

    for file in pdf_files:
        final_docs = await process_file(str(file))
        all_final_clauses.extend(final_docs)

    return all_final_clauses

def run_indexing_pipeline():
    
    final_clauses = asyncio.run(process_all_files())

    logger.info(f"Total enriched clauses: {len(final_clauses)}")
    embed_and_store_clauses(final_clauses)
    
if __name__ == "__main__":
    run_indexing_pipeline()