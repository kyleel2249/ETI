import os
from dotenv import load_dotenv

load_dotenv()

def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "").strip()
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "").strip()
ALPACA_PAPER = env_bool("ALPACA_PAPER", True)
ALPACA_PAPER_ORDER_ROUTING_ENABLED = env_bool("ALPACA_PAPER_ORDER_ROUTING_ENABLED", False)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "").strip()
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "").strip()
BINANCE_TESTNET_ENABLED = env_bool("BINANCE_TESTNET_ENABLED", False)
BINANCE_TESTNET_ORDER_ROUTING_ENABLED = env_bool("BINANCE_TESTNET_ORDER_ROUTING_ENABLED", False)
LIVE_TRADING_ENABLED = False
BINANCE_PUBLIC_BASE_URL = os.getenv("BINANCE_PUBLIC_BASE_URL", "https://api.binance.com").rstrip("/")
BINANCE_TESTNET_BASE_URL = "https://testnet.binance.vision"
ALPACA_DATA_FEED = os.getenv("ALPACA_DATA_FEED", "iex").lower()
REQUEST_TIMEOUT_SECONDS = float(os.getenv("PROVIDER_TIMEOUT_SECONDS", "12"))
