from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.integrations import binance, config


def test_binance_interval_validation_happens_before_network():
    with pytest.raises(ValueError):
        binance.klines("BTCUSDT", "2w", 10)


def test_binance_order_book_limit_validation():
    with pytest.raises(ValueError):
        binance.order_book("BTCUSDT", 17)


def test_binance_private_operations_refuse_production_mode(monkeypatch):
    monkeypatch.setattr(config, "BINANCE_TESTNET_ENABLED", False)
    with pytest.raises(PermissionError):
        binance.account()


def test_binance_testnet_order_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr(config, "BINANCE_TESTNET_ENABLED", True)
    monkeypatch.setattr(config, "BINANCE_TESTNET_ORDER_ROUTING_ENABLED", False)
    with pytest.raises(PermissionError):
        binance.submit_testnet_market_order("BTCUSDT", "BUY", "0.001")


def test_alpaca_paper_order_is_disabled_by_default(monkeypatch):
    from app.integrations import alpaca
    monkeypatch.setattr(config, "ALPACA_PAPER", True)
    monkeypatch.setattr(config, "ALPACA_PAPER_ORDER_ROUTING_ENABLED", False)
    with pytest.raises(PermissionError):
        alpaca.submit_paper_market_order("AAPL", 1, "BUY")


def test_provider_status_route_reports_live_disabled():
    client = TestClient(app)
    with patch("app.integrations.binance.public_status", return_value={"provider": "binance", "public_market_data": "connected"}):
        response = client.get("/api/providers/status")
    assert response.status_code == 200
    assert response.json()["live_trading_enabled"] is False
