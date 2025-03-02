import streamlit as st
import random
import time

# Configure page
st.set_page_config(
    page_title="Permit Query Demo",
    page_icon="🏗️",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🏗️ Permit Query System")
st.markdown("""
    This demo shows how you can interact with our permit database using natural language queries. 
    Ask questions about permit types, timelines, requirements, or specific permit details.
""")

# Sample responses for demo
SAMPLE_RESPONSES = [
    {
        "answer": "Based on the permit records, amendments typically fall into several categories: structural modifications, timeline extensions, and scope changes. The most common type is the conversion from long-form to short-form permits, which usually occurs when the project scope is simplified during the development process.",
        "sources": ["Permit #A1157640: Amendment to convert from long-form to short-form permit",
                   "Permit #B234567: Timeline extension amendment requested",
                   "Permit #C789012: Structural modification amendment approved"]
    },
    {
        "answer": "The average processing time for residential permits in the last quarter was 45 days. However, this can vary significantly based on the complexity of the project and completeness of the application. Simple permits might be processed in as few as 15 days, while complex projects could take up to 90 days.",
        "sources": ["2023 Q4 Permit Processing Report",
                   "Residential Permit Guidelines Document",
                   "Permit Processing Timeline Analysis"]
    },
    {
        "answer": "Commercial construction permits require several key documents: detailed architectural plans, structural calculations, environmental impact assessments, and proof of compliance with local zoning laws. All submissions must be certified by a licensed architect or engineer.",
        "sources": ["Commercial Permit Requirements Guide",
                   "Building Code Section 7.2.3",
                   "Zoning Compliance Documentation"]
    }
]

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
        This demo showcases:
        - 🔍 Natural language querying
        - 📊 Real-time responses
        - 📑 Source documentation
        - 💡 Context-aware answers
    """)
    
    st.header("Sample Questions")
    st.markdown("""
        Try asking about:
        - Types of permit amendments
        - Average processing times
        - Required documentation
        - Specific permit numbers
        - Construction types
        - & More!
    """)

# Main query interface
query = st.text_input("What would you like to know about permits?", 
                     placeholder="e.g., 'What types of amendments are most common?'")

if st.button("Search", type="primary"):
    if query:
        with st.spinner('Searching permit database...'):
            # Simulate processing time
            time.sleep(2)
            
            # Get random sample response for demo
            response = random.choice(SAMPLE_RESPONSES)
            
            # Display answer
            st.markdown("### 📝 Answer")
            st.write(response["answer"])
            
            # Display sources
            st.markdown("### 📚 Sources")
            for source in response["sources"]:
                with st.expander(f"Source: {source[:50]}..."):
                    st.write(source)
                    
            # Add confidence score for demo
            confidence = random.uniform(0.85, 0.98)
            st.markdown(f"*Confidence Score: {confidence:.2%}*")
    else:
        st.warning("Please enter a question.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>🏗️ Permit Query System Demo | Built with Streamlit</p>
    </div>
""", unsafe_allow_html=True)
