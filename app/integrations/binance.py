import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from . import config


def _base_url() -> str:
    return config.BINANCE_TESTNET_BASE_URL if config.BINANCE_TESTNET_ENABLED else config.BINANCE_PUBLIC_BASE_URL


def _request(method: str, path: str, params: dict[str, Any] | None = None, signed: bool = False) -> Any:
    values = dict(params or {})
    headers = {}
    if signed:
        if not config.BINANCE_TESTNET_ENABLED:
            raise PermissionError("Authenticated ETI Binance operations are restricted to the Spot Test Network.")
        if not config.BINANCE_API_KEY or not config.BINANCE_SECRET_KEY:
            raise RuntimeError("Binance testnet credentials are not configured.")
        values.setdefault("recvWindow", 5000)
        values["timestamp"] = int(time.time() * 1000)
        query = urlencode(values, doseq=True)
        values["signature"] = hmac.new(config.BINANCE_SECRET_KEY.encode(), query.encode(), hashlib.sha256).hexdigest()
        headers["X-MBX-APIKEY"] = config.BINANCE_API_KEY
    with httpx.Client(timeout=config.REQUEST_TIMEOUT_SECONDS) as client:
        response = client.request(method, _base_url() + path, params=values, headers=headers)
        response.raise_for_status()
        return response.json()


def public_status() -> dict[str, Any]:
    try:
        _request("GET", "/api/v3/ping")
        return {"provider": "binance", "public_market_data": "connected",
                "environment": "spot_testnet" if config.BINANCE_TESTNET_ENABLED else "production_public_data",
                "private_account_configured": bool(config.BINANCE_API_KEY and config.BINANCE_SECRET_KEY),
                "testnet_order_routing_enabled": config.BINANCE_TESTNET_ORDER_ROUTING_ENABLED,
                "live_trading_enabled": False}
    except Exception as exc:
        return {"provider": "binance", "public_market_data": "error",
                "error": type(exc).__name__, "live_trading_enabled": False}


def exchange_info(symbol: str | None = None) -> dict[str, Any]:
    params = {"symbol": symbol.upper()} if symbol else None
    return _request("GET", "/api/v3/exchangeInfo", params)


def ticker_24h(symbol: str) -> dict[str, Any]:
    return _request("GET", "/api/v3/ticker/24hr", {"symbol": symbol.upper()})


def order_book(symbol: str, limit: int = 100) -> dict[str, Any]:
    allowed = {5, 10, 20, 50, 100, 500, 1000, 5000}
    if limit not in allowed:
        raise ValueError(f"Order-book limit must be one of {sorted(allowed)}.")
    raw = _request("GET", "/api/v3/depth", {"symbol": symbol.upper(), "limit": limit})
    bids = [[float(p), float(q)] for p, q in raw.get("bids", [])]
    asks = [[float(p), float(q)] for p, q in raw.get("asks", [])]
    best_bid = bids[0][0] if bids else None
    best_ask = asks[0][0] if asks else None
    spread = best_ask - best_bid if best_bid is not None and best_ask is not None else None
    bid_qty = sum(q for _, q in bids)
    ask_qty = sum(q for _, q in asks)
    total = bid_qty + ask_qty
    return {"provider": "binance", "symbol": symbol.upper(), "last_update_id": raw.get("lastUpdateId"),
            "bids": bids, "asks": asks, "best_bid": best_bid, "best_ask": best_ask,
            "spread": spread, "bid_quantity": bid_qty, "ask_quantity": ask_qty,
            "depth_imbalance": ((bid_qty - ask_qty) / total) if total else None,
            "interpretation": "snapshot_only; not a guaranteed executable price"}


def klines(symbol: str, interval: str = "1h", limit: int = 100) -> dict[str, Any]:
    intervals = {"1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"}
    if interval not in intervals:
        raise ValueError("Unsupported Binance kline interval.")
    limit = max(1, min(int(limit), 1000))
    rows = _request("GET", "/api/v3/klines", {"symbol": symbol.upper(), "interval": interval, "limit": limit})
    from datetime import datetime, timezone
    candles = [{
        "timestamp": datetime.fromtimestamp(row[0] / 1000, tz=timezone.utc).isoformat(),
        "open": float(row[1]), "high": float(row[2]), "low": float(row[3]),
        "close": float(row[4]), "volume": float(row[5]),
        "close_timestamp": datetime.fromtimestamp(row[6] / 1000, tz=timezone.utc).isoformat(),
        "quote_volume": float(row[7]), "trade_count": int(row[8]),
    } for row in rows]
    quote = next((q for q in ("USDT", "USDC", "BUSD", "FDUSD", "BTC", "ETH", "BNB", "USD") if symbol.upper().endswith(q)), "unknown")
    return {"provider": "binance", "symbol": symbol.upper(), "asset_class": "crypto_spot",
            "venue": "binance_spot", "quote_currency": quote,
            "timeframe": interval, "candles": candles}


def account() -> dict[str, Any]:
    if not config.BINANCE_TESTNET_ENABLED:
        raise PermissionError("Private Binance account access is restricted to testnet in this release.")
    raw = _request("GET", "/api/v3/account", signed=True)
    return {"provider": "binance", "environment": "spot_testnet",
            "can_trade": bool(raw.get("canTrade")), "can_withdraw": False,
            "balances": [{"asset": x["asset"], "free": x["free"], "locked": x["locked"]}
                         for x in raw.get("balances", []) if float(x.get("free", 0)) or float(x.get("locked", 0))],
            "live_trading_enabled": False}


def submit_testnet_market_order(symbol: str, side: str, quantity: str) -> dict[str, Any]:
    if not config.BINANCE_TESTNET_ENABLED or not config.BINANCE_TESTNET_ORDER_ROUTING_ENABLED:
        raise PermissionError("Binance testnet order routing is disabled. Enable it explicitly after testing.")
    if side.upper() not in {"BUY", "SELL"}:
        raise ValueError("side must be BUY or SELL")
    if not quantity or float(quantity) <= 0:
        raise ValueError("quantity must be positive")
    result = _request("POST", "/api/v3/order",
                      {"symbol": symbol.upper(), "side": side.upper(), "type": "MARKET", "quantity": quantity},
                      signed=True)
    return {"provider": "binance", "environment": "spot_testnet", "order": result,
            "live_trading_enabled": False}
