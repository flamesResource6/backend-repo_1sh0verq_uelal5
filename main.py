import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

from database import db, create_document, get_documents

app = FastAPI(title="Dark Whale SaaS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Dark Whale SaaS API running"}


# Generic create endpoint leveraging schemas defined in schemas.py via collection name
class CreatePayload(BaseModel):
    collection: str
    data: Dict[str, Any]


@app.post("/api/create")
def api_create(payload: CreatePayload):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    collection = payload.collection.lower()
    try:
        inserted_id = create_document(collection, payload.data)
        return {"inserted_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/list/{collection}")
def api_list(collection: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        docs = get_documents(collection.lower(), {}, limit=100)
        # Convert ObjectId to string
        from bson import ObjectId
        def transform(doc):
            d = dict(doc)
            if isinstance(d.get("_id"), ObjectId):
                d["_id"] = str(d["_id"]) 
            return d
        return [transform(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
