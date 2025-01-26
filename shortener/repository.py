# shortener/repository.py

import os
import random
import string
from datetime import datetime, timedelta

from pymongo import MongoClient

class UrlRepository:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.client = MongoClient(mongo_uri)
        self.db = self.client["url_shortener_db"]
        self.collection = self.db["urls"]

        # unique index on short_code
        self.collection.create_index("short_code", unique=True)

        # Calling create_index multiple times with
        # the same definition (same fields, options, etc.)
        # doesn’t create duplicate indexes.
        # MongoDB will return the index name if it already exists.
        self.collection.create_index(
            "expires_at",
            expireAfterSeconds=0
        )

    def find_by_short_code(self, short_code: str):
        """
        Returns a document if it exists (and not yet removed by TTL).
        """
        return self.collection.find_one({"short_code": short_code})

    def find_by_original_url(self, original_url: str):
        """
        Returns a document if it exists (and not yet removed by TTL).
        """
        return self.collection.find_one({"original_url": original_url})

    def save_url_mapping(self, short_code: str, original_url: str,
                         created_at: datetime, expiration_seconds: int):
        """
        Insert a new document with an expires_at field, so MongoDB TTL can remove it.
        """
        expires_at = created_at + timedelta(seconds=expiration_seconds)

        doc = {
            "short_code": short_code,
            "original_url": original_url,
            "created_at": created_at,
            "expires_at": expires_at
        }
        self.collection.insert_one(doc)

    def generate_unique_short_code(self, length=6) -> str:
        """
        Generate a random alphanumeric short code of given length.
        """
        chars = string.ascii_letters + string.digits
        while True:
            short_code = ''.join(random.choice(chars) for _ in range(length))
            if not self.find_by_short_code(short_code):
                return short_code
