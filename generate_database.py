from langchain.schema import Document
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import requests
import re
from bs4 import BeautifulSoup
import os
import pandas as pd
from datetime import datetime


chunksize = 1000
chunkoverlap = 500
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'Data'))


def main():
    generate_database()

    # testfunction()

    

def generate_database():    
    documents = load_documents()
    save_to_faiss(documents)
    return


def load_documents():
    documents = []
    
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".csv"):
            df = pd.read_csv(os.path.join(DATA_PATH, filename))
            for idx, row in df.iterrows():
                text = f'Product Name: {row["title"]}\n description: {row["description"]}\n Brand: {row["brand"]}\n initial price: {row["initial_price"]}\n final price: {row["final_price"]}\n discount: {row["discount"]}\n rating: {row["rating"]}\n review count: {row["reviews_count"]}\n url: {row["url"]}\navailability: {row["availability"]}\n reviews count: {row["reviews_count"]}\n item weight: {row["item_weight"]}\n rating: {row["rating"]}\n product dimensions: {row["product_dimensions"]}\n discount: {row["discount"]}\n category: {row["department"]}\n top review: {row["top_review"]}\n features: {row["features"]}\n url: {row["url"]}'
                doc = Document(page_content=text, metadata={"source": filename, "row": idx})
                documents.append(doc)
    
    return documents



def save_to_faiss(documents: list[Document]):
    print("Making FAISS directory")
    FAISS_PATH = os.path.join(os.path.dirname(__file__),'faiss_index')
    os.makedirs(FAISS_PATH, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print(f'Using embeddings model: {embeddings.model_name}')

    db = FAISS.from_documents(documents, embeddings)
    
    db.save_local(FAISS_PATH)
    print(f'Saved {len(documents)} to {FAISS_PATH}')
    
def testfunction():
    input_query = "What is the best product in the category of electronics?"
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.load_local(os.path.join(os.path.dirname(__file__), 'faiss_index'), embedding_function,allow_dangerous_deserialization=True )


    results = db.similarity_search_with_score(
        input_query,
            k=5
        )
            
    if len(results) == 0:
        return "No relevant data found. Try indexing some content first."
            
    # Format is slightly different than Chroma
    context = "\n".join([doc.page_content for doc, score in results])
    for i, (doc, score) in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Score: {score}")
        print(doc.page_content)







if __name__ == "__main__":
    main()






