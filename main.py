from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth.auth_controller import router as auth_api
from app.api.v1.prediction.prediction_controller import router as prediction_api

app = FastAPI(
    title="Energy Consumption Prediction API",
    description="API for predicting energy consumption using hexagonal architecture",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api)
app.include_router(prediction_api)

@app.get("/")
def read_root():
    return {
        "message": "Energy Consumption Prediction API",
        "version": "2.0.0",
        "architecture": "Hexagonal",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
