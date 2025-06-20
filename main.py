from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth.auth_controller import router as auth_api
from app.api.v1.prediction.prediction_controller import router as recomendation_api

app = FastAPI(title="Osinergmin Energy Recomendation APIs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth_api)
app.include_router(recomendation_api)
@app.get("/")
def read_root():
    return {"Hello": "World"}
