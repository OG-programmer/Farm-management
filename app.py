import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import auth  # Import the authentication module

# Check if the user is authenticated before showing the app
if auth.check_authentication():

    # Set up sidebar image and title
    image_path = "assets/image2.jpg"  # Replace with your image path
    if os.path.exists(image_path):
        st.sidebar.image(image_path, use_container_width=True)
    else:
        st.sidebar.warning("Image not found. Please check the path.")
    
    st.sidebar.write("Manage your farm's livestock and expenses here.")

    # Database setup function
    def init_db():
        conn = sqlite3.connect("farm_management.db")
        cursor = conn.cursor()
        # Create tables if they do not exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS livestock (
                        id INTEGER PRIMARY KEY,
                        type TEXT,
                        quantity INTEGER,
                        date_added TEXT
                    )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY,
                        description TEXT,
                        amount REAL,
                        date TEXT
                    )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS rainfall (
                        id INTEGER PRIMARY KEY,
                        measurement REAL,
                        date TEXT
                    )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS activity_log (
                        id INTEGER PRIMARY KEY,
                        action TEXT,
                        details TEXT,
                        timestamp TEXT
                    )''')
        conn.commit()
        conn.close()

    # Function to log activities and keep only the 20 latest logs
    def log_activity(action, details):
        conn = sqlite3.connect("farm_management.db")
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
        # Insert the new log
        cursor.execute("INSERT INTO activity_log (action, details, timestamp) VALUES (?, ?, ?)",
                    (action, details, timestamp))
    
        # Check the number of logs in the table
        cursor.execute("SELECT COUNT(*) FROM activity_log")
        log_count = cursor.fetchone()[0]
    
        # If there are more than 20 logs, delete the oldest one
        if log_count > 20:
            cursor.execute("DELETE FROM activity_log WHERE id = (SELECT MIN(id) FROM activity_log)")

        conn.commit()
        conn.close()

    # Function to view a table
    def view_table(table_name):
        conn = sqlite3.connect("farm_management.db")
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df

    # Function to view the log history
    def view_log_history():
        conn = sqlite3.connect("farm_management.db")
        df = pd.read_sql_query("SELECT * FROM activity_log ORDER BY timestamp DESC", conn)
        conn.close()
        return df

    # Initialize the database
    init_db()

    # Custom CSS for styling, including background image
    st.markdown("""
        <style>
        body {
            background-image: url('background.jpg');  /* Path to your image */
            background-size: cover;
            background-position: center;
            font-family: 'Roboto', sans-serif;
        }

        .stApp {
            background-color: rgba(255, 255, 255, 0.5);  /* Semi-transparent overlay */
        }

        .title {
            font-size: 60px;
            color: #808000;
            text-align: center;
        }

        .header {
            font-size: 26px;
            color: #006400;
        }

        .subheader {
            font-size: 26px;
            color: #006400;
        }

        .body {
            font-size: 30px;
        }

        .dataframe {
            border-collapse: collapse;
            width: 100%;
        }

        .dataframe th, .dataframe td {
            border: 5px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main app
    st.markdown('<div class="title">Farm Management </div>', unsafe_allow_html=True)

    # Sidebar with navigation
    sidebar = st.sidebar
    sidebar.markdown('<div class="header"></div>', unsafe_allow_html=True)
    tab = sidebar.radio("Choose a Tab", ["Livestock Records", "Expenses Costs", "Rain Gauge Measurement", "Monthly Records", "Document Upload", "Log History"])

    # Livestock Records Tab
    if tab == "Livestock Records":
        st.markdown('<div class="header">Livestock Records</div>', unsafe_allow_html=True)
        livestock_type = st.selectbox("Livestock Type", ["Cow", "Goat", "Sheep", "Chicken"])
        quantity = st.number_input("Quantity", min_value=1)
    
        if st.button("Add Livestock Record"):
            conn = sqlite3.connect("farm_management.db")
            cursor = conn.cursor()
            date_added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO livestock (type, quantity, date_added) VALUES (?, ?, ?)",
                        (livestock_type, quantity, date_added))
            conn.commit()
            conn.close()
        
            # Log the activity
            log_activity("Add Livestock Record", f"Added {quantity} {livestock_type}(s).")
            st.success("Livestock record added successfully!")

    # Expenses/Costs Tab
    elif tab == "Expenses Costs":
        st.markdown('<div class="header">Expenses/Costs</div>', unsafe_allow_html=True)

        # Input for date
        expense_date = st.date_input("Select Expense Date", datetime.now())
    
        # Input fields for amounts and descriptions
        new_amount = st.number_input("Enter Amount (R)", min_value=0.0, format="%.2f", key="amount_input")
        description = st.text_input("Description of Expense")

        # Button to add the amount and description to the list
        if st.button("Add Expense"):
            if new_amount > 0 and description:
                # Insert expense into the database
                conn = sqlite3.connect("farm_management.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO expenses (description, amount, date) VALUES (?, ?, ?)",
                           (description, new_amount, expense_date.strftime('%Y-%m-%d')))
                conn.commit()
                conn.close()
            
                # Log the activity
                log_activity("Add Expense", f"Added expense: {description} for R{new_amount:.2f}.")
                st.success("Expense added successfully!")
            
                # Reset the input fields
                new_amount = 0.0
                description = ""

    # Rain Gauge Measurement Tab
    elif tab == "Rain Gauge Measurement":
        st.markdown('<div class="header">Rain Gauge Measurement</div>', unsafe_allow_html=True)
        rain_date = st.date_input("Select Rainfall Date", datetime.now())
        rainfall = st.number_input("Enter Rainfall Measurement (mm)", min_value=0.0, format="%.2f")

        if st.button("Add Rainfall Record"):
            conn = sqlite3.connect("farm_management.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO rainfall (measurement, date) VALUES (?, ?)", 
                        (rainfall, rain_date.strftime('%Y-%m-%d')))
            conn.commit()
            conn.close()

            # Log the activity
            log_activity("Add Rainfall Record", f"Recorded rainfall of {rainfall} mm on {rain_date}.")
            st.success("Rainfall record added successfully!")

    # Monthly Records Tab
    elif tab == "Monthly Records":
        st.markdown('<div class="header">Monthly Records</div>', unsafe_allow_html=True)

        # Livestock Records Section
        st.subheader("Livestock Records")
        livestock_df = view_table("livestock")

        # Ensure the date is in datetime format and create month_year column
        livestock_df['month_year'] = pd.to_datetime(livestock_df['date_added']).dt.to_period('M')

        # Group by month_year and livestock type, summing quantities
        monthly_livestock = livestock_df.groupby(['month_year', 'type']).agg({
            'quantity': 'sum'
        }).reset_index()

        for month in monthly_livestock['month_year'].unique():
            with st.expander(f"Livestock Records for {month}"):
                month_data = monthly_livestock[monthly_livestock['month_year'] == month][['month_year', 'type', 'quantity']]
                st.dataframe(month_data)

        # Expenses Records Section
        st.subheader("Expenses Records")
        expenses_df = view_table("expenses")

        # Ensure all dates are in the correct format by adding '-01' if they are in 'year-month' format
        expenses_df['date'] = expenses_df['date'].apply(lambda x: x + "-01" if len(x.split('-')) == 2 else x)

        # Convert the 'date' column to datetime format
        try:
            expenses_df['date'] = pd.to_datetime(expenses_df['date'], errors='raise')
        except Exception as e:
            st.error(f"Error while converting dates: {e}")
            st.stop()  # Stop further processing if there's an issue with the dates

        # Create month-year period
        expenses_df['month_year'] = expenses_df['date'].dt.to_period('M')

        # Group by month_year and aggregate by summing amounts
        monthly_expenses = expenses_df.groupby('month_year').agg({'amount': 'sum'}).reset_index()

        for month in monthly_expenses['month_year'].unique():
            with st.expander(f"Expenses Records for {month}"):
                month_data = expenses_df[expenses_df['month_year'] == month][['month_year', 'description', 'amount']]
                st.dataframe(month_data)

    # Document Upload Tab
    elif tab == "Document Upload":
        st.markdown('<div class="header">Document Upload</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Choose files to upload", accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.write(f"Uploaded file: {uploaded_file.name}")

    # Log History Tab
    elif tab == "Log History":
        st.markdown('<div class="header">Log History</div>', unsafe_allow_html=True)
        log_df = view_log_history()
        st.dataframe(log_df)



