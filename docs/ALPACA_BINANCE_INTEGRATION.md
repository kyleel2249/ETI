# Alpaca and Binance integration guide

## Scope of this release

ETI includes REST adapters for Alpaca paper account/historical stock data and Binance Spot public market data. Binance private account access and testnet market orders are restricted to the Binance Spot Test Network. Alpaca paper order routing is independently opt-in. Live trading is not implemented and is hard-disabled.

## Credential safety

Store keys only in an untracked local .env file or a managed deployment secret store. .env.example contains variable names only. Never enable withdrawal permissions. Never commit credentials. Avoid exposing order-submission routes to the public internet; this starter does not yet provide user authentication/authorization for those routes.

## Data semantics

Every returned candle includes provider and venue context and UTC timestamps. Alpaca stock data is equity-market data with a USD quote currency and selected feed; feed access is subscription-dependent. Binance Spot data uses the symbol's quote asset. The adapter preserves the symbol and venue; it does not convert USDT to USD or imply that prices from different venues are fungible.

Binance order-book depth is a point-in-time snapshot. Its depth imbalance is a descriptive calculation, not a prediction or executable liquidity guarantee.

## Verification levels

- not_configured: credentials absent.
- configured_not_verified: credentials exist, but no authenticated request has been confirmed.
- connected: an authenticated or public connectivity request succeeded.
- error: the provider request failed; the response exposes an exception class, not secret-bearing request details.

Credentials and provider entitlements are user-specific. CI uses mocked responses and does not claim authenticated connectivity.

## Deferred capabilities

Persistent WebSocket stream management, complete historical candle storage, instrument-specification-driven sizing, authenticated user controls for order routes, order idempotency/reconciliation, and full portfolio/risk integration are not claimed as completed in this release.
