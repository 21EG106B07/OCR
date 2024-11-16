import re
import pdfplumber
import pandas as pd
import sqlite3
import streamlit as st

# Database configuration
db_path = 'data.db'

# Initialize SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables for storing data
def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS StockReports (
            Filename TEXT,
            Product TEXT,
            UnitsSold INTEGER,
            UnitsInStock INTEGER,
            UnitPrice REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PurchaseOrders (
            Filename TEXT,
            ProductID TEXT,
            Product TEXT,
            Quantity INTEGER,
            UnitPrice REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            Filename TEXT,
            OrderID TEXT,
            Product TEXT,
            Quantity INTEGER,
            UnitPrice REAL,
            Total REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Invoices (
            Filename TEXT,
            OrderID TEXT,
            ProductID TEXT,
            Product TEXT,
            Quantity INTEGER,
            UnitPrice REAL,
            TotalPrice REAL
        )
    """)
    conn.commit()

# Save data to database
def save_to_database(data, table_name):
    if not data.empty:
        data.to_sql(table_name, conn, if_exists='append', index=False)

# Extract data from a PDF by path
def extract_data_from_pdf(file_path):
    filename = file_path.split("\\")[-1]  # Extract filename from path
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return {"Filename": filename, "Text": text}

# Process extracted data into categories
def process_data(data_dict):
    stock_reports = []
    purchase_orders = []
    orders = []
    invoices = []

    filename = data_dict["Filename"]
    text = data_dict["Text"]
    
    if "Stock Report" in text:
        items = re.findall(r"(\D+)\s+(\d+)\s+(\d+)\s+([\d.]+)", text)
        for item in items:
            stock_reports.append({"Filename": filename, "Product": item[0].strip(), 
                                  "UnitsSold": item[1], "UnitsInStock": item[2], "UnitPrice": item[3]})
    
    if "Purchase Orders" in text:
        items = re.findall(r"(\d+)\s+([A-Za-z\s]+)\s+(\d+)\s+([\d.]+)", text)
        for item in items:
            purchase_orders.append({"Filename": filename, "ProductID": item[0], "Product": item[1].strip(), 
                                    "Quantity": item[2], "UnitPrice": item[3]})
    
    if "Order ID:" in text:
        order_id_match = re.search(r"Order ID[:\s]+(\d+)", text)
        if order_id_match:
            order_id = order_id_match.group(1)
            products = re.findall(r"Product[:\s]+(.+?)\s+Quantity[:\s]+(\d+)\s+Unit Price[:\s]+([\d.]+)\s+Total[:\s]+([\d.]+)", 
                                  text, re.DOTALL)
            for product in products:
                orders.append({"Filename": filename, "OrderID": order_id, 
                               "Product": product[0], "Quantity": product[1], 
                               "UnitPrice": product[2], "Total": product[3]})
    
    if "Invoice" in text or "invoice" in text:  
        order_id_match = re.search(r"Order ID[:\s]+(\d+)", text)
        if order_id_match:
            order_id = order_id_match.group(1)
            items = re.findall(r"(\d+)\s+([A-Za-z'’\s]+)\s+(\d+)\s+([\d.]+)", text)
            total_price_match = re.search(r"TotalPrice[:\s]+([\d.]+)", text)
            total_price = total_price_match.group(1) if total_price_match else "N/A"
            for item in items:
                invoices.append({"Filename": filename, "OrderID": order_id, 
                                 "ProductID": item[0], "Product": item[1].strip(), 
                                 "Quantity": item[2], "UnitPrice": item[3], "TotalPrice": total_price})

    return {
        "StockReports": pd.DataFrame(stock_reports),
        "PurchaseOrders": pd.DataFrame(purchase_orders),
        "Orders": pd.DataFrame(orders),
        "Invoices": pd.DataFrame(invoices),
    }

# Main Streamlit app
st.title("Process PDF from File Path")

# Create tables if they don't exist
create_tables()

# Input the file path
file_path = st.text_input("Enter the file path of the PDF:")

if file_path:
    try:
        extracted_data = extract_data_from_pdf(file_path)
        categorized_data = process_data(extracted_data)

        # Display and save data into the database
        if st.button("Process and Save Data"):
            for table, data in categorized_data.items():
                save_to_database(data, table)
            st.success("Data has been processed and saved to the database.")

        # Display extracted data
        st.header("Extracted Data")
        for table, data in categorized_data.items():
            if not data.empty:
                st.subheader(table)
                st.dataframe(data)

    except Exception as e:
        st.error(f"An error occurred: {e}")
