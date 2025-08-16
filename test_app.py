from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    print("Root endpoint hit")
    return {"message": "Test app is working!"}