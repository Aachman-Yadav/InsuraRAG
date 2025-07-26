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