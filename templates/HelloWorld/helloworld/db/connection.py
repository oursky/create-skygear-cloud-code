from contextlib import contextmanager
import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.environ['DATABASE_URL']

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = sa.create_engine(DATABASE_URL)
    return _engine


Session = sessionmaker(bind=_get_engine())


@contextmanager
def open_session():
    session = Session()
    yield session
    try:
        session.commit()
    except: # noqa
        session.rollback()
        raise
    finally:
        session.close()
