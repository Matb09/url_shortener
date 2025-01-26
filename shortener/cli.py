# shortener/cli.py
import argparse
from .service import UrlShortenerService
from .repository import UrlRepository
from .exceptions import UrlNotFoundOrExpired

def parse_args():
    parser = argparse.ArgumentParser(description="URL Shortener Tool")
    parser.add_argument('--minify', type=str, help='URL to shorten')
    parser.add_argument('--expand', type=str, help='Shortened URL to expand')

    # Default TTL of 120 seconds, but user can override
    parser.add_argument('--expire', type=int, default=120, help='Expiration in seconds')

    parser.add_argument('--base-url', type=str, default='https://myurlshortener.com',
                        help='Base URL for short links')
    return parser.parse_args()

def main():
    args = parse_args()
    repo = UrlRepository()
    service = UrlShortenerService(args.base_url, args.expire, repo)

    if args.minify:
        short_url = service.minify_url(args.minify)
        print(f"Shortened URL: {short_url}")

    elif args.expand:
        try:
            original_url = service.expand_url(args.expand)
            print(f"Original URL: {original_url}")
        except UrlNotFoundOrExpired as e:
            print(str(e))
    else:
        print("Please use either --minify=<URL> or --expand=<SHORT_URL>")
