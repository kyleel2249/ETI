# ETI Predictive Intelligence Specification

## Product objective

Build a rigorous, multi-asset forecasting system that estimates when an instrument may offer a favourable buy or sell opportunity and where price may travel over a specified horizon. ETI should generate actionable, timestamped forecast sequences and trade plans, while communicating uncertainty honestly. Exact future prices, dates and turning points are not knowable with certainty; the system must never promise them.

## Supported markets

Use provider adapters for cryptoassets/tokens (spot and derivatives separately), listed equities and ETFs, forex pairs, gold, silver and other supported commodities/metals, indices, and additional instruments only when reliable data and specifications exist. Keep quote currency, venue, trading calendar, session, contract multiplier, tick/lot size, leverage, funding, borrowability and market-hours metadata explicit. Never treat spot, futures, perpetuals, CFDs or equities as mechanically interchangeable.

## Forecast output contract

Every forecast must include:
- Instrument, venue, asset class, quote currency and data provenance.
- Generated-at timestamp, source-data cutoff timestamp, model/version and forecast horizon.
- Ordered timestamp/price sequences with a central path and lower/upper prediction bands.
- Forecast distribution or bear/base/bull scenario probabilities with assumptions.
- Estimated entry and exit windows and price zones.
- Potential local extrema windows and price zones, expressed probabilistically, never as guaranteed exact highs/lows.
- Invalidation conditions, stop proposal, risk/reward, expected holding period and transaction-cost estimates.
- Confidence/calibration status, data-quality flags, limitations and explicit abstention reasons.
- BUY, SELL, WAIT or NO-TRADE recommendation, interpreted according to position and instrument mechanics.

Support multiple horizons (intraday, daily, weekly and monthly where granularity permits). Use UTC as canonical time and Africa/Accra (GMT/UTC+0) for local presentation. Never output unjustified decimal precision.

## Forecasting methodology

1. Validate and normalize data; detect gaps, duplicates, outliers, stale timestamps, bad ticks, suspicious volume and venue divergence.
2. Build point-in-time features from OHLCV, volatility, trend/momentum, spreads, order-book depth and liquidity where licensed, correlations, funding/open interest, macro releases, earnings, tokenomics/on-chain metrics, and timestamped news/sentiment where available.
3. Establish simple baselines before advanced models. Candidate families may include statistical time-series models, gradient-boosted trees, regime/state models and sequence/deep-learning models. Select by out-of-sample performance, stability, calibration and operational cost—not novelty.
4. Produce probabilistic forecasts and calibrated prediction intervals.
5. Translate distributions into candidate entry/exit windows only where expected return after fees, spread, slippage and risk is favourable.
6. Pass every candidate through independent portfolio/risk gates. Risk has veto authority.
7. Persist every forecast, input cutoff, model version, decision and subsequent realized outcome for reproducibility and scoring.

## Evaluation and model governance

- Use chronological train/validation/test partitions and rolling walk-forward evaluation.
- Prevent look-ahead, target leakage, survivorship bias, data snooping and future information in features.
- Include delisted assets and point-in-time universes where relevant.
- Simulate realistic fees, spread, slippage, funding, borrow costs, latency, liquidity, partial fills, market hours and execution constraints.
- Evaluate forecast quality by instrument, asset class, horizon and regime using MAE/RMSE, directional accuracy, prediction-interval coverage/width, calibration and Brier/log loss for probabilistic events where applicable.
- Evaluate trading outcomes separately using expectancy, net return, drawdown, turnover, exposure, tail loss and risk-adjusted metrics.
- Compare against naive/random-walk and simple rule-based baselines; reject models that do not robustly beat relevant baselines after costs.
- Detect drift and strategy decay; trigger warnings, retraining review or automatic disablement when performance degrades.
- Maintain an immutable forecast ledger so past predictions cannot be silently rewritten after outcomes are known.

## Trade planning and execution

Each plan must include entry zone, expiry/time window, invalidation, stop, targets, sizing, maximum account risk, exposure impact, liquidity checks and reasons. A missed or expired entry must not be chased automatically. Recompute the plan when new data materially changes the forecast.

The current ETI release is research/paper-only. Any future automated trading must be separately reviewed and explicitly opted in, with least-privilege credentials, broker/exchange-specific controls, idempotent order handling, reconciliation, audit logs, emergency kill switch, withdrawal-disabled API keys where applicable, and extensive paper/live-canary testing. Forecast quality alone never authorizes execution.

## User experience

The dashboard should provide a forecast timeline with timestamped projected prices and uncertainty bands; entry/exit windows and scenario ranges in Accra time and UTC; separate forecast accuracy panels for each asset/horizon; model/data freshness indicators; regime warnings and reasons for WAIT/NO-TRADE; clear distinction between observed prices and projections; and downloadable forecast/backtest reports with model/data version references.

## Acceptance criteria

Do not mark predictive intelligence production-ready until:
1. Verified/licensed data adapters cover each claimed market and report provenance/freshness.
2. Forecast records persist reproducibly with timestamped sequences, intervals and scenarios.
3. Walk-forward, out-of-sample evaluation and leakage tests pass.
4. Backtests include realistic transaction/execution costs and are reproducible.
5. Calibration and forecast errors are reported by horizon/instrument; interval coverage is measured.
6. Risk veto, stale-data abstention, expired-entry handling and kill-switch tests pass.
7. Paper trading gathers meaningful forward results and demonstrates performance against baselines across multiple market regimes.
8. Documentation/UI never imply exactness or guaranteed profits.

Until all criteria are met, label the capability experimental or planned and keep it out of live execution.
