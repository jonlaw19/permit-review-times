import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import requests
import os

# Use secrets for API key
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Initialize everything
@st.cache_resource
def init_qa_system():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Use a local directory for ChromaDB
    chroma_client = chromadb.Client(Settings(persist_directory="./chromadb_data"))
    try:
        collection = chroma_client.get_collection("test_collection")
    except:
        collection = chroma_client.create_collection("test_collection")
    return model, collection

# OpenAI client
class SimpleOpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        
    def create_chat_completion(self, messages):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages
        }
        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']

# Main app
st.title("Permit Query System")

# Initialize
model, collection = init_qa_system()
openai_client = SimpleOpenAIClient(openai_api_key)

# Query input
query = st.text_input("Ask a question about permits:")
if st.button("Search"):
    if query:
        with st.spinner('Searching...'):
            # Get similar documents
            query_embedding = model.encode([query])[0].tolist()
            results = collection.query(query_embeddings=[query_embedding], n_results=3)
            
            # Get OpenAI response
            context = "\n---\n".join(results["documents"][0])
            messages = [
                {"role": "system", "content": "Answer based on the context provided."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            answer = openai_client.create_chat_completion(messages)
            
            # Show results
            st.subheader("Answer")
            st.write(answer)
            
            st.subheader("Source Documents")
            for doc in results["documents"][0]:
                st.text(doc)
