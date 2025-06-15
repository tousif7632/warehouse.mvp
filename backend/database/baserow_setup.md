# Baserow Setup Instructions

## 1. Create Workspace
- Go to Baserow.io and create new workspace "Warehouse Management"

## 2. Create Tables
### Products Table
- Table name: `Products`
- Fields:
  - MSKU (Text, Primary Key)
  - Description (Text)
  - Category (Single Select: Electronics, Clothing, Food, Other)
  - Unit Cost (Number)
  - Weight (Number)

### Variants Table
- Table name: `Variants`
- Fields:
  - SKU (Text, Primary Key)
  - MSKU (Link to Products table)
  - Marketplace (Single Select: Amazon, Shopify, eBay, Walmart)
  - Attributes (Long Text)

### Orders Table
- Table name: `Orders`
- Fields:
  - Order ID (Text)
  - Order Date (Date)
  - Marketplace (Single Select)
  - Customer (Text)
  - Total Amount (Number)

### Order Items Table
- Table name: `Order Items`
- Fields:
  - Order ID (Link to Orders)
  - SKU (Link to Variants)
  - Quantity (Number)
  - Price (Number)

## 3. Set Up Relationships
- Link Variants.MSKU → Products.MSKU
- Link Order Items.Order ID → Orders.Order ID
- Link Order Items.SKU → Variants.SKU

## 4. Import Data
- Use the "Import Data" feature to upload CSV files
- Map columns to appropriate fields