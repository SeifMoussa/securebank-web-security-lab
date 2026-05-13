"""FastAPI application entrypoint."""

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.requests import Request

from securebank.auth.routes import router as auth_router
from securebank.banking.routes import router as banking_router
from securebank.config import Settings, get_settings
from securebank.database import SessionLocal, configure_database, init_db
from securebank.security.headers import security_headers_middleware
from securebank.seed import seed_demo_data

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"


def create_app(settings: Settings | None = None, *, initialize_database: bool = True) -> FastAPI:
    """Create and configure the FastAPI application."""
    resolved_settings = settings or get_settings()
    configure_database(resolved_settings.database_url)
    if initialize_database:
        init_db()
        if resolved_settings.seed_demo_data:
            with SessionLocal() as db:
                seed_demo_data(db)

    app = FastAPI(title="SecureBank Web Security Lab", debug=resolved_settings.debug)
    template_env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(default=True, default_for_string=True),
    )
    templates = Jinja2Templates(env=template_env)

    app.state.settings = resolved_settings
    app.state.templates = templates
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.middleware("http")
    async def headers_middleware(request: Request, call_next):
        return await security_headers_middleware(request, call_next, resolved_settings)

    @app.get("/healthz", include_in_schema=False)
    @app.get("/health", include_in_schema=False)
    def health_check() -> dict[str, str]:
        """Health check for container and smoke-test wiring."""
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(banking_router)
    return app


app = create_app()
