#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных MindVPN
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Org, Node, User, NodeCapability
from src.models.node import NodeStatus
from src.core.config import settings

async def create_test_data():
    """Создает тестовые данные для MindVPN."""
    
    print("🌱 Creating test data for MindVPN...")
    
    # Создаем подключение к БД
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Создаем таблицы если их нет
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Создаем организацию
        print("📋 Creating organization...")
        org = Org(
            slug="mindvpn",
            name="MindVPN Organization"
        )
        db.add(org)
        db.flush()  # Получаем ID
        
        print(f"✅ Created organization: {org.name} (ID: {org.id})")
        
        # Создаем тестового пользователя
        print("👤 Creating test user...")
        user = User(
            org_id=org.id,
            email="admin@mindvpn.local",
            role="OWNER",
            status="ACTIVE"
        )
        db.add(user)
        db.flush()
        
        print(f"✅ Created user: {user.email} (ID: {user.id})")
        
        # Создаем тестовые узлы
        print("🖥️ Creating test nodes...")
        
        nodes_data = [
            {
                "name": "EU-Hetzner-01",
                "hostname": "eu-hetzner-01.mindvpn.local",
                "ipv4": "192.168.1.100",
                "region": "EU",
                "provider": "hetzner",
                "labels": {"region": "EU", "provider": "hetzner", "tier": "production"},
                "status": NodeStatus.READY
            },
            {
                "name": "US-DigitalOcean-01", 
                "hostname": "us-digitalocean-01.mindvpn.local",
                "ipv4": "192.168.1.101",
                "region": "US",
                "provider": "digitalocean",
                "labels": {"region": "US", "provider": "digitalocean", "tier": "production"},
                "status": NodeStatus.READY
            }
        ]
        
        for node_data in nodes_data:
            node = Node(
                org_id=org.id,
                **node_data
            )
            db.add(node)
            db.flush()
            
            # Добавляем возможности узла
            capabilities = [
                NodeCapability(
                    node_id=node.id,
                    protocol="XRAY",
                    version="1.8.0",
                    features={"reality": True, "xtls": True, "grpc": True}
                ),
                NodeCapability(
                    node_id=node.id,
                    protocol="SINGBOX",
                    version="1.7.0",
                    features={"reality": True, "hysteria2": True, "tuic": True}
                )
            ]
            
            for cap in capabilities:
                db.add(cap)
            
            print(f"✅ Created node: {node.name} (ID: {node.id})")
        
        # Сохраняем изменения
        db.commit()
        
        print("\n🎉 Test data created successfully!")
        print(f"📊 Summary:")
        print(f"  - Organization: {org.name}")
        print(f"  - Users: 1")
        print(f"  - Nodes: {len(nodes_data)}")
        print(f"  - Capabilities: {len(nodes_data) * 2}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test data: {e}")
        raise
    finally:
        db.close()

def main():
    """Точка входа."""
    try:
        asyncio.run(create_test_data())
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
