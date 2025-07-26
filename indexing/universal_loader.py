######################
# Document Loader
######################

import os
import uuid
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredEmailLoader, UnstructuredWordDocumentLoader, TextLoader
from utils.logger import logger
from utils.clean_text import clean_text
from utils.blob_handler import download_blob

def load_document(blob_url: str) -> List[Document]:
    """Internal helper to load and clean a single file into LangChain Documents."""

    try:
        # file_path = download_blob(blob_url)
        file_path = blob_url  
        filename = os.path.basename(file_path)
        ext = filename.split('.')[-1].lower()
        doc_id = str(uuid.uuid4())[:12]

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

        documents = []
        for i, doc in enumerate(loader.load()):
            doc.page_content = clean_text(doc.page_content)
            doc.metadata["source"] = filename
            doc.metadata["file_type"] = ext
            doc.metadata["doc_id"] = doc_id
            logger.info(f"Loaded chunk {i+1} from {filename} ({len(doc.page_content)} chars)")
            documents.append(doc)

        return documents

    except Exception as e:
        logger.error(f"Failed to load file {file_path}: {e}")
        raise RuntimeError(f"Failed to load file {file_path}: {e}")