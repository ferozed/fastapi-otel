import pkg_resources

from fastapi import FastAPI
from fastapi import APIRouter
from typing import Dict,Any
from opentelemetry import trace
from contextlib import asynccontextmanager
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

import logging
LOG = logging.getLogger(__name__)
'''
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
for handler in root_logger.handlers:
  handler.setLevel(logging.DEBUG)
  
logconfig_dict.update({"root": {"level":"DEBUG", "handlers": ["error"]}})
'''

'''
from opentelemetry import trace, propagators, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
'''

tags_metadata = [
    {
        "name": "root",
        "description": "root route",
    }
]

app = FastAPI(
    title="fastapi-otel-test",
    description="This is a REST api that test otel with fastapi.",
    version="0.1.2",
    openapi_tags=tags_metadata,
)
# Freeze OpenAPI verstion. OpenAPI 3.1.0 is not fully backward compatible
app.openapi_version = "3.0.3"
app.add_middleware(ProxyHeadersMiddleware)

'''
def server_request_hook(span, scope: Dict[str, Any]):
     if span and span.is_recording():
         span.set_attribute("service.name", "fastapi-otel")

FastAPIInstrumentor.instrument_app(app,
                                   tracer_provider=provider,
                                   server_request_hook=server_request_hook)
'''
FastAPIInstrumentor.instrument_app(app)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    LOG.error("lifespan() start")
    yield
    LOG.info("lifespan() end")

router = APIRouter()

import httpx
@router.get("/", tags=["root"])
async def root():
    async with httpx.AsyncClient() as client:
      response = await client.get("http://localhost:8000/foo")
    LOG.info(response.headers)
    return "Hello world"

@router.get("/foo", tags=["root"])
async def foo():
    return "Hello foo"

app.include_router(router)

