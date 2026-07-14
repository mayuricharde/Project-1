import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt 
import seaborn as sns
import mysql.connector

# MUST be the very first Streamlit call
st.set_page_config(page_title="My Project BrickView", layout="wide")

# Connect to MySQL
connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Mayuri1997',
    database='BrickView'
)
if connection.is_connected():
    print('connection to MySQL database is Successful.')

# Load ALL tables here at the top so every page can use them
listings_df = pd.read_sql("SELECT * FROM listings", connection)
listings_df.columns = listings_df.columns.str.lower()  # Normalize all column names to lowercase

# Load ALL tables here at the top so every page can use them
property_df = pd.read_sql("SELECT * FROM property", connection)
property_df.columns = property_df.columns.str.lower()  # Normalize all column names to lowercase

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Project Introduction", "Filter and Explore", "Data Visualization", "CRUD Operation", "SQL Queries"])

sql_categories = {
    "📊 Property & Pricing Analysis": {"What is the average days on market by city"
},
    "⏱️ Sales & Market Performance": {},
    "🧑‍💼 Agent Performance": {},
    "🧍 Buyer & Financing Behavior": {}
}

# -------------------------------------------------------

# Dictionary of queries
queries = {

"1. What is the average listing price by city?": """
SELECT
    City,
    ROUND(AVG(Price), 2) AS avg_listing_price
FROM listings
WHERE Price IS NOT NULL
GROUP BY City
ORDER BY avg_listing_price DESC;
""",

"2. What is the average price per square foot by property type?": """
SELECT
    Property_Type,
    ROUND(AVG(Price / Sqft), 2) AS avg_price_per_sqft
FROM listings
WHERE Price IS NOT NULL
AND Sqft IS NOT NULL
AND Sqft > 0
GROUP BY Property_Type
ORDER BY avg_price_per_sqft DESC;
""",

"3. How does furnishing status impact property prices?": """
SELECT
    p.furnishing_status,
    AVG(l.Price) AS avg_price
FROM listings l
JOIN property p
ON l.Listing_ID = p.listing_id
GROUP BY p.furnishing_status;
""",

"4. Do properties closer to metro stations command higher prices?": """
SELECT
    CASE
        WHEN p.metro_distance_km <= 1 THEN 'Near Metro'
        ELSE 'Far from Metro'
    END AS near_metro,
    AVG(l.Price) AS avg_price
FROM listings l
JOIN property p
ON l.Listing_ID = p.listing_id
GROUP BY
    CASE
        WHEN p.metro_distance_km <= 1 THEN 'Near Metro'
        ELSE 'Far from Metro'
    END;
""",

"5. Are rented properties priced differently from non-rented ones?": """
SELECT
    CASE
        WHEN p.is_rented = 1 THEN 'Rented'
        ELSE 'Not Rented'
    END AS rental_status,
    AVG(l.Price) AS avg_price
FROM listings l
JOIN property p
ON l.Listing_ID = p.listing_id
GROUP BY p.is_rented;
""",

"6. How do bedrooms and bathrooms affect pricing?": """
SELECT
    p.bedrooms,
    p.bathrooms,
    AVG(l.Price) AS avg_price
FROM listings l
JOIN property p
ON l.Listing_ID = p.listing_id
GROUP BY p.bedrooms, p.bathrooms;
""",

"7. Do properties with parking and power backup sell at higher prices?": """
SELECT
    p.parking_available,
    p.power_backup,
    AVG(l.Price) AS avg_price
FROM listings l
JOIN property p
ON l.Listing_ID = p.listing_id
GROUP BY p.parking_available, p.power_backup;
""",

"8. How does year built influence listing price?": """
SELECT
    p.year_built,
    AVG(l.Price) AS avg_price
FROM listings l
JOIN property p
ON l.Listing_ID = p.listing_id
GROUP BY p.year_built;
""",

"9. Which cities have the highest average property prices?": """
SELECT
    City,
    AVG(Price) AS avg_price
FROM listings
GROUP BY City
ORDER BY avg_price DESC;
""",

"10. How are properties distributed across price buckets?": """
SELECT
    CASE
        WHEN Price <= 3000000 THEN '0-30L'
        WHEN Price <= 5000000 THEN '30L-50L'
        WHEN Price <= 7000000 THEN '50L-70L'
        WHEN Price <= 9000000 THEN '70L-90L'
        ELSE '90L+'
    END AS price_range,
    COUNT(*) AS property_count
FROM listings
GROUP BY
    CASE
        WHEN Price <= 3000000 THEN '0-30L'
        WHEN Price <= 5000000 THEN '30L-50L'
        WHEN Price <= 7000000 THEN '50L-70L'
        WHEN Price <= 9000000 THEN '70L-90L'
        ELSE '90L+'
    END
ORDER BY property_count DESC;
""",
    
"11. What is the average days on market by city?": """
SELECT
    l.City,
    AVG(s.Days_on_Market) AS avg_days_on_market
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
GROUP BY l.City;
""",

"12. Which property types sell the fastest?": """
SELECT
    l.Property_Type,
    AVG(s.Days_on_Market) AS avg_days_on_market
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
GROUP BY l.Property_Type
ORDER BY avg_days_on_market ASC;
""",

"13. What percentage of properties are sold above listing price?": """
SELECT
    (SUM(CASE
        WHEN s.Sale_Price > l.Price THEN 1
        ELSE 0
    END) * 100.0) / COUNT(*) AS percentage_higher_than_list_price
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID;
""",

"14. What is the sale-to-list price ratio by city?": """
SELECT
    l.City,
    AVG(s.Sale_Price / l.Price) * 100 AS avg_price_ratio_percentage
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
GROUP BY l.City;
""",

"15. What percentage of properties stayed on the market for more than 90 days by city?": """
SELECT
    l.City,
    AVG(
        CASE
            WHEN s.Days_on_Market > 90 THEN 1
            ELSE 0
        END
    ) * 100 AS percentage_above_90_days
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
GROUP BY l.City;
""",

"16. Which listings took more than 90 days to sell?": """
SELECT
    l.*,
    s.Days_on_Market,
    s.Sale_Price,
    s.Date_Sold
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
WHERE s.Days_on_Market > 90;
""",

"17. How does metro distance affect time on market?": """
SELECT
    p.metro_distance_km,
    AVG(s.Days_on_Market) AS avg_days_on_market
FROM property p
JOIN sales s
ON p.listing_id = s.Listing_ID
GROUP BY p.metro_distance_km
ORDER BY p.metro_distance_km;
""",

"18. What is the monthly sales trend?": """
SELECT
    DATE_FORMAT(Date_Sold, '%Y-%m') AS month,
    COUNT(*) AS total_sales
FROM sales
GROUP BY DATE_FORMAT(Date_Sold, '%Y-%m')
ORDER BY month;
""",

"19. Which properties are currently unsold?": """
SELECT *
FROM listings
WHERE Listing_ID NOT IN (
    SELECT Listing_ID
    FROM sales
);
""",

"20. Which agents have closed the most sales?": """
SELECT
    a.Name,
    COUNT(*) AS total_sales
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
JOIN agents a
ON l.Agent_ID = a.Agent_ID
GROUP BY a.Name
ORDER BY total_sales DESC;
""",
"21. Who are the top agents by total sales revenue?": """
SELECT
    a.Name,
    SUM(s.Sale_Price) AS total_sales_revenue
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
JOIN agents a
ON l.Agent_ID = a.Agent_ID
GROUP BY a.Name
ORDER BY total_sales_revenue DESC;
""",

"22. Which agents close deals fastest?": """
SELECT
    a.Name,
    AVG(s.Days_on_Market) AS avg_days_on_market
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
JOIN agents a
ON l.Agent_ID = a.Agent_ID
GROUP BY a.Name
ORDER BY avg_days_on_market ASC;
""",

"23. Does experience correlate with deals closed?": """
SELECT
    experience_years,
    deals_closed
FROM agents
ORDER BY experience_years DESC;
""",

"24. Do agents with higher ratings close deals faster?": """
SELECT
    a.Agent_ID,
    a.Name,
    a.rating,
    AVG(s.Days_on_Market) AS avg_days_on_market
FROM sales s
JOIN listings l
ON s.Listing_ID = l.Listing_ID
JOIN agents a
ON l.Agent_ID = a.Agent_ID
GROUP BY a.Agent_ID, a.Name, a.rating
ORDER BY a.rating DESC;
""",

"25. What is the average commission earned by each agent?": """
SELECT
    Name,
    commission_rate
FROM agents;
""",

"26. Which agents currently have the most active listings?": """
SELECT
    a.Name,
    COUNT(*) AS total_active_listings
FROM listings l
JOIN agents a
ON l.Agent_ID = a.Agent_ID
GROUP BY a.Name
ORDER BY total_active_listings DESC;
""",

"27. What percentage of buyers are investors vs end users?": """
SELECT
    buyer_type,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM buyers) AS percentage
FROM buyers
GROUP BY buyer_type;
""",

"28. Which cities have the highest loan uptake rate?": """
SELECT
    l.City,
    AVG(b.loan_taken) * 100 AS loan_uptake_percentage
FROM buyers b
JOIN sales s
ON b.sale_id = s.sale_id
JOIN listings l
ON s.Listing_ID = l.Listing_ID
GROUP BY l.City
ORDER BY loan_uptake_percentage DESC;
""",

"29. What is the average loan amount by buyer type?": """
SELECT
    buyer_type,
    AVG(loan_amount) AS avg_loan_amount
FROM buyers
GROUP BY buyer_type;
""",

"30. Which payment mode is most commonly used?": """
SELECT
    payment_mode,
    COUNT(*) AS total_count
FROM buyers
GROUP BY payment_mode
ORDER BY total_count DESC;
"""

}
# PAGE 1: Project Introduction
# -------------------------------------------------------
if page == "Project Introduction":
    st.title("My Project BrickView")
    st.write("Real-time stats coming here")
    x = st.slider("Pick a number", 0, 100)
    st.write("You picked", x)
    st.subheader("📊 A Streamlit App for Exploring the Real Estate Market")
    st.write("""
    This project analyzes real estate market data using a MySQL database. The real estate market is vast
    and dynamic, with properties being listed, sold, and evaluated every day. Buyers, sellers, and agents
    often lack accessible tools to monitor trends, pricing, and sales performance. This project aims to
    build a Real Estate Listings Dashboard that uses SQL and Streamlit to:

    1. Analyze property listings, agent performance, and sales patterns
    2. Provide insights into pricing, time on market, and property types
    3. Enable filtering by location, property type, price, and sales agent
    4. Display interactive visuals like maps and bar charts for better understanding

    **Business Use Cases**
    1. Assist buyers and investors in making data-informed decisions
    2. Help agents track sales performance and property types in demand
    3. Understand pricing trends across regions and neighborhoods
    4. Monitor time-on-market trends to improve sales strategies
    """)
    st.write(listings_df)
    st.write(property_df)

