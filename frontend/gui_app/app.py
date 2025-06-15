import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from sku_mapper import SKUMapper
import pandas as pd
import logging
import os

class MappingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SKU Mapping Tool")
        self.geometry("900x700")
        self.mapper = SKUMapper()
        self.processed_data = None
        self._setup_ui()
        
    def _setup_ui(self):
        # Configure styles
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TFrame", padding=10)
        
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # File input section
        file_frame = ttk.LabelFrame(main_frame, text="File Input")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Master file
        ttk.Label(file_frame, text="Master SKUs:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.master_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.master_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_master).grid(row=0, column=2, padx=5, pady=5)
        
        # Sales file
        ttk.Label(file_frame, text="Sales Data:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sales_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.sales_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_sales).grid(row=1, column=2, padx=5, pady=5)
        
        # Marketplace selection
        ttk.Label(file_frame, text="Marketplace:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.marketplace = tk.StringVar(value="general")
        marketplace_combo = ttk.Combobox(
            file_frame, 
            textvariable=self.marketplace,
            values=["general", "amazon", "shopify", "ebay", "walmart"],
            state="readonly",
            width=15
        )
        marketplace_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Process button
        ttk.Button(file_frame, text="Process Data", command=self.process_data).grid(row=3, column=1, pady=10)
        
        # Results table
        table_frame = ttk.LabelFrame(main_frame, text="Mapping Results")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview with scrollbars
        self.tree = ttk.Treeview(table_frame, columns=("Input SKU", "Mapped MSKU", "Status"), show="headings")
        self.tree.heading("Input SKU", text="Input SKU")
        self.tree.heading("Mapped MSKU", text="Mapped MSKU")
        self.tree.heading("Status", text="Status")
        self.tree.column("Input SKU", width=200)
        self.tree.column("Mapped MSKU", width=200)
        self.tree.column("Status", width=100)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Log panel
        log_frame = ttk.LabelFrame(main_frame, text="Log Messages")
        log_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure logging
        self.log_handler = TextHandler(self.log_area)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)
        
        # Export buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="Export CSV", command=lambda: self.export_data('csv')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export Excel", command=lambda: self.export_data('excel')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Add Combo Product", command=self.add_combo_dialog).pack(side=tk.RIGHT, padx=5)
    
    def browse_master(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.master_path.set(file_path)
            if self.mapper.load_master(file_path):
                logging.info("Master SKUs loaded successfully")
    
    def browse_sales(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.sales_path.set(file_path)
            logging.info(f"Sales data selected: {os.path.basename(file_path)}")
    
    def process_data(self):
        if not self.master_path.get():
            messagebox.showerror("Error", "Please select a master SKU file first")
            return
        if not self.sales_path.get():
            messagebox.showerror("Error", "Please select a sales data file")
            return
        
        marketplace = self.marketplace.get()
        self.processed_data = self.mapper.process_file(
            self.sales_path.get(), 
            marketplace
        )
        
        if self.processed_data is not None:
            self.display_results()
            logging.info("Data processing completed")
    
    def display_results(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate treeview
        sku_col = next((col for col in self.processed_data.columns if 'sku' in col.lower()), None)
        if not sku_col:
            logging.error("SKU column not found in processed data")
            return
        
        for _, row in self.processed_data.iterrows():
            sku = row[sku_col]
            msku = row.get('MSKU', '')
            status = "Mapped" if pd.notna(msku) and msku != '' else "Unmapped"
            tags = ("mapped",) if status == "Mapped" else ("unmapped",)
            self.tree.insert("", tk.END, values=(sku, msku, status), tags=tags)
        
        # Configure tag colors
        self.tree.tag_configure("mapped", background="#e6f7e6")
        self.tree.tag_configure("unmapped", background="#ffe6e6")
    
    def export_data(self, format):
        if self.processed_data is None:
            messagebox.showinfo("Info", "No data to export. Process data first.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(f"{format.upper()} files", f"*.{format}")]
        )
        if not file_path:
            return
        
        try:
            if format == 'csv':
                self.processed_data.to_csv(file_path, index=False)
            else:
                self.processed_data.to_excel(file_path, index=False)
            logging.info(f"Data exported successfully to {file_path}")
            messagebox.showinfo("Success", "Data exported successfully")
        except Exception as e:
            logging.error(f"Export error: {str(e)}")
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def add_combo_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Combo Product")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="SKUs (comma separated):").pack(pady=(10, 5), padx=10, anchor=tk.W)
        sku_entry = ttk.Entry(dialog, width=40)
        sku_entry.pack(padx=10, fill=tk.X)
        
        ttk.Label(dialog, text="Master SKU:").pack(pady=(10, 5), padx=10, anchor=tk.W)
        msku_entry = ttk.Entry(dialog, width=40)
        msku_entry.pack(padx=10, fill=tk.X)
        
        def save_combo():
            skus = [s.strip() for s in sku_entry.get().split(",") if s.strip()]
            msku = msku_entry.get().strip()
            
            if len(skus) < 2:
                messagebox.showerror("Error", "At least two SKUs required for combo")
                return
            if not msku:
                messagebox.showerror("Error", "Master SKU is required")
                return
            
            self.mapper.add_combo_product(skus, msku)
            logging.info(f"Added combo product: {skus} -> {msku}")
            messagebox.showinfo("Success", "Combo product added successfully")
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Save", command=save_combo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.config(state=tk.NORMAL)
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = MappingApp()
    app.mainloop()