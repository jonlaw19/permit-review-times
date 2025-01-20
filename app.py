import streamlit as st
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import requests
import json

# Use secrets for API key
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Initialize sentence transformer
@st.cache_resource
def init_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('permit_data.csv')
    return df

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
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

# Function to find similar documents
def find_similar_documents(query_embedding, embeddings, texts, k=3):
    # Convert string embeddings to numpy arrays
    if isinstance(embeddings[0], str):
        embeddings = [json.loads(emb) for emb in embeddings]
    embeddings = np.array(embeddings)
    
    # Calculate similarities
    similarities = np.dot(embeddings, query_embedding)
    top_k_indices = np.argsort(similarities)[-k:][::-1]
    
    return [texts[i] for i in top_k_indices]

# Main app
st.title("Permit Query System")
# Initialize
model = init_model()
df = load_data()
openai_client = SimpleOpenAIClient(openai_api_key)

# Query input
query = st.text_input("Ask a question about permits:")
if st.button("Search"):
    if query:
        with st.spinner('Searching...'):
            # Generate query embedding
            query_embedding = model.encode([query])[0].tolist()
            
            # Find similar documents
            similar_docs = find_similar_documents(
                query_embedding, 
                df['embeddings'].tolist(), 
                df['combined_text'].tolist()
            )
            
            # Get OpenAI response
            context = "\n---\n".join(similar_docs)
            messages = [
                {"role": "system", "content": "Answer based on the context provided."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            try:
                answer = openai_client.create_chat_completion(messages)
                
                # Show results
                st.subheader("Answer")
                st.write(answer)
                
                st.subheader("Source Documents")
                for doc in similar_docs:
                    st.text(doc)
            except Exception as e:
                st.error(f"Error getting answer: {str(e)}")
