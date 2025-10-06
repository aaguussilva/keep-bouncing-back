import json
from app.database import SessionLocal
from app.models import trick

def seed_tricks():
    db = SessionLocal()
    try:
        with open('highline_tricks.json', 'r', encoding='utf-8') as file:
            tricks_by_level = json.load(file)
            inserted = 0
            for level, tricks_list in tricks_by_level.items():
                for name in tricks_list:
                    if not db.query(trick.Trick).filter_by(name=name).first():
                        db.add(trick.Trick(name=name, level=int(level)))
                        inserted += 1
            db.commit()
            print(f"{inserted} trucos insertados correctamente.")
    except Exception as e:
        print(f"Error al insertar trucos: {e}")
        db.rollback()
    finally:
        db.close()
