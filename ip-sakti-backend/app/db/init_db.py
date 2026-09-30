import json
from pathlib import Path
from sqlalchemy import inspect, text
from app.db.database import Base, engine, SessionLocal
from app.models.tkdl_demo import TKDLDemoModel
from app.models.user import UserModel
from app.models.session import SessionModel
from app.models.query_log import QueryLogModel
from app.models.escalation import EscalationModel
from app.models.paid_source import PaidSourceConsentModel

def init_db(db=None):
    # Create all tables (users, sessions, query_logs, escalations, tkdl_demo)
    bind = db.get_bind() if db is not None else engine
    Base.metadata.create_all(bind=bind)
    _add_missing_columns(bind)
    
    # Seed TKDL illustrative records if empty
    owns_session = db is None
    db = db or SessionLocal(bind=bind)
    try:
        count = db.query(TKDLDemoModel).count()
        if count == 0:
            seed_file = Path(__file__).resolve().parent.parent.parent / "corpus" / "seed_data" / "tkdl_demo_records.json"
            if seed_file.exists():
                with open(seed_file, "r", encoding="utf-8") as f:
                    records = json.load(f)
                    for item in records:
                        rec = TKDLDemoModel(
                            formulation_keyword=item["formulation_keyword"],
                            classification=item["classification"],
                            matched_note=item["matched_note"],
                            is_illustrative=True
                        )
                        db.add(rec)
                    db.commit()
    finally:
        if owns_session:
            db.close()


def _add_missing_columns(bind):
    """Add additive tracking columns when upgrading an existing deployment."""
    additions = {
        "users": {
            "last_login_at": "TIMESTAMP",
            "login_count": "INTEGER NOT NULL DEFAULT 0",
        },
        "sessions": {"user_id": "VARCHAR(36)"},
        "query_logs": {"user_id": "VARCHAR(36)"},
        "escalations": {
            "user_id": "VARCHAR(36)",
            "assigned_expert_id": "VARCHAR(36)",
        },
    }
    inspector = inspect(bind)
    with bind.begin() as connection:
        for table_name, columns in additions.items():
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_type in columns.items():
                if column_name not in existing:
                    connection.execute(text(
                        f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type}'
                    ))

if __name__ == "__main__":
    init_db()
