
import os
import streamlit as st


TEMP_DIR_NAME="/tmp/"

def save_uploaded_file(uploadedfile):
     with open(os.path.join(TEMP_DIR_NAME,uploadedfile.name),"wb") as f:
         f.write(uploadedfile.getbuffer())
     return st.success("Saved File:{} to {}".format(uploadedfile.name,TEMP_DIR_NAME))

def reset_chat():
    st.session_state.messages = []

def read_txt_file(path_txt:str):
    with open(path_txt,'r') as f:
        text=" ".join(f.readlines()).strip()
    return text