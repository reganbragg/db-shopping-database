import datetime
import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from configparser import ConfigParser


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


with st.expander("Explore customers' orders"):
    with st.container():
        st.header("Customer Orders")

        widget_col, gap_col, content_col = st.columns([1, 0.2, 3])

        with widget_col:
            sql_customer_info = "SELECT loyalty_number FROM Customers;"
            try:
                customers_info = query_db(sql_customer_info)["loyalty_number"].tolist()
                customer = st.selectbox("Choose a customer", customers_info)
            except:
                st.write("Sorry! Something went wrong with your query, please try again.")

            date1 = st.date_input("Select a begin date", datetime.date(2022, 1, 1))
            date2 = st.date_input("Select a end date", datetime.date(2022, 12, 31))

        with content_col:
            if date1 and date2 and customer:
                if date1 > date2:
                    st.write("Please select an end date that occurs after the begin date.")
                else:
                    sql_orders = f"""
                        SELECT order_id, order_date
                        FROM orders_ordered
                        WHERE loyalty_number = '{customer}'
                        AND order_date >= '{date1}' AND order_date <= '{date2}';"""
                    try:
                        orders = query_db(sql_orders)

                        num_orders = len(orders)
                        if num_orders > 1:
                            subheader_text = "Customer #" + customer + " has placed " + str(num_orders) + " orders"
                        elif num_orders == 1:
                            subheader_text = "Customer #" + customer + " has placed 1 order"
                        else:
                            subheader_text = "Customer #" + customer + " has not placed any orders"
                        st.subheader(subheader_text)

                        for i in range(num_orders):
                            order_id, order_date = orders.iloc[i, 0], orders.iloc[i, 1]
                            sql_order_info = f"""
                                SELECT iss.shop_name, iss.item_name
                                FROM orders_ordered o, shoppingcarts_contain_items sci, items_soldin_shops iss
                                WHERE o.cart_id = sci.cart_id AND (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
                                AND o.order_id = {order_id};"""
                            try:
                                order_info = query_db(sql_order_info)
                                order_string = "Order #" + str(order_id) + ": placed on " + str(order_date)
                                st.subheader(order_string)
                                st.dataframe(order_info)
                            except:
                                st.write("Sorry! Something went wrong with your query, please try again.")
                    except:
                        st.write("Sorry! Something went wrong with your query, please try again.")

with st.expander("Explore where orders are coming from"):
    with st.container():
        st.markdown(":world_map: Where are orders going to?")

        col1, col2, col3 = st.columns([3, 0.5, 3])

        with col1:
            sql_shop_names = "SELECT DISTINCT shop_name FROM items_soldIn_shops;"
            try:
                shop_names = query_db(sql_shop_names)['shop_name'].tolist()
                shop_options = st.multiselect('Choose a shop or multiple shops:', shop_names)
            except:
                st.write("Sorry! Something went wrong with your query, please try again.")

        with col3:
            num_states = st.slider('Select the number of top results you want to view', 1, 5, 1)

        if shop_options and num_states:
            if len(shop_options) > 1:
                shop_options = tuple(shop_options)
                sql_states_info = f"""
                                SELECT o.state as state, COUNT(*) as count
                                FROM orders_ordered o, shoppingcarts_contain_items sci, items_soldIn_shops iss
                                WHERE o.cart_id = sci.cart_id AND (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
                                AND iss.shop_name IN {shop_options}
                                GROUP BY o.state
                                ORDER BY COUNT(*) DESC
                                LIMIT {num_states};"""
            elif len(shop_options) == 1:
                shop = shop_options[0]
                sql_states_info = f"""
                                SELECT o.state as state, COUNT(*) as count
                                FROM orders_ordered o, shoppingcarts_contain_items sci, items_soldIn_shops iss
                                WHERE o.cart_id = sci.cart_id AND (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
                                AND iss.shop_name = '{shop}'
                                GROUP BY o.state
                                ORDER BY COUNT(*) DESC
                                LIMIT {num_states};"""
            try:
                states_info = query_db(sql_states_info)
                fig = px.choropleth(states_info, locations='state', locationmode="USA-states", scope="usa", hover_name = "state", hover_data=["count"], labels={'state': 'State', 'count': '# of Orders'})
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.write("Sorry! Something went wrong with your query, please try again.")
        elif num_states:
            sql_states_info = f"""
                                SELECT o.state as state, COUNT(*) as count
                                FROM orders_ordered o, shoppingcarts_contain_items sci, items_soldIn_shops iss
                                WHERE o.cart_id = sci.cart_id AND (sci.item_id, sci.shop_id) = (iss.id, iss.shop_id)
                                GROUP BY o.state
                                ORDER BY COUNT(*) DESC
                                LIMIT {num_states};"""
            try:
                states_info = query_db(sql_states_info)
                fig = px.choropleth(states_info, locations='state', locationmode="USA-states", scope="usa", hover_name = "state", hover_data=["count"], labels={'state': 'State', 'count': '# of Orders'})
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.write("Sorry! Something went wrong with your query, please try again.")

with st.expander("Explore demographics of our customers"):
    with st.container():
        st.markdown("How old are our customers?")

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
