# Hiddify Compatibility Library

Эта библиотека содержит генераторы конфигураций, извлеченные из проекта HiddifyPanel для использования в MindVPN.

## Лицензия

**ВАЖНО**: Эта библиотека содержит код из HiddifyPanel, который распространяется под лицензией GNU General Public License v3.0 (GPL-3.0).

### Исходный код
- **Проект**: HiddifyPanel
- **Автор**: Hiddify
- **Лицензия**: GPL-3.0
- **Репозиторий**: https://github.com/hiddify/hiddify-config

### Условия использования

1. Любые изменения в этой библиотеке должны распространяться под той же лицензией GPL-3.0
2. При использовании этой библиотеки в коммерческих проектах необходимо соблюдать условия GPL-3.0
3. Полный текст лицензии GPL-3.0 доступен в файле LICENSE

## Структура

```
hiddi_compat/
├── generators/
│   ├── xray.py          # Xray-core конфигурации
│   ├── singbox.py       # Sing-box конфигурации
│   └── common.py        # Общие утилиты
├── templates/
│   ├── xray/            # Jinja2 шаблоны для Xray
│   └── singbox/         # Jinja2 шаблоны для Sing-box
└── presets/
    ├── vless_reality.py # VLESS + Reality пресеты
    ├── hysteria2.py     # Hysteria2 пресеты
    ├── tuic.py          # TUIC пресеты
    └── trojan.py        # Trojan пресеты
```

## Использование

```python
from hiddi_compat.generators import render_inbound

# Генерация конфигурации VLESS + Reality
config_files = render_inbound(
    protocol="vless",
    port=443,
    preset="reality_tcp",
    overrides={
        "server_name": "example.com",
        "private_key": "your_private_key",
        "short_ids": ["", "a", "b", "c"]
    },
    node_caps={
        "protocol": "XRAY",
        "version": "1.8.0",
        "features": ["reality", "xtls"]
    }
)

# config_files содержит словарь {filename: content}
```

## Поддерживаемые протоколы

- **VLESS + Reality** (TCP, gRPC, XHTTP)
- **Hysteria2** (UDP)
- **TUIC** (UDP)
- **Trojan** (TCP + TLS)
- **Shadowsocks** (различные методы шифрования)

## Безопасность

- Все конфигурации генерируются с учетом лучших практик безопасности
- Поддержка валидации конфигураций перед применением
- Совместимость с последними версиями Xray-core и Sing-box