# -------------------------------------------------------
# PAGE 2: Filter and Explore
# -------------------------------------------------------
elif page == "Filter and Explore":
    st.title("🔴 Filters & Property Explorer")

    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.selectbox("City", ["All"] + sorted(listings_df["city"].dropna().unique().tolist()))
    with col2:
        property_type = st.selectbox("Property Type", ["All"] + sorted(listings_df["property_type"].dropna().unique().tolist()))
    with col3:
        min_price = int(listings_df["price"].min())
        max_price = int(listings_df["price"].max())
        price_range = st.slider("Price Range ($)", min_price, max_price, (min_price, max_price))

    col4, col5 = st.columns(2)
    with col4:
        listed_from = st.date_input("Listed From", value=pd.to_datetime(listings_df["date_listed"]).min())
    with col5:
        listed_to = st.date_input("Listed To", value=pd.to_datetime(listings_df["date_listed"]).max())

    filtered_df = listings_df.copy()
    # Merge listings with property attributes
    filtered_df= pd.merge(
        listings_df,
        property_df,
        on="listing_id",
        how="inner"
    )
    if city != "All":
        filtered_df = filtered_df[filtered_df["city"] == city]
    if property_type != "All":
        filtered_df = filtered_df[filtered_df["property_type"] == property_type]
    filtered_df = filtered_df[
        (filtered_df["price"] >= price_range[0]) & (filtered_df["price"] <= price_range[1])
    ]
    filtered_df["date_listed"] = pd.to_datetime(filtered_df["date_listed"])
    filtered_df = filtered_df[
        (filtered_df["date_listed"] >= pd.to_datetime(listed_from)) &
        (filtered_df["date_listed"] <= pd.to_datetime(listed_to))
    ]
    results_found = len(filtered_df)
    if results_found > 0:
        avg_price = int(filtered_df["price"].mean())
        avg_sqft = int(filtered_df["sqft"].mean())
        avg_bedrooms = round(filtered_df["bedrooms"].mean(), 1)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Results Found", f"{results_found:,}")
        with m2:
            st.metric("Avg Price", f"${avg_price:,}")
        with m3:
            st.metric("Avg Sqft", f"{avg_sqft:,} sq ft")
        with m4:
            st.metric("Avg Bedrooms", f"{avg_bedrooms}")
    else:
        st.warning("No results found for the selected filters.")

    st.markdown("---")
    st.dataframe(filtered_df, use_container_width=True)

