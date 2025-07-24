import re
from typing import List, Dict
from langchain_core.documents import Document

def parse_clause_list_output(raw_text: str, source_metadata: dict) -> List[Document]:
    """Parses clause list output (e.g. '1. clause text') into Document objects with basic metadata."""
    
    pattern = r"\d+\.\s"  
    splits = re.split(pattern, raw_text.strip())
    numbers = re.findall(pattern, raw_text.strip())

    clauses = []
    for i, clause in enumerate(splits):
        clause = clause.strip()
        if not clause:
            continue

        doc = Document(
            page_content=clause,
            metadata={
                "clause_number": numbers[i].strip().rstrip('.') if i < len(numbers) else f"{i+1}",
                "source_chunk": source_metadata.get("chunk_index"),
                "source_file": source_metadata.get("source"),
                "chunk_size": source_metadata.get("chunk_size"),
            }
        )
        clauses.append(doc)

    return clauses

def parse_metadata_output(raw_text: str) -> Dict[str, str]:
    """Parses a single metadata output."""
    
    pattern = r"""Clause Metadata:\s*
title:\s*(.*?)\s*
type:\s*(.*?)\s*
summary:\s*(.*?)\s*
category:\s*(.*?)\s*
key_entities:\s*\[([^\]]*)\]"""

    match = re.search(pattern, raw_text.strip(), re.DOTALL)
    if not match:
        raise ValueError("Metadata format is invalid or incomplete.")

    title = match.group(1).strip()
    type_ = match.group(2).strip()
    summary = match.group(3).strip()
    category = match.group(4).strip()
    key_entities = [e.strip().strip('"').strip("'") for e in match.group(5).split(",") if e.strip()]

    return {
        "title": title,
        "type": type_,
        "summary": summary,
        "category": category,
        "key_entities": key_entities,
    }

def attach_metadata_to_clause_docs(clause_docs: List[Document], metadata_outputs: List[Dict]) -> List[Document]:
    """Merges metadata extracted from LLM into the corresponding clause Documents."""
    
    enriched_clauses = []

    for doc, meta in zip(clause_docs, metadata_outputs):
        combined_metadata = {**doc.metadata, **meta}
        enriched_doc = Document(page_content=doc.page_content, metadata=combined_metadata)
        enriched_clauses.append(enriched_doc)

    return enriched_clauses
