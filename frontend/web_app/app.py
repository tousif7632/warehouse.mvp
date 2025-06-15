import streamlit as st
import pandas as pd
import os
import sys
import time

# ✅ Step 1: Fix import path so Python can find the 'backend' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# ✅ Now import modules from backend
from data_processor import process_sales_data
from backend.api.schemas import ExportRequest
from backend.database.database_connector import BaserowConnector

# Initialize session state
def init_session():
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
        st.session_state.metrics = None
        st.session_state.baserow_connected = False

# Page config
st.set_page_config(page_title="Warehouse Dashboard", layout="wide")
init_session()

# Sidebar
with st.sidebar:
    st.header("Configuration")
    api_token = st.text_input("Baserow API Token", type="password")
    base_url = st.text_input("Baserow Base URL", "https://api.baserow.io")
    table_id = st.text_input("Table ID")
    
    if st.button("Connect to Baserow"):
        try:
            st.session_state.connector = BaserowConnector(base_url, api_token)
            st.session_state.baserow_connected = True
            st.success("Connected to Baserow!")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
    
    st.divider()
    st.header("Data Upload")
    master_file = st.file_uploader("Master SKUs", type=["csv", "xlsx"])
    sales_files = st.file_uploader("Sales Data", type=["csv", "xlsx"], accept_multiple_files=True)
    marketplace = st.selectbox("Marketplace", ["Amazon", "Shopify", "eBay", "Walmart", "Other"])
    process_btn = st.button("Process Data")

# Main content area
st.title("Warehouse Management Dashboard")

# Process data
if process_btn and master_file and sales_files:
    with st.spinner("Processing data..."):
        try:
            os.makedirs("temp", exist_ok=True)
            master_path = f"temp/{master_file.name}"
            with open(master_path, "wb") as f:
                f.write(master_file.getbuffer())
            
            sales_paths = []
            for file in sales_files:
                path = f"temp/{file.name}"
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                sales_paths.append(path)
            
            result = process_sales_data(master_path, sales_paths, marketplace)
            st.session_state.processed_data = result['data']
            st.session_state.metrics = result['metrics']
            st.success("Data processed successfully!")
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")

# Display results
if st.session_state.processed_data is not None:
    st.header("Sales Overview")
    cols = st.columns(4)
    cols[0].metric("Total Orders", st.session_state.metrics['total_orders'])
    cols[1].metric("Total Revenue", f"${st.session_state.metrics['total_revenue']:,.2f}")
    cols[2].metric("Unique Products", st.session_state.metrics['unique_products'])
    cols[3].metric("Avg Order Value", f"${st.session_state.metrics['avg_order_value']:,.2f}")
    
    st.subheader("Processed Data Preview")
    st.dataframe(st.session_state.processed_data.head(50))
    
    if st.session_state.get('baserow_connected', False):
        if st.button("Export to Baserow"):
            with st.spinner("Exporting data..."):
                try:
                    request = ExportRequest(
                        table_id=table_id,
                        data=st.session_state.processed_data.to_dict(orient='records')
                    )
                    st.session_state.connector.export_data(request)
                    st.success("Data exported to Baserow successfully!")
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
    else:
        st.warning("Connect to Baserow to enable export")

# AI Query Section
st.divider()
st.header("AI-Powered Insights")

if st.session_state.get('baserow_connected', False):
    query = st.text_input("Ask a question about your data:")
    if query:
        with st.spinner("Processing your query..."):
            try:
                from backend.ai_layer.query_processor import AIQueryProcessor
                processor = AIQueryProcessor(st.session_state.connector)
                result = processor.process_query(query, table_id)
                
                if result.get('type') == 'text':
                    st.write(result['content'])
                elif result.get('type') == 'chart':
                    st.plotly_chart(result['content'])
                elif result.get('type') == 'table':
                    st.dataframe(result['content'])
            except Exception as e:
                st.error(f"Query processing error: {str(e)}")
else:
    st.info("Connect to Baserow to enable AI insights")
