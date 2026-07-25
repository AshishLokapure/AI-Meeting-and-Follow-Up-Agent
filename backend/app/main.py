from fastapi import FastAPI

app = FastAPI(title="AI Meeting Agent API")

@app.get("/")
def read_root():
    return {"message": "AI Meeting Agent API is running"}
