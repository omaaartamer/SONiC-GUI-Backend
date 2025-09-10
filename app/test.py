from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


loader = TextLoader(r"E:\Orange\SONiC-GUI\SONiC-GUI-Backend\app\documentation.txt", encoding="utf-8")
documents = loader.load()


text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = Chroma.from_documents(texts, embeddings)

query = "What is this document about?"
docs = db.similarity_search(query)

print("Most relevant chunk:\n", docs[0].page_content)
