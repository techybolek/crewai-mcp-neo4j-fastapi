# FastAPI server using CrewAI and Neo4j MCP

This is a simple FastAPI server that uses CrewAI and Neo4j MCP to process queries about the data within a Neo4j graph database.


## Setup
Copy the sample.env file to .env and fill in the values.

## Running
```
poetry run uvicorn main:app --reload
```

Interactive docs will be accessible at:
http://127.0.0.1:8000/docs
