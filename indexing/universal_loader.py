######################
# Document Loader
######################

import os
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredEmailLoader, UnstructuredWordDocumentLoader, TextLoader
from utils.generate_uid import generate_doc_uid
from utils.logger import logger

def load_document(file_path: str):
    """It Loads a single document file (PDF, EMAIL, DOCX) and return them as LangChain Document"""
    
    ext = file_path.lower().split('.')[-1]
    filename = os.path.basename(file_path)
    doc_uid = generate_doc_uid()
    
    try: 
        if ext == 'pdf':
            loader = PyMuPDFLoader(file_path, mode='single')
        elif ext == 'docx':
            loader = UnstructuredWordDocumentLoader(file_path)
        elif ext in ['eml', 'msg']:
            loader = UnstructuredEmailLoader(file_path)
        elif ext == 'txt':
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported File Type: {ext}")
        
        logger.info(f"Loading file: {filename} ({ext.upper()})")
        
        for i, doc in enumerate(loader.lazy_load()):
            doc.metadata["source"] = filename
            doc.metadata["file_type"] = ext
            doc.metadata["doc_uid"] = doc_uid
            logger.info(f"Loaded chunk {i+1} from {filename} ({len(doc.page_content)} chars)")
            yield doc

    except Exception as e:
        logger.error(f"Failed to load file {filename}: {e}")
        raise RuntimeError(f"Failed to lazily load file {filename}: {e}")