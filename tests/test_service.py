# tests/test_service.py

import pytest
import time
from datetime import datetime, timedelta

from shortener.service import UrlShortenerService
from shortener.repository import UrlRepository
from shortener.exceptions import UrlNotFoundOrExpired

@pytest.fixture
def repo():
    # In real usage, you might connect to a separate test DB
    # and drop it before/after tests.
    return UrlRepository()

@pytest.fixture
def service(repo):
    return UrlShortenerService(
        base_url="https://myurlshortener.com",
        expiration_seconds=5,
        repo=repo
    )

def test_minify_url(service):
    original_url = "https://www.example.com/test"
    short_url = service.minify_url(original_url)
    assert short_url.startswith("https://myurlshortener.com/"), "Incorrect base URL"

def test_expand_url(service):
    original_url = "https://www.example.com/test_expand"
    short_url = service.minify_url(original_url)
    expanded_url = service.expand_url(short_url)
    assert expanded_url == original_url, "Expanded URL does not match original"

def test_expiration(service):
    """
    Demonstrate TTL-based expiration.
    Mongo's internal TTL monitor typically runs once a minute.
    For a reliable test, we either:
      - artificially back-date the doc's expires_at, or
      - wait enough time (which may be up to 60+ seconds).
    """

    original_url = "https://www.example.com/expire"
    short_url = service.minify_url(original_url)

    # Artificially update the document so it expires immediately (back-dating expires_at).
    doc = service.repo.find_by_original_url(original_url)
    now = datetime.utcnow()
    # Set expires_at to 1 second in the past
    new_expires_at = now - timedelta(seconds=1)

    service.repo.collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"expires_at": new_expires_at}}
    )

    # Wait a bit to allow the TTL monitor to remove it
    # This might take up to 60 seconds by default.
    time.sleep(61)

    # Now attempt expand; we expect the doc to be removed or not found
    with pytest.raises(UrlNotFoundOrExpired) as e:
        service.expand_url(short_url)
    assert "does not exist or has expired" in str(e.value)
