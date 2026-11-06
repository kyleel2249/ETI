from datetime import datetime, timedelta, timezone
from typing import Any

from . import config


def _credentials() -> tuple[str, str]:
    if not config.ALPACA_API_KEY or not config.ALPACA_SECRET_KEY:
        raise RuntimeError("Alpaca credentials are not configured.")
    return config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY


def connection_status(check_account: bool = False) -> dict[str, Any]:
    configured = bool(config.ALPACA_API_KEY and config.ALPACA_SECRET_KEY)
    result = {
        "provider": "alpaca", "configured": configured,
        "environment": "paper" if config.ALPACA_PAPER else "live_not_supported",
        "paper_order_routing_enabled": config.ALPACA_PAPER_ORDER_ROUTING_ENABLED,
        "live_trading_enabled": False,
        "status": "configured_not_verified" if configured else "not_configured",
    }
    if check_account and configured:
        try:
            account = get_account()
            result.update({"status": "connected", "account_status": str(account.status),
                           "currency": str(account.currency),
                           "trading_blocked": bool(account.trading_blocked)})
        except Exception as exc:
            result.update({"status": "error", "error": type(exc).__name__})
    return result


def _trading_client():
    if not config.ALPACA_PAPER:
        raise RuntimeError("Only Alpaca paper mode is supported by this ETI release.")
    key, secret = _credentials()
    from alpaca.trading.client import TradingClient
    return TradingClient(key, secret, paper=True)


def get_account():
    return _trading_client().get_account()


def get_stock_bars(symbol: str, timeframe: str = "1Hour", limit: int = 100) -> dict[str, Any]:
    key, secret = _credentials()
    if not config.ALPACA_PAPER:
        raise RuntimeError("Live Alpaca configuration is not supported.")
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

    frames = {
        "1Min": TimeFrame.Minute, "5Min": TimeFrame(5, TimeFrameUnit.Minute),
        "15Min": TimeFrame(15, TimeFrameUnit.Minute), "1Hour": TimeFrame.Hour,
        "1Day": TimeFrame.Day,
    }
    if timeframe not in frames:
        raise ValueError("Unsupported Alpaca timeframe. Use 1Min, 5Min, 15Min, 1Hour or 1Day.")
    limit = max(1, min(int(limit), 1000))
    days = 7 if timeframe.endswith("Min") else (45 if timeframe == "1Hour" else 730)
    client = StockHistoricalDataClient(key, secret)
    request = StockBarsRequest(
        symbol_or_symbols=symbol.upper(), timeframe=frames[timeframe],
        start=datetime.now(timezone.utc) - timedelta(days=days), limit=limit,
        feed=config.ALPACA_DATA_FEED,
    )
    response = client.get_stock_bars(request)
    bars = response.data.get(symbol.upper(), [])
    return {
        "provider": "alpaca", "symbol": symbol.upper(), "asset_class": "equity",
        "venue": "alpaca", "quote_currency": "USD", "timeframe": timeframe,
        "data_feed": config.ALPACA_DATA_FEED,
        "candles": [{
            "timestamp": bar.timestamp.astimezone(timezone.utc).isoformat(),
            "open": float(bar.open), "high": float(bar.high),
            "low": float(bar.low), "close": float(bar.close),
            "volume": float(bar.volume),
        } for bar in bars],
    }


def submit_paper_market_order(symbol: str, quantity: float, side: str) -> dict[str, Any]:
    if not config.ALPACA_PAPER or not config.ALPACA_PAPER_ORDER_ROUTING_ENABLED:
        raise PermissionError("Alpaca paper order routing is disabled. Enable it explicitly after testing.")
    if config.LIVE_TRADING_ENABLED:
        raise PermissionError("Live trading is prohibited by this ETI release.")
    if quantity <= 0 or side.upper() not in {"BUY", "SELL"}:
        raise ValueError("Quantity must be positive and side must be BUY or SELL.")
    from alpaca.trading.enums import OrderSide, TimeInForce
    from alpaca.trading.requests import MarketOrderRequest
    client = _trading_client()
    order = client.submit_order(MarketOrderRequest(
        symbol=symbol.upper(), qty=quantity,
        side=OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
    ))
    return {"provider": "alpaca", "environment": "paper", "order_id": str(order.id),
            "symbol": order.symbol, "side": str(order.side), "status": str(order.status),
            "live_trading_enabled": False}
