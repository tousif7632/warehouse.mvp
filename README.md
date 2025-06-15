# Warehouse Management System (WMS)

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.2-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

A complete Warehouse Management System with SKU mapping, inventory tracking, and API integration.

## Features

- **SKU Mapping Engine**: Automatically map product variants to master SKUs
- **Multi-platform Support**: Amazon, Shopify, eBay, Walmart formats
- **Fuzzy Matching**: Handle SKU variations with intelligent matching
- **Combo Products**: Support for bundled/kit products
- **REST API**: FastAPI backend for system integration
- **Data Export**: CSV/Excel/Baserow export capabilities

## Project Structure
warehouse-mvp/
├── api/ # FastAPI backend
│ ├── pycache/
│ ├── main.py # API entry point
│ └── requirements.txt # Backend dependencies
├── app/ # Tkinter GUI application
│ ├── pycache/
│ ├── app.py # GUI entry point
│ ├── sku_mapper.py # Core mapping logic
│ └── requirements.txt # GUI dependencies
├── data/ # Sample data files
│ ├── master_skus.csv
│ └── sales_data.csv
└── README.md # This file

text

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/warehouse-mvp.git
   cd warehouse-mvp
Set up virtual environment:

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
Install dependencies:

bash
# For GUI application
cd app
pip install -r requirements.txt

# For API backend
cd ../api
pip install -r requirements.txt
Usage
GUI Application
bash
cd app
python app.py
API Backend
bash
cd api
uvicorn main:app --reload
Configuration
Create .env file in the api directory:

ini
DATABASE_URL=mysql+pymysql://user:password@localhost/warehouse
API_KEY=your-secret-key
API Endpoints
Endpoint	Method	Description
/skus	GET	List all SKU mappings
/skus	POST	Create new SKU mapping
/skus/{sku}	GET	Get specific SKU details
/inventory	GET	Current inventory levels
/sales/import	POST	Import sales data
Examples
Map SKUs via API:

python
import requests

response = requests.post(
    "http://localhost:8000/skus",
    json={
        "sku": "GOLD-APPLE-123",
        "msku": "APPLE_GOLD",
        "marketplace": "amazon"
    }
)
Dependencies
Python 3.9+

FastAPI (Backend)

Tkinter (GUI)

Pandas (Data processing)

TheFuzz (Fuzzy matching)

License
MIT License - See LICENSE for details.

Support
For issues or questions, please open an issue.

text

This README includes:

1. **Project metadata** with badges
2. **Key features** of the system
3. **Directory structure** matching your project
4. **Installation instructions** with environment setup
5. **Usage examples** for both GUI and API
6. **Configuration** guidance
7. **API documentation** for main endpoints
8. **Code examples** for integration
9. **Dependency** information
10. **License** and support information

You can customize the GitHub URLs, API endpoints, and configuration details to match your specific implementation. The markdown formatting ensures proper display on GitHub and other platforms.



Loom Video: https://www.loom.com/share/c3f0781389fc4382a45c4dff9d137da2?sid=93be169a-a70c-4b01-a967-90ecb4d5806e
