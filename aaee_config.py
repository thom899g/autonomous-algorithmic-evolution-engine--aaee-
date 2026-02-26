"""
AAEE Configuration Module
Centralized configuration management with environment validation
"""
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

@dataclass
class AAEEConfig:
    """AAEE Configuration Dataclass"""
    # Firestore Configuration
    firestore_project_id: str = os.getenv('FIRESTORE_PROJECT_ID', 'aaee-production')
    firestore_credentials_path: Optional[str] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Trading Configuration
    initial_population_size: int = 50
    max_generations: int = 1000
    mutation_rate: float = 0.15
    crossover_rate: float = 0.65
    elite_size: int = 5
    
    # Market Data
    default_timeframe: str = '1h'
    data_lookback_days: int = 90
    min_data_points: int = 500
    
    # Reinforcement Learning
    rl_learning_rate: float = 0.001
    rl_discount_factor: float = 0.95
    rl_episodes: int = 1000
    
    # Risk Management
    max_position_size_pct: float = 0.1
    max_drawdown_pct: float = 0.25
    stop_loss_pct: float = 0.02
    
    # Performance Thresholds
    min_sharpe_ratio: float = 1.0
    min_profit_factor: float = 1.5
    max_mdd_threshold: float = 0.15
    
    # Logging Configuration
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = 'aaee_evolution.log'
    
    # Validation flags
    _validated: bool = field(default=False, init=False)
    
    def validate(self) -> None:
        """Validate configuration parameters"""
        if not self.firestore_project_id:
            raise ValueError("FIRESTORE_PROJECT_ID must be set")
        
        if self.mutation_rate < 0 or self.mutation_rate > 1:
            raise ValueError(f"Mutation rate {self.mutation_rate} must be between 0 and 1")
            
        if self.max_position_size_pct <= 0 or self.max_position_size_pct > 1:
            raise ValueError(f"Max position size {self.max_position_size_pct} must be between 0 and 1")
            
        if self.max_drawdown_pct <= 0 or self.max_drawdown_pct > 1:
            raise ValueError(f"Max drawdown {self.max_drawdown_pct} must be between 0 and 1")
            
        self._validated = True
        logging.info("Configuration validated successfully")

config = AAEEConfig()

def initialize_firestore() -> firestore.firestore.Client:
    """Initialize Firestore connection with error handling"""
    try:
        if config.firestore_credentials_path and os.path.exists(config.firestore_credentials_path):
            cred = credentials.Certificate(config.firestore_credentials_path)
            firebase_admin.initialize_app(cred, {
                'projectId': config.firestore_project_id
            })
        else:
            # Use default credentials (for GCP environments)
            firebase_admin.initialize_app()
        
        db = firestore.client()
        logging.info(f"Firestore initialized for project: {config.firestore_project_id}")
        return db
    except Exception as e:
        logging.error(f"Firestore initialization failed: {e}")
        raise

def setup_logging() -> None:
    """Configure logging for AAEE system"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.log_level))
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # File handler
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Root logger configuration
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[console_handler, file_handler]
    )
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logging.info(f"Logging configured. Level: {config.log_level}, File: {config.log_file}")