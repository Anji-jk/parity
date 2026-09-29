from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.firebase import init_firebase

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import AppError

from app.services.auth.routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    lifespan=lifespan,
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.error_code, "message": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return await app_error_handler(
        request,
        AppError(
            "VALIDATION_ERROR",
            422,
            "Please check the submitted information.",
        ),
    )

# Standard CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all domain routers under /v1
API_PREFIX = "/v1"

app.include_router(auth_router, prefix=API_PREFIX)
