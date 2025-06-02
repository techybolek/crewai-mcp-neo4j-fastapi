from crewai import Agent, Task, Crew, Process
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
            reasoning=False,
            verbose=False,
            step_callback=log_step_callback,
        )
        
        # Passing query directly into task
        processing_task = Task(
            description=f"""Process the following query about the Neo4j graph database: {query}
            
            Provide a detailed and comprehensive answer to the query.""",
            expected_output=f"A comprehensive answer to the query: {query}",
            agent=analyst_agent,
            markdown=False,
            context=[{
                "query": query,
                "description": f"Process and answer the following query: {query}",
                "expected_output": f"A detailed and accurate answer to: {query}"
            }],
            callback=log_task_callback,
        )
        
        data_crew = Crew(
            agents=[analyst_agent],
            tasks=[processing_task],
            verbose=False
        )
    
        result = data_crew.kickoff()
        return {"result": result}

# For running as a script
if __name__ == "__main__":
    run_crew_query("What is the total value of all orders?")