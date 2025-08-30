import json
import os
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, Template
import subprocess
import tempfile

class XrayGenerator:
    """Генератор конфигураций для Xray-core."""
    
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "../templates/xray")
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render_inbound(
        self,
        port: int,
        preset: str,
        overrides: Dict[str, Any],
        node_caps: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Генерирует конфигурацию inbound для Xray.
        
        Args:
            port: Порт для inbound
            preset: Пресет (reality_tcp, reality_grpc, etc.)
            overrides: Дополнительные параметры
            node_caps: Возможности узла
            
        Returns:
            Словарь {filename: content}
        """
        
        # Базовые настройки
        config = {
            "core_type": "xray",
            "log_level": "INFO",
            "reality_enable": True,
            "reality_private_key": overrides.get("private_key", ""),
            "reality_short_ids": ",".join(overrides.get("short_ids", ["", "a", "b", "c"])),
            "path_vless": "/",
            "path_grpc": "/grpc",
            "path_xhttp": "/xhttp"
        }
        
        # Домены для Reality
        domains = [{
            "domain": overrides.get("server_name", "example.com"),
            "internal_port_special": port,
            "mode": preset
        }]
        
        # Пользователи (клиенты)
        users = []
        for user in overrides.get("users", []):
            users.append({
                "uuid": user.get("uuid", ""),
                "email": user.get("email", "")
            })
        
        # Контекст для шаблонов
        context = {
            "hconfigs": config,
            "domains": domains,
            "users": users,
            "port": port
        }
        
        # Выбираем шаблон в зависимости от пресета
        template_name = self._get_template_name(preset)
        template = self.env.get_template(template_name)
        
        # Рендерим конфигурацию
        config_content = template.render(**context)
        
        # Создаем полную конфигурацию Xray
        full_config = self._create_full_config(config_content, overrides)
        
        return {
            "config.json": json.dumps(full_config, indent=2),
            "inbound.json": config_content
        }
    
    def _get_template_name(self, preset: str) -> str:
        """Возвращает имя шаблона для пресета."""
        preset_map = {
            "reality_tcp": "05_inbounds_02_reality_main.json.j2",
            "reality_grpc": "05_inbounds_02_reality_main.json.j2",
            "reality_xhttp": "05_inbounds_02_reality_main.json.j2",
            "vmess": "05_inbounds_02_xtls_main.json.j2",
            "trojan": "05_inbounds_02_xtls_main.json.j2"
        }
        return preset_map.get(preset, "05_inbounds_02_reality_main.json.j2")
    
    def _create_full_config(self, inbound_config: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Создает полную конфигурацию Xray."""
        
        # Парсим inbound конфигурацию
        try:
            inbound_data = json.loads(inbound_config)
        except json.JSONDecodeError:
            inbound_data = {"inbounds": []}
        
        # Базовая конфигурация
        config = {
            "log": {
                "loglevel": "info",
                "access": "/var/log/xray/access.log",
                "error": "/var/log/xray/error.log"
            },
            "inbounds": inbound_data.get("inbounds", []),
            "outbounds": [
                {
                    "protocol": "freedom",
                    "tag": "direct"
                }
            ],
            "routing": {
                "rules": [
                    {
                        "type": "field",
                        "ip": ["geoip:private"],
                        "outboundTag": "direct"
                    }
                ]
            }
        }
        
        return config
    
    def validate_config(self, config_content: str) -> bool:
        """
        Валидирует конфигурацию Xray.
        
        Args:
            config_content: JSON конфигурация
            
        Returns:
            True если конфигурация валидна
        """
        try:
            # Проверяем JSON синтаксис
            config = json.loads(config_content)
            
            # Создаем временный файл для валидации
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(config_content)
                temp_file = f.name
            
            try:
                # Запускаем xray -test для валидации
                result = subprocess.run(
                    ["xray", "test", "-c", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                return result.returncode == 0
                
            finally:
                # Удаляем временный файл
                os.unlink(temp_file)
                
        except (json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
