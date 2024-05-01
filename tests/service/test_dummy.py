import pytest


@pytest.fixture()
def mongo_item(monkeypatch):
    pass


def test_hello_world(mongo_item):
    assert 1 == 1
