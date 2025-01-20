import streamlit as st
from sentence_transformers import SentenceTransformer
import requests
from databricks import sql
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get secrets and show connection status
st.sidebar.write("Checking connections...")

try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    databricks_host = st.secrets["DATABRICKS_HOST"]
    databricks_token = st.secrets["DATABRICKS_TOKEN"]
    databricks_cluster = st.secrets["DATABRICKS_CLUSTER_ID"]
    st.sidebar.success("✅ Loaded secrets")
except Exception as e:
    st.sidebar.error(f"❌ Error loading secrets: {str(e)}")
    st.stop()

# Initialize sentence transformer
@st.cache_resource
def init_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# Test Databricks connection
try:
    with sql.connect(
        server_hostname=databricks_host,
        http_path=f'/sql/1.0/warehouses/{databricks_cluster}',
        access_token=databricks_token
    ) as connection:
        with connection.cursor() as cursor:
            # Simple test query
            cursor.execute("SELECT 1")
            st.sidebar.success("✅ Databricks connection successful")
except Exception as e:
    st.sidebar.error(f"❌ Databricks connection failed: {str(e)}")
    st.stop()

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
            "messages": messages,
            "temperature": 0.7
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        return response.json()['choices'][0]['message']['content']

# Function to get similar documents
def get_similar_documents(query_embedding, k=3):
    with sql.connect(
        server_hostname=databricks_host,
        http_path=f'/sql/1.0/warehouses/{databricks_cluster}',
        access_token=databricks_token
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                WITH similarities AS (
                    SELECT 
                        combined_text,
                        embeddings,
                        (SELECT SUM(a * b) 
                         FROM UNNEST(embeddings) WITH ORDINALITY AS t1(a, i)
                         CROSS JOIN UNNEST(%s) WITH ORDINALITY AS t2(b, i)
                         WHERE t1.i = t2.i) as similarity
                    FROM embeddings_table
                )
                SELECT combined_text
                FROM similarities
                ORDER BY similarity DESC
                LIMIT {k}
            """, (query_embedding,))
            
            results = cursor.fetchall()
            return [row[0] for row in results]

# Main app
st.title("Permit Query System")

# Initialize
model = init_model()
openai_client = SimpleOpenAIClient(openai_api_key)

# Query input
query = st.text_input("Ask a question about permits:")
if st.button("Search"):
    if query:
        with st.spinner('Searching...'):
            try:
                # Generate query embedding
                query_embedding = model.encode([query])[0].tolist()
                st.sidebar.success("✅ Generated query embedding")
                
                # Get similar documents
                similar_docs = get_similar_documents(query_embedding)
                st.sidebar.success("✅ Retrieved similar documents")
                
                # Get OpenAI response
                context = "\n---\n".join(similar_docs)
                messages = [
                    {"role": "system", "content": "Answer based on the context provided."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ]
                
                answer = openai_client.create_chat_completion(messages)
                st.sidebar.success("✅ Generated answer")
                
                # Show results
                st.subheader("Answer")
                st.write(answer)
                
                st.subheader("Source Documents")
                for doc in similar_docs:
                    st.text(doc)
            except Exception as e:
                st.sidebar.error(f"❌ Error during processing: {str(e)}")
