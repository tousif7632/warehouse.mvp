from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database.database_connector import BaserowConnector, ExportRequest
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

app = FastAPI()

# Config
BASEROW_URL = os.getenv("BASEROW_URL", "https://api.baserow.io")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

connector = BaserowConnector(BASEROW_URL, BASEROW_TOKEN)

# Example LangChain use
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

@app.post("/export/")
async def export_data(request: ExportRequest):
    try:
        connector.export_data(request)
        return {"message": "Data exported successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
