# **URL Shortener CLI**

A simple Python URL shortener that uses MongoDB for storage and includes an automatic expiration mechanism using MongoDB’s TTL index.

### Overview

This CLI application provides two primary commands:

* **Minify (--minify)**: Given a long URL, generate a shorter URL (and store it in MongoDB).
* **Expand (--expand)**: Given a shortened URL, retrieve the original long URL.

Each short URL has an expiration time. When the expiration passes, MongoDB automatically removes the document using a TTL index, and attempts to expand it will fail.

### Features

* **Automatic Expiration**: Uses expires_at and a TTL index in MongoDB to remove expired links.
* **Customizable TTL**: Default expiration is 120 seconds, but you can override it via --expire CLI argument.
* **Unique Short Codes**: Randomly generated 6-character alphanumeric codes, guaranteed unique in the database.
* **Docker & Docker-Compose**: Easily spin up both the application and a MongoDB instance.
* **Pytest Support**: Unit tests to verify functionality.

### Project Structure
```bash
url_shortener/
├── shortener/
│   ├── __init__.py
│   ├── cli.py          <-- CLI logic & argument parsing
│   ├── exceptions.py   <-- Custom exception classes
│   ├── repository.py   <-- MongoDB repository (handles DB connections/queries)
│   └── service.py      <-- Core business logic (shortening, expanding)
├── tests/
│   ├── test_service.py <-- Unit tests (pytest)
│   └── __init__.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── main.py          
```

### Prerequisites

* Python 3.9+ installed locally (if running outside of Docker).
* MongoDB accessible (if not using Docker, ensure it’s running on localhost or your preferred host).
* Docker & Docker Compose installed (if running in containers).

### How to use
* Clone, run and exec into the container
```bash
git clone https://github.com/your-username/url_shortener.git
cd url_shortener
docker-compose up -d --build
docker exec -it url-shortener bash
```

* Run the CLI
```bash
# Minify a URL with the default 120s TTL
python main.py --minify="https://www.google.com"

# Minify a URL with a custom TTL (e.g., 300 seconds)
python main.py --minify="https://www.amazon.com" --expire=300

# Expand a previously shortened URL
python main.py --expand="https://myurlshortener.com/abc123"
```

### Configuration
* **Default TTL**: 120 seconds. Override with --expire=N.
* **Base URL**: Defaults to https://myurlshortener.com. Override with --base-url="https://yourdomain.com".
* **Mongo URI**: The code reads MONGO_URI from environment variables. By default, it uses mongodb://localhost:27017.


### Testing
This project uses pytest for unit tests
```bash
docker-compose exec url-shortener pytest tests/
```

Note: Because MongoDB’s TTL monitor may take up to 60 seconds to remove expired docs, expiration tests can be non-deterministic if you rely on immediate removal. Some tests use a time offset or wait a short interval to demonstrate the concept.

### Notes on TTL

* **TTL Interval**: MongoDB’s TTL cleanup runs every 60 seconds by default. So a document may remain in the collection up to a minute past its expires_at time.
* **Custom TTL**: Each new short URL document has a custom expires_at = created_at + expiration_seconds. If you pass --expire=300, your short URL will be removed about 300 seconds after creation, depending on the TTL monitor cycle.
* **Concurrency**: In a high-concurrency scenario, two processes might generate the same random code in parallel. Both check the database, see that it doesn’t exist, and then both try to insert. Because the database has a unique index on short_code, the second insert will fail with a DuplicateKeyError. It’s not a big deal for small-scale usage, but in a large-scale scenario, we may want to catch that DB exception and retry generating a code.
* **Production vs. Test DB**: In real usage, we probably want separate MongoDB databases for test vs. production. we could parameterize our UrlRepository so that if ENV=test, it connects to a url_shortener_test_db, and if ENV=prod, it connects to url_shortener_db. This way, test runs don’t pollute production data.