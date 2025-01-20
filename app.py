import streamlit as st
from sentence_transformers import SentenceTransformer
import requests
from databricks import sql

# Initialize with proper error handling
st.title("Permit Query System")

# First check secrets
try:
    # Get secrets
    if 'DATABRICKS_HOST' not in st.secrets:
        st.error("Missing Databricks secrets. Please add them in Streamlit settings.")
        st.write("Required secrets:")
        st.write("- DATABRICKS_HOST")
        st.write("- DATABRICKS_TOKEN")
        st.write("- DATABRICKS_CLUSTER_ID")
        st.write("- OPENAI_API_KEY")
        st.stop()
    
    # If we get here, try to read all secrets
    databricks_host = st.secrets["DATABRICKS_HOST"]
    databricks_token = st.secrets["DATABRICKS_TOKEN"]
    databricks_cluster = st.secrets["DATABRICKS_CLUSTER_ID"]
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    
    st.sidebar.success("✅ Successfully loaded all secrets")
except Exception as e:
    st.error(f"Error loading secrets: {str(e)}")
    st.stop()

# Test Databricks connection
try:
    with sql.connect(
        server_hostname=databricks_host,
        http_path=f'/sql/1.0/warehouses/{databricks_cluster}',
        access_token=databricks_token
    ) as connection:
        # Test query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                st.sidebar.success("✅ Databricks connection successful")
            else:
                st.sidebar.error("❌ Databricks test query failed")
                st.stop()
except Exception as e:
    st.sidebar.error(f"❌ Databricks connection failed: {str(e)}")
    st.stop()

# Initialize model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    st.sidebar.success("✅ Model initialized")
except Exception as e:
    st.sidebar.error(f"❌ Model initialization failed: {str(e)}")
    st.stop()

# Define OpenAI helper
def get_openai_response(messages):
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json={
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7
        }
    )
    return response.json()['choices'][0]['message']['content']

# Query interface
query = st.text_input("Ask a question about permits:")

if st.button("Search"):
    if query:
        try:
            with st.spinner('Processing query...'):
                # Generate embedding
                query_embedding = model.encode([query])[0].tolist()
                st.sidebar.success("✅ Generated query embedding")
                
                # Query Databricks
                with sql.connect(
                    server_hostname=databricks_host,
                    http_path=f'/sql/1.0/warehouses/{databricks_cluster}',
                    access_token=databricks_token
                ) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT combined_text FROM embeddings_table LIMIT 3")
                        results = cursor.fetchall()
                        
                context = "\n---\n".join([r[0] for r in results])
                
                # Get OpenAI response
                messages = [
                    {"role": "system", "content": "Answer based on the provided context."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ]
                
                answer = get_openai_response(messages)
                
                # Display results
                st.subheader("Answer")
                st.write(answer)
                
                st.subheader("Source Documents")
                for doc in [r[0] for r in results]:
                    st.text(doc)
                    
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
