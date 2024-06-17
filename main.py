import os

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.schema import schema

from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello")
async def say_hello():
    return {"message": "Hello World"}


@app.get("/")
async def index():
    return {"message": "Welcome to the Student API"}


graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)