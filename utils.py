import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import sqlite3
from datetime import datetime
from load_from_drive import extract_text_from_file
import requests
from bokeh.models.widgets import Div
import webbrowser


# Connect to SQLite database
conn = sqlite3.connect("users.db")
c = conn.cursor()



def get_google_code():
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    flow = Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=scopes,
        redirect_uri="https://bigdataia-spring2023-team-12-sutraai-streamlit-main-soxlc4.streamlit.app/"
    )
    # Generate the authorization URL and redirect the user
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(auth_url, unsafe_allow_html=True)

    

def get_creds_service(code):
    # Get the authorization code from the user and exchange it for an access token
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    flow = Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=scopes,
        redirect_uri="https://bigdataia-spring2023-team-12-sutraai-streamlit-main-soxlc4.streamlit.app/"
    )
    flow.fetch_token(code=code)

    # Use the access token to build a Drive API service instance
    creds = flow.credentials
    service = build('drive', 'v3', credentials=creds)

    return creds, service



def update_latest_refresh():
    """
    Creates or updates a SQLite database named 'latest_refresh.db' with one table named 'refresh_timestamp',
    which stores a single row containing the timestamp of the most recent click on the 'refresh' button in
    a Streamlit application.

    If the 'refresh_timestamp' table does not exist, it is created. If the table already exists, the single
    row it contains is updated with the current timestamp.

    Args:
        None

    Returns:
        None
    """
    # Create connection to database
    conn = sqlite3.connect('latest_refresh.db')
    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute('CREATE TABLE IF NOT EXISTS refresh_timestamp (timestamp TEXT)')

    # Update or insert row with current timestamp
    timestamp = str(datetime.now())
    cursor.execute('SELECT COUNT(*) FROM refresh_timestamp')
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        cursor.execute('INSERT INTO refresh_timestamp (timestamp) VALUES (?)', (timestamp,))
    else:
        cursor.execute('UPDATE refresh_timestamp SET timestamp=?', (timestamp,))
    conn.commit()

    # Close connection
    cursor.close()
    conn.close()


def check_file_id_in_table(email, file_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM file_info WHERE file_id = ? AND email = ?', (file_id, email))
    result = c.fetchone()
    conn.close()
    if result:
        return True
    else:
        return False

def add_user_info(email, file_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO file_info (email, file_id) VALUES (?, ?)', (email, file_id))
    conn.commit()
    conn.close()
    


def get_file_text(creds, drive_service):
    folder_name = "SutraAI"
    # Find the folder ID
    query1 = f"mimeType='application/vnd.google-apps.folder' and trashed = false and name='{folder_name}'" 
    results1 = drive_service.files().list(q=query1).execute().get('files', [])
    if len(results1) == 0:
        print('No folder found with name: %s' % folder_name)
        exit()
    else:
        folder_id = results1[0]['id']
        print('Folder ID: %s' % folder_id)
    # get user email
    about = drive_service.about().get(fields='user(emailAddress)').execute()
    email_address = about['user']['emailAddress']
    # List all files in the folder
    query = "trashed = false and '" + folder_id + "' in parents"
    results = drive_service.files().list(q=query).execute().get('files', [])
    # Print the file names
    for file in results:
        if not check_file_id_in_table(email_address,file['id']):
            text = extract_text_from_file(file['id'],creds)
            # function request to fastapi
            url = "http://54.86.128.1:8000/upsert/"  # Replace with the actual URL of the endpoint
            data = {
                "input_str": f"{text}",
                "filename": f"{file['name']}"
            }
            response = requests.post(url, json=data)

            if response.status_code == 200:
                add_user_info(email_address,file['id'])    
                st.write(file['name'] + " processed!")
            else:
                st.error(f"Error uploading file: {file['name']} ")
        else:
            st.write(f"{file['name']} already uploaded!")
    return "All files uploaded"
    

def generative_search(query):
    url = f'http://54.86.128.1:8000/vec-search/{query}'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        st.write(response.json()["response"])
    else:
        st.error("Error searching query") 


