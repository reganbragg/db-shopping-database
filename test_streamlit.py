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

    sql_all_table_names = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
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

st.header("Plotly test")

sql_payments_info = "SELECT * FROM payment_methods;"
try:
    payments_info = query_db(sql_payments_info)
    st.dataframe(payments_info)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

fig = px.choropleth(df, locations='state', locationmode="USA-states", scope="usa")
st.plotly_chart(fig)


# with st.container():
#     st.header("Discounts")

#     widget_col, gap_col, content_col = st.columns([1, 0.2, 4])

#     with widget_col:
#         date1 = st.date_input("Select a date", datetime.date(2022, 1, 1))

#     with content_col:
#         if date1:
#             sql_discounts = f"SELECT i.item_name as Item_Name, i.shop_name as Shop_Name, d.percent as Percent FROM have_discounts d, items_soldin_shops i WHERE (d.item_id, d.shop_id) = (i.id, i.shop_id) AND d.begin_date <= '{date1}' and d.end_date >= '{date1}';"
#             try:
#                 discounts_info = query_db(sql_discounts)
#                 st.dataframe(discounts_info)
#             except:
#                 st.write(
#                     "Sorry! Something went wrong with your query, please try again."
#                 )


# st.header("Query shops")

# sql_shop_names = "SELECT DISTINCT shop_name FROM Items_soldIn_Shops;"
# try:
#     shop_names = query_db(sql_shop_names)["shop_name"].tolist()
#     shop_name = st.selectbox("Choose a shop", shop_names)
# except:
#     st.write("Sorry! Something went wrong with your query, please try again.")

# if shop_name:
#     sql_shop = f"SELECT item_name, item_description, price FROM items_soldin_shops WHERE shop_name ='{shop_name}';"
#     try:
#         items_info = query_db(sql_shop)
#         st.dataframe(items_info)
#     except:
#         st.write(
#             "Sorry! Something went wrong with your query, please try again."
#         )

