#!/bin/bash

set -e

echo "🚀 MindVPN Development Bootstrap"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p certs
mkdir -p deploy/grafana/provisioning/datasources
mkdir -p deploy/grafana/provisioning/dashboards
mkdir -p deploy/grafana/dashboards

# Generate CA certificates if they don't exist
if [ ! -f "certs/ca.crt" ]; then
    print_status "Generating CA certificates..."
    chmod +x scripts/gen_ca.sh
    ./scripts/gen_ca.sh
else
    print_status "CA certificates already exist, skipping generation."
fi

# Create init.sql for PostgreSQL
print_status "Creating database initialization script..."
cat > deploy/init.sql << 'EOF'
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_nodes_labels ON nodes USING GIN (labels jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_tasks_status_created ON tasks(status, created_at);
CREATE INDEX IF NOT EXISTS idx_nodes_org_status ON nodes(org_id, status);
EOF

# Create Grafana datasource configuration
print_status "Creating Grafana datasource configuration..."
cat > deploy/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Create basic Grafana dashboard
print_status "Creating basic Grafana dashboard..."
cat > deploy/grafana/dashboards/mindvpn-overview.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "MindVPN Overview",
    "tags": ["mindvpn"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Nodes Status",
        "type": "stat",
        "targets": [
          {
            "expr": "mindvpn_nodes_total",
            "legendFormat": "Total Nodes"
          }
        ]
      },
      {
        "id": 2,
        "title": "Active Tasks",
        "type": "stat",
        "targets": [
          {
            "expr": "mindvpn_tasks_running",
            "legendFormat": "Running Tasks"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "10s"
  }
}
EOF

# Create dashboard provisioning
cat > deploy/grafana/provisioning/dashboards/dashboards.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'MindVPN'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# Build and start services
print_status "Building and starting services..."
cd deploy
docker-compose build
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are healthy
print_status "Checking service health..."

# Check API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ API is healthy"
else
    print_warning "⚠️  API health check failed, but continuing..."
fi

# Check UI
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "✅ UI is healthy"
else
    print_warning "⚠️  UI health check failed, but continuing..."
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    print_status "✅ Prometheus is healthy"
else
    print_warning "⚠️  Prometheus health check failed, but continuing..."
fi

# Check Grafana
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    print_status "✅ Grafana is healthy"
else
    print_warning "⚠️  Grafana health check failed, but continuing..."
fi

# Start mock agents in background
print_status "Starting mock agents..."
cd ..
if command -v go &> /dev/null; then
    # Start mock agents if Go is available
    cd apps/agent
    go run cmd/mock-agent/main.go --node-id=node-1 --labels="region=EU,provider=hetzner" &
    MOCK_AGENT_1_PID=$!
    go run cmd/mock-agent/main.go --node-id=node-2 --labels="region=US,provider=digitalocean" &
    MOCK_AGENT_2_PID=$!
    cd ../..
    
    # Save PIDs for cleanup
    echo $MOCK_AGENT_1_PID > /tmp/mock_agent_1.pid
    echo $MOCK_AGENT_2_PID > /tmp/mock_agent_2.pid
    
    print_status "Mock agents started with PIDs: $MOCK_AGENT_1_PID, $MOCK_AGENT_2_PID"
else
    print_warning "Go not found, skipping mock agents. Install Go to run mock agents."
fi

# Create test data
print_status "Creating test data..."
if docker-compose -f deploy/docker-compose.yml exec -T api python -m scripts.seed_data > /dev/null 2>&1; then
    print_status "✅ Test data created successfully"
else
    print_warning "⚠️  Failed to create test data, but continuing..."
fi

echo ""
echo "🎉 MindVPN development environment is ready!"
echo ""
echo "📋 Service URLs:"
echo "  UI:          http://localhost:3000"
echo "  API:         http://localhost:8000"
echo "  Grafana:     http://localhost:3001 (admin/admin)"
echo "  Prometheus:  http://localhost:9090"
echo ""
echo "🔧 Useful commands:"
echo "  make logs    - View logs"
echo "  make down    - Stop services"
echo "  make test    - Run e2e tests"
echo "  make seed    - Recreate test data"
echo ""
echo "🤖 Mock agents are running on ports 9101 and 9102"
echo "   To stop them: make stop-mock-agents"
echo ""
