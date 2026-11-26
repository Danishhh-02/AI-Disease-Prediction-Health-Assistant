import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import init_db
from backend.routes import auth, symptoms, prediction, diseases, feedback, admin

app = FastAPI(
    title="AI Disease Prediction & Health Assistant API",
    description="Production-grade AI/ML Decision Support API for Disease Prediction and Educational Health Guidance",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "AI Disease Prediction & Health Assistant Backend API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

# Include Routers
app.include_router(auth.router)
app.include_router(symptoms.router)
app.include_router(prediction.router)
app.include_router(diseases.router)
app.include_router(feedback.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
