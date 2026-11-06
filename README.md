# Elite Trading Intelligence (ETI)

A safety-first, deployable foundation for an AI-assisted trading research and decision-support platform.

## Current implementation
- FastAPI web application with a responsive command-centre dashboard.
- Persistent SQLite storage for trader profiles, market snapshots, decisions and trade journal entries.
- Curated elite-trader methodology library. Documented facts are separated from inferred strategy interpretations.
- Market-readiness engine that can return `STRONG_TRADE_CONDITIONS`, `TRADEABLE_WITH_CAUTION`, `WAIT_FOR_CONFIRMATION`, `NO_TRADE`, or `INSUFFICIENT_DATA`.
- Explicit stale/missing-data rejection. The app does not invent live prices or technical indicators.
- Risk sizing calculator and portfolio risk guardrails.
- Paper-trading journal endpoints.
- Live execution is deliberately disabled; no broker credentials or order-routing code are included in this starter.

## Quick start (Python 3.11+)
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs

## Docker
```bash
docker compose up --build
```

## Tests
```bash
PYTHONPATH=. python -m pytest -q
```

## Data integrity and safety
- A market snapshot must include a source, timestamp, price and instrument.
- Snapshots older than the configured freshness window are rejected for tradeable verdicts.
- Signals are decision-support, not guarantees or personalised investment advice.
- `LIVE_TRADING_ENABLED` is hard-disabled in this release. Do not enable live trading by simply changing an environment variable; a separately reviewed broker adapter, permissions model, reconciliation, kill switch and end-to-end tests are required.
- Never put API keys, broker passwords, exchange secrets or wallet seed phrases in source control.

## Deployment
The included Dockerfile and `render.yaml` provide a straightforward deployment path on a container host. Configure a persistent disk for `/data` and set `DATABASE_URL=sqlite:////data/eti.db`, or use a managed PostgreSQL service and a compatible SQLAlchemy URL.

## Planned integration boundary
Implement provider adapters only after choosing and validating licensed market-data sources. Provider interfaces must report source, timestamp, instrument, quote currency, bid/ask and data quality. Do not label delayed or cached prices as live.

## Project identity and safety

This project is **ETI — Elite Trading Intelligence**. It is a research, decision-support, and paper-trading foundation. It does not promise profits or loss-free trading. Market signals require verified, sufficiently fresh market data; missing or stale data must result in no trade. Live brokerage execution is intentionally disabled in this foundation.

## Continuous integration

GitHub Actions runs Python compilation and the automated test suite on pushes and pull requests targeting `main`.

## Predictive intelligence — core product requirement

ETI's target capability is a multi-asset, probabilistic forecasting and trade-planning engine. It must analyse supported cryptoassets/tokens, equities, forex, precious metals (including gold and silver), indices and other instruments for multiple forecast horizons.

For each instrument and horizon, the engine should estimate:
- The most likely buy/entry and sell/exit windows, with dates and timestamps (UTC plus Africa/Accra/GMT display).
- Forecast price paths as ordered timestamp/price sequences, not just a single target.
- Expected price ranges and calibrated prediction intervals, including plausible downside/upside scenarios.
- Potential support/resistance zones and conditional local-high/local-low windows, with probability and uncertainty; never label a forecast turning point as a guaranteed exact high or low.
- Expected entry zone, invalidation level, stop, targets, transaction costs, liquidity and risk/reward.
- A clear BUY / SELL / WAIT / NO-TRADE recommendation, rationale, model version, data timestamp, forecast horizon and confidence/calibration metadata.

Forecasts must use validated historical and current data, with suitable OHLCV, volatility, liquidity, spreads, macroeconomic, fundamental, market-structure and timestamped news/sentiment inputs where licensed and available. Every input must carry provenance, timestamp, market, currency and quality metadata. Missing, stale, manipulated, inconsistent or insufficient data must reduce confidence or force abstention.

Model governance is mandatory: use chronological splits, walk-forward and strictly out-of-sample tests; prevent look-ahead, survivorship, leakage and delisted-asset bias; simulate realistic fees, spread, slippage, funding, borrow costs, latency, liquidity and execution constraints; compare with simple baselines; report forecast error, directional accuracy, interval coverage, calibration, drawdown, expectancy and risk-adjusted returns by asset, horizon and market regime. Detect drift and strategy decay, and retain immutable forecast snapshots for later scoring.

Forecasts must show distributions, ranges and alternative scenarios—not false precision. A forecast is not a trade instruction by itself: the independent risk engine must approve each proposed trade and may veto it. Start in research and paper-trading mode. Automated live execution remains disabled until separately reviewed, explicitly opted-in, broker-specific controls, reconciliation, a kill switch, audit trail and extensive validation are implemented.

See [docs/PREDICTIVE_INTELLIGENCE.md](docs/PREDICTIVE_INTELLIGENCE.md) for the detailed functional and acceptance specification.

## Current implementation boundary

The current release is a foundation: dashboard, trader-methodology seed library, conservative market-readiness checks, risk sizing, paper journal, and container deployment files. The predictive forecasting engine described above is a required future capability, not yet implemented or validated. Real-time market-data integrations, advanced backtesting, portfolio optimization, multi-agent council orchestration, and live brokerage execution are also not represented as completed features.
