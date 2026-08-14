# import_runner.py
from datetime import datetime
from models import Run, CardPick, RelicPick

def parse_run_data(data, db):
    player = data["players"][0]
    character_short = player["character"].replace("CHARACTER.", "")

    start_dt = datetime.fromtimestamp(data["start_time"])

    # total rooms across all acts
    history = data.get("map_point_history", [])
    floor_reached = sum(len(act) for act in history)

    run = Run(
        character=character_short,
        ascension=data.get("ascension", 0),
        victory=data.get("win", False),
        floor_reached=floor_reached,
        seed=data.get("seed", ""),
        run_time=data.get("run_time", 0),
        start_time=start_dt,
        platform=data.get("platform_type", "unknown"),
        build_id=data.get("build_id", ""),
        game_mode=data.get("game_mode", "standard"),
        was_abandoned=data.get("was_abandoned", False),
        killed_by_encounter=data.get("killed_by_encounter"),
        killed_by_event=data.get("killed_by_event"),
        full_history=history,
    )

    # deck cards
    for card in player.get("deck", []):
        run.cards.append(CardPick(
            card_id=card["id"],
            floor_added=card.get("floor_added_to_deck", 0),
            upgrade_level=card.get("current_upgrade_level", 0),
            enchantment=card.get("enchantment"),
            was_picked=True
        ))

    # relics
    for relic in player.get("relics", []):
        run.relics.append(RelicPick(
            relic_id=relic["id"],
            floor_added=relic.get("floor_added_to_deck", 0),
            props=relic.get("props")
        ))

    db.add(run)
    db.commit()
    return run