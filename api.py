"""Web API entry point: uvicorn api:app. The application lives in the server package."""
import logging

from server.app import create_app

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

app = create_app()