# PAGE 3 : Data Visulaization

elif page == "Data Visualization":
     st.title("📊 Analytics & Visualizations")
    
     col1, col2 = st.columns(2)

    # Property Listings Map
     with col1:
         st.subheader("🗺️ Property Listings Map")
         map_query = """
         SELECT latitude, longitude, property_type
         FROM listings
         WHERE latitude IS NOT NULL
         AND longitude IS NOT NULL;
         """


         map_df = pd.read_sql(map_query, connection)

         fig = px.scatter_mapbox(
            map_df,
            lat="latitude",
            lon="longitude",
            color="property_type",
            zoom=3,
            height=500
         )

         fig.update_layout(mapbox_style="carto-darkmatter")
         st.plotly_chart(fig, use_container_width=True)

     # Average Price by City
     with col2:
         st.subheader("🏙️ Average Price by City")
         avg_query = """
         SELECT city,
                AVG(price) AS avg_price,
                COUNT(*) AS total_listings
         FROM listings
         GROUP BY city
         ORDER BY avg_price DESC;
         """
         avg_df = pd.read_sql(avg_query, connection)
         fig = px.bar(
             avg_df,
             x="city",
             y="avg_price",
             text="total_listings",
             color="city"
         )

         st.plotly_chart(fig, use_container_width=True)
         
     #🏠 Property Type Distribution  

     with col1:
         st.subheader("🏠 Property Type Distribution")
         property_query = """
         SELECT
           property_type,
           COUNT(*) AS total_properties
         FROM listings
         GROUP BY property_type
         ORDER BY total_properties DESC;
         """
         property_df = pd.read_sql(property_query, connection)

         fig = px.pie(
             property_df,
             names="property_type",
             values="total_properties",
             hole=0.5
         )
         st.plotly_chart(fig, use_container_width=True)

     with col2:
         st.subheader("🗓️ Monthly Sales & Listings Trend")
         trend_query = """
         SELECT
             MONTHNAME(Date_Sold) AS Month,
             MONTH(Date_Sold) AS Month_No,
             COUNT(Listing_ID) AS Total_Sales
         FROM sales
         GROUP BY MONTH(Date_Sold), MONTHNAME(Date_Sold)
         ORDER BY Month_No;
         """
         trend_df = pd.read_sql(trend_query, connection)

         fig = px.line(
             trend_df,
             x="Month",
             y="Total_Sales",
             markers=True
         )
         fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Sales Count"
         )
         st.plotly_chart(fig, use_container_width=True)


     with col1:
          st.subheader("🏆 Top 10 Agents by Deals Closed")
          agent_query = """
          SELECT
              Agent_ID,
              Name,
             deals_closed,
             rating
          FROM agents
          ORDER BY deals_closed DESC
          LIMIT 10;
          """
          agent_df = pd.read_sql(agent_query, connection)

          fig = px.bar(
              agent_df,
              x="deals_closed",
              y="Name",
              orientation="h",
              color="rating",
              text="deals_closed",
              color_continuous_scale="RdYlGn"
          )

          fig.update_layout(
              xaxis_title="Deals Closed",
              yaxis_title="Agent",
              yaxis=dict(categoryorder="total ascending")
          )

          st.plotly_chart(fig, use_container_width=True)

     with col2:
          st.subheader("💳 Buyer Payment Mode Distribution")
          payment_query = """
          SELECT
             payment_mode,
             buyer_type,
             COUNT(*) AS total_buyers
          FROM buyers
          GROUP BY payment_mode, buyer_type
          ORDER BY payment_mode;
          """
          payment_df = pd.read_sql(payment_query, connection)
          fig = px.bar(
              payment_df,
              x="payment_mode",
              y="total_buyers",
              color="buyer_type",
              barmode="group",
              text="total_buyers"
          )

          fig.update_layout(
              xaxis_title="Payment Mode",
              yaxis_title="Number of Buyers"
          )

          st.plotly_chart(fig, use_container_width=True)

