import langchain
from langchain.schema import SystemMessage
from langchain import LLMMathChain, OpenAI
from langchain.agents import Tool, OpenAIFunctionsAgent,initialize_agent
from langchain.agents import AgentType,AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
from langchain.llms import OpenAI
from config import OPEN_AI_MODEL_NAME,DEBUG_MODE_LLM
from image_processor import ImageProcessor
import math

langchain.debug = DEBUG_MODE_LLM
load_dotenv()

#img preproc and ocr helper
processor=ImageProcessor()
system_message = SystemMessage(content="""You are an expert invoice, receipt summarizer, you're supposed to analyze every text in english or spanish and return data like restaurant name, items or products bought and its price as well as the total amount in a dictionary following the same
                                structure, {'item1':value,'item2':value,'total':total_amount}, however you cannot read images""")

#memory placeholder
memory = ConversationBufferMemory(memory_key="chat_history")

#initial system prompt
prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)
#define LLM to use
llm = ChatOpenAI(temperature=0.1, model=OPEN_AI_MODEL_NAME)

#tools to use as functions to trigger from the llm
tools = [
    ImageProcessor()
]

#initialize the gent
conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True
)

llm = ChatOpenAI(
    temperature=0,
    model_name=OPEN_AI_MODEL_NAME
)

agent = initialize_agent(
    agent="chat-conversational-react-description",
    tools=tools,
    llm=llm,
    max_iterations=5,
    verbose=True,
    memory=conversational_memory,
    early_stopping_method='generate',
    prompt=prompt
)

if __name__=="__main__":
    
    image_path = "/mnt/c/Users/jhon.parra/Documents/invoice-llm-summarizer/images/raw/invoice0.jpg"
    user_question = "Hello, could you please tell me what products were bought in this receipt? "
    response = agent.run(f'{user_question}, here is the image path: {image_path}')
    print(response)
    user_question = "What was the most expensive product?"
    response = agent.run(f'{user_question}, here is the image path: {image_path}')
    print(response)