from src.shared.db.config.base import Base
from src.shared.db.config.connection import engine
from src.shared.db.config.session import SessionLocal


def init_db() -> None:
    import src.shared.db.models

    Base.metadata.create_all(bind=engine)