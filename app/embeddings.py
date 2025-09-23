import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Define path where Chroma DB will be saved
PERSIST_DIR = "app/db/chroma_db" #delete chroma_db file whenever the documentation.txt file changes so it can be automatically recreated

# Use HuggingFace embeddings (no API key required)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if not os.path.exists(PERSIST_DIR):
    print("⚡ Creating new Chroma DB...")

# Load documents
    loader = TextLoader("app/documentation.txt",encoding="utf-8")
    documents = loader.load()

# Split documents into smaller chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

# Create & persist DB
    db = Chroma.from_documents(texts, embeddings, persist_directory=PERSIST_DIR)
    db.persist()   # save to disk

else:
    print("⚡ Loading existing Chroma DB...")
    db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)

