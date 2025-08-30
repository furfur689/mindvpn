# MindVPN API Documentation

## Overview

MindVPN API предоставляет RESTful интерфейс для управления мультисерверной VPN инфраструктурой.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://cp.mindvpn.local`

## Authentication

API использует mTLS для аутентификации. Все запросы должны быть подписаны клиентским сертификатом.

## Endpoints

### Nodes Management

#### Register Node
```http
POST /v1/nodes/register
Content-Type: application/json

{
  "hostname": "node-1.mindvpn.local",
  "labels": {
    "region": "EU",
    "provider": "hetzner"
  },
  "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----..."
}
```

Response:
```json
{
  "node_id": 1,
  "agent_config": {
    "cp_url": "https://cp.mindvpn.local",
    "node_id": 1
  },
  "cert_pem": "-----BEGIN CERTIFICATE-----...",
  "ca_pem": "-----BEGIN CERTIFICATE-----..."
}
```

#### Node Heartbeat
```http
POST /v1/nodes/{node_id}/heartbeat
Content-Type: application/json

{
  "loads": {
    "cpu": 45.2,
    "ram": 67.8
  },
  "versions": {
    "agent": "1.0.0",
    "xray": "1.8.0"
  },
  "users_online": 15
}
```

#### List Nodes
```http
GET /v1/nodes?region=EU&provider=hetzner&status=READY
```

Response:
```json
[
  {
    "id": 1,
    "name": "EU-Hetzner-01",
    "hostname": "eu-hetzner-01.mindvpn.local",
    "status": "READY",
    "region": "EU",
    "provider": "hetzner",
    "labels": {
      "region": "EU",
      "provider": "hetzner"
    },
    "last_heartbeat_at": "2024-01-15T10:30:00Z"
  }
]
```

### Inbounds Management

#### Create Inbound
```http
POST /v1/inbounds
Content-Type: application/json

{
  "node_id": 1,
  "protocol": "xray",
  "port": 443,
  "preset": "reality_tcp",
  "overrides": {
    "server_name": "example.com",
    "private_key": "your_private_key",
    "short_ids": ["", "a", "b", "c"],
    "users": [
      {
        "uuid": "user-uuid",
        "email": "user@example.com"
      }
    ]
  }
}
```

Response:
```json
{
  "id": 1,
  "node_id": 1,
  "protocol": "xray",
  "port": 443,
  "status": "PENDING",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### List Inbounds
```http
GET /v1/inbounds?node_id=1&status=APPLIED
```

### Tasks Management

#### Create Task
```http
POST /v1/tasks
Content-Type: application/json

{
  "action": "APPLY_INBOUND",
  "target_type": "INBOUND",
  "target_id": 1,
  "payload": {
    "config_files": {
      "config.json": "..."
    }
  }
}
```

#### Get Task Status
```http
GET /v1/tasks/{task_id}
```

Response:
```json
{
  "id": 1,
  "action": "APPLY_INBOUND",
  "status": "SUCCESS",
  "logs": "Task completed successfully",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:00Z"
}
```

### User Bundles

#### Generate Bundle
```http
GET /v1/users/{user_id}/bundle
```

Response:
```json
{
  "user_id": 1,
  "uris": [
    "vless://user-uuid@node1.mindvpn.local:443?security=reality&sni=example.com&fp=chrome&pbk=public_key&sid=short_id&type=tcp&flow=xtls-rprx-vision#EU-Hetzner-01",
    "vless://user-uuid@node2.mindvpn.local:443?security=reality&sni=example.com&fp=chrome&pbk=public_key&sid=short_id&type=tcp&flow=xtls-rprx-vision#US-DigitalOcean-01"
  ],
  "qr_codes": [
    "data:image/svg+xml;base64,..."
  ]
}
```

### Metrics

#### Prometheus Metrics
```http
GET /v1/metrics/prometheus
```

#### Dashboard Metrics
```http
GET /v1/metrics/dashboard
```

Response:
```json
{
  "nodes": {
    "total": 5,
    "online": 4,
    "offline": 1
  },
  "users": {
    "total": 100,
    "active": 85
  },
  "tasks": {
    "total": 150,
    "running": 3,
    "completed": 145,
    "failed": 2
  },
  "inbounds": {
    "total": 10,
    "active": 9
  }
}
```

## Error Responses

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per node

## Examples

### Using curl

```bash
# Register a node
curl -X POST http://localhost:8000/v1/nodes/register \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "node-1.mindvpn.local",
    "labels": {"region": "EU", "provider": "hetzner"},
    "csr_pem": "mock-csr"
  }'

# Create inbound
curl -X POST http://localhost:8000/v1/inbounds \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": 1,
    "protocol": "xray",
    "port": 443,
    "preset": "reality_tcp",
    "overrides": {
      "server_name": "example.com",
      "private_key": "mock_key",
      "short_ids": ["", "a", "b", "c"]
    }
  }'

# Get user bundle
curl http://localhost:8000/v1/users/1/bundle
```

### Using Python

```python
import httpx

async with httpx.AsyncClient() as client:
    # Register node
    response = await client.post(
        "http://localhost:8000/v1/nodes/register",
        json={
            "hostname": "node-1.mindvpn.local",
            "labels": {"region": "EU", "provider": "hetzner"},
            "csr_pem": "mock-csr"
        }
    )
    node_data = response.json()
    
    # Create inbound
    response = await client.post(
        "http://localhost:8000/v1/inbounds",
        json={
            "node_id": node_data["node_id"],
            "protocol": "xray",
            "port": 443,
            "preset": "reality_tcp",
            "overrides": {
                "server_name": "example.com",
                "private_key": "mock_key",
                "short_ids": ["", "a", "b", "c"]
            }
        }
    )
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
