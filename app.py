import streamlit as st
import os
import time
import logging
from datetime import datetime
import base64

# Dummy user database
if 'users' not in st.session_state:
    st.session_state['users'] = {
        "user1": "password1",
        "user2": "password2"
    }

# Setup logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Directory to save uploaded files
UPLOAD_DIR = 'uploaded_files'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Function to save uploaded files
def save_uploaded_file(uploaded_file, uploader):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{uploader}_{timestamp}_{uploaded_file.name}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    logging.info(f"File uploaded: {filename} by {uploader}")
    return filepath, filename

# Function to get uploader from filename
def get_uploader_from_filename(filename):
    return filename.split('_')[0]

# Function to display login form
def login_form():
    st.title('Login')
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.session_state['users'] and st.session_state['users'][username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

# Function to display registration form
def registration_form():
    st.title('Register')
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    if st.button("Register"):
        if username in st.session_state['users']:
            st.error("Username already exists")
        else:
            st.session_state['users'][username] = password
            st.success("Registration successful! Please login.")

# Function to generate a shareable link
def generate_shareable_link(filename):
    link = f"{st.secrets['base_url']}?file={base64.urlsafe_b64encode(filename.encode()).decode()}"
    return link

# Streamlit app UI
st.title('File Sharing Platform')

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_or_register = st.radio("Login or Register", ('Login', 'Register'))
    if login_or_register == 'Login':
        login_form()
    else:
        registration_form()
else:
    st.write(f"Logged in as {st.session_state['username']}")
    uploader = st.session_state['username']
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a file (any type)", type=None)
    if uploaded_file is not None:
        if uploaded_file.size > 1 * 1024 * 1024 * 1024:  # 1GB limit
            st.error("File size exceeds 1GB limit")
        else:
            file_path, filename = save_uploaded_file(uploaded_file, uploader)
            shareable_link = generate_shareable_link(filename)
            st.success(f"File uploaded successfully: {file_path}")
            st.write(f"Shareable link: [Download {filename}]({shareable_link})")

    # Display uploaded files with download option
    st.subheader("Uploaded Files")
    files = os.listdir(UPLOAD_DIR)
    if not files:
        st.write("No files available.")
    else:
        for filename in files:
            file_path = os.path.join(UPLOAD_DIR, filename)
            uploader_from_file = get_uploader_from_filename(filename)
            st.write(f"**{filename}** (uploaded by {uploader_from_file})")
            if st.download_button(
                label="Download",
                data=open(file_path, 'rb').read(),
                file_name=filename,
            ):
                logging.info(f"File downloaded: {filename} by {uploader}")
                st.write(f"Uploader {uploader_from_file} will be notified of this download.")

    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.experimental_rerun()

# Handling shared link downloads
if 'file' in st.query_params:
    encoded_filename = st.query_params['file'][0]
    filename = base64.urlsafe_b64decode(encoded_filename.encode()).decode()
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        st.write(f"Downloading file: {filename}")
        st.download_button(
            label="Download",
            data=open(file_path, 'rb').read(),
            file_name=filename,
        )
        uploader_from_file = get_uploader_from_filename(filename)
        logging.info(f"File downloaded via link: {filename} by {uploader_from_file}")
    else:
        st.error("File not found!")
