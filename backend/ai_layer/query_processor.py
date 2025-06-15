import pandas as pd
import plotly.express as px
from langchain.chains import create_sql_query_chain
from langchain.utilities import SQLDatabase
from langchain_community.llms import OpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from backend.database.database_connector import BaserowConnector

class AIQueryProcessor:
    def __init__(self, connector: BaserowConnector):
        self.connector = connector
        self.llm = OpenAI(temperature=0)
    
    def process_query(self, query: str, table_id: str):
        # Retrieve data from Baserow
        data = self._retrieve_table_data(table_id)
        df = pd.DataFrame(data)
        
        # Simple question answering
        if "how many" in query.lower():
            return self._answer_count_question(df, query)
        
        # Visualization requests
        if "chart" in query.lower() or "graph" in query.lower():
            return self._generate_visualization(df, query)
        
        # Fallback to text response
        return self._text_response(df, query)
    
    def _retrieve_table_data(self, table_id: str):
        response = requests.get(
            f"{self.connector.base_url}/api/database/rows/table/{table_id}/?user_field_names=true",
            headers=self.connector.headers
        )
        response.raise_for_status()
        return response.json()['results']
    
    def _answer_count_question(self, df, query):
        if "orders" in query.lower():
            count = df['order_id'].nunique()
            return {'type': 'text', 'content': f"Total Orders: {count}"}
        elif "products" in query.lower():
            count = df['MSKU'].nunique()
            return {'type': 'text', 'content': f"Unique Products: {count}"}
        elif "revenue" in query.lower():
            total = df['price'].sum()
            return {'type': 'text', 'content': f"Total Revenue: ${total:,.2f}"}
        else:
            return self._text_response(df, query)
    
    def _generate_visualization(self, df, query):
        if "sales over time" in query.lower():
            df['order_date'] = pd.to_datetime(df['order_date'])
            df['month'] = df['order_date'].dt.to_period('M')
            monthly_sales = df.groupby('month')['price'].sum().reset_index()
            fig = px.line(monthly_sales, x='month', y='price', title="Monthly Sales Trend")
            return {'type': 'chart', 'content': fig}
        
        if "top products" in query.lower():
            top_products = df.groupby('MSKU')['price'].sum().nlargest(10).reset_index()
            fig = px.bar(top_products, x='MSKU', y='price', title="Top Selling Products")
            return {'type': 'chart', 'content': fig}
        
        return {'type': 'text', 'content': "Could not generate visualization for your query"}
    
    def _text_response(self, df, query):
        # Simple text response for other queries
        return {
            'type': 'text',
            'content': f"I processed your query: '{query}'. The dataset contains {len(df)} records."
        }