from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
import pytest
from app.engine import assess_market, calculate_position_size

def test_missing_snapshot_is_insufficient():
    assert assess_market(None)["verdict"] == "INSUFFICIENT_DATA"

def test_stale_snapshot_is_no_trade():
    s = SimpleNamespace(observed_at=datetime.now(timezone.utc)-timedelta(hours=1),
                        bid=99.9, ask=100.1, price=100)
    assert assess_market(s)["verdict"] == "NO_TRADE"

def test_fresh_single_quote_waits_for_confirmation():
    s = SimpleNamespace(observed_at=datetime.now(timezone.utc),
                        bid=99.99, ask=100.01, price=100)
    result = assess_market(s)
    assert result["verdict"] == "WAIT_FOR_CONFIRMATION"
    assert result["confidence"] == 0

def test_invalid_quote_rejected():
    s = SimpleNamespace(observed_at=datetime.now(timezone.utc),
                        bid=101, ask=100, price=100)
    assert assess_market(s)["verdict"] == "NO_TRADE"

def test_position_size():
    r = calculate_position_size(10000, .005, 2000, 1990)
    assert r["risk_cash"] == 50
    assert r["units"] == 5

def test_risk_cap_enforced():
    with pytest.raises(ValueError):
        calculate_position_size(10000, .02, 2000, 1990)
