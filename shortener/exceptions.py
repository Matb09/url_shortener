# shortener/exceptions.py
class UrlNotFoundOrExpired(Exception):
    """Exception indicating that a short URL was not found or its link has expired."""
    pass
