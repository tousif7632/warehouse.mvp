import sys
import os

# Add parent folder (frontend) to sys.path so gui_app can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from gui_app.sku_mapper import SKUMapper

def auto_detect_column(df, keywords):
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            return col
    return None

def process_sales_data(master_path, sales_paths, marketplace):
    mapper = SKUMapper()
    if not mapper.load_master(master_path):
        raise Exception("Failed to load master SKUs")
    
    all_data = []
    for path in sales_paths:
        df = mapper.process_file(path, marketplace)
        if df is not None:
            all_data.append(df)
    
    combined = pd.concat(all_data) if all_data else pd.DataFrame()
    
    metrics = {}
    if not combined.empty:
        # Auto-detect columns
        order_id_col = auto_detect_column(combined, ['order', 'id'])
        price_col = auto_detect_column(combined, ['price', 'amount', 'revenue'])
        
        if not order_id_col or not price_col:
            raise Exception("Could not detect required columns in sales data")
        
        # Calculate metrics
        total_orders = combined[order_id_col].nunique()
        total_revenue = combined[price_col].sum()
        unique_products = combined['MSKU'].nunique()
        avg_order_value = total_revenue / total_orders if total_orders else 0
        
        metrics = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'unique_products': unique_products,
            'avg_order_value': avg_order_value
        }
    else:
        metrics = {
            'total_orders': 0,
            'total_revenue': 0,
            'unique_products': 0,
            'avg_order_value': 0
        }
    
    return {
        'data': combined,
        'metrics': metrics
    }
