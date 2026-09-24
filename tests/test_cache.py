import pytest

from flask_forge import Cache
from flask_forge.exceptions import MissingDataError


def test_cache_setting_and_set_alias():
    cache = Cache(max_size=2)
    cache.setting("a", 1)
    cache.set("b", 2)
    assert cache.get("a") == 1
    assert cache.get("b") == 2


def test_cache_lru_eviction():
    cache = Cache(max_size=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.get("a")
    cache.set("c", 3)
    assert cache.has("a")
    assert not cache.has("b")
    assert cache.has("c")


def test_cache_get_or_raise():
    cache = Cache()
    with pytest.raises(MissingDataError):
        cache.get_or_raise("missing")
