import json
import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
try:
    MY_GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    MY_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MY_GOOGLE_MODEL = os.environ.get("GOOGLE_MODEL", "models/gemini-2.0-flash")

def load_rules():
    with open("rules.json", "r") as f:
        rules_data = json.load(f)
    return rules_data.get("rules", [])

def load_vectorstore(vectorstore_path="vectorstore"):
    if not os.path.exists(vectorstore_path):
        raise FileNotFoundError(f"Vectorstore not found at {vectorstore_path}")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)

def check_compliance(contract_text, rule, vectorstore, api_key=None):
    if api_key is None:
        api_key = MY_GOOGLE_API_KEY

    if contract_text:
        context = contract_text[:4000]
        relevant_docs = []
        sources = ["selected_contract"]
    else:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        relevant_docs = retriever.invoke(rule["description"])
        context_pieces = [f"[{doc.metadata.get('source', 'unknown')}]\n{doc.page_content[:500]}" for doc in relevant_docs]
        context = "\n\n".join(context_pieces)
        sources = [doc.metadata.get("source", "unknown") for doc in relevant_docs]
    
    prompt_template = """You are a compliance auditor. Check if the contract complies with this rule:

Rule: {rule_name}
Description: {rule_description}

Contract Section:
{context}

Determine if the contract satisfies this rule. Respond with:
1. Compliance Status: YES or NO
2. Evidence: Quote relevant text from the contract
3. Remediation: If non-compliant, suggest how to fix it

Format:
Status: [YES/NO]
Evidence: [relevant text]
Remediation: [suggestion or N/A]"""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["rule_name", "rule_description", "context"]
    )
    
    llm = ChatGoogleGenerativeAI(model=MY_GOOGLE_MODEL, temperature=0.3, google_api_key=api_key)
    
    formatted_prompt = PROMPT.format(
        rule_name=rule["name"],
        rule_description=rule["description"],
        context=context
    )
    
    response = llm.invoke(formatted_prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    return {
        "rule_id": rule["id"],
        "rule_name": rule["name"],
        "status": "COMPLIANT" if "YES" in answer.upper() else "NON-COMPLIANT",
        "response": answer,
        "sources": sources,
        "raw_docs": relevant_docs,
    }

def check_all_rules(vectorstore, api_key=None):
    rules = load_rules()
    results = []
    
    for rule in rules:
        try:
            result = check_compliance("", rule, vectorstore, api_key)
            results.append(result)
            print(f"Checked rule {rule['id']}: {rule['name']} - {result['status']}")
        except Exception as e:
            results.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "status": "ERROR",
                "response": str(e),
                "sources": []
            })
            print(f"Error checking rule {rule['id']}: {e}")
    
    return results
