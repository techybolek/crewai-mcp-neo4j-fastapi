# OPTIONAL -------------------------------
# Using ollama - by default OpenAI is used
# Remove / comment this block if using OpenAI
# from crewai import LLM
# from langchain_community.chat_models import ChatOpenAI

# llm = ChatOpenAI(
#     model="ollama/qwen3:latest",
#     base_url="http://localhost:11434",
#     streaming=True
# )
# ----------------------------------------

from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from langfuse import Langfuse
from langfuse.openai import openai  # LangFuse's OpenAI wrapper
import os
from dotenv import load_dotenv

# Initialize LangFuse (optional tracing)
load_dotenv()

langfuse_client = None

if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
    # Initialize LangFuse client  
    langfuse_client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
    # Configure OpenAI with LangFuse tracing - this is the key!
    openai.langfuse_auth_check()
    print("LangFuse tracing enabled")
else:
    print("LangFuse tracing disabled - set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable")

# Create a StdioServerParameters object
neo4j_server_params=[
    StdioServerParameters(
        command="uvx", 
        args=["mcp-neo4j-cypher"],
        env=os.environ,
    )
]

#make sure DB_SERVER, DB_USER and DB_PASSWORD are defined
if not os.getenv("DB_SERVER") or not os.getenv("DB_USER") or not os.getenv("DB_PASSWORD"):
    raise ValueError("DB_SERVER, DB_USER and DB_PASSWORD must be defined")

# Create a StdioServerParameters object


# Create a StdioServerParameters object
mssql_server_params=[
    StdioServerParameters(
        command="npx", 
        args=["mcp-mssql-server"],
        env=os.environ,
    )
]

server_params = mssql_server_params

# Simple logging callbacks
def log_step_callback(output):
    print(f"""
        Step completed!
        details: {output.__dict__}
    """)

def log_task_callback(output):
    print(f"""
        Task completed!
        details: {output.__dict__}
    """)

#read the rules from .ai/mssql-server.mdc
with open('.ai/mssql-server.mdc', 'r') as file:
    mssql_rules = file.read()

print(mssql_rules)

# Create and run Crew
def run_crew_query(query: str):

    with MCPServerAdapter(server_params) as tools:
    
        print(f"Available tools from Stdio MCP server: {[tool.name for tool in tools]}")

        analyst_agent = Agent(
            role="Local Data Processor",
            goal="Process data using a local Stdio-based tool.",
            backstory="An AI that leverages local scripts via MCP for specialized tasks.",
            tools=tools,
            reasoning=False,
            verbose=False,
            step_callback=log_step_callback,
        )
        
        processing_task_neo4j = Task(
            description="""Process the following query about the Neo4j graph database: {query}
            
            Provide a detailed and comprehensive answer to the query.""",
            expected_output="A comprehensive answer to the query: {query}",
            agent=analyst_agent,
            callback=log_task_callback,
        )
        
        processing_task_mssql = Task(
            description="""Process the following query about the MSSQL database: {query}
            Observe the following rules: """ + mssql_rules,
            expected_output="A comprehensive answer to the query: {query}",
            agent=analyst_agent,
            callback=log_task_callback,
        )
        
        data_crew = Crew(
            agents=[analyst_agent],
            tasks=[processing_task_mssql],
            verbose=False
        )
    
        # Optional: Add high-level trace for the query
        if langfuse_client:
            trace = langfuse_client.trace(
                name="crewai_query",
                input={"query": query},
                metadata={
                    "agent_role": "Local Data Processor",
                    "tools": [tool.name for tool in tools],
                    "session_type": "neo4j_query"
                }
            )

        result = data_crew.kickoff(inputs={"query": query})
        
        # Update trace with result
        if langfuse_client and 'trace' in locals():
            trace.update(output={"result": str(result)})
            langfuse_client.flush()
        
        return {"result": result}

# For running as a script
# ie poetry run python cai.py
if __name__ == "__main__":
    #result = run_crew_query("Which staff member manages the delivery service delivering the most orders?")
    #result = run_crew_query("how many docs in db?")
    result = run_crew_query("list all categories")
    print(f"""
        Query completed!
        result: {result}
    """)