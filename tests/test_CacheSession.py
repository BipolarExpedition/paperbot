import os
import shutil
import pytest

from paperbot import caching


@pytest.fixture(scope="function", autouse=True)
def clean_tts_cache():
    cache_dir = "tts_cache"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)


def test_is_incache():
    text = b"hello world"
    cache = caching.CacheSession()
    bres = cache.is_incache(text)
    assert not bres
    cache.add_to_cache(text, b"data")
    assert cache.is_incache(text)


def test_get_size():
    data = b"hello world"

    assert caching.CacheSession.get_size(data) == len(data)

    assert caching.CacheSession.get_size(__file__) == os.path.getsize(__file__)


def test_get_cached_size():
    text = b"hello world"
    cache = caching.CacheSession()
    assert cache.get_cached_size(text) == -1

    cache.add_to_cache(text, b"data")
    assert cache.get_cached_size(text) == len(b"data")


def test_get_cached_data():
    text = b"hello world"
    data = b"data"
    cache = caching.CacheSession()
    with pytest.raises(ValueError):
        cache.get_cached_data(text)

    cache.add_to_cache(text, data)
    assert cache.get_cached_data(text) == data


def test_clear_cache():
    text = b"hello world"
    cache = caching.CacheSession()
    cache.add_to_cache(text, b"data")
    cache.clear_cache()
    assert not cache.is_incache(text)


def test_remove_from_cache():
    text = b"hello world"
    cache = caching.CacheSession()
    cache.add_to_cache(text, b"data")
    cache.remove_from_cache(text)
    assert not cache.is_incache(text)


def test_add_to_cache():
    text = b"hello world"
    data = b"data"
    cache = caching.CacheSession()
    cache.add_to_cache(text, data)
    assert cache.get_cached_size(text) == len(data)