# Page 4 - CRUD Operation

elif page == "CRUD Operation":

    st.title("📕 CRUD Operations")
    st.write("Create, Read, Update, and Delete records across all database tables.")

    # Select Table
    table = st.selectbox(
        "📋 Select Table",
        ["listings", "agents", "buyers", "sales", "property"]
    )

    primary_keys = {
        "agents": "agent_id",
        "listings": "listing_id",
        "buyers": "buyer_id",
        "sales": "sale_id",
        "property": "property_id"
    }

    pk = primary_keys[table]

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["👁️ View", "➕ Add", "✏️ Update", "🗑️ Delete"]
    )

    # =========================
    # VIEW
    # =========================
    with tab1:

        rows = st.slider("Rows to display", 10, 500, 50)

        query = f"""
        SELECT *
        FROM {table}
        LIMIT {rows}
        """

        df = pd.read_sql(query, connection)

        st.dataframe(
            df,
            use_container_width=True
        )

    # =========================
    # ADD
    # =========================
    with tab2:

        st.subheader("➕ Add Record")

        cols_query = f"SHOW COLUMNS FROM {table}"
        cols_df = pd.read_sql(cols_query, connection)

        form_data = {}

        col1, col2, col3 = st.columns(3)

        for i, column in enumerate(cols_df["Field"]):

            if i % 3 == 0:
                with col1:
                    form_data[column] = st.text_input(
                        column,
                        key=f"add_{column}"
                    )

            elif i % 3 == 1:
                with col2:
                    form_data[column] = st.text_input(
                        column,
                        key=f"add_{column}"
                    )

            else:
                with col3:
                    form_data[column] = st.text_input(
                        column,
                        key=f"add_{column}"
                    )

        if st.button("✅ Insert Record"):

            columns = ",".join(form_data.keys())
            placeholders = ",".join(["%s"] * len(form_data))

            sql = f"""
            INSERT INTO {table}
            ({columns})
            VALUES ({placeholders})
            """

            cursor = connection.cursor()

            cursor.execute(
                sql,
                tuple(form_data.values())
            )

            connection.commit()

            st.success("Record inserted successfully!")

            st.rerun()

    # =========================
    # UPDATE
    # =========================
    with tab3:

        st.subheader("✏️ Update Record")

        record_id = st.text_input(
            f"Primary Key ({pk})",
            key="update_pk"
        )

        if record_id:

            query = f"""
            SELECT *
            FROM {table}
            WHERE {pk}=%s
            """

            df = pd.read_sql(
                query,
                connection,
                params=(record_id,)
            )

            if not df.empty:

                st.success("Record Found")

                updated_data = {}

                cols = st.columns(3)

                count = 0

                for column in df.columns:

                    if column == pk:
                        continue

                    with cols[count % 3]:
                        updated_data[column] = st.text_input(
                            column,
                            str(df.iloc[0][column]),
                            key=f"update_{column}"
                        )

                    count += 1

                if st.button("✏️ Update Record"):

                    set_clause = ", ".join(
                        [f"{col}=%s" for col in updated_data.keys()]
                    )

                    values = list(updated_data.values())
                    values.append(record_id)

                    sql = f"""
                    UPDATE {table}
                    SET {set_clause}
                    WHERE {pk}=%s
                    """

                    cursor = connection.cursor()

                    cursor.execute(
                        sql,
                        values
                    )

                    connection.commit()

                    st.success("Record Updated Successfully!")

                    st.rerun()

            else:
                st.error("Record not found")

    # =========================
    # DELETE
    # =========================
    with tab4:

        st.subheader("🗑️ Delete Record")

        st.warning(
            "⚠️ Deletion is permanent and cannot be undone."
        )

        record_id = st.text_input(
            f"Primary Key ({pk}) to delete",
            key="delete_pk"
        )

        if record_id:

            query = f"""
            SELECT *
            FROM {table}
            WHERE {pk}=%s
            """

            df = pd.read_sql(
                query,
                connection,
                params=(record_id,)
            )

            if not df.empty:

                st.dataframe(
                    df,
                    use_container_width=True
                )

                if st.button("🗑️ Delete Record"):

                    sql = f"""
                    DELETE FROM {table}
                    WHERE {pk}=%s
                    """

                    cursor = connection.cursor()

                    cursor.execute(
                        sql,
                        (record_id,)
                    )

                    connection.commit()

                    st.success(
                        "Record Deleted Successfully!"
                    )

                    st.rerun()

            else:
                st.error("Record not found")

                
# Page 4 - SQL Queries
# Streamlit Page
elif page == "SQL Queries":

    st.title("🔍 SQL Queries Explorer")
    st.write("Select any problem statement (1-30) to run the corresponding SQL query.")

    # Dropdown
    task = st.selectbox("Choose Task", list(queries.keys()))

    # Run button
    if st.button("Run Query"):
        query = queries[task]
        df = pd.read_sql(query, connection)

        st.dataframe(df, use_container_width=True)
    


            