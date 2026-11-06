from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import TraderProfile, MarketSnapshot, DecisionRecord, JournalEntry
from .schemas import SnapshotIn, JournalIn
from .seed import seed_traders
from .engine import assess_market, calculate_position_size
from .integrations.router import router as providers_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Elite Trading Intelligence", version="0.2.0",
              description="Safety-first multi-provider market research and paper-trading foundation. Live execution is disabled.")
app.include_router(providers_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def startup():
    with next(get_db()) as db:
        seed_traders(db)

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    context = {
        "request": request,
        "trader_count": db.query(TraderProfile).count(),
        "snapshot_count": db.query(MarketSnapshot).count(),
        "decision_count": db.query(DecisionRecord).count(),
        "journal_count": db.query(JournalEntry).count(),
        "live_enabled": False,
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)

@app.get("/health")
def health():
    return {"status": "ok", "service": "eti", "live_trading_enabled": False}

@app.get("/api/traders")
def list_traders(db: Session = Depends(get_db)):
    return [{"id": t.id, "name": t.name, "specialty": t.specialty,
             "methodology": t.methodology, "evidence_status": t.evidence_status,
             "net_worth": t.net_worth, "source_url": t.source_url}
            for t in db.query(TraderProfile).order_by(TraderProfile.name).all()]

@app.post("/api/market-snapshots")
def create_snapshot(payload: SnapshotIn, db: Session = Depends(get_db)):
    observed = payload.observed_at
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)
    else:
        observed = observed.astimezone(timezone.utc)
    row = MarketSnapshot(symbol=payload.symbol.upper(), price=payload.price,
        observed_at=observed, source=payload.source, bid=payload.bid,
        ask=payload.ask, timeframe=payload.timeframe)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "symbol": row.symbol, "observed_at": row.observed_at, "source": row.source}

@app.get("/api/market-snapshots/{symbol}/latest")
def latest_snapshot(symbol: str, db: Session = Depends(get_db)):
    row = db.query(MarketSnapshot).filter_by(symbol=symbol.upper()).order_by(MarketSnapshot.observed_at.desc()).first()
    if not row:
        raise HTTPException(404, "No sourced market snapshot found.")
    return {"id": row.id, "symbol": row.symbol, "price": row.price,
            "observed_at": row.observed_at, "source": row.source,
            "bid": row.bid, "ask": row.ask, "timeframe": row.timeframe}

@app.get("/api/market-readiness/{symbol}")
def market_readiness(symbol: str, db: Session = Depends(get_db)):
    row = db.query(MarketSnapshot).filter_by(symbol=symbol.upper()).order_by(MarketSnapshot.observed_at.desc()).first()
    result = assess_market(row)
    record = DecisionRecord(symbol=symbol.upper(), verdict=result["verdict"],
                            rationale="; ".join(result["rationale"]),
                            source_snapshot_id=row.id if row else None)
    db.add(record); db.commit()
    return {"symbol": symbol.upper(), **result, "live_execution": "disabled"}

@app.post("/api/risk/position-size")
def position_size(payload: dict):
    try:
        return calculate_position_size(
            float(payload["equity"]), float(payload["risk_fraction"]),
            float(payload["entry"]), float(payload["stop"]),
            float(payload.get("contract_multiplier", 1.0)))
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(422, str(exc))

@app.post("/api/journal")
def add_journal(payload: JournalIn, db: Session = Depends(get_db)):
    if payload.side.upper() not in ("BUY", "SELL"):
        raise HTTPException(422, "side must be BUY or SELL")
    if not payload.is_paper:
        raise HTTPException(403, "This release accepts paper journal entries only; live trading is disabled.")
    row = JournalEntry(symbol=payload.symbol.upper(), side=payload.side.upper(),
        entry_price=payload.entry_price, exit_price=payload.exit_price,
        risk_amount=payload.risk_amount, notes=payload.notes, is_paper=True)
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "status": "paper_journal_saved"}

@app.get("/api/decisions")
def decisions(db: Session = Depends(get_db)):
    return [{"id": d.id, "symbol": d.symbol, "verdict": d.verdict,
             "rationale": d.rationale, "created_at": d.created_at}
            for d in db.query(DecisionRecord).order_by(DecisionRecord.created_at.desc()).limit(50).all()]

@app.get("/api/system")
def system_status():
    return {"application": "ETI", "version": "0.2.0",
            "mode": "research_and_paper_foundation",
            "live_trading_enabled": False,
            "market_data": "Alpaca and Binance provider adapters available; credentials and entitlements determine connectivity",
            "status": "operational"}
