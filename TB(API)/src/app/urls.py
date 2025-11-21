from contextlib import asynccontextmanager
from src.app import app
from src.constants.constants import Constants
from src.commons.validator import validate_db_connection
from src.utils.traceback_utils import print_traceback
from src.commons import fetch_response
import sys
from fastapi import APIRouter
router = APIRouter()

@asynccontextmanager
async def lifespan(app: app):
    try:
        await validate_db_connection()
    except Exception as e:
        print_traceback(e.__traceback__)
        sys.exit(Constants.FORCE_TERMINATE)
    yield  # Application runs after this
    # You can add shutdown logic here if needed

# Attach lifespan to app
app.router.lifespan_context = lifespan

# Include user routes
app.include_router(fetch_response.router, prefix="/api", tags=["User"])
app.include_router(router, prefix="/api", tags=["WebSocket"])
