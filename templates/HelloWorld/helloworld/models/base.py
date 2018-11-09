import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData


SCHEMA_NAME = os.environ['SCHEMA_NAME']

metadata = MetaData(schema=SCHEMA_NAME)
Base = declarative_base(metadata=metadata)
