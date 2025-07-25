######################
# Generate UID
######################
import uuid

def generate_doc_uid() -> str:
    """Generate a unique UUID for a document."""
    return str(uuid.uuid4())[:12] 

def generate_chunk_uid(doc_uid: str, chunk_index: int) -> str:
    """Generate a unique chunk ID combining document UID and chunk index."""
    return f"{doc_uid}-CH{chunk_index:03d}"

def generate_clause_id(doc_id: str, chunk_index: int, clause_number: int) -> str:
    """Generates a unique clause ID combining document ID, chunk index, and clause number."""
    return f"{doc_id}_{chunk_index}_{clause_number}"