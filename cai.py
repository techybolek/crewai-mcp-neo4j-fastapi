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

from crewai import Agent, Task, Crew, LLM
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from langfuse.callback import CallbackHandler
from langfuse import Langfuse
from langfuse.openai import openai  # LangFuse's OpenAI wrapper
from langchain_openai import ChatOpenAI
import os
import logging

# Enable detailed logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize LangFuse (optional tracing)
langfuse_handler = None
langfuse_client = None

if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
    # Initialize LangFuse client  
    langfuse_client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
    # Configure OpenAI with LangFuse tracing
    try:
        openai.langfuse_auth_check()
        logger.info("LangFuse OpenAI wrapper initialized successfully")
        print("LangFuse tracing enabled with OpenAI integration")
    except Exception as e:
        logger.error(f"LangFuse OpenAI wrapper failed: {e}")
        print(f"LangFuse OpenAI integration failed: {e}")
else:
    print("LangFuse tracing disabled - set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable")

# Create a StdioServerParameters object
server_params=[
    StdioServerParameters(
        command="uvx", 
        args=["mcp-neo4j-cypher"],
        env=os.environ,
    )
]

# Enhanced logging callbacks with LangFuse integration
def log_step_callback(output):
    print(f"""
        Step completed!
        details: {output.__dict__}
    """)
    
    # Additional LangFuse logging if enabled
    if langfuse_client and hasattr(output, 'raw'):
        try:
            langfuse_client.trace(
                name="agent_step",
                metadata={
                    "agent_output": str(output.__dict__),
                    "step_type": "agent_execution"
                }
            )
        except Exception as e:
            print(f"LangFuse step logging error: {e}")

def log_task_callback(output):
    print(f"""
        Task completed!
        details: {output.__dict__}
    """)
    
    # Additional LangFuse logging if enabled
    if langfuse_client and hasattr(output, 'raw'):
        try:
            langfuse_client.trace(
                name="task_completion",
                metadata={
                    "task_output": str(output.__dict__),
                    "completion_type": "task_finished"
                }
            )
        except Exception as e:
            print(f"LangFuse task logging error: {e}")

# Create and run Crew
def run_crew_query(query: str):

    with MCPServerAdapter(server_params) as tools:
    
        print(f"Available tools from Stdio MCP server: {[tool.name for tool in tools]}")

        analyst_agent = Agent(
            role="Local Data Processor",
            goal="Process data using a local Stdio-based tool.",
            backstory="An AI that leverages local scripts via MCP for specialized tasks.",
            tools=tools,
            reasoning=False, # Optional
            verbose=False, # Optional
            step_callback=log_step_callback, # Optional
        )
        
        # Passing query directly into task
        processing_task = Task(
            description="""Process the following query about the Neo4j graph database: {query}
            
            Provide a detailed and comprehensive answer to the query.""",
            expected_output="A comprehensive answer to the query: {query}",
            agent=analyst_agent,
            callback=log_task_callback, # Optional
        )
        
        data_crew = Crew(
            agents=[analyst_agent],
            tasks=[processing_task],
            verbose=False
        )
    
        # Add query context to LangFuse trace
        trace = None
        if langfuse_client:
            try:
                trace = langfuse_client.trace(
                    name="crewai_query",
                    input={"query": query},
                    metadata={
                        "agent_role": "Local Data Processor",
                        "tools": [tool.name for tool in tools],
                        "session_type": "neo4j_query"
                    }
                )
            except Exception as e:
                print(f"LangFuse trace initialization error: {e}")

        result = data_crew.kickoff(inputs={"query": query})
        
        # Log final result to LangFuse
        if trace:
            try:
                trace.update(output={"result": str(result)})
                langfuse_client.flush()  # Ensure data is sent
            except Exception as e:
                print(f"LangFuse result logging error: {e}")
        
        return {"result": result}

# For running as a script
# ie poetry run python cai.py
if __name__ == "__main__":
    result = run_crew_query("Which staff member manages the delivery service delivering the most orders?")
    print(f"""
        Query completed!
        result: {result}
    """)