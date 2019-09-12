import time

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


def test_match_storage(session):
    service = worker_factory(MatchService, rep=session)

    # check player start matches (after fixture)
    assert len(service.get_player_matches(USER("A"))) == 1
    assert len(service.get_player_matches(USER("B"))) == 1
    assert len(service.get_player_matches(USER("C"))) == 0

    # save new match
    assert service.end_match(USER("A"), USER("C"), SCORE_LOW, SCORE_HIGH)

    # check new match is added
    assert len(service.get_player_matches(USER("A"))) == 2
    assert len(service.get_player_matches(USER("B"))) == 1
    assert len(service.get_player_matches(USER("C"))) == 1

    # check if 2 wins against 1, then result is 2
    assert service.end_match(USER("D"), USER("E"), SCORE_LOW, SCORE_HIGH)
    assert service.get_player_matches(USER("D"))[0]["result"] == 2

    # check if 1 wins against 2, then result is 1
    assert service.end_match(USER("F"), USER("G"), SCORE_HIGH, SCORE_LOW)
    assert service.get_player_matches(USER("F"))[0]["result"] == 1

    # check if draw, then result is 0
    assert service.end_match(USER("H"), USER("I"), SCORE_HIGH, SCORE_HIGH)
    assert service.get_player_matches(USER("H"))[0]["result"] == 0

    # check all matches have been added
    assert len(service.get_all_matches()) == 5


def test_flags():
    service = worker_factory(MatchService, rep=session)

    code_a = service.generate_match_code(USER("A"), USER("B"), time.time())
    time.sleep(1)
    code_b = service.generate_match_code(USER("A"), USER("B"), time.time())

    flags_a = service.get_flags(code_a, n_flags=30)
    flags_b = service.get_flags(code_b, n_flags=30)

    # there are 30 flags
    assert len(flags_a[0]) == 30
    assert len(flags_a[1]) == 30

    assert len(flags_b[0]) == 30
    assert len(flags_b[1]) == 30

    # flags are different
    assert len(set(flags_a[1])) == 30
    assert len(set(flags_b[1])) == 30

    # for different codes, different flags
    assert len(set(flags_a[1]).union(set(flags_b[1]))) > 30


def test_match_progress(session):
    service = worker_factory(MatchService, rep=session)

    # check codes are different in different conditions
    start_time = time.time()
    code_a = service.generate_match_code(USER("A"), USER("B"), start_time)
    code_b = service.generate_match_code(USER("A"), USER("C"), start_time)
    code_c = service.generate_match_code(USER("B"), USER("C"), start_time)

    assert code_a != code_b
    assert code_a != code_c
    assert code_b != code_c

    time.sleep(0.1)
    code_d = service.generate_match_code(USER("A"), USER("B"), time.time())

    assert code_a != code_d

    # simulate guess
    code = service.generate_match_code(USER("A"), USER("B"), time.time())

    flags_names, flags_urls = service.get_flags(code)

    assert service.guess_flag(code, "Wrong Country") is None

    for i in range(20):
        flag_url = service.guess_flag(code, flags_names[i])
        assert flag_url == flags_urls[i]
