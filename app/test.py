from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables (if needed for other things)
load_dotenv()

# Load documents
loader = TextLoader("D:/Desktop/SONiC/SONiC-GUI-Backend/app/documentation.txt")
documents = loader.load()

# Split documents into smaller chunks
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Use HuggingFace embeddings (no API key required)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create Chroma database
db = Chroma.from_documents(texts, embeddings)

# Perform a similarity search
query = "What is the command to show vlans?"
docs = db.similarity_search(query)

print(docs[0].page_content)
