from app.routers import feature1
from fastapi import FastAPI

app = FastAPI()

app.include_router(feature1.router)
