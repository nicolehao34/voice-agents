from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor

# load environment variables from .env file
load_dotenv()

llm =ChatOpenAI(model="gpt-4o-mini")
# response = llm.invoke("What is the capital of France?")
# print(response)

# set up a prompt template

# Build response model
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = ChatOpenAI(model="gpt-4o-mini")

# parser allows us to parse the output of the LLM into a structured format defined by our Pydantic model
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# now we can use the parser as a python object!

# now, let's create a prompt template that includes instructions for the LLM to use the parser to format its response correctly

# I want to create a private equity dilliegnce agent that can research a topic and return a structured response with a summary, sources, and tools used in the research process. 
# I will use the PydanticOutputParser to ensure that the LLM's response is formatted correctly according to the ResearchResponse model.

# Specifically, I'm researching the background of a company called "Acme Corp" 
# and I want to know about their history, products, and any recent news. I will use the prompt template to instruct the LLM to provide this information in a structured format.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a research assistant. When given a topic, you will provide a summary, list of sources, and tools used in your research wrap the input in this format and provide no other text: {parser_format}"),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("assistant", "Please provide your response in the following format: {parser_format}")
    ]
).partial(format_instructions=parser.get_format_instructions())

# create a tool calling agent, you can define the tools later
agent = create_tool_calling_agent(
    llm=llm, 
    prompt=prompt, 
    output_parser=parser,
    tools = []
)

# now we can create an agent executor to run the agent
agent_executor = AgentExecutor(agent= agent, tools = [], verbose = True)

# let's run the agent with a query about Acme Corp
raw_response = agent_executor.invoke({"query": "Research the background of Acme Corp, including their history, products, and any recent news.", "client_name":"Nicole"})

print(raw_response)