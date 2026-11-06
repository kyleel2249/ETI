from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from . import alpaca, binance
from ..database import get_db
from ..models import MarketSnapshot

router = APIRouter(prefix="/api/providers", tags=["Market Data Providers"])


class PaperOrderIn(BaseModel):
    symbol: str = Field(min_length=2, max_length=30)
    side: str
    quantity: float = Field(gt=0)


class BinanceTestnetOrderIn(BaseModel):
    symbol: str = Field(min_length=5, max_length=20)
    side: str
    quantity: str = Field(min_length=1, max_length=30)


@router.get("/status")
def provider_status():
    return {"alpaca": alpaca.connection_status(), "binance": binance.public_status(),
            "live_trading_enabled": False}


@router.get("/alpaca/status")
def alpaca_status(check_account: bool = False):
    return alpaca.connection_status(check_account=check_account)


@router.get("/alpaca/account")
def alpaca_account():
    try:
        account = alpaca.get_account()
        return {"provider": "alpaca", "environment": "paper", "status": str(account.status),
                "currency": str(account.currency), "equity": str(account.equity),
                "buying_power": str(account.buying_power), "trading_blocked": bool(account.trading_blocked),
                "live_trading_enabled": False}
    except Exception as exc:
        raise HTTPException(503, f"Alpaca account unavailable: {type(exc).__name__}") from exc


@router.get("/alpaca/stocks/{symbol}")
def alpaca_stock_bars(symbol: str, timeframe: str = "1Hour", limit: int = Query(100, ge=1, le=1000)):
    try:
        return alpaca.get_stock_bars(symbol, timeframe, limit)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"Alpaca data request failed: {type(exc).__name__}") from exc


@router.post("/alpaca/paper-orders")
def alpaca_paper_order(payload: PaperOrderIn):
    try:
        return alpaca.submit_paper_market_order(payload.symbol, payload.quantity, payload.side)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"Alpaca paper order failed: {type(exc).__name__}") from exc


@router.get("/binance/status")
def binance_status():
    return binance.public_status()


@router.get("/binance/exchange-info")
def binance_exchange_info(symbol: str | None = None):
    try:
        return binance.exchange_info(symbol)
    except Exception as exc:
        raise HTTPException(502, f"Binance exchange information unavailable: {type(exc).__name__}") from exc


@router.get("/binance/ticker/{symbol}")
def binance_ticker(symbol: str):
    try:
        return binance.ticker_24h(symbol)
    except Exception as exc:
        raise HTTPException(502, f"Binance ticker request failed: {type(exc).__name__}") from exc


@router.get("/binance/klines")
def binance_klines(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    try:
        result = binance.klines(symbol, interval, limit)
        if result["candles"]:
            latest = result["candles"][-1]
            row = MarketSnapshot(symbol=f"BINANCE:{symbol.upper()}", price=latest["close"],
                observed_at=datetime.fromisoformat(latest["timestamp"]),
                source="binance", timeframe=interval)
            db.add(row)
            db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(502, f"Binance kline request failed: {type(exc).__name__}") from exc


@router.get("/binance/order-book")
def binance_order_book(symbol: str = "BTCUSDT", limit: int = 100):
    try:
        return binance.order_book(symbol, limit)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"Binance order-book request failed: {type(exc).__name__}") from exc


@router.get("/binance/account")
def binance_account():
    try:
        return binance.account()
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(503, f"Binance testnet account unavailable: {type(exc).__name__}") from exc


@router.post("/binance/testnet-orders")
def binance_testnet_order(payload: BinanceTestnetOrderIn):
    try:
        return binance.submit_testnet_market_order(payload.symbol, payload.side, payload.quantity)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"Binance testnet order failed: {type(exc).__name__}") from exc
