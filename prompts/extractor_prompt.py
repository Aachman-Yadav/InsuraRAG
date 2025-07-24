##############################
# Clause Extractor Prompt
##############################

from langchain_core.prompts import PromptTemplate

clause_extraction_prompt = PromptTemplate.from_template("""
You are a legal language analyst.

Your task is to extract all self-contained legal or insurance-related **clauses** from the provided text chunk.

Each clause must:
- Represent a complete and logically independent statement
- Be understandable without requiring context from other parts of the document
- Preserve original language, formatting, and punctuation

Do NOT include:
- Partial sentences or incomplete thoughts
- Headers, section numbers, or labels not forming a clause
- Clauses that require prior context to be understood

Input Chunk:
```{chunk}```

Output:
Return only a numbered list of fully-formed clauses, nothing else:

1. <clause text>
2. <clause text>
...

Rules:
- Do NOT paraphrase or summarize the clause.
- Do NOT add commentary or explanations.
""")

##############################
# Metadata Extractor Prompt
##############################

metadata_extraction_prompt = PromptTemplate.from_template("""
You are a legal metadata extraction AI.

Given a **single clause** from an insurance policy document, extract well-structured metadata with high accuracy. Your output will help build a transparent and explainable claim evaluation system.

Clause:
```{clause}```

Return exactly these fields:

Clause Metadata:
title: A short, meaningful heading (max 10 words) that captures the clause intent.
type: One of ["Eligibility", "Coverage", "Exclusion", "Claim Process", "Definition", "Other"]
summary: A clear, plain English summary (1 line) capturing the clause's meaning.
category: A general category such as "Financial", "Medical", "Operational", "Benefits", "Terms", etc.
key_entities: A Python-style list of all relevant parties/entities mentioned or implied (e.g., ["insured", "insurer", "hospital"])

Strict Instructions:
- Do NOT repeat or paraphrase the clause in any field.
- Do NOT include the clause text again.
- Do NOT add commentary, reasoning, or extra fields.
- Only return the metadata block in the exact format shown above.
- If a field like key_entities has no identifiable parties, return an empty list: []
""")