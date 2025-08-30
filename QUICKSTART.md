# MindVPN Quick Start Guide

## 🚀 Быстрый запуск

### Предварительные требования

- Docker & Docker Compose
- Git
- Go 1.22+ (для разработки агента)
- Node.js 18+ (для разработки UI)
- Python 3.11+ (для разработки API)

### 1. Клонирование и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/mindvpn/mindvpn.git
cd mindvpn

# Запустить все сервисы
make up

# Создать тестовые данные
make seed

# Запустить e2e тесты
make test
```

### 2. Проверка работоспособности

После запуска проверьте доступность сервисов:

- **UI**: http://localhost:3000
- **API**: http://localhost:8000
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### 3. Структура проекта

```
mindvpn/
├── apps/
│   ├── api/              # FastAPI backend
│   ├── ui/               # Next.js frontend
│   ├── worker/           # Celery worker
│   └── agent/            # Go agent
├── libs/
│   └── hiddi_compat/     # Hiddify config generators
├── deploy/               # Docker compose & monitoring
├── scripts/              # Bootstrap & utilities
└── tests/                # E2E tests
```

### 4. Основные команды

```bash
# Управление сервисами
make up          # Запустить все сервисы
make down        # Остановить сервисы
make logs        # Просмотр логов
make clean       # Очистка данных

# Разработка
make fmt         # Форматирование кода
make test        # Запуск тестов
make seed        # Создание тестовых данных

# Мониторинг
make health      # Проверка здоровья сервисов
```

### 5. E2E Тест

Автоматический тест проверяет полный цикл:

1. ✅ Регистрация 2 виртуальных узлов
2. ✅ Создание inbound на оба узла
3. ✅ Применение конфигов агентами
4. ✅ Проверка статуса в UI
5. ✅ Генерация bundle для клиента

### 6. Архитектура

```
┌─────────────────┐    mTLS gRPC/WS    ┌─────────────────┐
│   Control Plane │ ◄─────────────────► │   Node Agent    │
│   (API + UI)    │                     │   (Go/Python)   │
└─────────────────┘                     └─────────────────┘
         │                                        │
         │                                        │
    ┌────▼────┐                              ┌────▼────┐
    │  Tasks  │                              │  Config │
    │  Queue  │                              │  Files  │
    └─────────┘                              └─────────┘
```

### 7. Технологический стек

- **Control Plane**: FastAPI (Python 3.11), SQLAlchemy, Pydantic
- **UI**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Worker**: Celery + Redis
- **Node Agent**: Go 1.22 (mTLS gRPC/WebSocket)
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Monitoring**: Prometheus + Grafana
- **Security**: mTLS с локальным CA

### 8. API Endpoints

Основные эндпоинты:

- `POST /v1/nodes/register` - Регистрация узла
- `POST /v1/nodes/{id}/heartbeat` - Heartbeat от агента
- `POST /v1/inbounds` - Создание inbound
- `GET /v1/users/{id}/bundle` - Генерация bundle
- `GET /v1/metrics/prometheus` - Метрики

### 9. Безопасность

- Все коммуникации защищены mTLS
- Агенты валидируют конфиги перед применением
- RBAC роли: OWNER/ADMIN/SUPPORT/READONLY
- Логи задач хранятся 7 дней

### 10. Разработка

```bash
# Запуск в режиме разработки
make dev-api     # API с hot reload
make dev-ui      # UI с hot reload
make dev-worker  # Worker с hot reload

# Mock агенты
make mock-agents        # Запустить mock агенты
make stop-mock-agents   # Остановить mock агенты
```

### 11. Мониторинг

Grafana дашборды:
- **Nodes Overview** - Статус узлов
- **Tasks Monitor** - Мониторинг задач
- **Traffic Analytics** - Аналитика трафика

### 12. Troubleshooting

```bash
# Проверка здоровья сервисов
make health

# Просмотр логов
make logs

# Сброс базы данных
make db-reset

# Пересоздание сертификатов
make gen-ca
```

### 13. Production Deployment

Для production развертывания:

1. Настройте внешний CA
2. Измените секретные ключи
3. Настройте SSL/TLS
4. Настройте backup базы данных
5. Настройте мониторинг

### 14. Поддержка

- Документация API: `apps/api/README_api.md`
- Примеры использования в тестах: `tests/test_e2e.py`
- Конфигурация в `deploy/docker-compose.yml`

---

🎉 **MindVPN готов к использованию!**
