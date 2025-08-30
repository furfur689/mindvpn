from typing import Dict, Any, Optional
from .xray import XrayGenerator
from .singbox import SingboxGenerator

def render_inbound(
    protocol: str,
    port: int,
    preset: str,
    overrides: Dict[str, Any],
    node_caps: Dict[str, Any]
) -> Dict[str, str]:
    """
    Генерирует конфигурационные файлы для inbound.
    
    Args:
        protocol: Протокол (xray, singbox)
        port: Порт для inbound
        preset: Пресет конфигурации (reality_tcp, hysteria2, etc.)
        overrides: Дополнительные параметры
        node_caps: Возможности узла
        
    Returns:
        Словарь {filename: content} с конфигурационными файлами
    """
    
    if protocol.lower() == "xray":
        generator = XrayGenerator()
    elif protocol.lower() == "singbox":
        generator = SingboxGenerator()
    else:
        raise ValueError(f"Unsupported protocol: {protocol}")
    
    return generator.render_inbound(port, preset, overrides, node_caps)

def validate_config(
    protocol: str,
    config_content: str
) -> bool:
    """
    Валидирует конфигурацию.
    
    Args:
        protocol: Протокол (xray, singbox)
        config_content: Содержимое конфигурации
        
    Returns:
        True если конфигурация валидна
    """
    
    if protocol.lower() == "xray":
        generator = XrayGenerator()
    elif protocol.lower() == "singbox":
        generator = SingboxGenerator()
    else:
        raise ValueError(f"Unsupported protocol: {protocol}")
    
    return generator.validate_config(config_content)

__all__ = ["render_inbound", "validate_config"]
