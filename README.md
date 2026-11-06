# Elite Trading Intelligence (ETI)

A safety-first, multi-asset market research, analysis and paper-trading foundation.

## Current implementation

- FastAPI application and responsive command-centre dashboard.
- Persistent SQLite storage for trader profiles, market snapshots, decisions and paper journal entries.
- Publicly documented trader-methodology seed library.
- Conservative market-readiness and position-sizing functions.
- **Alpaca adapter:** paper-account status, historical stock bars and opt-in paper market orders.
- **Binance adapter:** public Spot ping, exchange information, 24-hour ticker, klines and order-book snapshots; optional read-only Spot Test Network account access and separately gated testnet market orders.
- Provider credentials loaded from environment variables / local .env; no credentials are stored in source code.
- Live trading is hard-disabled in this release.

Provider functionality depends on credentials, account eligibility, market-data entitlements and network availability. A configured key is not proof of a successful authenticated connection. The provider status endpoint distinguishes configuration from verified account connectivity.

## Quick start (Python 3.11+)

    python -m venv .venv
    # Windows: .venv\Scripts\activate
    # macOS/Linux: source .venv/bin/activate
    python -m pip install -r requirements.txt
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000 and API docs at http://127.0.0.1:8000/docs.

## Provider configuration

Copy .env.example to .env in the project root. Add your own credentials locally; never paste keys into source code, chat, screenshots or GitHub.

### Alpaca

1. Create an Alpaca account and verify eligibility for your country and the services you intend to use.
2. Generate paper-trading credentials in the Alpaca dashboard.
3. Set ALPACA_API_KEY, ALPACA_SECRET_KEY, and keep ALPACA_PAPER=true.
4. The default feed is iex; access to other feeds depends on your Alpaca subscription.
5. Account status: GET /api/providers/alpaca/status?check_account=true.
6. Account details: GET /api/providers/alpaca/account.
7. Historical stock bars: GET /api/providers/alpaca/stocks/AAPL?timeframe=1Hour&limit=100.

Paper order routing is disabled by default. Only after validating your setup, set ALPACA_PAPER_ORDER_ROUTING_ENABLED=true locally and use POST /api/providers/alpaca/paper-orders with JSON containing symbol AAPL, side BUY and quantity 1. This route is paper-only and must not be exposed publicly without authentication and authorization.

### Binance

Public market-data endpoints require no API key:

- GET /api/providers/binance/status
- GET /api/providers/binance/exchange-info?symbol=BTCUSDT
- GET /api/providers/binance/ticker/BTCUSDT
- GET /api/providers/binance/klines?symbol=BTCUSDT&interval=1h&limit=100
- GET /api/providers/binance/order-book?symbol=BTCUSDT&limit=100

For private account testing, create a restricted Spot Test Network key at https://testnet.binance.vision/, set BINANCE_TESTNET_ENABLED=true, and configure BINANCE_API_KEY and BINANCE_SECRET_KEY. Testnet account access is GET /api/providers/binance/account.

Binance testnet order routing is separately disabled by default. To explicitly enable it in a local test environment, set BINANCE_TESTNET_ORDER_ROUTING_ENABLED=true and call POST /api/providers/binance/testnet-orders. Never use production trading permissions. Withdrawal permissions must remain disabled.

## Provider routes

See /docs for the complete OpenAPI contract. GET /api/providers/status provides provider configuration/connectivity status. Binance public status performs a public ping. Alpaca status only performs an authenticated account check when check_account=true.

## Safety and deployment

- LIVE_TRADING_ENABLED is hard-disabled in code; changing the environment variable cannot enable live execution.
- Alpaca order routing, even in paper mode, is separately opt-in and should only be enabled locally until authenticated access controls are implemented.
- Binance private access is restricted to the Spot Test Network in this release. Authenticated calls use the testnet host only.
- No withdrawals or production Binance orders are implemented.
- Do not expose private order routes to the public internet without user authentication, authorization, CSRF protections where applicable, audit logging and rate limits.
- Provider data is venue-specific. BTCUSDT is not automatically interchangeable with BTC/USD. Quote currency, venue and source timestamps must be preserved.
- The current adapters are REST-based. They do not claim persistent real-time WebSocket streaming. WebSocket streaming, full candle-history persistence, portfolio reconciliation, and advanced forecasting/backtesting remain follow-on work.
- Market data can be delayed, incomplete or unavailable. Never present cached data as live or forecasts as guaranteed.

## Tests

    PYTHONPATH=. python -m pytest -q
    python -m compileall -q app tests

Tests use mocks and do not require API secrets or provider availability.

## Predictive intelligence

See docs/PREDICTIVE_INTELLIGENCE.md. Forecasting remains a required future capability, not a validated production forecasting engine.
