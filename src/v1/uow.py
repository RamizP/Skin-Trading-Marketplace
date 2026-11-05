# order/infra/unit_of_work.py
from sqlalchemy import text
from sqlalchemy.orm import Session


class UnitOfWork:
    def begin(self): ...
    def commit(self): ...
    def rollback(self): ...


class SQLiteUnitOfWork(UnitOfWork):
    def __init__(self, db: Session):
        self.session = db

    def begin(self):
        self.session.execute(text("BEGIN IMMEDIATE;"))

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
