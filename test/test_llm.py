from text_summarizer import agent
import os

test_img="test_img.jpg"

class TestLLM:
    def test_llm(self):
        user_question = "Hello, could you please tell me what products were bought in this receipt i'm attaching? return a python dictionary with all you find"
        response = agent.run(f'{user_question}, here is the image path: {os.path.join(os.path.dirname(__file__), test_img)}')
        assert "tequila" in response.lower(),ValueError("Tequila not found in the receipt")