import os
import json
import pandas as pd
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

txt_folder = "CUAD_v1/full_contract_txt"
master_csv = "CUAD_v1/master_clauses.csv"
vectorstore_dir = "vectorstore"

print("Loading contracts from text files...")
documents = []
txt_files = sorted(Path(txt_folder).glob("*.txt"))[:50]  

for txt_file in txt_files:
    try:
        with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        doc = Document(
            page_content=content,
            metadata={
                "source": txt_file.stem,
                "file_path": str(txt_file)
            }
        )
        documents.append(doc)
        print(f"Loaded: {txt_file.name}")
    except Exception as e:
        print(f"Error loading {txt_file}: {e}")

print(f"Total contracts loaded: {len(documents)}")

print("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
chunks = text_splitter.split_documents(documents)
print(f"Total chunks created: {len(chunks)}")

print("Building FAISS vector store...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)

os.makedirs(vectorstore_dir, exist_ok=True)
vectorstore.save_local(vectorstore_dir)
print(f"Vector store saved to '{vectorstore_dir}/'")
print("Preprocessing complete.")
