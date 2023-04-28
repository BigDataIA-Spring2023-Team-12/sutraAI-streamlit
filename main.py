import streamlit as st
import os
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import Flow
from _utils import get_file_text, get_creds_service, get_google_code, generative_search

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"




def main():
    md_text = '''
    # 🚀 SutraAI: Building a Smart Query Tool for Querying Multiple Documents 📚
     
     👋 In today's world, there is a lot of textual data present in various formats, and accessing the required information from this data can be a challenging task. The proposed project aims to build a 🔍 smart query tool that can query multiple documents and retrieve the relevant information based on user input queries. 
    '''

    # Set page title and layout
    st.set_page_config(page_title="SutraAI")

    # create_users_table()
    st.markdown(md_text)
    st.header("Connect to Google Drive 📁")

    if st.button("Authorize 🔑"):
        get_google_code()
    
    code  = st.text_input("Enter Authorization Code 🔑")
    st.header("Upload files! 📤")

    if st.button("Upload Files 📥"):
        creds, service = get_creds_service(code)
        get_file_text(creds,service)

    st.markdown("---")
    st.header("Query Important Information 🕵️‍♀️")

    # Text box for user input
    query = st.text_input("Enter your query here 🔍")

    # Submit button
    if st.button("Search 🔎"):
        generative_search(query)
            
        

    st.markdown("---")


if __name__ == "__main__":
    main()