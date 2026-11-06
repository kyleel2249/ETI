from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class SnapshotIn(BaseModel):
    symbol: str = Field(min_length=2, max_length=40)
    price: float = Field(gt=0)
    observed_at: datetime
    source: str = Field(min_length=2, max_length=200)
    bid: float | None = Field(default=None, gt=0)
    ask: float | None = Field(default=None, gt=0)
    timeframe: str = "unknown"

class JournalIn(BaseModel):
    symbol: str
    side: str
    entry_price: float = Field(gt=0)
    exit_price: float | None = Field(default=None, gt=0)
    risk_amount: float = Field(gt=0)
    notes: str = ""
    is_paper: bool = True

class TraderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    specialty: str
    methodology: str
    evidence_status: str
    net_worth: str
    source_url: str
