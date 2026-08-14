# import_history.py
import os
import glob
import json
from database import SessionLocal, engine
from models import Base, Run
from import_runner import parse_run_data

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

HISTORY_PATH = r"C:\Program Files (x86)\Steam\userdata\180100533\2868840\remote\profile1\saves\history"

def main():
    db = SessionLocal()
    files = glob.glob(os.path.join(HISTORY_PATH, "*.RUN"))
    print(f"Found {len(files)} .RUN files")

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            seed = data.get("seed")
            if db.query(Run).filter(Run.seed == seed).first():
                print(f"Skipping {file_path} (seed {seed} already imported)")
                continue

            run = parse_run_data(data, db)
            print(f"Imported {file_path} -> {run.character} (floors: {run.floor_reached})")
        except Exception as e:
            print(f"Error with {file_path}: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    main()