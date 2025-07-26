######################
# Parser
######################

import re
from typing import List
from langchain_core.documents import Document

def parse_clause_list_output(raw_text: str, source_metadata: dict) -> List[Document]:
    """Parses clause list output (e.g. '1. clause text') into Document objects with basic metadata."""
    
    pattern = r"(?m)^\d+\.\s"
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