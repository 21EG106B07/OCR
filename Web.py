import streamlit as st
import pandas as pd
import plotly.express as px

# Load the Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    # Read all sheets
    stock_reports = pd.read_excel(uploaded_file, sheet_name='Stock Reports')
    purchase_orders = pd.read_excel(uploaded_file, sheet_name='Purchase Orders')
    orders = pd.read_excel(uploaded_file, sheet_name='Orders')
    invoices = pd.read_excel(uploaded_file, sheet_name='Invoices')

    st.title("Business Dashboard")
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Overview", "Stock Reports", "Purchase Orders", "Orders", "Invoices"])

    if page == "Overview":
        st.header("Overview")
        # Total Revenue
        total_revenue_orders = orders['Total'].sum()
        total_revenue_invoices = invoices['Total Price'].sum()
        st.metric("Total Revenue (Orders)", f"${total_revenue_orders:,.2f}")
        st.metric("Total Revenue (Invoices)", f"${total_revenue_invoices:,.2f}")

        # Top Selling Product (Stock Reports)
        top_selling_product = stock_reports.loc[stock_reports['Units Sold'].idxmax()]
        st.write(f"Top Selling Product: **{top_selling_product['Product']}** with **{top_selling_product['Units Sold']} units sold**")

    elif page == "Stock Reports":
        st.header("Stock Reports")
        st.dataframe(stock_reports)
        fig = px.bar(stock_reports, x='Product', y=['Units Sold', 'Units in Stock'], barmode='group', title="Stock Overview")
        st.plotly_chart(fig)

    elif page == "Purchase Orders":
        st.header("Purchase Orders")
        st.dataframe(purchase_orders)
        fig = px.pie(purchase_orders, names='Product', values='Quantity', title="Purchase Quantity by Product")
        st.plotly_chart(fig)

    elif page == "Orders":
        st.header("Orders")
        st.dataframe(orders)
        fig = px.line(orders, x='Order ID', y='Total', title="Revenue per Order")
        st.plotly_chart(fig)

    elif page == "Invoices":
        st.header("Invoices")
        st.dataframe(invoices)
        fig = px.scatter(invoices, x='Order ID', y='Total Price', size='Quantity', color='Product', title="Invoices Analysis")
        st.plotly_chart(fig)
