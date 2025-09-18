# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title('My Parents New Healthy Diner')
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name of Smoothie:')
st.write('The name of your Smoothie will be:', name_on_order)

cnx = st.connection('snowflake')
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients?'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:

    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        st.dataframe(pd_df)
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen].iloc[0]
        # search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH ON'].iloc[0]
        # st.write(search_on)
        st.stop()
      
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    time_to_insert = st.button("Submit Order")
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
      
