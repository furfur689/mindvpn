# MindVPN - Multi-Server VPN Management Platform

MindVPN - это форк панели Hiddify с мультисерверным управлением, реализованный как Control Plane с Node Agent архитектурой.

## Архитектура

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

## Технологический стек

- **Control Plane**: FastAPI (Python 3.11), SQLAlchemy, Pydantic
- **UI**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Worker**: Celery + Redis
- **Node Agent**: Go 1.22 (mTLS gRPC/WebSocket)
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Monitoring**: Prometheus + Grafana
- **Security**: mTLS с локальным CA

## Быстрый старт

### Требования

- Docker & Docker Compose
- Go 1.22+ (для разработки агента)
- Node.js 18+ (для разработки UI)
- Python 3.11+ (для разработки API)

### Запуск в dev режиме

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

### Доступ к сервисам

- **UI**: http://localhost:3000
- **API**: http://localhost:8000
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## Структура проекта

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

## API Endpoints

### Nodes Management
- `POST /v1/nodes/register` - Регистрация нового узла
- `POST /v1/nodes/{id}/heartbeat` - Heartbeat от агента
- `GET /v1/nodes` - Список узлов с фильтрацией

### Inbounds Management
- `POST /v1/inbounds` - Создание нового inbound
- `GET /v1/inbounds` - Список inbounds
- `POST /v1/inbounds/import` - Импорт существующих конфигов

### Tasks
- `POST /v1/tasks` - Создание задачи
- `GET /v1/tasks/{id}` - Статус задачи
- `GET /v1/tasks` - Список задач

### User Bundles
- `GET /v1/users/{id}/bundle` - Генерация bundle для клиента

## Константы

- **BRAND**: MindVPN
- **ORG_SLUG**: mindvpn
- **DOMAIN_CP**: cp.mindvpn.local (dev)
- **GIT_NAMESPACE**: mindvpn

## Лицензия

Проект использует компоненты из HiddifyPanel под GPL лицензией. См. `libs/hiddi_compat/README.md` для деталей.

## Разработка

```bash
# Форматирование кода
make fmt

# Запуск тестов
make test

# Остановка сервисов
make down

# Логи
make logs
```

## E2E Тест

Автоматический тест проверяет полный цикл:
1. Регистрация 2 виртуальных узлов
2. Создание inbound на оба узла
3. Применение конфигов агентами
4. Проверка статуса в UI
5. Генерация bundle для клиента

## Безопасность

- Все коммуникации защищены mTLS
- Агенты валидируют конфиги перед применением
- RBAC роли: OWNER/ADMIN/SUPPORT/READONLY
- Логи задач хранятся 7 дней
