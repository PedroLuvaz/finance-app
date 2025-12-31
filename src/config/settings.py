"""
Configurações centralizadas do aplicativo.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List
import json


@dataclass
class DatabaseConfig:
    """Configurações do banco de dados."""
    name: str = "financas.db"
    
    @property
    def path(self) -> Path:
        return Settings.get_data_dir() / self.name


@dataclass
class ThemeConfig:
    """Configurações de tema."""
    mode: str = "dark"  # "dark" ou "light"
    color_theme: str = "blue"
    
    # Cores personalizadas
    colors: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#3498db",
        "success": "#27ae60",
        "danger": "#e74c3c",
        "warning": "#f39c12",
        "info": "#17a2b8",
        "secondary": "#6c757d",
    })


@dataclass  
class AppConfig:
    """Configurações gerais do aplicativo."""
    name: str = "Controle de Finanças"
    version: str = "2.0.0"
    window_width: int = 1200
    window_height: int = 750
    min_width: int = 1000
    min_height: int = 600


class Settings:
    """Gerenciador de configurações do aplicativo."""
    
    _instance = None
    _config_file = "config.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa as configurações."""
        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.theme = ThemeConfig()
        self._load_config()
    
    @staticmethod
    def get_base_dir() -> Path:
        """Retorna o diretório base do projeto."""
        return Path(__file__).parent.parent.parent
    
    @staticmethod
    def get_data_dir() -> Path:
        """Retorna o diretório de dados."""
        data_dir = Settings.get_base_dir() / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    @staticmethod
    def get_config_dir() -> Path:
        """Retorna o diretório de configurações."""
        config_dir = Settings.get_base_dir() / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    def _load_config(self):
        """Carrega configurações do arquivo JSON."""
        config_path = self.get_config_dir() / self._config_file
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'theme' in data:
                        self.theme.mode = data['theme'].get('mode', self.theme.mode)
            except Exception:
                pass
    
    def save_config(self):
        """Salva configurações no arquivo JSON."""
        config_path = self.get_config_dir() / self._config_file
        data = {
            'theme': {
                'mode': self.theme.mode
            }
        }
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def set_theme_mode(self, mode: str):
        """Define o modo do tema."""
        self.theme.mode = mode
        self.save_config()


# Singleton para acesso global
settings = Settings()
