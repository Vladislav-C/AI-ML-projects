from dotenv import load_dotenv
from pydantic import BaseModel, field_validator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

    @field_validator('summary')
    def summary_not_empty(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Summary must not be empty and should be meaningful")
        return v
    
    @field_validator('sources')
    def sources_not_empty(cls, v):
        if not v:
            raise ValueError("At least one source must be provided")
        return v

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
parser = PydanticOutputParser(pydantic_object=ResearchResponse)
 
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                You are a helpful research assistant. Your goal is to provide accurate, 
                well-researched information on any topic. Use the tools available to you 
                to gather information, and structure your response according to the required format.\n{format_instructions}
            """
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("What can I help you? ")
raw_response = agent_executor.invoke({"query": query})

try:
    structured_response = parser.parse(raw_response.get("output"))
    print("\n===== RESEARCH RESULTS =====")
    print(f"Topic: {structured_response.topic}")
    print(f"Summary: {structured_response.summary}")
    print("\nSources:")
    for source in structured_response.sources:
        print(f"- {source}")
    print("\nTools Used:")
    for tool in structured_response.tools_used:
        print(f"- {tool}")

except Exception as e:
    print("Error parsing response", e, "Raw Response -", raw_response)






