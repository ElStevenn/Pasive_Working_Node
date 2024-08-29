from sqlalchemy import String, Float, DateTime, Text, ForeignKey, JSON, INT, Column
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship, DeclarativeBase
import uuid

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id = Column(String(255), primary_key=True)
    username = Column(String(40), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    email = Column(String(40), nullable=False, unique=True)
    country = Column(String(100), nullable=False)
    session_ips = Column(JSON, nullable=True)
    picture = Column(Text, nullable=True)

    alerts = relationship("Alert", back_populates="user")
    feargreedsubscription = relationship("FearGreedSubscription", back_populates="user")
    economic_calendar_alerts = relationship("EconomicCalendarAlerts", back_populates="user", uselist=False)
    user_configuration = relationship("UserConfiguration", back_populates="user", uselist=False)
    fear_greed_bot = relationship("FearGreedBot", back_populates="user", uselist=False)
    token_handle = relationship("TokenHandle", back_populates="user", uselist=False)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey('user.id'), nullable=False)
    execution_alert_datetime = Column(DateTime)
    type = Column(String(40), nullable=False)
    headline = Column(Text, nullable=True)
    message = Column(Text, nullable=False)

    user = relationship("User", back_populates="alerts")

class FearGreedSubscription(Base):
    __tablename__ = "feargreedsubscription"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey('user.id'), nullable=False)
    notification_level = Column(String(256), default="1")

    user = relationship("User", back_populates="feargreedsubscription")

class ErrorsLogs(Base):
    __tablename__ = "errors_logs"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(String(55), nullable=False)
    text = Column(Text, nullable=True)

class UserConfiguration(Base):
    __tablename__ = "user_configuration"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey('user.id'), nullable=False)
    cvi = Column(JSON)

    user = relationship("User", back_populates="user_configuration", uselist=False)

class FearGreedBot(Base):
    __tablename__ = "fear_greed_bot"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey('user.id'), nullable=False)
    level = Column(INT, nullable=False)

    user = relationship("User", back_populates="fear_greed_bot", uselist=False)

class EconomicCalendarAlerts(Base):
    __tablename__ = "economic_calendar_alerts"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey('user.id'), nullable=False)
    status = Column(String(255), default="pending")
    alert_name = Column(String(255))
    zone = Column(String(255))
    previous_value = Column(String(255))
    value = Column(String(255), nullable=True, default=None) 
    event_execution = Column(DateTime)
    timezone = Column(String(255))

    user = relationship("User", back_populates="economic_calendar_alerts", uselist=False)


class TokenHandle(Base):
    __tablename__ = "token_handle"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey('user.id'), nullable=False)
    oauth_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=False)
    main_service =  Column(String(255))

    user = relationship("User", back_populates="token_handle", uselist=False)


# MIGRATE MODEL
"""
 - alembic upgrade head
 - alembic revision --autogenerate -m "Updated models"
"""