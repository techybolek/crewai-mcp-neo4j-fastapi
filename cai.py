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
import os

# Create a StdioServerParameters object
server_params=[
    StdioServerParameters(
        command="uvx", 
        args=["mcp-neo4j-cypher"],
        env=os.environ,
    )
]

# Optionally logging callbacks from Agents & Tasks
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
            # llm=llm, # Optional - Remove if using OpenAI
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
    
        result = data_crew.kickoff(inputs={"query": query})
        return {"result": result}

# For running as a script
# ie poetry run python cai.py
if __name__ == "__main__":
    result = run_crew_query("Which staff member manages the delivery service delivering the most orders?")
    print(f"""
        Query completed!
        result: {result}
    """)