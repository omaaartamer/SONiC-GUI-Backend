from fastapi import FastAPI
from app.api.auth.routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

# Allow all origins for testing (you can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing; use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])