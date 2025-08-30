
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, create_engine, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///app.db", future=True)
SessionLocal = sessionmaker(bind=engine, future=True)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    platform_id = Column(String, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    link = Column(Text)
    source = Column(String, default="linkedin")
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="new")      # new|applied|skipped|confirmed
    notes = Column(Text)

    __table_args__ = (UniqueConstraint("platform_id", "source"),)

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, index=True)
    submitted = Column(Boolean, default=False)
    confirmation_email_id = Column(String, nullable=True)
    confirmation_subject = Column(Text, nullable=True)
    confirmation_at = Column(DateTime, nullable=True)

def init_db():
    Base.metadata.create_all(engine)
