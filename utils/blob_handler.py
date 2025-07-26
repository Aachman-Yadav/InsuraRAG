import os
import uuid
import requests
import mimetypes
from tenacity import retry, stop_after_attempt, wait_random_exponential
from utils.logger import logger  

def infer_extension(url: str, headers: dict) -> str:
    """Infer file extension from URL or Content-Type headers."""
    
    for ext in [".pdf", ".docx", ".eml", ".txt"]:
        if ext in url.lower():
            return ext

    content_type = headers.get("Content-Type", "").split(";")[0].strip()
    extension = mimetypes.guess_extension(content_type)
    
    if content_type == "application/pdf":
        return ".pdf"
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return ".docx"
    elif content_type == "message/rfc822":
        return ".eml"
    elif content_type in ["text/plain", "text/utf-8"]:
        return ".txt"
    
    return extension or ".bin"

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=4))
def download_blob(blob_url: str, save_dir: str = "temp_files") -> str:
    """Download a file from a blob URL and save it locally with retries, timeout, and smart extension handling."""
    
    os.makedirs(save_dir, exist_ok=True)
    logger.info(f"[BlobHandler] Downloading from blob URL: {blob_url}")

    with requests.get(blob_url, stream=True, timeout=15) as response:
        response.raise_for_status()

        ext = infer_extension(blob_url, response.headers)
        local_path = os.path.join(save_dir, f"{uuid.uuid4()}{ext}")

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    logger.info(f"[BlobHandler] Saved file to: {local_path}")
    return local_path
