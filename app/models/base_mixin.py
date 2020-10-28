import datetime

from sqlalchemy import Column, Integer, DateTime


class BaseMixin(object):
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)
