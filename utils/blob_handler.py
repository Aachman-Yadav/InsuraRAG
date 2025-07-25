import os
import uuid
import requests

def download_blob(blob_url: str, save_dir: str = "temp_files") -> str:
    """Download a file from a blob URL and save it locally."""
    
    os.makedirs(save_dir, exist_ok=True)
    local_ext = ".pdf" if ".pdf" in blob_url else ".docx"  
    local_path = os.path.join(save_dir, str(uuid.uuid4()) + local_ext)

    with requests.get(blob_url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return local_path
