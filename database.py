from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    role = Column(String)  # user, assistant, o system
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_message(db, user_id: str, role: str, content: str):
    """Agrega un mensaje a la base de datos."""
    message = Conversation(
        user_id=user_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    return message

def get_user_history(db, user_id: str, limit: int = 3):
    """Obtiene el historial de mensajes de un usuario."""
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
        .all()
    )
