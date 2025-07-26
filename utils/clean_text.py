import re

def clean_text(text: str) -> str:
    """Cleans raw text by removing noise and normalizing punctuation."""
    
    text = re.sub(r'Page\s*\d+\s*(of)?\s*\d+', '', text, flags=re.IGNORECASE)  
    text = re.sub(r'\s{2,}', ' ', text)  
    text = re.sub(r'[\r\n]+', ' ', text)  
    text = re.sub(r'[“”]', '"', text)
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[–—]", "-", text)  
    text = re.sub(r"\s*•\s*", " - ", text) 
    text = re.sub(r"\.\s*\.\s*\.", "...", text)
    text = re.sub(r"\.\s*\.\s*\.", "...", text)
    return text.strip()