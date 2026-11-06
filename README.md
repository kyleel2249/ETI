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

## Current implementation boundary

This initial release includes the dashboard, persistence models, trader-methodology seed library, conservative market-readiness checks, risk sizing, paper journal, and container deployment files. Real-time market-data integrations, advanced backtesting, portfolio optimization, multi-agent council orchestration, and live brokerage execution are not represented as completed features.
