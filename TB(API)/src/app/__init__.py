from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS (same as Flask-CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # you can restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import your routes
from src.app import urls
