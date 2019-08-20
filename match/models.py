from sqlalchemy import (
    Column, DateTime, Integer, String
)


import os
from sqlalchemy import create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from nameko.extensions import DependencyProvider
import datetime


def get_url():
    return (
        "postgresql://{db_user}:{db_pass}@{db_host}:"
        "{db_port}/{db_name}"
    ).format(
        db_user=os.getenv("DB_USER", "postgres"),
        db_pass=os.getenv("DB_PASSWORD", "password"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=os.getenv("DB_PORT", "5432"),
        db_name=os.getenv("DB_NAME", "match"),
    )


DeclarativeBase = declarative_base()


class Match(DeclarativeBase):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username1 = Column(String)
    username2 = Column(String)
    scoreP1 = Column(Integer)
    scoreP2 = Column(Integer)
    result = Column(Integer)
    match_end = Column(DateTime, default=datetime.datetime.utcnow)


class MatchRepository:
    db: Session = None

    def __init__(self, db):
        self.db = db

    def create_match(self, username1: str, username2: str, score1: int, score2: int, result: int):
        match = Match(username1=username1, username2=username2,
                      scoreP1=score1, scoreP2=score2, result=result)

        try:
            self.db.add(match)
            self.db.commit()
            return True
        except Exception:
            return False

    def get_player_matches(self, username: str):
        matches = self.db.query(Match)\
            .filter(or_(Match.username1 == username, Match.username2 == username))\
            .all()
        return matches

    def get_all_matches(self):
        matches = self.db.query(Match).order_by(Match.match_end).all()
        return matches


class MatchDatabase(DependencyProvider):
    db = None

    def setup(self):
        engine = create_engine(get_url())
        DeclarativeBase.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        self.db = session()

    def get_dependency(self, worker_ctx):
        return MatchRepository(self.db)
