from sqlalchemy.orm import Session
from .models import TraderProfile

TRADERS = [
("Jason Berry","Short-term momentum and relative-value futures","Publicly reported short-term momentum, time-of-day structural setups and spreads. Exact proprietary rules are not public; treat reconstructed rules as hypotheses.","Reported claims; verify primary records","Not reliably established","https://chatwithtraders.com/"),
("Rick Bandazian Jr.","Event-driven equities","Publicly described event research, merger/deal analysis, rapid execution and time-based risk controls. Verify reported performance independently.","Reported claims; partial verification described by interviewer","Not reliably established","https://excessreturnspod.substack.com/"),
("Linda Bradford Raschke","Technical futures, equities and swing trading","Publicly documented price-action and momentum setups including Holy Grail, Turtle Soup and 80-20 patterns.","Books/interviews; individual results vary","Not reliably established","https://www.lbrgroup.com/"),
("Paul Tudor Jones","Global macro","Macro trends, technical confirmation, asymmetric opportunities and strict loss control.","Public career; personal net worth estimates vary by date","Public estimates vary; verify current source","https://www.tudor.com/"),
("Larry Hite","Systematic trend following","Rules-based trend following, position sizing, diversification and predefined exits.","Public career; historical fund records require context","Not reliably established","https://www.amazon.com/s?k=The+Rule+Larry+Hite"),
("Silvan Abicht","Systematic forex and stock trading","Systematic execution and risk/drawdown control; distinguish competition results from longer track records.","Reported track record; independently verify statements","Not reliably established","https://www.wsot.com/fame"),
("Joachim Klindworth","Algorithmic equities","Algorithmic and multi-strategy trading; exact strategy implementation is not fully public.","Competition record; limited methodology disclosure","Not reliably established","https://www.wsot.com/fame"),
("Ignacio Colón Bolea","Risk control","Competition risk-control result; do not infer undisclosed proprietary rules.","Competition result","Not reliably established","https://www.wsot.com/fame"),
("Aatu Kokkila","Macro and event-driven research","Macro research and event analysis; strategy-level records must not be represented as personal wealth.","Strategy-level reported record","Not reliably established","https://www.wsot.com/fame"),
("Joachim Moser","Systematic multi-strategy","Public descriptions include systematic portfolio approaches; verify exact methodology and performance before replication.","Limited public evidence","Not reliably established","https://www.wsot.com/fame"),
]
def seed_traders(db: Session):
    for row in TRADERS:
        if not db.query(TraderProfile).filter_by(name=row[0]).first():
            db.add(TraderProfile(name=row[0], specialty=row[1], methodology=row[2],
                                 evidence_status=row[3], net_worth=row[4], source_url=row[5]))
    db.commit()
