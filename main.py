from fastapi import FastAPI
from api.sample.endpoint import chapter

app = FastAPI()

app.include_router(chapter.router, prefix="/api/v1")
