from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import health, data_collection, jurors, deliberations

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(data_collection.router, prefix=f"{settings.API_V1_STR}/data")
app.include_router(jurors.router, prefix=f"{settings.API_V1_STR}/jurors")
app.include_router(deliberations.router, prefix=f"{settings.API_V1_STR}/deliberations")


@app.get("/")
async def root():
    return {
        "message": "FreudLaw Jury Simulation Backend",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }