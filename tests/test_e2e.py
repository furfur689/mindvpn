#!/usr/bin/env python3
"""
E2E тест для MindVPN
Проверяет полный цикл: регистрация узлов → создание inbounds → применение конфигов → генерация bundle
"""

import asyncio
import httpx
import json
import time
import pytest
from typing import Dict, Any

# Конфигурация теста
API_BASE_URL = "http://localhost:8000"
MOCK_AGENT_1_URL = "http://localhost:9101"
MOCK_AGENT_2_URL = "http://localhost:9102"

class MindVPNE2ETest:
    def __init__(self):
        self.api_client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0)
        self.node_ids = []
        self.inbound_ids = []
        self.user_id = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.api_client.aclose()

    async def wait_for_service(self, url: str, max_retries: int = 30) -> bool:
        """Ждет готовности сервиса."""
        for i in range(max_retries):
            try:
                response = await self.api_client.get("/health")
                if response.status_code == 200:
                    print(f"✅ Service {url} is ready")
                    return True
            except Exception as e:
                print(f"⏳ Waiting for {url}... ({i+1}/{max_retries})")
                await asyncio.sleep(2)
        return False

    async def register_mock_nodes(self) -> None:
        """Регистрирует два mock узла."""
        print("\n🔧 Registering mock nodes...")
        
        # Регистрируем первый узел
        node1_data = {
            "hostname": "mock-node-1",
            "labels": {"region": "EU", "provider": "hetzner"},
            "csr_pem": "mock-csr-1"  # В реальности это был бы CSR
        }
        
        response = await self.api_client.post("/v1/nodes/register", json=node1_data)
        assert response.status_code == 200, f"Failed to register node 1: {response.text}"
        
        node1_result = response.json()
        self.node_ids.append(node1_result["node_id"])
        print(f"✅ Registered node 1: {node1_result['node_id']}")
        
        # Регистрируем второй узел
        node2_data = {
            "hostname": "mock-node-2", 
            "labels": {"region": "US", "provider": "digitalocean"},
            "csr_pem": "mock-csr-2"
        }
        
        response = await self.api_client.post("/v1/nodes/register", json=node2_data)
        assert response.status_code == 200, f"Failed to register node 2: {response.text}"
        
        node2_result = response.json()
        self.node_ids.append(node2_result["node_id"])
        print(f"✅ Registered node 2: {node2_result['node_id']}")

    async def create_inbounds(self) -> None:
        """Создает inbounds на обоих узлах."""
        print("\n🔧 Creating inbounds...")
        
        for i, node_id in enumerate(self.node_ids):
            inbound_data = {
                "node_id": node_id,
                "protocol": "xray",
                "port": 443 + i,
                "preset": "reality_tcp",
                "overrides": {
                    "server_name": f"example{i+1}.com",
                    "private_key": f"mock_private_key_{i+1}",
                    "short_ids": ["", "a", "b", "c"],
                    "users": [
                        {
                            "uuid": f"user-{i+1}-uuid",
                            "email": f"user{i+1}@example.com"
                        }
                    ]
                }
            }
            
            response = await self.api_client.post("/v1/inbounds", json=inbound_data)
            assert response.status_code == 200, f"Failed to create inbound {i+1}: {response.text}"
            
            inbound_result = response.json()
            self.inbound_ids.append(inbound_result["id"])
            print(f"✅ Created inbound {i+1}: {inbound_result['id']}")

    async def wait_for_tasks_completion(self) -> None:
        """Ждет завершения всех задач."""
        print("\n⏳ Waiting for tasks completion...")
        
        max_wait = 60  # секунд
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            all_completed = True
            
            for inbound_id in self.inbound_ids:
                response = await self.api_client.get(f"/v1/inbounds/{inbound_id}")
                if response.status_code == 200:
                    inbound = response.json()
                    if inbound["status"] != "APPLIED":
                        all_completed = False
                        print(f"⏳ Inbound {inbound_id} status: {inbound['status']}")
                        break
                else:
                    all_completed = False
                    break
            
            if all_completed:
                print("✅ All inbounds applied successfully")
                return
                
            await asyncio.sleep(2)
        
        raise TimeoutError("Tasks did not complete within timeout")

    async def create_test_user(self) -> None:
        """Создает тестового пользователя."""
        print("\n🔧 Creating test user...")
        
        user_data = {
            "email": "test@mindvpn.local",
            "role": "ADMIN"
        }
        
        response = await self.api_client.post("/v1/users", json=user_data)
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        
        user_result = response.json()
        self.user_id = user_result["id"]
        print(f"✅ Created user: {self.user_id}")

    async def generate_bundle(self) -> None:
        """Генерирует bundle для пользователя."""
        print("\n🔧 Generating user bundle...")
        
        response = await self.api_client.get(f"/v1/users/{self.user_id}/bundle")
        assert response.status_code == 200, f"Failed to generate bundle: {response.text}"
        
        bundle = response.json()
        assert "uris" in bundle, "Bundle should contain URIs"
        assert len(bundle["uris"]) > 0, "Bundle should not be empty"
        
        print(f"✅ Generated bundle with {len(bundle['uris'])} URIs")
        for uri in bundle["uris"]:
            print(f"  📱 {uri[:50]}...")

    async def verify_metrics(self) -> None:
        """Проверяет метрики."""
        print("\n🔧 Verifying metrics...")
        
        # Проверяем метрики API
        response = await self.api_client.get("/v1/metrics/prometheus")
        assert response.status_code == 200, "Failed to get metrics"
        
        metrics_text = response.text
        assert "mindvpn_nodes_total" in metrics_text, "Should have nodes metric"
        assert "mindvpn_tasks_total" in metrics_text, "Should have tasks metric"
        
        print("✅ Metrics are available")

    async def run_full_test(self) -> None:
        """Запускает полный E2E тест."""
        print("🚀 Starting MindVPN E2E Test")
        print("=" * 50)
        
        # Ждем готовности API
        if not await self.wait_for_service(API_BASE_URL):
            raise Exception("API service is not ready")
        
        # Выполняем тестовые шаги
        await self.register_mock_nodes()
        await self.create_inbounds()
        await self.wait_for_tasks_completion()
        await self.create_test_user()
        await self.generate_bundle()
        await self.verify_metrics()
        
        print("\n🎉 E2E Test completed successfully!")
        print("=" * 50)

@pytest.mark.asyncio
async def test_mindvpn_e2e():
    """Основной E2E тест."""
    async with MindVPNE2ETest() as tester:
        await tester.run_full_test()

if __name__ == "__main__":
    # Запуск теста напрямую
    asyncio.run(test_mindvpn_e2e())
