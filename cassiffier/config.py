"""Configuration management for CAssIffier."""

import json
from pathlib import Path


class Config:
    """Configuration manager for CAssIffier."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        "confidence_threshold": 0.7,
        "max_duration": 30.0,  # seconds, files longer than this are likely not one-shots
        "min_duration": 0.01,  # seconds, very short files might be corrupted
        "use_ml_classifier": True,
        "ml_model_path": "models/classifier.joblib",
        "database_path": "cassiffier.db",
        "review_folder_name": "⚠_Review",
        "scan_extensions": [".wav", ".mp3"],
        "enable_genre_detection": True,
        "genre_confidence_threshold": 0.6,
        "duplicate_action": "ask",  # ask, skip, keep_both, delete
    }
    
    def __init__(self, config_path=None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config file. If None, uses defaults.
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path
        
        if config_path and Path(config_path).exists():
            self.load(config_path)
    
    def load(self, config_path):
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to config file.
        """
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            self.config.update(user_config)
        self.config_path = config_path
    
    def save(self, config_path=None):
        """Save configuration to JSON file.
        
        Args:
            config_path: Path to save config. Uses self.config_path if None.
        """
        path = config_path or self.config_path
        if not path:
            raise ValueError("No config path specified")
        
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        """Get configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
            
        Returns:
            Configuration value.
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value.
        
        Args:
            key: Configuration key.
            value: Configuration value.
        """
        self.config[key] = value
    
    def __getitem__(self, key):
        """Get configuration value using dict-like access."""
        return self.config[key]
    
    def __setitem__(self, key, value):
        """Set configuration value using dict-like access."""
        self.config[key] = value
