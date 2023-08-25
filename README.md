# invoice-LLM-summarizer


Invoice| Receipt analyzer using openCV+OCR+LLM 


- Images were obtained from google images
- A preprocessing module was included for images, (binarization, watermark removal)
- Pytesseract is used for as the default OCR engine
- LLM (OpenAI) - LangChain conversational agent which triggers a tool(functions) 


# How to Use

Using a virtual env of your preference with python 3.9+ run the following

```bash
chmod +x setup.sh
pip install -r requirements.txt
```

# Demo

TODO


# Tests

Some unit tests were included, run `pytest` in the root folder.