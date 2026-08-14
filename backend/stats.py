# backend/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from database import SessionLocal
from models import Run, CardPick

router = APIRouter(prefix="/stats", tags=["stats"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.get("/winrate")
def winrate_by_character(db: Session = Depends(get_db)):
    # Group by character and compute win rate
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

@router.get("/top-cards")
def top_cards(limit: int = 100, db: Session = Depends(get_db)):
    # Count picks per card (only picked cards)
    picks = db.query(
        CardPick.card_id,
        func.count(CardPick.id).label("pick_count")
    ).filter(
        CardPick.was_picked == True,
        CardPick.card_id.not_in(list(IGNORE_CARDS))\
    ).group_by(CardPick.card_id)\
     .order_by(func.count(CardPick.id).desc())\
     .limit(limit).all()
    return [{"card_id": c, "count": cnt} for c, cnt in picks]

@router.get("/card-winrate")
def card_winrate(limit: int = 100, min_picks: int = 0, db: Session = Depends(get_db)):
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
     .having(func.count(CardPick.id) >= min_picks)\
     .all()

    # Compute win rate and sort in Python (to avoid complex SQL ordering)
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