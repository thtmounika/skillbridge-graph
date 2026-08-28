import os
from contextlib import contextmanager

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USER", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")

if not URI or not PASSWORD:
    driver = None
else:
    driver = GraphDatabase.driver(
        URI,
        auth=(USER, PASSWORD),
        max_connection_pool_size=10,
    )


def verify_connection():
    if driver is None:
        raise RuntimeError("CognoDB credentials are not configured.")
    driver.verify_connectivity()


@contextmanager
def session():
    if driver is None:
        raise RuntimeError("CognoDB credentials are not configured.")
    s = driver.session()
    try:
        yield s
    finally:
        s.close()


def close():
    if driver is not None:
        driver.close()
