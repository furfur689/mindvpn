from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import time

from .deps import get_db
from .routers import nodes, tasks, users, bundles, metrics
from .services.metrics import setup_metrics
from .core.config import settings

# Prometheus metrics
REQUEST_COUNT = Counter('mindvpn_http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('mindvpn_http_request_duration_seconds', 'HTTP request latency')
ACTIVE_CONNECTIONS = Gauge('mindvpn_active_connections', 'Number of active connections')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting MindVPN API...")
    setup_metrics()
    yield
    # Shutdown
    print("🛑 Shutting down MindVPN API...")

# Create FastAPI app
app = FastAPI(
    title="MindVPN API",
    description="Multi-Server VPN Management Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://ui:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "cp.mindvpn.local", "api", "worker"]
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.observe(process_time)
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mindvpn-api",
        "version": "1.0.0"
    }

# Include routers
app.include_router(nodes.router, prefix="/v1/nodes", tags=["nodes"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/v1/users", tags=["users"])
app.include_router(bundles.router, prefix="/v1/bundles", tags=["bundles"])
app.include_router(metrics.router, prefix="/v1/metrics", tags=["metrics"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "MindVPN API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
