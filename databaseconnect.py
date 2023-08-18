from sqlalchemy import create_engine
import os


def get_engine():
    user = os.getenv("USER")
    passwd = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    db = os.getenv("DATABASE")
    dialect = "postgresql"
    driver = "psycopg2"
    port = "5432"

    url = f"{dialect}+{driver}://{user}:{passwd}@{host}:{port}/{db}"
    # if not database_exists(url):
    #    create_database(url)
    engine = create_engine(url, pool_size=50, echo=False)
    return [url, engine]
