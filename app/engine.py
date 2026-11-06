from datetime import datetime, timezone
import os

MAX_AGE = int(os.getenv("DATA_MAX_AGE_SECONDS", "300"))

def assess_market(snapshot, now=None):
    now = now or datetime.now(timezone.utc)
    if snapshot is None:
        return {"verdict": "INSUFFICIENT_DATA", "confidence": 0,
                "rationale": ["No verified market snapshot is available. No price or signal has been invented."]}
    observed = snapshot.observed_at
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)
    age = (now - observed).total_seconds()
    if age < -30:
        return {"verdict": "NO_TRADE", "confidence": 0,
                "rationale": ["Snapshot timestamp is in the future; data integrity check failed."]}
    if age > MAX_AGE:
        return {"verdict": "NO_TRADE", "confidence": 0,
                "rationale": [f"Market data is stale ({int(age)} seconds old; limit {MAX_AGE})."]}
    if snapshot.bid is not None and snapshot.ask is not None:
        if snapshot.ask < snapshot.bid:
            return {"verdict": "NO_TRADE", "confidence": 0,
                    "rationale": ["Invalid quote: ask is below bid."]}
        spread_pct = ((snapshot.ask - snapshot.bid) / snapshot.price) * 100
        if spread_pct > 0.5:
            return {"verdict": "NO_TRADE", "confidence": 0,
                    "rationale": [f"Quoted spread is unusually wide ({spread_pct:.3f}% of price)."]}
    return {"verdict": "WAIT_FOR_CONFIRMATION", "confidence": 0,
            "rationale": [
                "A fresh sourced price is available, but one snapshot cannot establish trend, momentum, liquidity or a valid entry.",
                "Provide validated OHLCV history, spread and instrument specifications before strategy assessment."
            ]}

def calculate_position_size(equity, risk_fraction, entry, stop, contract_multiplier=1.0):
    if equity <= 0 or not (0 < risk_fraction <= 0.01) or entry <= 0 or stop <= 0:
        raise ValueError("Invalid sizing inputs; risk fraction must be >0 and <=1%.")
    distance = abs(entry - stop)
    if distance == 0:
        raise ValueError("Entry and stop must differ.")
    risk_cash = equity * risk_fraction
    units = risk_cash / (distance * contract_multiplier)
    return {"risk_cash": round(risk_cash, 2), "units": units, "stop_distance": distance}
