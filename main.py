from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

class QueryRequest(BaseModel):
    query: str

# Create a StdioServerParameters object
server_params=StdioServerParameters(
    command="uvx", 
    args=["mcp-neo4j-cypher"],
    env=os.environ,
)

app = FastAPI()

@app.post("/kickoff/")
async def kickoff_crew_endpoint(request: QueryRequest):

    print(f'Input query: {request.query}')

    with MCPServerAdapter(server_params) as tools:
        print(f"Available tools from Stdio MCP server: {[tool.name for tool in tools]}")

        # Example: Using the tools from the Stdio MCP server in a CrewAI Agent
        research_agent = Agent(
            role="Local Data Processor",
            goal="Process data using a local Stdio-based tool.",
            backstory="An AI that leverages local scripts via MCP for specialized tasks.",
            tools=tools,
            reasoning=False,
            verbose=False,
        )
        
        processing_task = Task(
            description=f"""Process the following query about the Neo4j graph database: {request.query}
            
            Provide a detailed and comprehensive answer to the query.""",
            expected_output=f"A comprehensive answer to the query: {request.query}",
            agent=research_agent,
            markdown=False,
            context=[{
                "query": request.query,
                "description": f"Process and answer the following query: {request.query}",
                "expected_output": f"A detailed and accurate answer to: {request.query}"
            }]
        )
        
        data_crew = Crew(
            agents=[research_agent],
            tasks=[processing_task],
            verbose=False,
            process=Process.sequential 
        )
    
        result = data_crew.kickoff()
        print(f"Result: {result}")
        return {"result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)