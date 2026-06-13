from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import generate

app = FastAPI(title="Trus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(generate.router, prefix="/api")
