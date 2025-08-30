.PHONY: help up down build test fmt seed logs clean

# Default target
help:
	@echo "MindVPN Development Commands:"
	@echo "  make up      - Start all services (docker-compose up -d)"
	@echo "  make down    - Stop all services (docker-compose down)"
	@echo "  make build   - Build all Docker images"
	@echo "  make test    - Run e2e tests"
	@echo "  make fmt     - Format code (black, isort, go fmt)"
	@echo "  make seed    - Create test data (org, admin user)"
	@echo "  make logs    - Show logs from all services"
	@echo "  make clean   - Clean up volumes and images"

# Bootstrap development environment
up:
	@echo "🚀 Starting MindVPN development environment..."
	@chmod +x scripts/dev_bootstrap.sh
	@./scripts/dev_bootstrap.sh

# Stop all services
down:
	@echo "🛑 Stopping MindVPN services..."
	docker-compose -f deploy/docker-compose.yml down

# Build all images
build:
	@echo "🔨 Building Docker images..."
	docker-compose -f deploy/docker-compose.yml build

# Run e2e tests
test:
	@echo "🧪 Running e2e tests..."
	cd tests && python -m pytest test_e2e.py -v

# Format code
fmt:
	@echo "🎨 Formatting Python code..."
	cd apps/api && black . && isort .
	@echo "🎨 Formatting Go code..."
	cd apps/agent && go fmt ./...
	@echo "🎨 Formatting TypeScript code..."
	cd apps/ui && npm run format

# Create test data
seed:
	@echo "🌱 Creating test data..."
	cd apps/api && python -m scripts.seed_data

# Show logs
logs:
	@echo "📋 Showing logs..."
	docker-compose -f deploy/docker-compose.yml logs -f

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f deploy/docker-compose.yml down -v
	docker system prune -f

# Generate CA certificates
gen-ca:
	@echo "🔐 Generating CA certificates..."
	@chmod +x scripts/gen_ca.sh
	@./scripts/gen_ca.sh

# Start mock agents
mock-agents:
	@echo "🤖 Starting mock agents..."
	cd apps/agent && go run cmd/mock-agent/main.go --node-id=node-1 --labels="region=EU,provider=hetzner" &
	cd apps/agent && go run cmd/mock-agent/main.go --node-id=node-2 --labels="region=US,provider=digitalocean" &

# Stop mock agents
stop-mock-agents:
	@echo "🛑 Stopping mock agents..."
	pkill -f "mock-agent" || true

# Development shortcuts
dev-api:
	@echo "🔧 Starting API in development mode..."
	cd apps/api && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-ui:
	@echo "🔧 Starting UI in development mode..."
	cd apps/ui && npm run dev

dev-worker:
	@echo "🔧 Starting worker in development mode..."
	cd apps/worker && celery -A src.worker worker --loglevel=info

# Database operations
db-migrate:
	@echo "🗄️ Running database migrations..."
	cd apps/api && alembic upgrade head

db-reset:
	@echo "🗄️ Resetting database..."
	cd apps/api && alembic downgrade base && alembic upgrade head

# Health checks
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ API not healthy"
	@curl -f http://localhost:3000 || echo "❌ UI not healthy"
	@curl -f http://localhost:9090/-/healthy || echo "❌ Prometheus not healthy"
	@curl -f http://localhost:3001/api/health || echo "❌ Grafana not healthy"
