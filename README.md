# Policy Compliance Checker - RAG System

A LangChain-based RAG system that evaluates whether company contracts and policies comply with predefined compliance rules. The system provides context-based evidence and suggestions for remediation.

## Project Structure

```
Task2/
├── preprocess_documents.py    # Load contracts and build vector store
├── compliance_checker.py       # Compliance checking logic
├── app.py                      # Streamlit web application
├── rules.json                  # 16 compliance rules
├── requirements.txt            # Python dependencies
├── vectorstore/                # FAISS vector store (created by preprocessing)
└── CUAD_v1/                    # Contract dataset (510 contracts)
    ├── full_contract_txt/      # Text versions of contracts
    ├── full_contract_pdf/      # PDF versions of contracts
    ├── master_clauses.csv      # Clause annotations
    └── CUAD_v1.json            # JSON format of clauses
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Preprocess Contracts (One-time setup)

This creates a FAISS vector store from the contract dataset:

```bash
python preprocess_documents.py
```

This will:
- Load contracts from CUAD_v1/full_contract_txt/
- Split into chunks for retrieval
- Generate embeddings using HuggingFace
- Build FAISS index
- Save to vectorstore/

### 3. Run the Streamlit App

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

## Features

### Single Rule Check
- Select a compliance rule from the dropdown
- Run compliance check on that specific rule
- View compliance status, evidence, and remediation suggestions

### Full Audit
- Run compliance check on all 16 rules simultaneously
- View summary metrics (compliant, non-compliant, errors)
- Get detailed results for each rule
- Save results to JSON file

### Rules List
- View all compliance rules in a table
- See rule descriptions and categories
- Total rule count

## Compliance Rules

The system includes 16 rules covering:

1. Parties Identification - All parties must be clearly identified
2. Agreement Date - Date when agreement was signed
3. Effective Date - Date when agreement becomes effective
4. Expiration Date - When agreement expires or if perpetual
5. Renewal Terms - How the agreement renews after expiration
6. Termination Notice - Notice period required to terminate
7. Governing Law - Which law governs the agreement
8. Jurisdiction - Where disputes are resolved
9. Payment Terms - How and when payments are made
10. Confidentiality - Protection of confidential information
11. Liability Limitation - Cap on damages and liability
12. Intellectual Property - IP ownership and rights
13. Indemnification - Protection against claims and losses
14. Entire Agreement - Complete and binding nature of contract
15. Amendment Procedures - How contract can be modified
16. Dispute Resolution - How disputes are resolved

## System Architecture

### Document Preprocessing
1. Load contracts from TXT files
2. Split into 1500-character chunks with 150-character overlap
3. Generate embeddings using HuggingFace `all-MiniLM-L6-v2`
4. Build FAISS vector index
5. Save to disk for fast retrieval

### Compliance Checking
1. Load compliance rules from rules.json
2. Retrieve relevant contract sections for each rule
3. Send to Gemini LLM with compliance check prompt
4. Get status (COMPLIANT/NON-COMPLIANT), evidence, and remediation
5. Return results with sources

### Web Interface (Streamlit)
- Single rule checking for targeted compliance review
- Full audit for comprehensive compliance assessment
- Rules list view for reference
- JSON export of results

## API Key Setup

The system uses a hardcoded API key in `compliance_checker.py`. For production, replace with your own Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Customization

### Add More Rules
Edit `rules.json` to add new compliance rules:

```json
{
  "id": 17,
  "name": "Rule Name",
  "description": "Rule description",
  "category": "Category"
}
```

### Adjust Retrieval Parameters
In `compliance_checker.py`, modify:

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
```

Change `k` to get more or fewer contract sections.

### Change LLM Temperature
In `compliance_checker.py`, adjust:

```python
llm = ChatGoogleGenerativeAI(model=MY_GOOGLE_MODEL, temperature=0.3)
```

Lower = more factual, Higher = more creative.

## Troubleshooting

### Vectorstore not found
Run preprocessing:
```bash
python preprocess_documents.py
```

### API quota exceeded
Ensure you have a valid Google API key with billing enabled. Only LLM calls use quota.

### Missing dependencies
Reinstall packages:
```bash
pip install -r requirements.txt
```

## References

- [CUAD Dataset](https://www.atticusprojectai.org/cuad)
- [LangChain](https://python.langchain.com/)
- [Google Gemini API](https://ai.google.dev/)
- [FAISS](https://github.com/facebookresearch/faiss)

---

**Created**: November 2025  
**Policy Compliance Checker RAG System**
