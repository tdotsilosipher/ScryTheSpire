from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    character = Column(String)
    ascension = Column(Integer)
    victory = Column(Boolean)
    floor_reached = Column(Integer)
    seed = Column(String)
    run_time = Column(Integer)
    start_time = Column(DateTime)
    platform = Column(String)
    build_id = Column(String)
    game_mode = Column(String)
    was_abandoned = Column(Boolean)
    killed_by_encounter = Column(String, nullable=True)
    killed_by_event = Column(String, nullable=True)
    full_history = Column(JSON, nullable=True)       # all act/room data

    cards = relationship("CardPick", back_populates="run")
    relics = relationship("RelicPick", back_populates="run")

class CardPick(Base):
    __tablename__ = "card_picks"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    card_id = Column(String)
    floor_added = Column(Integer)
    upgrade_level = Column(Integer, default=0)
    enchantment = Column(JSON, nullable=True)
    was_picked = Column(Boolean, default=True)
    run = relationship("Run", back_populates="cards")

class RelicPick(Base):
    __tablename__ = "relic_picks"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    relic_id = Column(String)
    floor_added = Column(Integer)
    props = Column(JSON, nullable=True)
    run = relationship("Run", back_populates="relics")