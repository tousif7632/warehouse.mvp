import requests
from typing import List, Dict
from pydantic import BaseModel

class ExportRequest(BaseModel):
    table_id: str
    data: List[Dict]

class BaserowConnector:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self):
        response = requests.get(
            f"{self.base_url}/api/database/tables/", 
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def export_data(self, request: ExportRequest):
        # First clear existing data
        delete_url = f"{self.base_url}/api/database/rows/table/{request.table_id}/batch/"
        rows = requests.get(
            f"{self.base_url}/api/database/rows/table/{request.table_id}/?user_field_names=true", 
            headers=self.headers
        ).json()['results']
        
        if rows:
            row_ids = [row['id'] for row in rows]
            requests.delete(
                delete_url,
                json={"items": row_ids},
                headers=self.headers
            )
        
        # Add new data in batches
        batch_url = f"{self.base_url}/api/database/rows/table/{request.table_id}/batch/"
        batch_size = 100
        for i in range(0, len(request.data), batch_size):
            batch = request.data[i:i+batch_size]
            payload = {
                "items": [
                    {"row": row, "user_field_names": True}
                    for row in batch
                ]
            }
            response = requests.post(batch_url, json=payload, headers=self.headers)
            response.raise_for_status()