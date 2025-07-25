##############################
# Clause Extractor Prompt
##############################

from langchain_core.prompts import PromptTemplate

clause_extraction_prompt = PromptTemplate.from_template("""
You are a professional legal language analyst.

Your task is to extract individual **self-contained legal or insurance-related clauses** from the given policy text chunk.

Each clause must:
- Express a complete, logically independent legal/insurance rule or obligation.
- Be understandable **without any additional context**.
- Retain all **original legal terms, formatting, and punctuation**.

Do NOT extract:
- Fragmented sentences or partial clauses
- Section headers, numbering, labels or references without content
- Sentences that require information from surrounding text to make sense

---

Input Chunk:
```{chunk}```

---

Output:
Return ONLY a clean, numbered list of **fully-formed clauses**, nothing else.

Example:
1. The insurer shall not be liable for any pre-existing condition.
2. Coverage will be provided only upon payment of the annual premium.
3. Claims must be submitted within 30 days of the incident.

---

Rules:
- No summaries, paraphrasing, or explanations
- Preserve the clause text exactly as in the original
- Each item must be a standalone legal clause
""")

##############################
# Metadata Extractor Prompt
##############################

metadata_extraction_prompt = PromptTemplate.from_template("""
You are a legal metadata extraction AI designed for insurance policy analysis.

Your task is to extract **well-structured and semantically meaningful metadata** from a single policy clause. This metadata will support automated, explainable decision-making in insurance systems.

---

Clause:
```{clause}```

---

Extract the following metadata fields:

Clause Metadata:
title: A concise title (≤ 10 words) summarizing the clause’s core intent.
type: One of ["Eligibility", "Coverage", "Exclusion", "Claim Process", "Definition", "Other"]
summary: A brief (1 sentence), plain English summary capturing the core meaning.
category: A high-level thematic category like "Financial", "Medical", "Operational", "Benefits", "Terms", etc.
key_entities: A Python-style list of all actors/roles involved in or impacted by the clause (e.g., ["insured", "insurer", "hospital", "policyholder"])

---

Instructions:
- Do NOT copy or paraphrase the clause in any field.
- Do NOT invent or guess missing details.
- Use consistent, legal-specific vocabulary.
- If no key entities are present, return an empty list: []
- Return ONLY the metadata block in this exact format — nothing else.

Example Output:
Clause Metadata:
title: Pre-existing Conditions Exclusion  
type: Exclusion  
summary: The insurer is not liable for conditions existing before policy start.  
category: Medical  
key_entities: ["insured", "insurer"]
""")