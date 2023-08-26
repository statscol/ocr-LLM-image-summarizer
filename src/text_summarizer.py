import langchain
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent,initialize_agent
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
#from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from dotenv import load_dotenv
from config import OPEN_AI_MODEL_NAME,DEBUG_MODE_LLM
from image_processor import ImageProcessor

langchain.debug = DEBUG_MODE_LLM
load_dotenv()

#img preproc and ocr helper
processor=ImageProcessor()
system_message = SystemMessage(content="""You are an expert invoice, receipt summarizer, you're supposed to analyze every text in english or spanish and return data like restaurant name, items or products bought and its price as well as the total amount, however you cannot read images so you must use a tool to convert and image to text""")


#initial system prompt
prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)

#define LLM to use
llm = ChatOpenAI(temperature=0.1, model=OPEN_AI_MODEL_NAME,)

#tools to use as functions to trigger from the llm
tools = [
    ImageProcessor()
]

#memory placeholder
# conversational_memory = ConversationBufferWindowMemory(
#     memory_key='chat_history',
#     k=5,
#     return_messages=True
# )


agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
}
conversational_memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

llm = ChatOpenAI(
    temperature=0,
    model_name=OPEN_AI_MODEL_NAME
)

agent = initialize_agent(
    agent=AgentType.OPENAI_FUNCTIONS,
    tools=tools,
    llm=llm,
    max_iterations=10,
    verbose=False,
    memory=conversational_memory,
    agent_kwargs=agent_kwargs,
    prompt=prompt
)

##TO DO, Remove agent and test sequential chain

if __name__=="__main__":
    
    image_path = "images/raw/invoice0.jpg"
    user_question = "Hello, could you please tell me what products were bought in this receipt i'm attaching? return a python dictionary with all you find"
    response = agent.run(f'{user_question}, here is the image path: {image_path}')
    print(response)
    ##testing memory
    response=agent.run("could you tell me what was the most expensive item in the last receipt?")
    print(response)
