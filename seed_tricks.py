import json
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def seed_tricks():
    """Poblar la base de datos con trucos desde el archivo JSON"""
    db = SessionLocal()
    
    try:
        # Leer el archivo JSON
        with open('highline_tricks.json', 'r', encoding='utf-8') as f:
            tricks_data = json.load(f)
        
        # Limpiar trucos existentes
        db.query(models.Trick).delete()
        
        # Insertar trucos por nivel
        for level_str, tricks_list in tricks_data.items():
            level = int(level_str)
            for trick_name in tricks_list:
                trick = models.Trick(name=trick_name, level=level)
                db.add(trick)
        
        db.commit()
        print(f"✅ Trucos insertados exitosamente")
        
    except Exception as e:
        print(f"❌ Error al insertar trucos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_tricks()

