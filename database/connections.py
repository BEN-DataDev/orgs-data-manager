import os
from sqlalchemy import create_engine
from dotenv import dotenv_values

# Load values directly from the .env file
config = dotenv_values()


PG13_CONNECTION = str(config.get("PG13_URL", "postgresql+pg8000://postgres:postgres@127.0.0.1:5433/community_mapping"))
PG17_CONNECTION = str(config.get("PG17_URL", "postgresql+pg8000://postgres:postgres@127.0.0.1:5432/postgres"))


pg13_engine = create_engine(PG13_CONNECTION, pool_pre_ping=True)
pg17_engine = create_engine(PG17_CONNECTION, pool_pre_ping=True)