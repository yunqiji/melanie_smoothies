# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session  removed
from snowflake.snowpark.functions import col
import requests
import pandas as pd
# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order=st.text_input('Name on Smoothie')
st.write('The name of your smoothie will be',name_on_order)


#If the line session = get_active_session() appears in your code two times, delete one of the lines. 
cnx = st.connection("snowflake")  ##added for moving from SiS to SniS
session = cnx.session() # old version is get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the snowpark DataFrame to a Panda DataFrame so we can use the LOC function
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect('Choose up to 5 ingredients:'
                                  ,my_dataframe
                                  ,max_selections=5) #maximun 5 selections
   
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen +''
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

    #st.write(ingredients_string) 
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('Submit Order')
    
    #if ingredients_string:
    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(f"Your Smoothie is ordered!, {name_on_order}", icon="✅")



