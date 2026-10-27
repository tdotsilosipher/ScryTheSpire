# backend/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from models import Run, CardPick, RelicPick
from rate_limit import rate_limit

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    # 30 requests/minute GLOBALLY across all /stats/* endpoints.
    dependencies=[Depends(rate_limit(limit=30, window=60, scope="stats"))],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Starter Cards
IGNORE_CARDS = [
    "CARD.ASCENDERS_BANE",
    "CARD.STRIKE_IRONCLAD",
    "CARD.DEFEND_IRONCLAD",
    "CARD.BASH",
    "CARD.STRIKE_SILENT",
    "CARD.DEFEND_SILENT",
    "CARD.NEUTRALIZE",
    "CARD.SURVIVOR",
    "CARD.STRIKE_REGENT",
    "CARD.DEFEND_REGENT",
    "CARD.FALLING_STAR",
    "CARD.VENERATE",
    "CARD.STRIKE_NECROBINDER",
    "CARD.DEFEND_NECROBINDER",
    "CARD.BODYGUARD",
    "CARD.UNLEASH",
    "CARD.STRIKE_DEFECT",
    "CARD.DEFEND_DEFECT",
    "CARD.ZAP",
    "CARD.DUALCAST"
]

# Starter Relics
IGNORE_RELICS = [
    "RELIC.BURNING_BLOOD",
    "RELIC.RING_OF_THE_SNAKE",
    "RELIC.DIVINE_RIGHT",
    "RELIC.BOUND_PHYLACTERY",
    "RELIC.CRACKED_CORE"
]

# Character Stats
@router.get("/characterWinrate",
    summary="Winrate By Character",
    description="Returns win rate, total run count, and total win for each character."
)
def winrate_by_character(db: Session = Depends(get_db)):
    chars = db.query(Run.character).distinct().all()
    result = []
    for (char,) in chars:
        total = db.query(Run).filter(Run.character == char).count()
        wins = db.query(Run).filter(Run.character == char, Run.victory == True).count()
        result.append({
            "character": char,
            "total_runs": total,
            "wins": wins,
            "win_rate": wins / total if total > 0 else 0
        })
    return result

# Cards
@router.get(
    "/topCards",
    summary="Most Picked Cards",
    description="Returns most picked cards sorted by descending pick count, starter cards are excluded."
)
def top_cards(limit: int = 100, db: Session = Depends(get_db)):
    picks = db.query(
        CardPick.card_id,
        func.count(CardPick.id).label("pick_count")
    ).filter(
        CardPick.was_picked == True,
        CardPick.card_id.not_in(list(IGNORE_CARDS))
    ).group_by(CardPick.card_id)\
     .order_by(func.count(CardPick.id).desc())\
     .limit(limit).all()
    return [{"card_id": c, "count": cnt} for c, cnt in picks]

@router.get(
    "/cardWinrate",
    summary="Highest Winrate Cards.",
    description="Returns highest win rate cards, with minimum pick count, starter cards are excluded."
)
def card_winrate(limit: int = 100, minPicks: int = 0, db: Session = Depends(get_db)):
    results = db.query(
        CardPick.card_id,
        func.count(CardPick.id).label("pick_count"),
        func.sum(Run.victory).label("win_count")
    ).join(Run, Run.id == CardPick.run_id)\
     .filter(
         CardPick.was_picked == True,
         CardPick.card_id.not_in(list(IGNORE_CARDS))
     )\
     .group_by(CardPick.card_id)\
     .having(func.count(CardPick.id) >= minPicks)\
     .all()

    sorted_results = sorted(
        results,
        key=lambda x: (x.win_count / x.pick_count) if x.pick_count > 0 else 0,
        reverse=True
    )[:limit]

    return [
        {
            "card_id": r.card_id,
            "times_picked": r.pick_count,
            "wins": r.win_count,
            "win_rate": r.win_count / r.pick_count if r.pick_count > 0 else 0
        }
        for r in sorted_results
    ]

# Relics
@router.get("/topRelics",
    summary="Most Picked Relics.",
    description="Returns most picked relics sorted by descending pick count, starter relics are excluded."
)
def top_relics(limit: int = 100, db: Session = Depends(get_db)):
    picks = db.query(
        RelicPick.relic_id,
        func.count(RelicPick.id).label("pick_count")
    ).filter(
        RelicPick.relic_id.not_in(list(IGNORE_RELICS))
    ).group_by(RelicPick.relic_id)\
     .order_by(func.count(RelicPick.id).desc())\
     .limit(limit).all()
    return [{"relic_id": r, "count": cnt} for r, cnt in picks]

@router.get("/relicWinrate",
    summary="Highest Winrate Relics.",
    description="Returns highest win rate relics, with minimum pick count, starter relics are excluded."
)
def relic_winrate(limit: int = 100, minPicks: int = 0, db: Session = Depends(get_db)):
    results = db.query(
        RelicPick.relic_id,
        func.count(RelicPick.id).label("pick_count"),
        func.sum(Run.victory).label("win_count")
    ).join(Run, Run.id == RelicPick.run_id)\
     .filter(RelicPick.relic_id.not_in(list(IGNORE_RELICS)))\
     .group_by(RelicPick.relic_id)\
     .having(func.count(RelicPick.id) >= minPicks)\
     .all()

    sorted_results = sorted(
        results,
        key=lambda x: (x.win_count / x.pick_count) if x.pick_count > 0 else 0,
        reverse=True
    )[:limit]

    return [
        {
            "relic_id": r.relic_id,
            "times_picked": r.pick_count,
            "wins": r.win_count,
            "win_rate": r.win_count / r.pick_count if r.pick_count > 0 else 0
        }
        for r in sorted_results
    ]