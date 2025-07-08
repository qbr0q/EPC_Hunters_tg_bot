from db.models import engine
from sqlmodel import Session, select


def get_records(table, filters=None, all_rows=False):
    with Session(engine) as session:
        stmt = select(table)
        if filters:
            for field, value in filters.items():
                stmt = stmt.where(getattr(table, field) == value)
        if all_rows:
            records = session.exec(stmt).all()
        else:
            records = session.exec(stmt).one()
        return records


def insert_or_update_record(record):
    with Session(engine) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
