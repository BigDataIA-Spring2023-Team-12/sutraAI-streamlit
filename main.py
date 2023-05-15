import streamlit as st
import os
from utils import get_file_text, get_creds_service, get_google_code, generative_search

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"




def main():

    # Set page title and layout
    st.set_page_config(page_title="SutraAI")

    st.title("On-site Planning")
    st.header("Query Important Information 🕵️‍♀️")

    # Text box for user input
    query = st.text_input("Enter your query here 🔍")

    # Submit button
    if st.button("Ask"):
        generative_search(query)
            
        

    st.markdown("---")


if __name__ == "__main__":
    main()