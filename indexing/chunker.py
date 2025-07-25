######################
# Chunker
######################

from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.generate_uid import generate_chunk_uid
from utils.logger import logger

def chunk_documents(documents, chunk_size=5000, chunk_overlap=500):
    """Splits loaded LangChain documents into smaller, overlapping chunks using RecursiveCharacterTextSplitter."""
    
    logger.info(f"Starting chunking: {len(documents)} documents, chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        separators=["\n\n", "\n", ".", " "]
    )
    
    chunked_docs = splitter.split_documents(documents)
    logger.info(f"Chunking complete: {len(chunked_docs)} total chunks generated.")
    
    for idx, chunk in enumerate(chunked_docs):
        
        doc_id = chunk.metadata.get("doc_id", "UNKNOWN")
                
        chunk.metadata["chunk_index"] = idx
        chunk.metadata["chunk_size"] = len(chunk.page_content)
        chunk.metadata["chunk_uid"] = generate_chunk_uid(doc_id, idx)
        chunk.metadata["doc_id"] = doc_id
        
    return chunked_docs