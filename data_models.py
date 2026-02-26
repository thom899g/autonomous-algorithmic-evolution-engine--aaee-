"""
AAEE Data Models
Type-safe data structures for strategy representation and evolution tracking
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import hashlib
import json

class StrategyStatus(Enum):
    """Status of a trading strategy in the evolution pipeline"""
    GENERATED = "generated"
    BACKTESTING = "backtesting"
    BACKTEST_COMPLETE = "backtest_complete"
    LIVE_TESTING = "live_testing"
    ACTIVE = "active"
    ARCHIVED = "archived"
    FAILED = "failed"

class IndicatorType(Enum):
    """Supported technical indicators for strategy generation"""
    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    MACD = "macd"
    BBANDS = "bbands"
    ATR = "atr"
    STOCH = "stoch"

@dataclass
class TradingIndicator:
    """Individual technical indicator configuration"""
    type: IndicatorType
    parameters: Dict[str, float]
    weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Firestore-compatible dictionary"""
        return {
            'type': self.type.value,
            'parameters': self.parameters,
            'weight': self.weight
        }
    
    @classmethod
    def from_dict(cls, data: