from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.gzip import GZipMiddleware

def add_middleware(app: FastAPI):
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust this as needed
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    # Session middleware
    app.add_middleware(SessionMiddleware, secret_key="88AC1A95756D9259823CCA6E17145A0")  # Replace with your secret key

    # GZip middleware for compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses larger than 1000 bytes

# This file is intentionally left blank.