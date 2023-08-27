import sys
sys.path.append("../src")
import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
import numpy as np
from PIL import Image
from app_utils import TEMP_DIR_NAME,save_uploaded_file,reset_chat
import os
from pathlib import Path
from text_summarizer import agent,processor

BOT_DEFAULT_MSG="Hello 👋 I'm a test AI assistant to help you with your questions about an input file, or feel free to ask me anything"
st.set_page_config(page_title="Invoice|Receipt LLM Summarizer",layout='wide',page_icon=":shark:")

#placeholders for temporal image path and an image processor in case we want to read img text separately
IMAGE_TMP_PATH=None
PROCESSOR=processor
img_text=""

with st.sidebar:

    st.markdown(
        f"<h1 style='text-align: center;'> Invoice|Receipt LLM Summarizer using OpenCV+Tesseract+LLM</h1><br><br>",
        unsafe_allow_html=True
    )
    input_image = st.file_uploader(label='Receipt|Invoice Image',help="Upload an image",type=['jpg','png','jpeg'])

    if input_image is not None:
        save_uploaded_file(input_image)
        IMAGE_TMP_PATH=os.path.join(TEMP_DIR_NAME,input_image.name)
        st.markdown(f"<h1 style='text-align: center;'> Image Uploaded and saved<br>",unsafe_allow_html=True)
        st.image(Image.open(IMAGE_TMP_PATH))
        st.markdown("***")
        inject_text=st.checkbox(label="Inject OCR output",value=False,help="Injects text found in the image without using the agent Action (Speeds response)")
        if inject_text:
            img_text=PROCESSOR.run(IMAGE_TMP_PATH)


    st.markdown("***")
    st.button("Reset Chat History", type="secondary", on_click=reset_chat,use_container_width=True)
    _,col_c,_=st.columns(3)
    with col_c:
        st.markdown("[![Foo](https://img.icons8.com/material-outlined/96/000000/github.png)](https://github.com/statscol/invoice-llm-summarizer)")


# Initialize chat history based on streamlit doc for chat applications https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": BOT_DEFAULT_MSG})


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Write a message to the AI assistant | Escribe un mensaje para el asistente de IA"):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    prompt_ad=f'{prompt}, img path: {IMAGE_TMP_PATH}' if (input_image is not None and not inject_text) else f'{prompt} text: {img_text}'
    ##streamlit callback https://python.langchain.com/docs/integrations/callbacks/streamlit
    st_callback = StreamlitCallbackHandler(st.container()) 
    #hotfix to errors
    try:
        response = agent.run(prompt_ad,callbacks=[st_callback])
    except ValueError as e:
        response = "Sorry i could't understand your last question."
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
