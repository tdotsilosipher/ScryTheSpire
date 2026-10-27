# backend/schemas.py
# Validates request data
# Fix and define SQLAlchemy outputs to API JSON

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any

class CardPickBase(BaseModel):
    card_id: str
    floor_added: int
    upgrade_level: int
    enchantment: Optional[Any] = None
    was_picked: bool = True

class CardPick(CardPickBase):
    id: int
    run_id: int

    class Config:
        from_attributes = True

class RelicPickBase(BaseModel):
    relic_id: str
    floor_added: int
    props: Optional[Any] = None

class RelicPick(RelicPickBase):
    id: int
    run_id: int

    class Config:
        from_attributes = True

class RunBase(BaseModel):
    character: str
    ascension: int
    victory: bool
    floor_reached: int
    seed: str
    run_time: int
    start_time: datetime
    platform: str
    build_id: str
    game_mode: str
    was_abandoned: bool
    killed_by_encounter: Optional[str] = None
    killed_by_event: Optional[str] = None
    full_history: Optional[Any] = None

class Run(RunBase):
    id: int
    cards: List[CardPick] = []
    relics: List[RelicPick] = []

    class Config:
        from_attributes = True