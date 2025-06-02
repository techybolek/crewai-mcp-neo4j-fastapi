from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cai import run_crew_query
import uvicorn
import os

class QueryRequest(BaseModel):
    query: str

app = FastAPI()

@app.post("/crewai")
async def query_crew_endpoint(request: QueryRequest):

    print(f'/query endpoint: Input query: {request.query}')

    return run_crew_query(request.query)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 4000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)