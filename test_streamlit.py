import pandas as pd
import psycopg2
import streamlit as st
import datetime
from configparser import ConfigParser
import plotly.express as px


@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df



st.title('Shopping Database')

with st.expander("Explore the data"):
    st.markdown(":memo: Tables")

    sql_all_table_names = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)' ORDER BY relname;"
    try:
        all_table_names = query_db(sql_all_table_names)["relname"].tolist()
        table_name = st.selectbox("Choose a table below:", all_table_names)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if table_name:
        f"Display the table"

        sql_table = f"SELECT * FROM {table_name};"
        try:
            df = query_db(sql_table)
            st.dataframe(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

# Discount button
discount_radio = st.radio('Do you want to see discounted items?', ('Yes', 'No'), horizontal=True)


sql_customer_ages = f"""
                    SELECT date_part('year', AGE(m.dob)) as age, COUNT(*) as count
                    FROM orders_ordered o, members m
                    WHERE m.loyalty_number = o.loyalty_number
                    GROUP BY age
                    ORDER BY age;"""

try:
    df = query_db(sql_customer_ages)
    fig = px.line(df, x='age', y='count', markers=True)
    st.plotly_chart(fig, use_container_width = True)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")


