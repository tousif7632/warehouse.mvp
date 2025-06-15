import pandas as pd
import numpy as np
from thefuzz import fuzz, process
import re
import logging

class SKUMapper:
    def __init__(self):
        self.master_map = pd.DataFrame(columns=["SKU", "MSKU"])
        self.combo_products = {}
        self.logger = logging.getLogger("SKUMapper")
        logging.basicConfig(level=logging.INFO)
    
    def load_master(self, file_path):
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # Auto-detect columns
            sku_col = self._detect_column(df, ['sku', 'stock', 'product_id'])
            msku_col = self._detect_column(df, ['master_sku', 'parent_sku', 'base_product'])
            
            self.master_map = df[[sku_col, msku_col]]
            self.master_map.columns = ['SKU', 'MSKU']
            self.logger.info(f"Loaded master mapping with {len(self.master_map)} records")
            return True
        except Exception as e:
            self.logger.error(f"Error loading master file: {str(e)}")
            return False

    def _detect_column(self, df, keywords):
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return col
        return df.columns[0]

    def validate_sku(self, sku, marketplace=None):
        patterns = {
            'amazon': r'^[A-Z0-9]{10}$',
            'shopify': r'^[a-zA-Z0-9_\-]{5,}$',
            'default': r'^[\w\-]{3,}$'
        }
        pattern = patterns.get(marketplace, patterns['default'])
        return bool(re.match(pattern, sku))

    def add_combo_product(self, sku_list, msku):
        key = tuple(sorted(sku_list))
        self.combo_products[key] = msku
        self.logger.info(f"Added combo product: {key} -> {msku}")

    def auto_map(self, input_sku, marketplace=None):
        # Validate SKU format
        if not self.validate_sku(input_sku, marketplace):
            self.logger.warning(f"Invalid SKU format: {input_sku}")
            return None
        
        # Check for exact match
        exact_match = self.master_map[self.master_map['SKU'].str.lower() == input_sku.lower()]
        if not exact_match.empty:
            return exact_match.iloc[0]['MSKU']
        
        # Check for combo products (e.g., "SKU1+SKU2")
        if '+' in input_sku:
            parts = [p.strip() for p in input_sku.split('+')]
            key = tuple(sorted(parts))
            if key in self.combo_products:
                return self.combo_products[key]
        
        # Fuzzy matching
        if not self.master_map.empty:
            matches = process.extractBests(
                input_sku, 
                self.master_map['SKU'], 
                scorer=fuzz.partial_ratio, 
                score_cutoff=80
            )
            if matches:
                best_match = matches[0][0]
                return self.master_map[self.master_map['SKU'] == best_match].iloc[0]['MSKU']
        
        self.logger.warning(f"No mapping found for SKU: {input_sku}")
        return None

    def process_file(self, file_path, marketplace=None):
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # Auto-detect SKU column
            sku_col = self._detect_column(df, ['sku', 'item_sku', 'product_id'])
            
            # Apply mapping
            df['MSKU'] = df[sku_col].apply(
                lambda x: self.auto_map(str(x), marketplace) if pd.notna(x) else None
            )
            
            # Log unmapped SKUs
            unmapped = df[df['MSKU'].isna()]
            if not unmapped.empty:
                self.logger.warning(f"{len(unmapped)} unmapped SKUs found")
            
            return df
        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            return None