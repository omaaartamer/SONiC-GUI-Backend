from fastapi import FastAPI
from app.routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from app.core.limiter import limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import PlainTextResponse
from slowapi.errors import RateLimitExceeded


app=FastAPI()


app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Allow all origins for testing 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return PlainTextResponse("Too many requests", status_code=429)