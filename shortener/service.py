# shortener/service.py

from datetime import datetime
from .repository import UrlRepository
from .exceptions import UrlNotFoundOrExpired

class UrlShortenerService:
    def __init__(self, base_url: str, expiration_seconds: int, repo: UrlRepository):
        """
        :param base_url: e.g., 'https://myurlshortener.com'
        :param expiration_seconds: e.g., 120 for 2 minutes expiration
        :param repo: an instance of UrlRepository
        """
        self.base_url = base_url
        self.expiration_seconds = expiration_seconds
        self.repo = repo

    def minify_url(self, original_url: str) -> str:
        """
        If the URL already exists in the DB (and is not yet TTL-removed),
        return the existing short link.
        Otherwise, create a new doc with an expires_at field.
        """
        existing_doc = self.repo.find_by_original_url(original_url)
        if existing_doc:
            # Document still in DB => Not expired
            short_code = existing_doc["short_code"]
        else:
            # Create a new short code and store it with expires_at
            short_code = self.repo.generate_unique_short_code()
            now = datetime.utcnow()
            self.repo.save_url_mapping(short_code, original_url, now, self.expiration_seconds)

        return f"{self.base_url}/{short_code}"

    def expand_url(self, short_url: str) -> str:
        """
        Parses the short code from short_url, checks DB.
        If the doc doesn't exist, it has likely been expired or never existed.
        """
        short_code = short_url.rsplit('/', 1)[-1]

        doc = self.repo.find_by_short_code(short_code)
        if not doc:
            raise UrlNotFoundOrExpired(
                f"Short URL {short_url} does not exist or has expired."
            )

        return doc['original_url']
