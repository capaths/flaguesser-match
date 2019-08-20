import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nameko.testing.services import worker_factory
from match.service import MatchService
from match.models import DeclarativeBase, MatchRepository, Match

USER = lambda x: f"User{x}"

SCORE_LOW = 3
SCORE_HIGH = 17


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    DeclarativeBase.metadata.create_all(engine)

    session_cls = sessionmaker(bind=engine)
    rep = MatchRepository(session_cls())
    rep.create_match(USER("A"), USER("B"), SCORE_LOW, SCORE_HIGH, 2)

    return rep


def test_match(session):
    service = worker_factory(MatchService, rep=session)

    assert len(service.get_player_matches(USER("A"))) == 1
    assert len(service.get_player_matches(USER("B"))) == 1
    assert len(service.get_player_matches(USER("C"))) == 0

    assert service.create_match(USER("A"), USER("C"), SCORE_LOW, SCORE_HIGH)

    assert len(service.get_player_matches(USER("A"))) == 2
    assert len(service.get_player_matches(USER("B"))) == 1
    assert len(service.get_player_matches(USER("C"))) == 1

    assert service.create_match(USER("D"), USER("E"), SCORE_LOW, SCORE_HIGH)
    assert service.get_player_matches(USER("D"))[0].result == 2

    assert service.create_match(USER("F"), USER("G"), SCORE_HIGH, SCORE_LOW)
    assert service.get_player_matches(USER("F"))[0].result == 1

    assert service.create_match(USER("H"), USER("I"), SCORE_HIGH, SCORE_HIGH)
    assert service.get_player_matches(USER("H"))[0].result == 0

    assert len(service.get_all_matches()) == 5


def test_flags():
    service = worker_factory(MatchService, rep=session)

    flags = service.get_flags(n_flags=20)
    assert len(flags) == 20

    names = list(map(lambda d : d["name"], flags))
    assert len(set(names)) == 20
