from typing import List, Protocol

import logging
import os
from pathlib import Path

import pandas as pd
import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

from schedulebot.db.models import metadata


class Table(Protocol):
    pass


class DatabaseClient:
    """SQLite database client implementation."""

    key = "DB_DPATH"

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

        load_dotenv()
        self.db_dpath = os.getenv(self.key)
        if self.db_dpath is None:
            raise ValueError(f"'{self.key}' env variable is not found")
        self.db_dpath = Path(self.db_dpath)
        self.db_dpath.mkdir(parents=True, exist_ok=True)

        self.db_fpath = self.db_dpath / "data.db"
        self._engine = sql.create_engine(f"sqlite:///{self.db_fpath}")

        self._session = sessionmaker(bind=self._engine)

        metadata.create_all(self._engine)
        self._logger.info(f"The engine {self.db_fpath} was created successfully")

    def add_df(self, df: pd.DataFrame, table_name: str, if_exist: str = "append"):
        """Load data from DataFrame into sql-table."""

        with self._engine.begin() as connection:
            df.to_sql(name=table_name, con=connection, if_exists=if_exist, index=False)

    def get_id_list(self, table: Table) -> List[int]:
        """Get list of unique ID values from the specified table."""

        with self._session() as session:
            ids = [val[0] for val in session.query(table.id).distinct()]
        return ids

    def add_record(self, record):
        """Add new row into the table."""

        with self._session() as session:
            session.add(record)
            session.commit()

    def get_id(self, table: Table, conditions: list):
        """Get record ID."""

        with self._session() as session:
            record = session.query(table).filter(and_(*conditions))[0]
        return record.id

    def get_filter_ids(self, table: Table, conditions: list):
        # TODO: unify get_id and get_filter_ids
        with self._session() as session:
            record = session.query(table).filter(and_(*conditions))
        filter_ids = [rec.id for rec in record]
        return filter_ids
