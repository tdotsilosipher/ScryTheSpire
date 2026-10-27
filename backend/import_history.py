# import_history.py
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from database import SessionLocal, engine
from models import Base, Run
from import_runner import parse_run_data

load_dotenv()

APP_ID = "2868840"
PROFILE = "profile1"


def find_steam_root() -> Path:
    """Locate the Steam installation directory on Windows."""
    env = os.getenv("STEAM_PATH")
    if env:
        p = Path(env)
        if (p / "userdata").is_dir():
            return p

    import winreg
    for hive, subkey, value in [
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Valve\Steam", "SteamPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
    ]:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                p = Path(winreg.QueryValueEx(key, value)[0])
            if (p / "userdata").is_dir():
                return p
        except OSError:
            pass

    for p in [Path(r"C:\Program Files (x86)\Steam"), Path(r"C:\Program Files\Steam")]:
        if (p / "userdata").is_dir():
            return p

    raise RuntimeError("Could not locate Steam. Set STEAM_PATH in .env")


def find_userdata(steam_root: Path) -> Path:
    """Pick the right userdata subfolder (numeric Steam ID)."""
    userdata = steam_root / "userdata"

    env_id = os.getenv("STEAM_USER_ID")
    if env_id and (userdata / env_id).is_dir():
        return userdata / env_id

    for child in userdata.iterdir():
        if child.is_dir() and child.name.isdigit():
            return child

    raise RuntimeError("No Steam userdata folder found.")


def get_history_path() -> Path:
    root = find_steam_root()
    user_dir = find_userdata(root)
    return user_dir / APP_ID / "remote" / PROFILE / "saves" / "history"


def main() -> None:
    Base.metadata.create_all(bind=engine)

    history_path = get_history_path()
    files = [
        p for p in history_path.iterdir()
        if p.is_file() and p.suffix.lower() == ".run"
    ]

    db = SessionLocal()
    try:
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                seed = data.get("seed")
                if not seed:
                    continue

                if db.query(Run).filter(Run.seed == seed).first():
                    continue

                parse_run_data(data, db)

            except Exception:
                db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()