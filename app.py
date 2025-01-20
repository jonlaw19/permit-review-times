import streamlit as st
from databricks import sql
import time

st.title("Databricks Connection Test")

# Display secrets status
st.write("1. Checking secrets...")
try:
    host = st.secrets["DATABRICKS_HOST"]
    token = st.secrets["DATABRICKS_TOKEN"]
    cluster = st.secrets["DATABRICKS_CLUSTER_ID"]
    st.success("✅ Secrets loaded successfully")
    
    # Display connection details (without showing sensitive info)
    st.write(f"Host: {host}")
    st.write(f"Cluster ID: {cluster}")
    st.write(f"Token: {token[:5]}...")
    
except Exception as e:
    st.error(f"Failed to load secrets: {e}")
    st.stop()

# Add a button to test connection
if st.button("Test Databricks Connection"):
    st.write("2. Testing Databricks connection...")
    try:
        with sql.connect(
            server_hostname=host,
            http_path=f'/sql/1.0/warehouses/{cluster}',
            access_token=token,
            connect_timeout=10
        ) as connection:
            with connection.cursor() as cursor:
                st.write("3. Executing test query...")
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                st.success(f"✅ Test query successful! Result: {result[0]}")
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")

st.write("Note: You can check your Databricks SQL warehouse settings at:")
st.write(f"https://{host}/sql/warehouses")
