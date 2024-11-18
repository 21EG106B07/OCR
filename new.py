import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Initialize SQLite database
db_path = 'data.db'

# Connect to the database
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
    data.to_sql(table_name, conn, if_exists='append', index=False)

# Load data from a specific table
def load_from_database(table_name):
    return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

# Main app
st.title("Business Dashboard with Database")

# Create tables if they don't exist
create_tables()

# Sidebar Navigation
page = st.sidebar.selectbox("Choose a page", ["Upload & Store Data", "View Data in Database", "Overview", "Stock Reports", "Purchase Orders", "Orders", "Invoices"])

if page == "Upload & Store Data":
    st.header("Upload & Store Data in Database")
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        # Read all sheets
        stock_reports = pd.read_excel(uploaded_file, sheet_name='Stock Reports')
        purchase_orders = pd.read_excel(uploaded_file, sheet_name='Purchase Orders')
        orders = pd.read_excel(uploaded_file, sheet_name='Orders')
        invoices = pd.read_excel(uploaded_file, sheet_name='Invoices')

        # Rename columns to remove spaces for compatibility with SQLite
        stock_reports.columns = [col.replace(" ", "") for col in stock_reports.columns]
        purchase_orders.columns = [col.replace(" ", "") for col in purchase_orders.columns]
        orders.columns = [col.replace(" ", "") for col in orders.columns]
        invoices.columns = [col.replace(" ", "") for col in invoices.columns]

        # Button to store data in the database
        if st.button("Store Data in Database"):
            save_to_database(stock_reports, "StockReports")
            save_to_database(purchase_orders, "PurchaseOrders")
            save_to_database(orders, "Orders")
            save_to_database(invoices, "Invoices")
            st.success("Data has been saved to the database.")

elif page == "View Data in Database":
    st.header("View Data in Database")
    table_name = st.selectbox("Select Table", ["StockReports", "PurchaseOrders", "Orders", "Invoices"])

    if st.button("Load Data"):
        data = load_from_database(table_name)
        st.dataframe(data)

elif page == "Overview":
    st.header("Overview")
    # Total Revenue
    orders_data = load_from_database("Orders")
    invoices_data = load_from_database("Invoices")
    total_revenue_orders = orders_data['Total'].sum()
    total_revenue_invoices = invoices_data['TotalPrice'].sum()
    st.metric("Total Revenue (Orders)", f"${total_revenue_orders:,.2f}")
    st.metric("Total Revenue (Invoices)", f"${total_revenue_invoices:,.2f}")

    # Top Selling Product (Stock Reports)
    stock_reports_data = load_from_database("StockReports")
    
    # Ensure 'UnitsSold' is numeric and handle invalid entries
    stock_reports_data['UnitsSold'] = pd.to_numeric(stock_reports_data['UnitsSold'], errors='coerce')
    stock_reports_data = stock_reports_data.dropna(subset=['UnitsSold'])
    stock_reports_data['UnitsSold'] = stock_reports_data['UnitsSold'].astype(int)

    if not stock_reports_data.empty:  # Ensure the DataFrame is not empty
        top_selling_product = stock_reports_data.loc[stock_reports_data['UnitsSold'].idxmax()]
        st.write(f"Top Selling Product: *{top_selling_product['Product']}* with *{top_selling_product['UnitsSold']} units sold*")
    else:
        st.write("No data available to determine the top-selling product.")

elif page == "Stock Reports":
    st.header("Stock Reports")
    stock_reports_data = load_from_database("StockReports")
    st.dataframe(stock_reports_data)
    fig = px.bar(stock_reports_data, x='Product', y=['UnitsSold', 'UnitsInStock'], barmode='group', title="Stock Overview")
    st.plotly_chart(fig)

elif page == "Purchase Orders":
    st.header("Purchase Orders")
    purchase_orders_data = load_from_database("PurchaseOrders")
    st.dataframe(purchase_orders_data)
    fig = px.pie(purchase_orders_data, names='Product', values='Quantity', title="Purchase Quantity by Product")
    st.plotly_chart(fig)

elif page == "Orders":
    st.header("Orders")
    orders_data = load_from_database("Orders")
    st.dataframe(orders_data)
    fig = px.line(orders_data, x='OrderID', y='Total', title="Revenue per Order")
    st.plotly_chart(fig)

elif page == "Invoices":
    st.header("Invoices")
    invoices_data = load_from_database("Invoices")
    st.dataframe(invoices_data)
    fig = px.scatter(invoices_data, x='OrderID', y='TotalPrice', size='Quantity', color='Product', title="Invoices Analysis")
    st.plotly_chart(fig)